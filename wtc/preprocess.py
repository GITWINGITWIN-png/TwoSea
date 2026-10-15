from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from .loaders import to_monthly_grid

MAX_INTERP_MONTHS = 3


@dataclass
class DeseasonInfo:
    slope: float
    annual_amp: float
    semiannual_amp: float
    frac_trend: float
    frac_season: float
    resid_std: float
    n_used: int


def _design(t: np.ndarray) -> np.ndarray:
    return np.column_stack(
        [t - t.mean(), np.ones_like(t)] +
        [f(2 * np.pi * k * t) for k in (1, 2) for f in (np.sin, np.cos)]
    )


def detrend_deseason(t: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, DeseasonInfo]:
    t = np.asarray(t, float)
    y = np.asarray(y, float)
    g = np.isfinite(y)
    if g.sum() < 24:
        raise ValueError(f"มีข้อมูลจริงแค่ {g.sum()} จุด — น้อยเกินกว่าจะฟิตฤดูกาลได้")

    A = _design(t)
    coef = np.linalg.lstsq(A[g], y[g], rcond=None)[0]
    resid = y - A @ coef

    trend_only = A[:, :2] @ coef[:2]
    after_trend = y - trend_only
    info = DeseasonInfo(
        slope=float(coef[0]),
        annual_amp=float(np.hypot(coef[2], coef[3])),
        semiannual_amp=float(np.hypot(coef[4], coef[5])),
        frac_trend=float(1 - np.var(after_trend[g]) / np.var(y[g])),
        frac_season=float(1 - np.var(resid[g]) / np.var(after_trend[g])),
        resid_std=float(np.std(resid[g])),
        n_used=int(g.sum()),
    )
    z = (resid - np.mean(resid[g])) / info.resid_std
    return z, info


def fill_gaps(y: np.ndarray, max_interp: int = MAX_INTERP_MONTHS
              ) -> tuple[np.ndarray, np.ndarray]:
    y = np.asarray(y, float).copy()
    filled = ~np.isfinite(y)
    if not filled.any():
        return y, filled
    if filled.all():
        raise ValueError("ไม่มีข้อมูลจริงเลยสักจุด")

    idx = np.arange(len(y))
    good = ~filled

    edges = np.flatnonzero(np.diff(np.r_[0, filled.view(np.int8), 0]))
    for a, b in zip(edges[::2], edges[1::2]):
        run = b - a
        touches_edge = a == 0 or b == len(y)
        if run <= max_interp and not touches_edge:
            y[a:b] = np.interp(idx[a:b], idx[good], y[good])
        else:
            y[a:b] = 0.0
    return y, filled


def common_window(series: dict[str, tuple[np.ndarray, np.ndarray]]) -> tuple[float, float]:
    lo = max(t[np.isfinite(v)][0] for t, v in series.values())
    hi = min(t[np.isfinite(v)][-1] for t, v in series.values())
    if hi <= lo:
        raise ValueError("ไม่มีหน้าต่างที่ทุกอนุกรมทับกัน")
    return float(lo), float(hi)


def align(series: dict[str, tuple[np.ndarray, np.ndarray]],
          start: float, stop: float) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    start = np.floor(start * 12) / 12
    stop = np.ceil(stop * 12) / 12
    grid = None
    out: dict[str, np.ndarray] = {}
    for name, (t, v) in series.items():
        g, vv = to_monthly_grid(np.asarray(t, float), np.asarray(v, float), start, stop)
        if grid is None:
            grid = g
        elif len(g) != len(grid) or not np.allclose(g, grid):
            raise ValueError(f"กริดของ {name} ไม่ตรงกับตัวอื่น")
        out[name] = vv
    assert grid is not None
    return grid, out
