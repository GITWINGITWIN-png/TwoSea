from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
import numpy as np

from .coherence import COND_MAX, SpectraCache, mwc_cached
from .metrics import BANDS, MAX_FILLED_FRACTION, awc, band_rows, filled_fraction, pasc, significance

MAX_Q = 5


def prepare_station(d, station: str, max_filled: float = MAX_FILLED_FRACTION):
    from .transform import DJ, DT_MONTHLY, coi_mask, cwt
    y_names = [str(s) for s in d["y_names"]]
    x_names = [str(s) for s in d["x_names"]]
    iy = y_names.index(station)
    Wy, scales, periods, coi = cwt(d["Y"][iy])
    W = {"y": Wy, **{k: cwt(x)[0] for k, x in zip(x_names, d["X"])}}
    cache = SpectraCache(W, DT_MONTHLY, DJ, scales)
    ok = {"y": fill_ok(d["Y_fill"][iy], scales, DT_MONTHLY, Wy.shape, max_filled)}
    ok.update({k: fill_ok(f, scales, DT_MONTHLY, Wy.shape, max_filled)
               for k, f in zip(x_names, d["X_fill"])})
    return cache, periods, coi, scales, coi_mask(periods, coi), ok


def all_subsets(names, max_q: int = MAX_Q) -> list[tuple]:
    names = list(names)
    return [s for q in range(1, max_q + 1) for s in combinations(names, q)]


def fill_ok(filled: np.ndarray | None, scales: np.ndarray, dt: float, shape: tuple,
            max_filled: float = MAX_FILLED_FRACTION) -> np.ndarray:
    if filled is None or not np.any(filled):
        return np.ones(shape, bool)
    return filled_fraction(filled, scales, dt) <= max_filled


@dataclass
class SearchTable:
    subsets: list[tuple]
    q: np.ndarray
    pasc: np.ndarray
    pasc_fixed: np.ndarray
    awc: np.ndarray
    mean_r2: np.ndarray
    n_valid: np.ndarray
    n_nan: np.ndarray
    cond_max: np.ndarray


def evaluate_subsets(cache: SpectraCache, y, subsets, thr: dict[int, np.ndarray],
                     periods: np.ndarray, inside: np.ndarray, ok: dict,
                     check_cond: bool = True, cond_max: float = COND_MAX) -> SearchTable:
    subsets = [tuple(s) for s in subsets]
    nb = len(BANDS)
    out = SearchTable(subsets=subsets, q=np.array([len(s) for s in subsets]),
                      pasc=np.full((len(subsets), nb), np.nan),
                      pasc_fixed=np.full((len(subsets), nb), np.nan),
                      awc=np.full((len(subsets), nb), np.nan),
                      mean_r2=np.full(len(subsets), np.nan),
                      n_valid=np.zeros((len(subsets), nb), int),
                      n_nan=np.zeros(len(subsets), int),
                      cond_max=np.full(len(subsets), np.nan))
    rows = [band_rows(periods, band) for band in BANDS.values()]
    base = inside & ok.get(y, True)
    for i, s in enumerate(subsets):
        q = len(s)
        R2, cond = mwc_cached(cache, y, s, cond_max=cond_max, where=inside, check_cond=check_cond)
        finite = np.isfinite(R2)
        valid = base & finite
        for k in s:
            valid = valid & ok.get(k, True)
        sig_q = significance(R2, thr[q])
        sig_1 = significance(R2, thr[1])
        out.n_nan[i] = int((inside & ~finite).sum())
        if check_cond:
            out.cond_max[i] = float(np.nanmax(cond[inside]))
        if valid.any():
            out.mean_r2[i] = float(R2[valid].mean())
        for b, band in enumerate(BANDS.values()):
            out.n_valid[i, b] = int(valid[rows[b]].sum())
            out.pasc[i, b] = pasc(sig_q, valid, periods, band)
            out.pasc_fixed[i, b] = pasc(sig_1, valid, periods, band)
            out.awc[i, b] = awc(np.nan_to_num(R2), sig_q, valid, periods, band)
    return out


def best_per_q(q: np.ndarray, values: np.ndarray, allowed: np.ndarray | None = None
               ) -> dict[int, tuple[int, float]]:
    out = {}
    for k in np.unique(q):
        m = (q == k) & np.isfinite(values)
        if allowed is not None:
            m &= allowed
        if m.any():
            idx = np.flatnonzero(m)
            j = idx[np.argmax(values[idx])]
            out[int(k)] = (int(j), float(values[j]))
    return out


