"""ชั้น CWT — ห่อ pycwt.cwt (อนุญาตให้เรียก) แล้วคุมสเกล/COI เอง

pycwt.cwt เรียกได้ตามที่ตกลงไว้ใน docs/syllabus-map.md (ทาง C ของ feasibility)
สิ่งที่ต้องคุมเองคือทุกอย่างที่อยู่รอบ ๆ มัน เพราะเปเปอร์ต้นทางไม่ประกาศพารามิเตอร์ไว้เลย

พารามิเตอร์ที่โปรเจกต์นี้ประกาศ (PLAN.md §4)
    Morlet omega0 = 6 · dj = 1/12 · dt = 1/12 ปี (รายเดือน)

📝 **แก้จาก PLAN.md หนึ่งจุด และเป็นการแก้ที่ตั้งใจ** — PLAN เขียนว่า `s0 = 2dt`
   แต่ 2dt ในที่นั้นควรหมายถึง "**คาบ**ที่สั้นที่สุดที่ยังแทนได้" = ความถี่ Nyquist
   ซึ่งตรงกับ **สเกล** s0 = 2dt/flambda ไม่ใช่ s0 = 2dt (สำหรับ Morlet omega0=6
   ค่า flambda = 4pi/(omega0 + sqrt(2+omega0^2)) ~ 1.033 ⇒ ต่างกัน 3.3%)
   เลือกแบบคาบเพราะ (ก) เป็นความหมายที่อยากประกาศในรายงานจริง ๆ
   (ข) เป็นค่า default ของ pycwt ⇒ ตอนตรวจประตู G1 ความต่างที่เห็นจะเป็นของ
   *โค้ดเรา* ล้วน ๆ ไม่ใช่ของการตั้งพารามิเตอร์คนละแบบ
   ⚠️ ต้องแก้ตัวเลขนี้ใน PLAN.md §4 และประกาศในรายงานตามนี้

เขียนแล้ว 2026-09-20 (W1)
"""
from __future__ import annotations
import numpy as np

OMEGA0 = 6.0          # Morlet: 6 คือค่ามาตรฐานที่ให้สมดุลเวลา-ความถี่ที่ดีและ flambda ~ 1
DJ = 1 / 12           # 12 สเกลต่อหนึ่ง octave — ละเอียดพอจะแยกแถบ 2-7 ปีกับ 8-16 ปีได้
DT_MONTHLY = 1 / 12   # หน่วยเวลาของทั้งโปรเจกต์คือ "ปี" ⇒ รายเดือน = 1/12 ปี


def morlet_flambda(omega0: float = OMEGA0) -> float:
    """ตัวคูณแปลงสเกลเป็นคาบฟูเรียร์: period = flambda * scale (Torrence & Compo 1998 Table 1)"""
    return 4 * np.pi / (omega0 + np.sqrt(2 + omega0 ** 2))


def cwt(y: np.ndarray, dt: float = DT_MONTHLY, dj: float = DJ,
        s0: float | None = None, j: int | None = None, omega0: float = OMEGA0):
    """CWT ของอนุกรมเดียว -> (W, scales, periods, coi)

    W       (nscale, ntime) สัมประสิทธิ์เชิงซ้อน
    scales  สเกลแบบดยาดิก s_j = s0 * 2^(j*dj) — metrics.py นับพื้นที่ PASC บนแกนนี้
    periods คาบฟูเรียร์ที่สมมูล = flambda * scales (หน่วยเดียวกับ dt)
    coi     คาบที่ยาวที่สุดที่ยังเชื่อได้ ณ เวลานั้น ๆ (ยาวกว่านี้คือโดนขอบกิน)

    ⚠️ ไม่ normalize ให้ — อนุกรมที่เข้ามาควรผ่าน preprocess.detrend_deseason มาแล้ว
    ซึ่ง normalize ให้ความแปรปรวนเป็น 1 ไปเรียบร้อย การ normalize ซ้ำไม่เปลี่ยน
    coherence (มันหารกันหายไป) แต่จะเปลี่ยน power ⇒ ไม่ทำเงียบ ๆ ดีกว่า
    """
    import pycwt                                   # อนุญาตเฉพาะ cwt — ห้าม wct

    y = np.asarray(y, float)
    if s0 is None:
        s0 = 2 * dt / morlet_flambda(omega0)       # ⇒ คาบสั้นสุด = 2dt = Nyquist
    if j is None:
        j = int(round(np.log2(y.size * dt / s0) / dj))
    W, scales, freqs, coi, _, _ = pycwt.cwt(y, dt, dj, s0, j, pycwt.Morlet(omega0))
    return W, scales, 1 / freqs, coi


def coi_mask(periods: np.ndarray, coi: np.ndarray) -> np.ndarray:
    """(nscale, ntime) True = อยู่ในกรวยอิทธิพล ใช้ได้จริง

    ทุกที่ที่นับพื้นที่หรือเฉลี่ยค่าต้องคูณ mask นี้ก่อนเสมอ — นอกกรวยคือบริเวณที่
    wavelet ยื่นออกไปนอกอนุกรมแล้วถูกเติมด้วยศูนย์ ค่าที่ได้จึงถูกกดลงโดยไม่มีความหมายทางกายภาพ
    เปเปอร์ต้นทางเรียกบริเวณนี้ว่า "invalid area" แต่ไม่เคยบอกตรง ๆ ว่าตัดออกจาก PASC หรือเปล่า
    — เราตัด และเขียนไว้ในรายงาน (PLAN.md §4)
    """
    return periods[:, None] <= coi[None, :]
