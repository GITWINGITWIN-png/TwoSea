"""★ cross-wavelet spectrum · wavelet coherence · multiple wavelet coherence

เส้นแบ่งที่ทำให้โปรเจกต์ผ่านหรือตกแกน "ตรงเป้า" ของวิชา
⛔ ห้ามเรียก pycwt.wct หรือ vectorwavelet::mwc ในไฟล์นี้เด็ดขาด
(ไฟล์นี้ import แค่ numpy กับ wtc.smoothing — ตรวจได้ด้วยตาที่บรรทัด import)

สมการเต็มอยู่ใน docs/source-paper-detail.md §3.1 และ §3.3

  xwt(Wx, Wy)                 cross-wavelet spectrum  W^XY = W^X * conj(W^Y)

  wtc(Wx, Wy, ...)            สมการ (1) ของ Grinsted et al. (2004)
                                  R^2 = |S(s^-1 W^XY)|^2
                                        / [ S(s^-1 |W^X|^2) * S(s^-1 |W^Y|^2) ]

  mwc(Wy, Wx_list, ...)       สมการ (4)-(6) ของ Hu & Si (2016)
                                  rho^2 = W~YX [W~XX]^-1 W~YX^H / W~YY
  SpectraCache + mwc_cached   ตัวเดียวกัน แต่เก็บ spectrum ที่ smooth แล้วไว้ใช้ซ้ำต่อคู่
                              (สำหรับค้นทุกชุดดัชนีใน W6 และสำหรับ null ของ MWC)

ตัวตรวจที่ทรงพลังที่สุดและได้มาฟรี: **mwc() ที่ q=1 ต้องเท่ากับ wtc() ภายใน 1e-10**

wtc เขียนแล้ว 2026-09-20 (W1) · mwc เขียนแล้ว 2026-09-30 (W5 ทำก่อนกำหนด)
"""
from __future__ import annotations
import numpy as np

from .smoothing import smooth


def xwt(Wx: np.ndarray, Wy: np.ndarray) -> np.ndarray:
    """cross-wavelet spectrum W^XY = W^X conj(W^Y)

    ขนาดบอก "สองอนุกรมมีพลังงานสูงพร้อมกันที่ไหน" ส่วนมุมบอกความต่างเฟส
    ⚠️ มันไม่ใช่ coherence — อนุกรมที่แรงทั้งคู่จะได้ค่าสูงแม้ไม่ได้สัมพันธ์กันเลย
    การหารด้วยพลังงานของแต่ละตัว (= ทำเป็น coherence) คือสิ่งที่แก้ปัญหานี้
    """
    return Wx * np.conj(Wy)


def _energy_density(W: np.ndarray, scales: np.ndarray) -> np.ndarray:
    """คูณตัวประกอบ s^-1 ก่อน smooth ตามที่สมการ (1) กำหนด

    ทำไมต้องมี: |W|^2 ที่สเกลใหญ่มีค่ามากกว่าโดยธรรมชาติเพราะหน้าต่างกว้างกว่า
    การหารด้วย s เปลี่ยนเป็น **ความหนาแน่นพลังงานต่อหน่วยสเกล** ซึ่งเทียบข้ามสเกลได้
    ลืมตัวนี้ = coherence เอียงเข้าหาสเกลใหญ่ทั้งระนาบ
    """
    return W / scales[:, None]


