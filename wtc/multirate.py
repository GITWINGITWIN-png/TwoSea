from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

HOURS_PER_DAY = 24
DAILY_HOUR = 12
MIN_DAYS_PER_MONTH = 15
MIN_MONTHS_PER_YEAR = 12

TIDES_CPD = {"M2": 1.9322736, "S2": 2.0, "N2": 1.8959819, "K2": 2.0054758,
             "K1": 1.0027379, "O1": 0.9295357, "P1": 0.9972621, "Q1": 0.8932441}


# 1. ออกแบบตัวกรอง — Kaiser window method (บทที่ 4)

def kaiser_beta(atten_db: float) -> float:
    a = float(atten_db)
    if a > 50:
        return 0.1102 * (a - 8.7)
    if a >= 21:
        return 0.5842 * (a - 21) ** 0.4 + 0.07886 * (a - 21)
    return 0.0


def kaiser_numtaps(atten_db: float, f_pass: float, f_stop: float, fs: float) -> int:
    d_omega = 2 * np.pi * (f_stop - f_pass) / fs
    n = int(np.ceil((atten_db - 8) / (2.285 * d_omega))) + 1
    return n if n % 2 == 1 else n + 1


def kaiser_window(numtaps: int, beta: float) -> np.ndarray:
    if numtaps == 1:
        return np.ones(1)
    n = np.arange(numtaps)
    alpha = (numtaps - 1) / 2
    r = (n - alpha) / alpha
    return np.i0(beta * np.sqrt(np.clip(1 - r ** 2, 0, None))) / np.i0(beta)


@dataclass
class FIRDesign:
    taps: np.ndarray
    fs: float
    f_pass: float
    f_stop: float
    atten_db: float
    beta: float
    formula_numtaps: int
    notes: list[str] = field(default_factory=list)

    @property
    def numtaps(self) -> int:
        return len(self.taps)

    @property
    def cutoff(self) -> float:
        return (self.f_pass + self.f_stop) / 2

    def response(self, nfft: int = 1 << 16) -> tuple[np.ndarray, np.ndarray]:
        H = np.abs(np.fft.rfft(self.taps, nfft))
        f = np.fft.rfftfreq(nfft, d=1 / self.fs)
        return f, H

    def gain_at(self, freqs) -> np.ndarray:
        n = np.arange(self.numtaps) - (self.numtaps - 1) / 2
        w = 2 * np.pi * np.atleast_1d(freqs)[:, None] / self.fs
        return np.abs(np.exp(-1j * w * n[None, :]) @ self.taps)

    def measured_stopband_db(self) -> float:
        f, H = self.response()
        return float(-20 * np.log10(H[f >= self.f_stop].max()))

    def measured_passband_ripple(self) -> float:
        f, H = self.response()
        return float(np.abs(H[f <= self.f_pass] - 1).max())


def design_lowpass(f_pass: float, f_stop: float, atten_db: float, fs: float,
                   max_extra: int = 200) -> FIRDesign:
    if not 0 < f_pass < f_stop <= fs / 2:
        raise ValueError(f"ต้องได้ 0 < f_pass < f_stop <= fs/2 แต่ได้ {f_pass}, {f_stop}, fs={fs}")
    beta = kaiser_beta(atten_db)
    n0 = kaiser_numtaps(atten_db, f_pass, f_stop, fs)
    fc = (f_pass + f_stop) / 2

    for extra in range(0, max_extra + 1, 2):
        n = n0 + extra
        alpha = (n - 1) / 2
        h = (2 * fc / fs) * np.sinc(2 * fc / fs * (np.arange(n) - alpha))
        h *= kaiser_window(n, beta)
        h /= h.sum()
        design = FIRDesign(h, fs, f_pass, f_stop, atten_db, beta, n0)
        if design.measured_stopband_db() >= atten_db:
            if extra:
                design.notes.append(f"สูตร Kaiser ทำนาย {n0} taps แต่วัดได้ไม่ถึง {atten_db} dB "
                                    f"⇒ เพิ่มเป็น {n} taps")
            return design
    raise RuntimeError(f"เพิ่ม taps ไปอีก {max_extra} ตัวแล้วยังไม่ถึง {atten_db} dB")


# 2. กรอง + decimate — คำนวณเฉพาะตัวอย่างที่จะเก็บ

