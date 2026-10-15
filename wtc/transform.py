from __future__ import annotations
import numpy as np

OMEGA0 = 6.0
DJ = 1 / 12
DT_MONTHLY = 1 / 12


def morlet_flambda(omega0: float = OMEGA0) -> float:
    return 4 * np.pi / (omega0 + np.sqrt(2 + omega0 ** 2))


def cwt(y: np.ndarray, dt: float = DT_MONTHLY, dj: float = DJ,
        s0: float | None = None, j: int | None = None, omega0: float = OMEGA0):
    import pycwt

    y = np.asarray(y, float)
    if s0 is None:
        s0 = 2 * dt / morlet_flambda(omega0)
    if j is None:
        j = int(round(np.log2(y.size * dt / s0) / dj))
    W, scales, freqs, coi, _, _ = pycwt.cwt(y, dt, dj, s0, j, pycwt.Morlet(omega0))
    return W, scales, 1 / freqs, coi


def coi_mask(periods: np.ndarray, coi: np.ndarray) -> np.ndarray:
    return periods[:, None] <= coi[None, :]
