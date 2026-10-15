"""โซ่ anti-alias + decimation ที่เขียนเอง — บทที่ 3 (multirate) และบทที่ 4 (FIR)

★ ไม่เรียก scipy.signal.decimate / firwin / kaiserord ในไฟล์นี้เลย — ทุกสูตรเขียนเอง
  (tests/test_multirate.py เอาไปเทียบกับ scipy เพื่อยืนยันว่าตรงกัน แบบเดียวกับประตู G1)

โซ่ที่ทำ (PLAN.md §2 Q7)

    รายชั่วโมง ──[ FIR lowpass Kaiser + เก็บทุก 24 ตัวอย่าง ]──> รายวัน
               ──[ ค่าเฉลี่ยเดือนปฏิทิน ]──────────────────────> รายเดือน   ← เทียบ PSMSL
               ──[ ค่าเฉลี่ย 12 เดือน ]─────────────────────────> รายปี     ← เทียบ PSMSL

## ทำไมต้องกรองก่อน decimate — ตัวเลขจริงของ KO TAPHAO NOI (วัดแล้ว 2026-09-30)

น้ำขึ้นน้ำลงอธิบายความแปรปรวนรายชั่วโมงถึง **95%** ถ้าสุ่มวันละครั้งโดยไม่กรอง
แต่ละองค์ประกอบจะพับลงมาที่ความถี่ |f - round(f)| รอบต่อวัน:

    M2  789 mm  1.9323 cpd  -> พับไปที่คาบ  14.8 วัน
    S2  400 mm  2.0000 cpd  -> พับไปที่ DC (กลายเป็นค่าคงที่เพี้ยน)
    K1  130 mm  1.0027 cpd  -> พับไปที่คาบ 365.2 วัน   ← วงรอบรายปีปลอม
    P1   38 mm  0.9973 cpd  -> พับไปที่คาบ 365.2 วัน   ← ซ้อนกับ K1
    K2  112 mm  2.0055 cpd  -> พับไปที่คาบ 182.6 วัน   ← วงรอบครึ่งปีปลอม

⇒ aliasing ไม่ได้แค่ "เพิ่ม noise" แต่**สร้างวงรอบรายปีและครึ่งปีปลอม** ลงในแถบเดียวกับ
วงรอบฤดูกาลจริงพอดี ซึ่งเป็นแถบที่ preprocess.detrend_deseason ต้องตัดออก — ถ้าไม่กรอง
เราจะไม่มีทางแยกได้เลยว่าวงรอบรายปีที่เห็นเป็นของจริงหรือเป็น K1 ที่พับลงมา

## สเปกตัวกรอง — ทุกตัวเลขมีที่มา

| สเปก | ค่า | เหตุผล |
| --- | --- | --- |
| fs | 24 ตัวอย่าง/วัน | ข้อมูลรายชั่วโมง |
| ขอบ stopband | 0.5 cpd | = Nyquist ของผลรายวัน ⇒ ไม่มีอะไรพับได้เลย (แบบเข้ม) |
| ขอบ passband | 0.1 cpd (คาบ 10 วัน) | ปลายทางคือรายเดือน (คาบ ≥ 60 วัน = 0.017 cpd) ⇒ เผื่อ 6 เท่า |
| stopband attenuation | **70 dB** | M2 789 mm · รวมทุกองค์ประกอบ 1,675 mm ⇒ ต้อง ≥ 64.5 dB ถึงจะเหลือเศษ < 1 mm |
| หน้าต่าง | Kaiser | คุม attenuation ด้วย beta ได้ตรง ๆ ตามสูตรที่สอนในบทที่ 4 |

**ทางเลือกที่ไม่เลือก** — ขอบ stopband ขยับไปได้ถึง 1 − 0.1 = 0.9 cpd (ปล่อยให้พลังงานช่วง
0.5–0.9 cpd พับลงไปอยู่ที่ 0.1–0.5 cpd ซึ่งไม่ใช่แถบที่สนใจ และค่าเฉลี่ยรายเดือนจะกินทิ้งอีกที)
จะได้ตัวกรองสั้นลงราว 2.4 เท่า แต่ Q1 (0.893 cpd) จะไปตกในแถบเปลี่ยนผ่านพอดี และต้องอธิบาย
เพิ่มอีกหนึ่งชั้น ⇒ เลือกแบบเข้มเพราะคำนวณถูกอยู่แล้ว (12,800 วัน × ~260 taps = ไม่ถึงวินาที)

## ขั้นรายเดือนใช้ค่าเฉลี่ยธรรมดา — โดยตั้งใจ

ค่าเฉลี่ยเดือนปฏิทินคือ boxcar ความยาว 28–31 วัน ซึ่งเป็น anti-alias ที่แย่ (sidelobe ~ −13 dB)
แต่มันคือ **นิยาม** ของ "ค่าเฉลี่ยรายเดือน" ที่ PSMSL รายงาน ถ้าเราออกแบบตัวกรองที่ดีกว่านี้
ผลจะต่างจากค่าอ้างอิง *โดยนิยาม* แล้วการเทียบ RMS จะไม่ได้วัดสิ่งที่อยากวัด

## การจัดการช่องว่าง — กฎเข้ม

ถ้าหน้าต่างของตัวกรองมี NaN แม้แต่ตัวเดียว ค่านั้นเป็น NaN เหตุผล: ตัวอย่างที่หายทำให้
"ศูนย์" ของตัวกรองที่ความถี่น้ำขึ้นน้ำลงเสีย แล้ว tide 789 mm รั่วเข้ามาได้ทันที
ที่ KO TAPHAO NOI ทำได้ในราคาถูก: ช่องว่างมีแค่ 17 ช่วง ทุกช่วงยาว ≥ 7 ชม. และ 97.5% ของ
ชั่วโมงที่หายอยู่ในช่วงยาวเกิน 2 วัน ⇒ กฎเข้มเสียข้อมูลเพิ่มจาก 3.10% เป็น 4.45% เท่านั้น

เขียนแล้ว 2026-09-30 (W2)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

HOURS_PER_DAY = 24
DAILY_HOUR = 12              # เก็บค่าเที่ยงวัน (GMT) = กึ่งกลางของวัน ตรงกับที่ UHSLC ใช้
MIN_DAYS_PER_MONTH = 15      # เดือนที่มีวันใช้ได้น้อยกว่านี้ถือว่าไม่มีค่า (เราเลือก = ครึ่งเดือน)
MIN_MONTHS_PER_YEAR = 12     # รายปีต้องครบ 12 เดือน — ไม่ยอมให้ฤดูใดฤดูหนึ่งหายไปแล้วเฉลี่ยเอียง

# ความถี่ขององค์ประกอบน้ำขึ้นน้ำลงหลัก (รอบต่อวัน) — ใช้ทั้งอธิบาย ทดสอบ และพล็อต
TIDES_CPD = {"M2": 1.9322736, "S2": 2.0, "N2": 1.8959819, "K2": 2.0054758,
             "K1": 1.0027379, "O1": 0.9295357, "P1": 0.9972621, "Q1": 0.8932441}


# ---------------------------------------------------------------------------
# 1. ออกแบบตัวกรอง — Kaiser window method (บทที่ 4)
# ---------------------------------------------------------------------------

def kaiser_beta(atten_db: float) -> float:
    """beta ของหน้าต่าง Kaiser จาก stopband attenuation ที่ต้องการ (Kaiser 1974)

    สูตรเชิงประสบการณ์ที่ใช้กันทั่วไป (Oppenheim & Schafer eq. 7.62):
        A > 50        beta = 0.1102 (A - 8.7)
        21 <= A <= 50 beta = 0.5842 (A - 21)^0.4 + 0.07886 (A - 21)
        A < 21        beta = 0   (= หน้าต่างสี่เหลี่ยม ซึ่งให้ ~21 dB อยู่แล้ว)
    """
    a = float(atten_db)
    if a > 50:
        return 0.1102 * (a - 8.7)
    if a >= 21:
        return 0.5842 * (a - 21) ** 0.4 + 0.07886 * (a - 21)
    return 0.0


def kaiser_numtaps(atten_db: float, f_pass: float, f_stop: float, fs: float) -> int:
    """จำนวน taps ขั้นต่ำจากสูตร Kaiser (Oppenheim & Schafer eq. 7.63) — บังคับเป็นเลขคี่

        M = (A - 8) / (2.285 * delta_omega)     delta_omega = 2 pi (f_stop - f_pass) / fs

    เลขคี่เพราะต้องการ Type I linear phase: หน่วงเวลา (N-1)/2 เป็นจำนวนเต็มพอดี
    ⇒ จัดตำแหน่งกลับได้เป๊ะโดยไม่ต้อง interpolate ครึ่งตัวอย่าง
    สูตรนี้เป็นค่าประมาณ ⇒ design_lowpass() วัด attenuation จริงแล้วเพิ่ม taps ถ้ายังไม่ถึง
    """
    d_omega = 2 * np.pi * (f_stop - f_pass) / fs
    n = int(np.ceil((atten_db - 8) / (2.285 * d_omega))) + 1
    return n if n % 2 == 1 else n + 1


def kaiser_window(numtaps: int, beta: float) -> np.ndarray:
    """w[n] = I0( beta sqrt(1 - ((n - alpha)/alpha)^2) ) / I0(beta)    alpha = (N-1)/2

    I0 = modified Bessel function ชนิดแรก อันดับศูนย์ (np.i0)
    beta ใหญ่ = หน้าต่างแคบลง = sidelobe ต่ำลง แต่ mainlobe กว้างขึ้น (แลกกันตรง ๆ)
    """
    if numtaps == 1:
        return np.ones(1)
    n = np.arange(numtaps)
    alpha = (numtaps - 1) / 2
    r = (n - alpha) / alpha
    return np.i0(beta * np.sqrt(np.clip(1 - r ** 2, 0, None))) / np.i0(beta)


@dataclass
class FIRDesign:
    """ตัวกรองที่ออกแบบแล้ว + สเปกที่มันถูกออกแบบมาให้ผ่าน (เก็บไว้รายงานและพล็อต)"""
    taps: np.ndarray
    fs: float                 # อัตราสุ่มขาเข้า (ตัวอย่าง/วัน)
    f_pass: float             # ขอบ passband (รอบ/วัน)
    f_stop: float             # ขอบ stopband (รอบ/วัน)
    atten_db: float           # attenuation ที่ **สเปก** ต้องการ
    beta: float
    formula_numtaps: int      # จำนวน taps ที่สูตร Kaiser ทำนาย (ก่อนปรับ)
    notes: list[str] = field(default_factory=list)

    @property
    def numtaps(self) -> int:
        return len(self.taps)

    @property
    def cutoff(self) -> float:
        return (self.f_pass + self.f_stop) / 2

    def response(self, nfft: int = 1 << 16) -> tuple[np.ndarray, np.ndarray]:
        """การตอบสนองขนาด |H(f)| บนแกน 0..fs/2 (รอบ/วัน) ด้วย FFT ที่เติมศูนย์ยาว ๆ"""
        H = np.abs(np.fft.rfft(self.taps, nfft))
        f = np.fft.rfftfreq(nfft, d=1 / self.fs)
        return f, H

    def gain_at(self, freqs) -> np.ndarray:
        """|H(f)| ที่ความถี่ใดก็ได้ — คำนวณ DTFT ตรง ๆ ไม่ต้องพึ่งกริดของ FFT"""
        n = np.arange(self.numtaps) - (self.numtaps - 1) / 2
        w = 2 * np.pi * np.atleast_1d(freqs)[:, None] / self.fs
        return np.abs(np.exp(-1j * w * n[None, :]) @ self.taps)

    def measured_stopband_db(self) -> float:
        """attenuation ที่วัดได้จริง = ค่าที่แย่ที่สุดใน [f_stop, fs/2]"""
        f, H = self.response()
        return float(-20 * np.log10(H[f >= self.f_stop].max()))

    def measured_passband_ripple(self) -> float:
        """ความคลาดเคลื่อนของ gain ที่แย่ที่สุดใน [0, f_pass] (หน่วยเท่า ไม่ใช่ dB)"""
        f, H = self.response()
        return float(np.abs(H[f <= self.f_pass] - 1).max())


def design_lowpass(f_pass: float, f_stop: float, atten_db: float, fs: float,
                   max_extra: int = 200) -> FIRDesign:
    """ออกแบบ FIR lowpass แบบ window method: sinc ในอุดมคติ × หน้าต่าง Kaiser

        h_d[n] = (2 fc / fs) sinc( 2 fc / fs * (n - alpha) )      fc = (f_pass + f_stop)/2
        h[n]   = h_d[n] w[n]  แล้ว normalize ให้ sum(h) = 1  (gain ที่ DC = 1 พอดี)

    ⚠️ สูตรจำนวน taps ของ Kaiser เป็นค่าประมาณ บางครั้งได้ attenuation ต่ำกว่าสเปกนิดหน่อย
    ⇒ วัดของจริงหลังออกแบบ ถ้ายังไม่ถึงให้เพิ่มทีละ 2 taps (คงความเป็นเลขคี่) จนกว่าจะถึง
    และจดไว้ใน notes ว่าต้องเพิ่มกี่ตัว — **ไม่ยอมรับตัวกรองที่ไม่ผ่านสเปกของตัวเอง**
    """
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


# ---------------------------------------------------------------------------
# 2. กรอง + decimate — คำนวณเฉพาะตัวอย่างที่จะเก็บ
# ---------------------------------------------------------------------------

def fir_at(x: np.ndarray, taps: np.ndarray, centers: np.ndarray) -> np.ndarray:
    """ค่าหลังกรองแบบ zero-phase **เฉพาะที่ตำแหน่ง centers** (กฎเข้มเรื่อง NaN)

    ทำไมไม่กรองทุกตัวอย่างแล้วค่อยเลือก: ใน 24 ตัวอย่างเราเก็บแค่ 1 ⇒ คำนวณอีก 23 ตัว
    แล้วทิ้งคือการเผางานเปล่า 96% หลักเดียวกับ polyphase decimator ในบทที่ 3
    (สลับลำดับ "กรอง" กับ "ลดอัตรา" ได้ถ้าทำให้ถูก — Noble identity)
    tests ยืนยันว่าได้ค่าเท่ากับ "กรองทั้งหมดแล้วค่อยเลือก" ทุกตัว

    zero-phase: taps ยาวคี่และสมมาตร ⇒ หน่วง (N-1)/2 พอดี จึงจัดกึ่งกลางหน้าต่างไว้ที่ center
    ได้ตรง ๆ ผลที่ center จึงแทนเวลา center จริง ไม่เลื่อน

    NaN: ขอบซ้าย/ขวาเติมด้วย NaN และ NaN ในข้อมูลก็ไม่แตะ ⇒ หน้าต่างไหนมี NaN
    ผลคูณเมทริกซ์ก็เป็น NaN เอง = กฎเข้มได้มาโดยไม่ต้องเขียนเงื่อนไขเพิ่ม
    """
    taps = np.asarray(taps, float)
    n = len(taps)
    if n % 2 == 0:
        raise ValueError("ต้องใช้ taps ยาวคี่ (Type I) เพื่อให้หน่วงเป็นจำนวนเต็ม")
    half = n // 2
    xp = np.pad(np.asarray(x, float), half, constant_values=np.nan)
    windows = sliding_window_view(xp, n)[np.asarray(centers)]   # แถว k = x[c-half : c+half+1]
    return windows @ taps[::-1]                                  # convolution = กลับด้าน taps


def hourly_to_daily(t_hourly: np.ndarray, v: np.ndarray, design: FIRDesign,
                    hour: int = DAILY_HOUR) -> tuple[np.ndarray, np.ndarray]:
    """รายชั่วโมง -> รายวัน: กรองด้วย FIR แล้วเก็บเฉพาะค่าที่ชั่วโมง `hour` ของแต่ละวัน

    t_hourly ต้องเป็น datetime64[h] บนกริดต่อเนื่อง (loaders.read_uhslc_grid ตรวจให้แล้ว)
    คืน (วัน datetime64[D], ค่ารายวัน) — วันที่หน้าต่างกรองไม่ครบเป็น NaN
    """
    if design.fs != HOURS_PER_DAY:
        raise ValueError(f"ตัวกรองออกแบบไว้ที่ fs={design.fs} แต่ข้อมูลเป็นรายชั่วโมง (24/วัน)")
    hours = (t_hourly - t_hourly.astype("datetime64[D]")).astype(int)
    centers = np.flatnonzero(hours == hour)
    return t_hourly[centers].astype("datetime64[D]"), fir_at(v, design.taps, centers)


def naive_daily(t_hourly: np.ndarray, v: np.ndarray,
                hour: int = DAILY_HOUR) -> tuple[np.ndarray, np.ndarray]:
    """รายชั่วโมง -> รายวัน **โดยไม่กรอง** (เก็บค่าชั่วโมงเดียวของวัน)

    มีไว้แสดงให้เห็นว่า aliasing ทำอะไรกับข้อมูล — **ห้ามใช้ผลิตผลจริง**
    """
    hours = (t_hourly - t_hourly.astype("datetime64[D]")).astype(int)
    idx = np.flatnonzero(hours == hour)
    return t_hourly[idx].astype("datetime64[D]"), np.asarray(v, float)[idx]


# ---------------------------------------------------------------------------
# 3. ค่าเฉลี่ยตามปฏิทิน — นิยามเดียวกับที่ PSMSL รายงาน
# ---------------------------------------------------------------------------

def _group_mean(keys: np.ndarray, values: np.ndarray, min_count: int
                ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """ค่าเฉลี่ยของค่าที่ไม่ใช่ NaN แยกตาม key (key ต้องเรียงอยู่แล้ว)"""
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
    """รายวัน -> ค่าเฉลี่ยเดือนปฏิทิน -> (เดือน datetime64[M], ค่า, จำนวนวันที่ใช้ได้)"""
    return _group_mean(days.astype("datetime64[M]"), daily, min_days)


def monthly_to_annual(months: np.ndarray, monthly: np.ndarray,
                      min_months: int = MIN_MONTHS_PER_YEAR
                      ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """รายเดือน -> ค่าเฉลี่ยรายปี -> (ปี int, ค่า, จำนวนเดือนที่ใช้ได้)

    เฉลี่ยจากรายเดือน (ไม่ใช่จากรายวันตรง ๆ) ⇒ ทุกเดือนมีน้ำหนักเท่ากัน ไม่ขึ้นกับว่า
    เดือนนั้นมีวันใช้ได้กี่วัน
    """
    years = months.astype("datetime64[Y]").astype(int) + 1970
    return _group_mean(years, monthly, min_months)


def monthly_mean_direct(t_hourly: np.ndarray, v: np.ndarray,
                        min_hours: int = MIN_DAYS_PER_MONTH * HOURS_PER_DAY
                        ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """ค่าเฉลี่ยรายเดือนจากรายชั่วโมงตรง ๆ **ไม่ผ่าน FIR** — ตัวเปรียบเทียบ

    boxcar ~730 ชม. ก็กด tide ได้ในตัวอยู่แล้วบางส่วน (sidelobe ของ sinc ที่ 1 cpd ~1%)
    มีไว้ตอบคำถามว่า "FIR ที่ออกแบบมาช่วยอะไรเพิ่มจากการเฉลี่ยเฉย ๆ" ด้วยตัวเลขจริง
    """
    return _group_mean(t_hourly.astype("datetime64[M]"), np.asarray(v, float), min_hours)


# ---------------------------------------------------------------------------
# 4. เทียบกับค่าอ้างอิง
# ---------------------------------------------------------------------------

def decimal_year_to_month(t: np.ndarray) -> np.ndarray:
    """ปีทศนิยมแบบกลางเดือนของ PSMSL (เช่น 1985.0417) -> datetime64[M]

    ปัดด้วย floor(t*12) แทนการลบปีแล้วคูณ — ทนต่อการที่ PSMSL เก็บเวลาแค่ทศนิยม 4 ตำแหน่ง
    (บั๊กเดียวกับที่เคยทำ to_monthly_grid ทำข้อมูลหาย 35% — ดู loaders.py)
    """
    k = np.floor(np.asarray(t, float) * 12 + 1e-6).astype(int)      # เดือนที่ k นับจากปี 0
    return (k - 1970 * 12).astype("datetime64[M]")


@dataclass
class Comparison:
    """ผลการเทียบอนุกรมของเรากับค่าอ้างอิงในช่วงที่ทับกัน"""
    n: int                    # จำนวนจุดที่มีค่าทั้งสองฝั่ง
    offset: float             # ค่าเฉลี่ยของ (เรา − อ้างอิง) = ความต่างของ datum
    median_offset: float      # ค่ากลางของ (เรา − อ้างอิง) — ทนต่อค่าโดด ใช้ดูขั้นบันไดของ datum
    rms: float                # RMS ของส่วนต่างหลังลบ offset
    corr: float
    max_abs: float
    keys: np.ndarray          # เวลา/เดือน/ปีของจุดที่ใช้เทียบ
    diff: np.ndarray          # ส่วนต่างหลังลบ offset


def compare(keys_a: np.ndarray, a: np.ndarray,
            keys_b: np.ndarray, b: np.ndarray) -> Comparison:
    """เทียบสองอนุกรมบน key ร่วม (เวลา) หลังลบ offset คงที่

    ทำไมลบ offset: UHSLC กับ PSMSL RLR อ้าง datum คนละตัว ความต่างที่เป็นค่าคงที่จึง
    ไม่ได้บอกอะไรเรื่องตัวกรอง — รายงาน offset แยกไว้ แต่ไม่นับรวมใน RMS
    """
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
