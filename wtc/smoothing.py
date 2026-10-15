from __future__ import annotations
import numpy as np

DELTA_J0 = 0.60


def gaussian_time_weights(scale: float, dt: float, truncate: float = 6.0) -> np.ndarray:
    sigma = scale / dt
    half = int(np.ceil(truncate * sigma))
    n = np.arange(-half, half + 1, dtype=float)
    w = np.exp(-(n ** 2) / (2 * sigma ** 2))
    return w / w.sum()


def boxcar_scale_weights(dj: float) -> np.ndarray:
    m = int(round(2 * DELTA_J0 / dj))
    m = max(m, 1)
    w = np.ones(m)
    if m >= 2:
        w[0] = w[-1] = 0.5
    return w / w.sum()


def smooth_time(W: np.ndarray, dt: float, scales: np.ndarray,
                pad: str = "zero") -> np.ndarray:
    W = np.asarray(W)
    n = W.shape[1]
    if pad == "wrap":
        m = n
    elif pad == "zero":
        m = int(2 ** np.ceil(np.log2(n)))
    else:
        raise ValueError(f"pad ต้องเป็น 'wrap' หรือ 'zero' ไม่ใช่ {pad!r}")
    k = 2 * np.pi * np.fft.fftfreq(m)
    sigma = (np.asarray(scales, float) / dt)[:, None]
    transfer = np.exp(-0.5 * (sigma ** 2) * (k[None, :] ** 2))
    out = np.fft.ifft(transfer * np.fft.fft(W, m, axis=1), axis=1)[:, :n]
    return out.real if np.isrealobj(W) else out


def smooth_scale(W: np.ndarray, dj: float, edge: str = "renorm") -> np.ndarray:
    W = np.asarray(W)
    w = boxcar_scale_weights(dj)
    if len(w) == 1:
        return W

    def conv_cols(a: np.ndarray) -> np.ndarray:
        return np.apply_along_axis(lambda col: np.convolve(col, w, mode="same"), 0, a)

    num = conv_cols(W)
    if edge == "zero":
        return num
    if edge != "renorm":
        raise ValueError(f"edge ต้องเป็น 'renorm' หรือ 'zero' ไม่ใช่ {edge!r}")
    den = conv_cols(np.ones((W.shape[0], 1)))
    return num / den


def smooth(W: np.ndarray, dt: float, dj: float, scales: np.ndarray,
           compat: bool = False) -> np.ndarray:
    if compat:
        return smooth_scale(smooth_time(W, dt, scales, pad="zero"), dj, edge="zero")
    return smooth_scale(smooth_time(W, dt, scales), dj)