def reduce_per_q(q: np.ndarray, values: np.ndarray, allowed: np.ndarray | None = None
                 ) -> tuple[np.ndarray, np.ndarray]:
    qs = np.unique(q)
    mx = np.full((len(qs), values.shape[1]), np.nan)
    mean = np.full_like(mx, np.nan)
    for i, k in enumerate(qs):
        m = q == k
        if allowed is not None:
            m = m & allowed
        if m.any():
            mx[i] = np.nanmax(values[m], axis=0)
            mean[i] = np.nanmean(values[m], axis=0)
    return mx, mean


def gains(best: dict[int, tuple[int, float]]) -> dict[int, float]:
    return {q: best[q][1] - best[q - 1][1] for q in sorted(best) if q - 1 in best}


def within_of_max(values: np.ndarray, q: np.ndarray, tol: float = 1.0) -> int:
    top = np.nanmax(values)
    cand = np.flatnonzero(values >= top - tol)
    smallest = q[cand].min()
    cand = cand[q[cand] == smallest]
    return int(cand[np.argmax(values[cand])])


# เส้นทางเร็วสำหรับ null — Cholesky แบบเพิ่มทีละตัวบนต้นไม้ของชุดดัชนี

class FastSearch:
    D2_MIN = 1e-8

    def __init__(self, names, subsets, thr: dict[int, np.ndarray], periods: np.ndarray,
                 inside: np.ndarray, ok: dict, y="y", block: int = 4096):
        self.names, self.y, self.block = list(names), y, block
        self.subsets = [tuple(s) for s in subsets]
        self.inside = inside
        self.max_q = max(len(s) for s in self.subsets)
        pos = {k: i for i, k in enumerate(self.names)}
        self._row_of = {tuple(pos[k] for k in s): i for i, s in enumerate(self.subsets)}
        scale_of_point = np.nonzero(inside)[0]
        self._thr = {q: np.nan_to_num(np.asarray(t, float), nan=np.inf)[scale_of_point]
                     for q, t in thr.items()}
        self._bands = [band_rows(periods, b)[scale_of_point] for b in BANDS.values()]
        self._ok_y = ok.get(y, np.ones(inside.shape, bool))[inside]
        self._ok_x = [None if ok.get(k) is None or ok[k][inside].all() else ok[k][inside]
                      for k in self.names]
        self.n_valid = self._count_valid()

    def _count_valid(self) -> np.ndarray:
        out = np.zeros((len(self.subsets), len(self._bands)), int)
        for pos, i in self._row_of.items():
            v = self._ok_y
            for k in pos:
                if self._ok_x[k] is not None:
                    v = v & self._ok_x[k]
            out[i] = [np.count_nonzero(v & b) for b in self._bands]
        return out

    def run(self, cache: SpectraCache) -> tuple[np.ndarray, np.ndarray, int]:
        ins, y, names = self.inside, self.y, self.names
        Syy = cache(y, y).real[ins]
        dx = [cache(k, k).real[ins] for k in names]
        u = [np.conj(cache(y, k)[ins] / np.sqrt(Syy * dx[i])) for i, k in enumerate(names)]
        c = {(i, j): cache(names[i], names[j])[ins] / np.sqrt(dx[i] * dx[j])
             for i in range(len(names)) for j in range(i + 1, len(names))}
        nsub, nb = len(self.subsets), len(self._bands)
        hit = np.zeros((nsub, nb), np.int64)
        hit_fixed = np.zeros((nsub, nb), np.int64)
        self._n_bad = 0
        for a in range(0, len(Syy), self.block):
            sl = slice(a, a + self.block)
            self._descend(sl, u, c, hit, hit_fixed, start=0, path=(), rows=[], diag=[], z=[],
                          rho2=None, valid=self._ok_y[sl])
        with np.errstate(invalid="ignore", divide="ignore"):
            return 100.0 * hit / self.n_valid, 100.0 * hit_fixed / self.n_valid, self._n_bad

    def _descend(self, sl, u, c, hit, hit_fixed, start, path, rows, diag, z, rho2, valid):
        m = len(path)
        for k in range(start, len(self.names)):
            l = []
            for j in range(m):
                acc = c[(path[j], k)][sl]
                if j:
                    acc = acc.copy()
                    for i in range(j):
                        acc -= np.conj(rows[j][i]) * l[i]
                l.append(acc / diag[j])
            d2 = 1.0 - sum((x.real ** 2 + x.imag ** 2 for x in l), 0.0) if m else None
            num = u[k][sl]
            if m:
                num = num.copy()
                for j in range(m):
                    num -= np.conj(l[j]) * z[j]
                bad = d2 <= self.D2_MIN
                if bad.any():
                    self._n_bad += int(bad.sum())
                    d2 = np.where(bad, np.nan, d2)
                with np.errstate(invalid="ignore"):
                    d = np.sqrt(d2)
                    zk = num / d
                    new_rho2 = rho2 + (zk.real ** 2 + zk.imag ** 2)
            else:
                d = 1.0
                zk = num
                new_rho2 = zk.real ** 2 + zk.imag ** 2
            v = valid if self._ok_x[k] is None else valid & self._ok_x[k][sl]
            row = self._row_of.get(path + (k,))
            if row is not None:
                q = m + 1
                with np.errstate(invalid="ignore"):
                    sig = (new_rho2 > self._thr[q][sl]) & v
                    sig1 = sig if q == 1 else (new_rho2 > self._thr[1][sl]) & v
                for b, band in enumerate(self._bands):
                    bb = band[sl]
                    hit[row, b] += np.count_nonzero(sig & bb)
                    hit_fixed[row, b] += np.count_nonzero(sig1 & bb)
            if m + 1 < self.max_q:
                self._descend(sl, u, c, hit, hit_fixed, k + 1, path + (k,), rows + [l], diag + [d],
                              z + [zk], new_rho2, v)