def wtc(Wx: np.ndarray, Wy: np.ndarray, dt: float, dj: float,
        scales: np.ndarray, compat: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """wavelet coherence -> (R2, phase)

    R2 อยู่ในช่วง [0, 1] เสมอโดย Cauchy-Schwarz (smoothing เป็นตัวดำเนินการเชิงบวก)
    ถ้าได้เกิน 1 แปลว่า smoothing พัง ⇒ ตรวจทันที ไม่ clip เงียบ ๆ

    phase = มุมของ S(s^-1 W^XY) หลัง smooth (ไม่ใช่ก่อน smooth อย่างที่ pycwt คืนมา)
    เพราะอันที่เข้าคู่กับค่า R2 ที่จุดเดียวกันคือตัวที่ผ่าน smoothing แล้ว
    0 = ไปด้วยกัน · pi = สวนทางกัน · pi/2 = X นำ Y อยู่หนึ่งในสี่ของคาบ

    compat=True ใช้การจัดการขอบแบบ pycwt — สำหรับตรวจประตู G1 เท่านั้น (ดู smoothing.smooth)
    """
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


# ---------------------------------------------------------------------------
# MWC — multiple wavelet coherence (W5)
# ---------------------------------------------------------------------------

# เกณฑ์ condition number ของเมทริกซ์ coherency C ที่เกินแล้วให้จุดนั้นเป็น NaN
#
# ที่มาของตัวเลข: MWC นิยามได้ทางคณิตศาสตร์ทุกครั้งที่ C เป็นบวกแน่นอน (ซึ่ง smoothing
# รับประกันให้อยู่แล้ว) ⇒ เหตุผลเดียวที่ต้องทิ้งจุดไหนคือ **ความแม่นของเลขทศนิยม**
# การ solve ระบบเชิงเส้นเสียความแม่นราว cond × 1e-16 ⇒ ที่ cond = 1e8 ความคลาดใน rho^2
# ยังอยู่ระดับ 1e-8 ซึ่งเล็กกว่าความละเอียดของ threshold (histogram 1000 ช่อง = 1e-3)
# ห้าห้าหลัก ⇒ ตัดที่นี่ปลอดภัย และ **ไม่ regularize** (การบวกค่าบนแนวทแยงเงียบ ๆ จะเปลี่ยน
# คำตอบไปจากนิยามโดยไม่มีใครรู้ — PLAN.md §8)
COND_MAX = 1e8


class SpectraCache:
    """S(s^-1 W^A conj(W^B)) ต่อคู่ (A, B) — คำนวณครั้งแรกที่ถูกขอ แล้วเก็บไว้

    ทำไมต้องมี: MWC ของทุกชุดดัชนีประกอบจาก spectrum ของ **คู่** อนุกรมเท่านั้น
    ⇒ ชุดดัชนี 218 ชุดของหนึ่งสถานีใช้ spectrum ร่วมกันแค่ 1 + 8 + 36 = 45 อัน
    ถ้าไม่ cache จะต้อง smooth ใหม่ทุกชุด (smoothing คือขั้นที่แพงที่สุดต่อหน่วย · PLAN.md §4)

    W       {ชื่อ: สัมประสิทธิ์ CWT (nscale, ntime)} — ชื่อเป็นอะไรก็ได้ที่ hash ได้
    ขอด้วย  cache(a, b) · ถ้าเคยคำนวณ (b, a) ไว้จะคืน conj ของตัวนั้น (Hermitian โดยนิยาม)
    """

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
            raw = np.abs(self.W[a]) ** 2                   # พลังงานของตัวเอง — จริงล้วน
        else:
            raw = xwt(self.W[a], self.W[b])
        S = smooth(_energy_density(raw, self.scales), self.dt, self.dj, self.scales,
                   self.compat)
        self._store[(a, b)] = S
        return S

    def with_series(self, name, W: np.ndarray) -> "SpectraCache":
        """cache ใหม่ที่อนุกรม `name` ถูกแทนด้วย W — คู่ที่ไม่เกี่ยวกับ `name` ใช้ของเดิมต่อ

        ใช้ตอนทำ null แบบ "Y ปลอม ดัชนีจริง": spectrum ของคู่ดัชนี–ดัชนี 36 อันไม่เปลี่ยน
        ⇒ smooth ใหม่แค่ 9 อันที่มี Y อยู่ (ไม่ copy ข้อมูล — ชี้ไปที่ array เดิม)
        """
        new = SpectraCache({**self.W, name: W}, self.dt, self.dj, self.scales, self.compat)
        new._store = {k: v for k, v in self._store.items() if name not in k}
        return new

    def __len__(self) -> int:
        return len(self._store)

    @property
    def nbytes(self) -> int:
        return sum(v.nbytes for v in self._store.values())


def coherency_matrix(cache: SpectraCache, xs, where: np.ndarray | None = None) -> np.ndarray:
    """C (nscale, ntime, q, q) — เมทริกซ์ W~XX ที่ normalize แนวทแยงเป็น 1
    (ถ้าให้ `where` มา คืนเฉพาะจุดที่ where เป็นจริง ⇒ รูปร่าง (npoint, q, q))

        C_ij = W~(Xi,Xj) / sqrt( W~(Xi,Xi) W~(Xj,Xj) )

    เทียบได้ตรงตัวกับ **เมทริกซ์สหสัมพันธ์** ของถดถอยพหุ แต่เป็นจำนวนเชิงซ้อนและ
    คิดแยกทุกจุด (s, t) · |C_ij|^2 คือ WTC ระหว่างดัชนี i กับ j ที่จุดนั้นพอดี
    Hermitian (C_ji = conj C_ij) โดยการสร้าง และบวกแน่นอนเพราะ smoothing ถ่วงน้ำหนักบวก
    """
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
    """MWC ของ y กับชุดดัชนี xs จาก spectrum ที่ cache ไว้ -> (R2, cond)

    สมการ (6) ของ Hu & Si (2016):

        rho^2 = W~YX [W~XX]^-1 W~YX^H / W~YY

    คำนวณในรูปที่ normalize แล้ว (พีชคณิตเหมือนกันทุกตัว แต่เลขดีกว่า):

        u_i   = W~(Y,Xi) / sqrt( W~(Y,Y) W~(Xi,Xi) )    ← coherency เชิงซ้อนของ Y กับ Xi
        rho^2 = u C^-1 u^H                              ← เหมือน R^2 = r' R^-1 r ของถดถอยพหุ

    (แทน A = D^½ C D^½ และ c = sqrt(W~YY) u D^½ ลงในสมการ (6) แล้ว D กับ W~YY หารกันหายหมด)
    ที่ q = 1 เหลือ |u|^2 = WTC พอดี ⇒ เป็นที่มาของเทสต์ "q=1 ต้องเท่ากับ WTC"

    cond  condition number ของ C ที่ทุกจุด (= lambda_max / lambda_min)
          จุดที่ cond > cond_max ⇒ R2 เป็น NaN **ไม่ regularize** (เหตุผลที่ COND_MAX)
          ผู้เรียกต้องนับสัดส่วน NaN แล้วรายงาน และตัดออกจากทั้งเศษและส่วนของ PASC

    MWC **ไม่มีเฟส** — ให้แค่ขนาด (docs/source-paper-detail.md §6 จ)

    สองตัวเลือกสำหรับงานที่ต้องเรียกเป็นแสนครั้ง (ค้นทุกชุด × null หลายร้อยรอบ · W6)
      where       mask (nscale, ntime) — คำนวณเฉพาะจุดที่เป็นจริง จุดอื่นได้ NaN ทั้ง R2 และ cond
                  (นอก COI ไม่ถูกนับอยู่แล้ว และเป็นที่เดียวที่เมทริกซ์ singular จริง)
      check_cond  False = ข้ามการหา condition number (ขั้นที่แพงที่สุด ~75% ของเวลา) แล้ว solve ตรง ๆ
                  cond ที่คืนเป็น NaN · ถ้าเมทริกซ์ singular จริง numpy จะ error ดัง ๆ ไม่เงียบ
                  **ใช้เฉพาะใน null** — W5 วัดแล้วว่า null 5000 ครั้งไม่มีจุดในกรวยเกิน COND_MAX เลย
                  ผลของข้อมูลจริงที่จะรายงานต้องใช้ check_cond=True เสมอ
    """
    xs = list(xs)
    if len(set(xs)) != len(xs):
        raise ValueError(f"ชุดดัชนีมีตัวซ้ำ {xs} — เมทริกซ์จะ singular โดยนิยาม")
    full_shape = cache(y, y).shape
    pick = (lambda a: a) if where is None else (lambda a: a[where])
    Syy = pick(cache(y, y).real)
    u = np.stack([pick(cache(y, x)) / np.sqrt(Syy * pick(cache(x, x).real)) for x in xs], axis=-1)

    if len(xs) == 1:                                   # ไม่ต้อง solve — C = [1]
        R2 = np.abs(u[..., 0]) ** 2
        cond = np.ones(R2.shape)
    else:
        C = coherency_matrix(cache, xs, where)
        if check_cond:
            ev = np.linalg.eigvalsh(C)                 # เรียงจากน้อยไปมาก · จริงเพราะ Hermitian
            with np.errstate(divide="ignore", invalid="ignore"):
                cond = np.where(ev[..., 0] > 0, ev[..., -1] / ev[..., 0], np.inf)
            ok = np.isfinite(cond) & (cond <= cond_max)  # singular จริง (cond = inf) ห้ามส่งเข้า solve
        else:
            cond = np.full(Syy.shape, np.nan)
            ok = np.ones(Syy.shape, bool)
        R2 = np.full(Syy.shape, np.nan)
        if ok.any():
            x = np.linalg.solve(C[ok], np.conj(u[ok])[..., None])[..., 0]   # C^-1 u^H
            R2[ok] = np.einsum("ki,ki->k", u[ok], x).real

    worst = np.nanmax(R2) if np.isfinite(R2).any() else 0.0
    if worst > 1 + 1e-8:
        raise ValueError(f"MWC = {worst:.6f} > 1 — smoothing หรือเมทริกซ์เพี้ยน ห้ามใช้ผลนี้ต่อ")
    if where is not None:                              # กระจายกลับเป็นระนาบเต็ม
        full_R2, full_cond = np.full(full_shape, np.nan), np.full(full_shape, np.nan)
        full_R2[where], full_cond[where] = R2, cond
        return full_R2, full_cond
    return R2, cond


def mwc(Wy: np.ndarray, Wx_list, dt: float, dj: float, scales: np.ndarray,
        compat: bool = False, cond_max: float = COND_MAX) -> tuple[np.ndarray, np.ndarray]:
    """MWC แบบเรียกครั้งเดียว (ไม่ต้องจัดการ cache เอง) -> (R2, cond)

    ใช้ตอนทดสอบ/สาธิต · ตอนค้นหลายชุดให้สร้าง SpectraCache เองแล้วเรียก mwc_cached
    เพื่อให้ spectrum ของคู่ที่ซ้ำกันถูก smooth ครั้งเดียว
    """
    Wx_list = list(Wx_list)
    for Wx in Wx_list:
        if Wx.shape != Wy.shape:
            raise ValueError(f"รูปร่างไม่ตรงกัน {Wx.shape} vs {Wy.shape}")
    W = {"y": Wy, **{i: Wx for i, Wx in enumerate(Wx_list)}}
    cache = SpectraCache(W, dt, dj, scales, compat)
    return mwc_cached(cache, "y", range(len(Wx_list)), cond_max)
