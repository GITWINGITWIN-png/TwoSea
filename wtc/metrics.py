from __future__ import annotations
import numpy as np

from .smoothing import smooth_time
from .transform import coi_mask

MAX_FILLED_FRACTION = 0.5
BANDS: dict[str, tuple[float, float] | None] = {
    "ทั้งระนาบ": None,
    "2–7 ปี": (2.0, 7.0),
    "8–16 ปี": (8.0, 16.0),
}


def filled_fraction(filled: np.ndarray, scales: np.ndarray, dt: float) -> np.ndarray:
    f = np.broadcast_to(np.asarray(filled, float)[None, :], (len(scales), len(filled)))
    num = smooth_time(f, dt, scales)
    den = smooth_time(np.ones_like(f), dt, scales)
    return num / den


def valid_mask(periods: np.ndarray, coi: np.ndarray, scales: np.ndarray, dt: float,
               *filled: np.ndarray, max_filled: float = MAX_FILLED_FRACTION) -> np.ndarray:
    ok = coi_mask(periods, coi)
    for m in filled:
        if m is not None and np.any(m):
            ok &= filled_fraction(m, scales, dt) <= max_filled
    return ok


def band_rows(periods: np.ndarray, band: tuple[float, float] | None) -> np.ndarray:
    if band is None:
        return np.ones(len(periods), bool)
    return (periods >= band[0]) & (periods <= band[1])


def pasc(sig: np.ndarray, valid: np.ndarray, periods: np.ndarray,
         band: tuple[float, float] | None = None) -> float:
    rows = band_rows(periods, band)
    v = valid[rows]
    n = int(v.sum())
    return float("nan") if n == 0 else 100.0 * float((sig[rows] & v).sum()) / n


def awc(R2: np.ndarray, sig: np.ndarray, valid: np.ndarray, periods: np.ndarray,
        band: tuple[float, float] | None = None) -> float:
    rows = band_rows(periods, band)
    m = sig[rows] & valid[rows]
    return float("nan") if not m.any() else float(R2[rows][m].mean())


def significance(R2: np.ndarray, threshold_per_scale: np.ndarray) -> np.ndarray:
    thr = np.asarray(threshold_per_scale, float)[:, None]
    with np.errstate(invalid="ignore"):
        return np.where(np.isfinite(thr), R2 > thr, False)


def summarize(R2: np.ndarray, sig: np.ndarray, valid: np.ndarray,
              periods: np.ndarray) -> dict[str, dict[str, float]]:
    out = {}
    for name, band in BANDS.items():
        rows = band_rows(periods, band)
        out[name] = {"pasc": pasc(sig, valid, periods, band),
                     "awc": awc(R2, sig, valid, periods, band),
                     "n_valid": int(valid[rows].sum())}
    return out