# null ของการค้นหาทั้งดุ้น (Q6) — ย้ายมาจาก scripts/null_control.py เมื่อ 2026-10-07 (W7)

NULL_CHUNK = 25


def search_null_chunk(task: dict):
    from .significance import ar1_surrogate, fit_ar1
    from .transform import DJ, DT_MONTHLY, cwt

    d, station, design = task["d"], task["station"], task["design"]
    thr = task["thr"]
    x_names = [str(s) for s in d["x_names"]]
    y_names = [str(s) for s in d["y_names"]]
    subsets = all_subsets(x_names, max(thr))
    real, periods, coi, scales, inside, ok = prepare_station(
        d, station, task.get("max_filled", MAX_FILLED_FRACTION))
    iy = y_names.index(station)
    n = d["Y"].shape[1]
    a_y, s_y = fit_ar1(d["Y"][iy], d["Y_fill"][iy])
    ar = [fit_ar1(x, f) for x, f in zip(d["X"], d["X_fill"])]
    if design == "fake_y":
        for i, a in enumerate(x_names):
            for b in x_names[i:]:
                real(a, b)

    fast = FastSearch(x_names, subsets, thr, periods, inside, ok)
    if design == "check":
        p, pf, n_bad = fast.run(real)
        return p[None].astype(np.float32), pf[None].astype(np.float32), n_bad

    rng = np.random.default_rng(task["seed"])
    n_bad = 0
    out = np.empty((task["nrep"], len(subsets), len(BANDS)), np.float32)
    out_fixed = np.empty_like(out)
    for r in range(task["nrep"]):
        if design == "fake_x":
            W = {"y": real.W["y"],
                 **{k: cwt(ar1_surrogate(n, a, s, rng))[0] for k, (a, s) in zip(x_names, ar)}}
            cache = SpectraCache(W, DT_MONTHLY, DJ, scales)
        else:
            cache = real.with_series("y", cwt(ar1_surrogate(n, a_y, s_y, rng))[0])
        out[r], out_fixed[r], bad = fast.run(cache)
        n_bad += bad
    return out, out_fixed, n_bad


def search_null(d, station: str, thr: dict, design: str, nrep: int, seed: int,
                workers: int = 1, max_filled: float = MAX_FILLED_FRACTION):
    d = {k: d[k] for k in ("Y", "Y_fill", "X", "X_fill", "y_names", "x_names")}
    sizes = [NULL_CHUNK] * (nrep // NULL_CHUNK) + ([nrep % NULL_CHUNK] if nrep % NULL_CHUNK else [])
    tasks = [dict(d=d, station=station, thr=thr, design=design, nrep=k_n, seed=seed + k,
                  max_filled=max_filled) for k, k_n in enumerate(sizes)]
    if workers <= 1 or len(tasks) == 1:
        parts = [search_null_chunk(t) for t in tasks]
    else:
        import multiprocessing as mp
        import os
        from concurrent.futures import ProcessPoolExecutor
        keys = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
        saved = {k: os.environ.get(k) for k in keys}
        os.environ.update({k: "1" for k in keys})
        try:
            with ProcessPoolExecutor(max_workers=min(workers, len(tasks)),
                                     mp_context=mp.get_context("spawn")) as pool:
                parts = list(pool.map(search_null_chunk, tasks))
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
    return (np.concatenate([p[0] for p in parts]), np.concatenate([p[1] for p in parts]),
            sum(p[2] for p in parts))
