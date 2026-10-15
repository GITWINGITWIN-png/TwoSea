from __future__ import annotations
from dataclasses import dataclass
import numpy as np


def fit_ar1(z: np.ndarray, filled: np.ndarray | None = None) -> tuple[float, float]:
    z = np.asarray(z, float)
    x0, x1 = z[:-1], z[1:]
    if filled is not None:
        f = np.asarray(filled, bool)
        real = ~f[:-1] & ~f[1:]
        x0, x1 = x0[real], x1[real]
        sd = float(np.std(z[~f]))
    else:
        sd = float(np.std(z))
    a = float(np.corrcoef(x0, x1)[0, 1])
    return a, sd * float(np.sqrt(max(1 - a ** 2, 0.0)))


def ar1_surrogate(n: int, a: float, sigma: float,
                  rng: np.random.Generator) -> np.ndarray:
    e = rng.normal(0.0, sigma, n)
    z = np.empty(n)
    z[0] = e[0]
    for i in range(1, n):
        z[i] = a * z[i - 1] + e[i]
    return (z - z.mean()) / z.std()


# threshold ของ WTC — เปอร์เซ็นไทล์ที่ 95 แยกรายสเกล (W4)

@dataclass
class WTCThreshold:
    level: float
    per_scale: np.ndarray
    nmc: int
    a_y: float
    a_x: float
    seed: int
    n_pooled: np.ndarray


def _quantile_from_hist(counts: np.ndarray, level: float, edges: np.ndarray) -> np.ndarray:
    total = counts.sum(axis=1)
    out = np.full(counts.shape[0], np.nan)
    width = edges[1] - edges[0]
    cum = np.cumsum(counts, axis=1)
    for i in np.flatnonzero(total > 0):
        target = level * total[i]
        k = int(np.searchsorted(cum[i], target))
        before = cum[i, k - 1] if k > 0 else 0
        frac = (target - before) / counts[i, k] if counts[i, k] else 0.0
        out[i] = edges[k] + frac * width
    return out


def threshold_wtc(n: int, a_y: float, s_y: float, a_x: float, s_x: float,
                  nmc: int = 1000, level: float = 0.95, seed: int = 0,
                  dt: float | None = None, dj: float | None = None,
                  nbins: int = 1000) -> WTCThreshold:
    from .coherence import wtc
    from .transform import DJ, DT_MONTHLY, coi_mask, cwt

    dt = DT_MONTHLY if dt is None else dt
    dj = DJ if dj is None else dj
    rng = np.random.default_rng(seed)
    edges = np.linspace(0.0, 1.0, nbins + 1)
    counts = None
    for _ in range(nmc):
        Wy, scales, periods, coi = cwt(ar1_surrogate(n, a_y, s_y, rng), dt, dj)
        Wx, _, _, _ = cwt(ar1_surrogate(n, a_x, s_x, rng), dt, dj)
        R2, _ = wtc(Wy, Wx, dt, dj, scales)
        inside = coi_mask(periods, coi)
        if counts is None:
            counts = np.zeros((len(scales), nbins), dtype=np.int64)
        b = np.clip((R2 * nbins).astype(int), 0, nbins - 1)
        rows = np.broadcast_to(np.arange(len(scales))[:, None], R2.shape)
        np.add.at(counts, (rows[inside], b[inside]), 1)
    assert counts is not None
    return WTCThreshold(level=level, per_scale=_quantile_from_hist(counts, level, edges),
                        nmc=nmc, a_y=a_y, a_x=a_x, seed=seed, n_pooled=counts.sum(axis=1))


def pasc_null(thr: WTCThreshold, n: int, s_y: float, s_x: float,
              nmc: int | None = None, seed: int | None = None,
              dt: float | None = None, dj: float | None = None) -> dict[str, np.ndarray]:
    from .coherence import wtc
    from .metrics import BANDS, pasc, significance
    from .transform import DJ, DT_MONTHLY, coi_mask, cwt

    dt = DT_MONTHLY if dt is None else dt
    dj = DJ if dj is None else dj
    nmc = thr.nmc if nmc is None else nmc
    rng = np.random.default_rng(thr.seed + 10_000 if seed is None else seed)
    out = {b: np.empty(nmc) for b in BANDS}
    for i in range(nmc):
        Wy, scales, periods, coi = cwt(ar1_surrogate(n, thr.a_y, s_y, rng), dt, dj)
        Wx, _, _, _ = cwt(ar1_surrogate(n, thr.a_x, s_x, rng), dt, dj)
        R2, _ = wtc(Wy, Wx, dt, dj, scales)
        sig = significance(R2, thr.per_scale)
        valid = coi_mask(periods, coi)
        for b, band in BANDS.items():
            out[b][i] = pasc(sig, valid, periods, band)
    return out


def empirical_p(observed: float, null: np.ndarray) -> float:
    null = np.asarray(null, float)
    null = null[np.isfinite(null)]
    if not np.isfinite(observed) or len(null) == 0:
        return float("nan")
    return float((np.sum(null >= observed) + 1) / (len(null) + 1))


# threshold ของ MWC — null รวมต่อ (q, สถานี) (W5)

MC_CHUNK = 50


@dataclass
class MWCThreshold:
    q: int
    level: float
    per_scale: np.ndarray
    nmc: int
    pooled: bool
    a_y: float
    a_x: tuple
    seed: int
    n_pooled: np.ndarray
    n_nan: int