def fir_at(x: np.ndarray, taps: np.ndarray, centers: np.ndarray) -> np.ndarray:
    taps = np.asarray(taps, float)
    n = len(taps)
    if n % 2 == 0:
        raise ValueError("ต้องใช้ taps ยาวคี่ (Type I) เพื่อให้หน่วงเป็นจำนวนเต็ม")
    half = n // 2
    xp = np.pad(np.asarray(x, float), half, constant_values=np.nan)
    windows = sliding_window_view(xp, n)[np.asarray(centers)]
    return windows @ taps[::-1]


def hourly_to_daily(t_hourly: np.ndarray, v: np.ndarray, design: FIRDesign,
                    hour: int = DAILY_HOUR) -> tuple[np.ndarray, np.ndarray]:
    if design.fs != HOURS_PER_DAY:
        raise ValueError(f"ตัวกรองออกแบบไว้ที่ fs={design.fs} แต่ข้อมูลเป็นรายชั่วโมง (24/วัน)")
    hours = (t_hourly - t_hourly.astype("datetime64[D]")).astype(int)
    centers = np.flatnonzero(hours == hour)
    return t_hourly[centers].astype("datetime64[D]"), fir_at(v, design.taps, centers)


def naive_daily(t_hourly: np.ndarray, v: np.ndarray,
                hour: int = DAILY_HOUR) -> tuple[np.ndarray, np.ndarray]:
    hours = (t_hourly - t_hourly.astype("datetime64[D]")).astype(int)
    idx = np.flatnonzero(hours == hour)
    return t_hourly[idx].astype("datetime64[D]"), np.asarray(v, float)[idx]


# 3. ค่าเฉลี่ยตามปฏิทิน — นิยามเดียวกับที่ PSMSL รายงาน

def _group_mean(keys: np.ndarray, values: np.ndarray, min_count: int
                ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    uniq, start = np.unique(keys, return_index=True)
    ok = np.isfinite(values)
    counts = np.add.reduceat(ok.astype(int), start)
    sums = np.add.reduceat(np.where(ok, values, 0.0), start)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = sums / counts
    mean[counts < min_count] = np.nan
    return uniq, mean, counts


def daily_to_monthly(days: np.ndarray, daily: np.ndarray,
                     min_days: int = MIN_DAYS_PER_MONTH
                     ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return _group_mean(days.astype("datetime64[M]"), daily, min_days)


def monthly_to_annual(months: np.ndarray, monthly: np.ndarray,
                      min_months: int = MIN_MONTHS_PER_YEAR
                      ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    years = months.astype("datetime64[Y]").astype(int) + 1970
    return _group_mean(years, monthly, min_months)


def monthly_mean_direct(t_hourly: np.ndarray, v: np.ndarray,
                        min_hours: int = MIN_DAYS_PER_MONTH * HOURS_PER_DAY
                        ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return _group_mean(t_hourly.astype("datetime64[M]"), np.asarray(v, float), min_hours)


# 4. เทียบกับค่าอ้างอิง

def decimal_year_to_month(t: np.ndarray) -> np.ndarray:
    k = np.floor(np.asarray(t, float) * 12 + 1e-6).astype(int)
    return (k - 1970 * 12).astype("datetime64[M]")


@dataclass
class Comparison:
    n: int
    offset: float
    median_offset: float
    rms: float
    corr: float
    max_abs: float
    keys: np.ndarray
    diff: np.ndarray


def compare(keys_a: np.ndarray, a: np.ndarray,
            keys_b: np.ndarray, b: np.ndarray) -> Comparison:
    common, ia, ib = np.intersect1d(keys_a, keys_b, return_indices=True)
    x, y = np.asarray(a, float)[ia], np.asarray(b, float)[ib]
    ok = np.isfinite(x) & np.isfinite(y)
    x, y, common = x[ok], y[ok], common[ok]
    d = x - y
    off, med = float(d.mean()), float(np.median(d))
    d = d - off
    return Comparison(n=int(ok.sum()), offset=off, median_offset=med,
                      rms=float(np.sqrt(np.mean(d ** 2))),
                      corr=float(np.corrcoef(x, y)[0, 1]), max_abs=float(np.abs(d).max()),
                      keys=common, diff=d)
