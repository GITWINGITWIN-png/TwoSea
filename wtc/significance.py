"""★ นัยสำคัญด้วย AR(1) surrogate — ส่วนที่เปเปอร์ต้นทางไม่บอกอะไรเลย

เปเปอร์ต้นทางเขียนแค่ "5% significance against red noise" ในคำบรรยายรูป
ไม่มีจำนวน surrogate ไม่มีวิธี fit AR(1) ไม่มี threshold ของ MWC สักตัว
(docs/source-paper-detail.md §3.4) -> ทุกอย่างในไฟล์นี้เป็นการเลือกของเรา
**ต้องประกาศให้ครบในรายงาน นั่นคือจุดขายเชิงวิธีของงานนี้**

จะมีอะไรบ้าง (PLAN.md §4)

  fit_ar1(z) -> (a, sigma)      ประมาณด้วย lag-1 autocorrelation (บทที่ 5)
  ar1_surrogate(n, a, sigma)    สร้างอนุกรมเทียม
  threshold_wtc(...)            เปอร์เซ็นไทล์ที่ 95 **แยกรายสเกล** จาก surrogate
  threshold_mwc(..., q)         null สร้างจาก AR(1) อิสระ q+1 เส้น
                                -> threshold ขึ้นกับ q ซึ่งเป็นเหตุผลว่าทำไม PASC
                                   ถึงพุ่งขึ้นเองเมื่อเพิ่มตัวแปร (เหมือน R^2 ของถดถอยพหุ)

จำนวน surrogate: 200 ตอนพัฒนา · **1000 ตอนรันจริง** · รายงาน threshold ทุกตัวในภาคผนวก
กลยุทธ์ลดเวลา: ใช้ null รวมต่อ (q, สถานี) ในขั้นค้นหา แล้วรัน null เต็มเฉพาะชุดที่รายงาน

ไม่ทำ areawise significance (Maraun & Kurths 2004) — เกินเวลา
ใช้การทดสอบดัชนีปลอมของ Q6 เป็นตัวแทนพื้นค่าเท็จแทน และเขียนข้อจำกัดนี้ไว้ให้ชัด

สถานะ: fit_ar1 + ar1_surrogate (W1) · threshold_wtc (W4 · 2026-09-30)
       threshold_mwc + pasc_null_mwc (W5 · 2026-09-30 ทำก่อนกำหนด)
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


def fit_ar1(z: np.ndarray, filled: np.ndarray | None = None) -> tuple[float, float]:
    """ประมาณ AR(1) จาก lag-1 autocorrelation -> (a, sigma ของ innovation)

        z[i] = a * z[i-1] + e[i]    โดย e ~ N(0, sigma^2)

    ใช้ lag-1 autocorrelation ตรง ๆ (Yule-Walker อันดับ 1) ตามบทที่ 5 ของวิชา
    ไม่ใช้ MLE เพราะ (ก) ที่ n ~ 865 ผลต่างเล็กมาก (ข) วิธีนี้อธิบายได้ในรายงานหนึ่งบรรทัด

    sigma มาจากความสัมพันธ์ var(z) = sigma^2 / (1 - a^2) ⇒ sigma = sd(z) * sqrt(1 - a^2)
    ⚠️ ถ้า a ใกล้ 1 มาก (อนุกรมเกือบเป็น random walk) ค่านี้จะเล็กลงจนเกือบศูนย์
    และ surrogate จะกลายเป็นเส้นแทบไม่ขยับ — ต้องดูค่า a ที่พิมพ์ออกมาทุกครั้ง ไม่ใช้แบบหลับตา

    filled (ถ้าให้มา): True = ตำแหน่งที่เป็นของเติม ⇒ ใช้เฉพาะคู่ (z[i-1], z[i]) ที่เป็น
    **ข้อมูลจริงทั้งคู่** (เพิ่ม 2026-09-30 · W4)

    ตัวที่ทำให้ a เพี้ยนจริงคือ **ช่องว่างสั้นที่เติมด้วยเส้นตรง** — จุดบนเส้นตรงเรียบต่อกัน
    เกินจริง ⇒ a ถูกดันขึ้น ⇒ null แดงเกินไป ⇒ threshold สูงเกิน ⇒ *พลาดสัญญาณจริง*
    (วัดแล้ว: AR(1) a=0.3 ที่มีรู 3 เดือนถี่ ๆ ได้ a=0.46 ถ้าไม่ใช้ mask · 0.325 ถ้าใช้)
    ส่วนช่องว่างยาวที่เติม 0 แทบไม่มีผล เพราะ anomaly มีค่าเฉลี่ย ≈ 0 คู่ (0,0) จึงไม่เพิ่ม
    อะไรให้ทั้งความแปรปรวนร่วมและความแปรปรวน — ตอนแรกเข้าใจผิดว่าตัวนี้คือปัญหา
    กับข้อมูลจริงของโปรเจกต์ผลต่างเล็ก (a เปลี่ยน ≤ 0.012) แต่ใช้ mask ไว้เพราะมันถูกต้องกว่า
    """
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
    """สร้างอนุกรมเทียม AR(1) ยาว n แล้ว normalize ให้เทียบกับของจริงได้

    ตั้งต้นด้วย z[0] = e[0] แล้วปล่อยให้ตัวมันเองวิ่ง — ช่วงต้นจะยังไม่เข้าสู่ภาวะคงตัว
    แต่ที่ n ~ 865 กับ a ~ 0.3-0.8 ช่วง burn-in สั้นกว่าความยาวอนุกรมมาก และ COI
    ก็ตัดขอบทิ้งอยู่แล้ว ⇒ ยอมรับได้ (ถ้า a เข้าใกล้ 1 เมื่อไร ต้องกลับมาทบทวนข้อนี้)
    """
    e = rng.normal(0.0, sigma, n)
    z = np.empty(n)
    z[0] = e[0]
    for i in range(1, n):
        z[i] = a * z[i - 1] + e[i]
    return (z - z.mean()) / z.std()


# ---------------------------------------------------------------------------
# threshold ของ WTC — เปอร์เซ็นไทล์ที่ 95 แยกรายสเกล (W4)
# ---------------------------------------------------------------------------

@dataclass
class WTCThreshold:
    """threshold ของ WTC หนึ่งคู่ + ทุกอย่างที่ต้องใช้รายงานในภาคผนวก"""
    level: float              # เช่น 0.95
    per_scale: np.ndarray     # threshold ของ R^2 แยกรายสเกล (NaN = สเกลที่ไม่มีจุดในกรวยเลย)
    nmc: int                  # จำนวน surrogate ที่ใช้จริง
    a_y: float
    a_x: float
    seed: int
    n_pooled: np.ndarray      # จำนวนค่าที่เอามาคิดในแต่ละสเกล (surrogate × จุดในกรวย)


def _quantile_from_hist(counts: np.ndarray, level: float, edges: np.ndarray) -> np.ndarray:
    """เปอร์เซ็นไทล์จาก histogram รายแถว + interpolate เชิงเส้นในช่อง"""
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
    """threshold ของ WTC ต่อสเกล จาก AR(1) surrogate คู่ที่เป็นอิสระต่อกัน

    วิธี (Grinsted et al. 2004 ทำแบบเดียวกัน)
      1. สร้างคู่อนุกรม AR(1) อิสระที่มี a เท่ากับของจริงแต่ละฝั่ง ยาวเท่าของจริง
      2. ส่งผ่านสายงานเดียวกันทุกขั้น (CWT -> smoothing -> WTC)
      3. ต่อสเกล: รวมค่า R^2 ของทุก surrogate **เฉพาะจุดที่อยู่ในกรวย COI**
         แล้วเอาเปอร์เซ็นไทล์ที่ `level`
    ⇒ ความหมายของ threshold: ถ้าสองอนุกรมไม่เกี่ยวกันเลยแต่มีความ "แดง" เท่าของจริง
      R^2 จะเกินค่านี้เพียง 5% ของจุดในกรวย ที่สเกลนั้น

    ทำไมแยกรายสเกล ไม่ใช้ค่าเดียวทั้งระนาบ: threshold เป็น **รูปตัว U** ตามสเกล
      - สเกลเล็กสุด (ใกล้ Nyquist) หน้าต่าง Gaussian กว้างแค่ sigma ≈ 1.9 ตัวอย่าง
        ⇒ เฉลี่ยจุดที่เป็นอิสระได้น้อย ⇒ R^2 ของ noise สูง
      - สเกลใหญ่ จุดในกรวย COI เหลือน้อยและเรียงติดกัน ⇒ R^2 ของ noise สูงอีก
      - ช่วงกลางแบนราว 0.59 (n = 865, a ~ 0.7/0.9)
    threshold ค่าเดียวทั้งระนาบจะทำให้สองปลาย "มีนัยสำคัญ" มั่วไปหมด

    ทำไมใช้ histogram: เก็บค่าดิบทั้งหมดต้องใช้ ~1000 × 107 × 865 ค่า ≈ 740 MB
    histogram 1000 ช่องต่อสเกลใช้ ~1 MB และละเอียดพอ (0.001 บนสเกล R^2 ที่อยู่ใน [0, 1])
    """
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
        b = np.clip((R2 * nbins).astype(int), 0, nbins - 1)       # ช่องของแต่ละจุด
        rows = np.broadcast_to(np.arange(len(scales))[:, None], R2.shape)
        np.add.at(counts, (rows[inside], b[inside]), 1)
    assert counts is not None
    return WTCThreshold(level=level, per_scale=_quantile_from_hist(counts, level, edges),
                        nmc=nmc, a_y=a_y, a_x=a_x, seed=seed, n_pooled=counts.sum(axis=1))


def pasc_null(thr: WTCThreshold, n: int, s_y: float, s_x: float,
              nmc: int | None = None, seed: int | None = None,
              dt: float | None = None, dj: float | None = None) -> dict[str, np.ndarray]:
    """การกระจายของ PASC เมื่อสองอนุกรม **ไม่เกี่ยวกันเลย** -> {ชื่อแถบ: PASC ของแต่ละ surrogate}

    ทำไมต้องมี (พบจากการทดสอบ 2026-09-30): threshold รายจุดรับประกันแค่ว่า "ค่าเฉลี่ย"
    ของ PASC ใน null ≈ 5% แต่ในแถบแคบ ๆ มันแกว่งมาก — คู่ AR(1) ที่ไม่เกี่ยวกันเลย
    ได้ PASC แถบ 2–7 ปีถึง ~22% ได้โดยบังเอิญ (sd ~5.5%) เพราะจุดข้างเคียงบนระนาบ
    สหสัมพันธ์กันสูง (ผ่าน smoothing มาแล้ว) จึงเกินเกณฑ์พร้อมกันเป็นก้อน
    ⇒ PASC ที่สังเกตได้ต้องเทียบกับการกระจายนี้ ไม่ใช่เทียบกับ 5% ตรง ๆ
    (นี่คือตัวแทนราคาถูกของ areawise significance ที่ PLAN.md §4 ตัดสินว่าไม่ทำ)

    ใช้ **surrogate ชุดใหม่** (seed ต่างจากที่ใช้คิด threshold) — ถ้าใช้ชุดเดิม
    แต่ละ surrogate จะถูกวัดด้วยเกณฑ์ที่ตัวมันเองมีส่วนสร้าง ผลจะเอียงเล็กน้อย
    """
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
    """p = (จำนวน null ที่ >= ค่าที่สังเกตได้ + 1) / (จำนวน null + 1)

    +1 ทั้งเศษและส่วนเพื่อไม่ให้ได้ p = 0 (ค่าที่สังเกตได้นับเป็นหนึ่งในชุดด้วย)
    ⇒ ด้วย 1000 surrogate ค่า p ที่เล็กที่สุดที่รายงานได้คือ 1/1001 ≈ 0.001
    """
    null = np.asarray(null, float)
    null = null[np.isfinite(null)]
    if not np.isfinite(observed) or len(null) == 0:
        return float("nan")
    return float((np.sum(null >= observed) + 1) / (len(null) + 1))


# ---------------------------------------------------------------------------
# threshold ของ MWC — null รวมต่อ (q, สถานี) (W5)
# ---------------------------------------------------------------------------

# surrogate ถูกแบ่งเป็นก้อนละ MC_CHUNK ชุด ก้อนที่ k ใช้ seed + k
# ⇒ ผลขึ้นกับ (seed, nmc) เท่านั้น **ไม่ขึ้นกับจำนวน worker** — รันบนเครื่องไหนก็ได้เลขเดิม
# และก้อนแรกใช้ seed ตรง ๆ ⇒ ถ้า nmc <= MC_CHUNK ลำดับการสุ่มจะเหมือน threshold_wtc ทุกตัว
# (เทสต์ใช้ข้อนี้ยืนยันว่า threshold_mwc ที่ q=1 ได้เลขเดียวกับ threshold_wtc เป๊ะ)
MC_CHUNK = 50


@dataclass
class MWCThreshold:
    """threshold ของ MWC ที่จำนวนดัชนี q หนึ่งค่า + ทุกอย่างที่ต้องรายงานในภาคผนวก"""
    q: int
    level: float
    per_scale: np.ndarray     # threshold ของ rho^2 แยกรายสเกล
    nmc: int
    pooled: bool              # True = สุ่มชุดดัชนีใหม่ทุก surrogate จากผู้สมัคร m ตัว
    a_y: float
    a_x: tuple                # a ของดัชนีผู้สมัครทั้งหมด (ตามลำดับที่ส่งเข้ามา)
    seed: int
    n_pooled: np.ndarray      # จำนวนค่าที่เอามาคิดในแต่ละสเกล
    n_nan: int                # จุดในกรวยที่ cond เกิน COND_MAX ใน null (คาดว่า 0)


def _mwc_null_chunk(task: dict) -> dict:
    """งานหนึ่งก้อน — ต้องอยู่ระดับโมดูลเพื่อให้ส่งข้าม process ได้

    ต่อ surrogate หนึ่งชุด:
      1. สร้าง Y และ X ผู้สมัคร **ทุกตัว** ตามลำดับเสมอ (การใช้เลขสุ่มจึงคงที่ ไม่ขึ้นกับว่า
         รอบนี้สุ่มได้ชุดไหน) — ถ้าผู้สมัครมี q ตัวพอดี ไม่ต้องสุ่มชุด
      2. สุ่มชุดดัชนีขนาด q หนึ่งชุดต่อ q (โหมด pooled)
      3. CWT + smooth เฉพาะอนุกรม/คู่ที่ถูกใช้จริง (SpectraCache คำนวณเมื่อถูกขอ)
      4. mode="hist": สะสม histogram ของ rho^2 รายสเกลในกรวย
         mode="pasc": คิด PASC ทุกแถบด้วย threshold ที่ให้มา
    """
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
    """แบ่ง nmc เป็นก้อน (ก้อน k ใช้ seed + k) แล้วรันทีละก้อนหรือขนานกัน — ผลเหมือนกันทุกกรณี"""
    sizes = [MC_CHUNK] * (nmc // MC_CHUNK) + ([nmc % MC_CHUNK] if nmc % MC_CHUNK else [])
    tasks = [dict(base, nmc=k_n, seed=seed + k) for k, k_n in enumerate(sizes)]
    if workers <= 1 or len(tasks) == 1:
        return [_mwc_null_chunk(t) for t in tasks]

    # ใช้ "spawn" + ตั้ง BLAS ให้เธรดเดียวก่อนเปิด process ลูก — ลูกจะ import numpy ใหม่
    # ด้วยค่านี้ ไม่งั้น worker หลายสิบตัว × BLAS หลายเธรดจะแย่งคอร์กันเอง (บทเรียนจาก W4)
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
    """threshold ของ MWC ต่อสเกล แยกตามจำนวนดัชนี q -> {q: MWCThreshold}

    a_x, s_x  พารามิเตอร์ AR(1) ของ **ดัชนีผู้สมัครทั้งหมด** (m ตัว)
    โหมดขึ้นกับ q เทียบกับ m
      q == m   null ของชุดนี้ชุดเดียวแบบเจาะจง (exact) — ใช้กับชุดที่รายงานเป็นผลสุดท้าย
      q <  m   **null รวมต่อ (q, สถานี)** — ทุก surrogate สุ่มชุดดัชนีขนาด q ใหม่จาก m ตัว
               ⇒ ได้ threshold เดียวใช้กับทุกชุดขนาด q (PLAN.md §4)

    ทำไมรวมได้: threshold ขึ้นกับความแดง (a) ของอนุกรมน้อยมาก — วัดจาก Q1 แล้วที่ q=1
    ดัชนี 8 ตัวที่ a ต่างกันตั้งแต่ 0.11 ถึง 0.96 ให้ threshold ต่างกันไม่เกิน ~0.03
    สิ่งที่ threshold ขึ้นกับจริงคือ **q** (ดู notebooks/05_mwc.ipynb §4 ที่ตรวจซ้ำที่ q > 1)
    ทำไมต้องรวม: null แยกทุกชุด = 218 ชุด × 1000 surrogate ต่อสถานี แพงกว่า ~50 เท่า

    null ของ MWC = Y กับ X ทุกตัว **อิสระต่อกันหมด** (ตามแบบของ Hu & Si 2016)
    ⇒ threshold ตอบคำถามว่า "ถ้าดัชนี q ตัวนี้ไม่เกี่ยวกับ Y เลย rho^2 จะสูงได้แค่ไหน"
    ซึ่งสูงขึ้นตาม q เสมอ — เหมือน R^2 ของถดถอยพหุที่สุ่มตัวทำนายมาใส่ก็ยังขึ้น

    workers > 1 รันขนาน — ผลเหมือนรันทีละก้อนทุกหลัก (ดู MC_CHUNK)
    ⚠️ สคริปต์ที่เรียกด้วย workers > 1 ต้องมี `if __name__ == "__main__":` ครอบโค้ดหลัก
       (process ลูกแบบ spawn จะ import สคริปต์นั้นใหม่ ถ้าไม่ครอบจะเปิด pool ซ้อนกันไม่รู้จบ)
       ในโน้ตบุ๊กไม่ต้อง เพราะ kernel ไม่มีไฟล์ __main__ ให้ import ซ้ำ
    """
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
    """การกระจายของ PASC ของ MWC เมื่อดัชนีไม่เกี่ยวกับ Y เลย -> {q: {แถบ: PASC ต่อ surrogate}}

    หลักเดียวกับ pasc_null ของ WTC (W4): threshold รายจุดคุมแค่ค่าเฉลี่ยของ PASC ใน null
    ส่วนการแกว่งรายแถบต้องวัดเอง · ใช้ **surrogate ชุดใหม่** (seed + 10000 เป็นค่าปริยาย)
    โหมด pooled/exact ตาม thr ที่ให้มา (สุ่มชุดดัชนีแบบเดียวกับตอนทำ threshold)
    """
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