def _mwc_null_chunk(task: dict) -> dict:
    from .coherence import SpectraCache, mwc_cached
    from .metrics import BANDS, pasc, significance
    from .transform import coi_mask, cwt

    t = task
    rng = np.random.default_rng(t["seed"])
    m, qs, nbins = len(t["a_x"]), t["qs"], t["nbins"]
    hist = {q: None for q in qs}
    n_nan = {q: 0 for q in qs}
    pas = {q: {b: [] for b in BANDS} for q in qs}
    for _ in range(t["nmc"]):
        y = ar1_surrogate(t["n"], t["a_y"], t["s_y"], rng)
        xs = [ar1_surrogate(t["n"], a, s, rng) for a, s in zip(t["a_x"], t["s_x"])]
        subsets = {q: tuple(range(m)) if q == m else
                   tuple(sorted(rng.choice(m, size=q, replace=False).tolist())) for q in qs}
        used = sorted(set().union(*subsets.values()))
        Wy, scales, periods, coi = cwt(y, t["dt"], t["dj"])
        W = {"y": Wy, **{i: cwt(xs[i], t["dt"], t["dj"])[0] for i in used}}
        cache = SpectraCache(W, t["dt"], t["dj"], scales)
        inside = coi_mask(periods, coi)
        for q in qs:
            R2, _ = mwc_cached(cache, "y", subsets[q])
            ok = inside & np.isfinite(R2)
            n_nan[q] += int((inside & ~np.isfinite(R2)).sum())
            if t["mode"] == "hist":
                if hist[q] is None:
                    hist[q] = np.zeros((len(scales), nbins), dtype=np.int64)
                b = np.clip((np.nan_to_num(R2) * nbins).astype(int), 0, nbins - 1)
                rows = np.broadcast_to(np.arange(len(scales))[:, None], R2.shape)
                np.add.at(hist[q], (rows[ok], b[ok]), 1)
            else:
                sig = significance(R2, t["thresholds"][q])
                for name, band in BANDS.items():
                    pas[q][name].append(pasc(sig, ok, periods, band))
    return {"hist": hist, "n_nan": n_nan, "pasc": pas}


def _run_chunks(base: dict, nmc: int, seed: int, workers: int) -> list[dict]:
    sizes = [MC_CHUNK] * (nmc // MC_CHUNK) + ([nmc % MC_CHUNK] if nmc % MC_CHUNK else [])
    tasks = [dict(base, nmc=k_n, seed=seed + k) for k, k_n in enumerate(sizes)]
    if workers <= 1 or len(tasks) == 1:
        return [_mwc_null_chunk(t) for t in tasks]

    import multiprocessing as mp
    import os
    from concurrent.futures import ProcessPoolExecutor
    keys = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
    saved = {k: os.environ.get(k) for k in keys}
    os.environ.update({k: "1" for k in keys})
    try:
        with ProcessPoolExecutor(max_workers=min(workers, len(tasks)),
                                 mp_context=mp.get_context("spawn")) as pool:
            return list(pool.map(_mwc_null_chunk, tasks))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def threshold_mwc(n: int, a_y: float, s_y: float, a_x, s_x, qs=(1, 2, 3, 4, 5),
                  nmc: int = 1000, level: float = 0.95, seed: int = 0,
                  dt: float | None = None, dj: float | None = None,
                  nbins: int = 1000, workers: int = 1) -> dict[int, MWCThreshold]:
    from .transform import DJ, DT_MONTHLY
    a_x, s_x = tuple(float(v) for v in a_x), tuple(float(v) for v in s_x)
    qs = tuple(int(q) for q in qs)
    if len(a_x) != len(s_x) or not all(1 <= q <= len(a_x) for q in qs):
        raise ValueError(f"q ต้องอยู่ระหว่าง 1 ถึงจำนวนผู้สมัคร ({len(a_x)}) · ได้ {qs}")
    base = dict(n=n, a_y=a_y, s_y=s_y, a_x=a_x, s_x=s_x, qs=qs, nbins=nbins,
                dt=DT_MONTHLY if dt is None else dt, dj=DJ if dj is None else dj,
                mode="hist", thresholds=None)
    parts = _run_chunks(base, nmc, seed, workers)
    edges = np.linspace(0.0, 1.0, nbins + 1)
    out = {}
    for q in qs:
        counts = sum(p["hist"][q] for p in parts)
        out[q] = MWCThreshold(q=q, level=level, per_scale=_quantile_from_hist(counts, level, edges),
                              nmc=nmc, pooled=q < len(a_x), a_y=a_y, a_x=a_x, seed=seed,
                              n_pooled=counts.sum(axis=1),
                              n_nan=sum(p["n_nan"][q] for p in parts))
    return out


def pasc_null_mwc(thr: dict[int, MWCThreshold], n: int, s_y: float, s_x,
                  nmc: int | None = None, seed: int | None = None,
                  dt: float | None = None, dj: float | None = None,
                  workers: int = 1) -> dict[int, dict[str, np.ndarray]]:
    from .transform import DJ, DT_MONTHLY
    first = next(iter(thr.values()))
    qs = tuple(sorted(thr))
    nmc = first.nmc if nmc is None else nmc
    seed = first.seed + 10_000 if seed is None else seed
    base = dict(n=n, a_y=first.a_y, s_y=s_y, a_x=first.a_x,
                s_x=tuple(float(v) for v in s_x), qs=qs, nbins=1,
                dt=DT_MONTHLY if dt is None else dt, dj=DJ if dj is None else dj,
                mode="pasc", thresholds={q: thr[q].per_scale for q in qs})
    parts = _run_chunks(base, nmc, seed, workers)
    from .metrics import BANDS
    return {q: {b: np.concatenate([np.asarray(p["pasc"][q][b], float) for p in parts])
                for b in BANDS} for q in qs}
