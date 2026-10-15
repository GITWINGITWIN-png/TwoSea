from __future__ import annotations
import numpy as np

from .smoothing import smooth


def xwt(Wx: np.ndarray, Wy: np.ndarray) -> np.ndarray:
    return Wx * np.conj(Wy)


def _energy_density(W: np.ndarray, scales: np.ndarray) -> np.ndarray:
    return W / scales[:, None]


def wtc(Wx: np.ndarray, Wy: np.ndarray, dt: float, dj: float,
        scales: np.ndarray, compat: bool = False) -> tuple[np.ndarray, np.ndarray]:
    if Wx.shape != Wy.shape:
        raise ValueError(f"รูปร่างไม่ตรงกัน {Wx.shape} vs {Wy.shape}")

    Sxy = smooth(_energy_density(xwt(Wx, Wy), scales), dt, dj, scales, compat)
    Sxx = smooth(_energy_density(np.abs(Wx) ** 2, scales), dt, dj, scales, compat)
    Syy = smooth(_energy_density(np.abs(Wy) ** 2, scales), dt, dj, scales, compat)

    R2 = np.abs(Sxy) ** 2 / (Sxx * Syy)
    worst = np.nanmax(R2)
    if worst > 1 + 1e-8:
        raise ValueError(f"R^2 = {worst:.6f} > 1 — smoothing เพี้ยน ห้ามใช้ผลนี้ต่อ")
    return R2, np.angle(Sxy)


# MWC — multiple wavelet coherence (W5)

COND_MAX = 1e8


class SpectraCache:
    def __init__(self, W: dict, dt: float, dj: float, scales: np.ndarray,
                 compat: bool = False):
        self.W, self.dt, self.dj, self.scales, self.compat = W, dt, dj, scales, compat
        self._store: dict = {}

    def __call__(self, a, b) -> np.ndarray:
        if (a, b) in self._store:
            return self._store[(a, b)]
        if (b, a) in self._store:
            return np.conj(self._store[(b, a)])
        if a == b:
            raw = np.abs(self.W[a]) ** 2
        else:
            raw = xwt(self.W[a], self.W[b])
        S = smooth(_energy_density(raw, self.scales), self.dt, self.dj, self.scales,
                   self.compat)
        self._store[(a, b)] = S
        return S

    def with_series(self, name, W: np.ndarray) -> "SpectraCache":
        new = SpectraCache({**self.W, name: W}, self.dt, self.dj, self.scales, self.compat)
        new._store = {k: v for k, v in self._store.items() if name not in k}
        return new

    def __len__(self) -> int:
        return len(self._store)

    @property
    def nbytes(self) -> int:
        return sum(v.nbytes for v in self._store.values())


def coherency_matrix(cache: SpectraCache, xs, where: np.ndarray | None = None) -> np.ndarray:
    q = len(xs)
    pick = (lambda a: a) if where is None else (lambda a: a[where])
    d = [pick(cache(x, x).real) for x in xs]
    shape = d[0].shape
    C = np.zeros(shape + (q, q), dtype=complex)
    for i in range(q):
        C[..., i, i] = 1.0
        for j in range(i + 1, q):
            cij = pick(cache(xs[i], xs[j])) / np.sqrt(d[i] * d[j])
            C[..., i, j] = cij
            C[..., j, i] = np.conj(cij)
    return C


def mwc_cached(cache: SpectraCache, y, xs, cond_max: float = COND_MAX,
               where: np.ndarray | None = None, check_cond: bool = True
               ) -> tuple[np.ndarray, np.ndarray]:
    xs = list(xs)
    if len(set(xs)) != len(xs):
        raise ValueError(f"ชุดดัชนีมีตัวซ้ำ {xs} — เมทริกซ์จะ singular โดยนิยาม")
    full_shape = cache(y, y).shape
    pick = (lambda a: a) if where is None else (lambda a: a[where])
    Syy = pick(cache(y, y).real)
    u = np.stack([pick(cache(y, x)) / np.sqrt(Syy * pick(cache(x, x).real)) for x in xs], axis=-1)

    if len(xs) == 1:
        R2 = np.abs(u[..., 0]) ** 2
        cond = np.ones(R2.shape)
    else:
        C = coherency_matrix(cache, xs, where)
        if check_cond:
            ev = np.linalg.eigvalsh(C)
            with np.errstate(divide="ignore", invalid="ignore"):
                cond = np.where(ev[..., 0] > 0, ev[..., -1] / ev[..., 0], np.inf)
            ok = np.isfinite(cond) & (cond <= cond_max)
        else:
            cond = np.full(Syy.shape, np.nan)
            ok = np.ones(Syy.shape, bool)
        R2 = np.full(Syy.shape, np.nan)
        if ok.any():
            x = np.linalg.solve(C[ok], np.conj(u[ok])[..., None])[..., 0]
            R2[ok] = np.einsum("ki,ki->k", u[ok], x).real

    worst = np.nanmax(R2) if np.isfinite(R2).any() else 0.0
    if worst > 1 + 1e-8:
        raise ValueError(f"MWC = {worst:.6f} > 1 — smoothing หรือเมทริกซ์เพี้ยน ห้ามใช้ผลนี้ต่อ")
    if where is not None:
        full_R2, full_cond = np.full(full_shape, np.nan), np.full(full_shape, np.nan)
        full_R2[where], full_cond[where] = R2, cond
        return full_R2, full_cond
    return R2, cond


def mwc(Wy: np.ndarray, Wx_list, dt: float, dj: float, scales: np.ndarray,
        compat: bool = False, cond_max: float = COND_MAX) -> tuple[np.ndarray, np.ndarray]:
    Wx_list = list(Wx_list)
    for Wx in Wx_list:
        if Wx.shape != Wy.shape:
            raise ValueError(f"รูปร่างไม่ตรงกัน {Wx.shape} vs {Wy.shape}")
    W = {"y": Wy, **{i: Wx for i, Wx in enumerate(Wx_list)}}
    cache = SpectraCache(W, dt, dj, scales, compat)
    return mwc_cached(cache, "y", range(len(Wx_list)), cond_max)
