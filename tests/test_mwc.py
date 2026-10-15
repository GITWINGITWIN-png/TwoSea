"""ทดสอบ wtc/coherence.mwc() — multiple wavelet coherence (W5)

เกณฑ์ผ่าน (PLAN.md §6)
  - ★ **mwc ที่ q=1 ต้องเท่ากับ wtc เป๊ะ ภายใน 1e-10**
    ตัวตรวจที่ทรงพลังที่สุดของทั้งโปรเจกต์ และได้มาฟรีจากนิยาม
  - เมทริกซ์ W~(X,X) ต้องเป็น Hermitian และค่าลักษณะเฉพาะ > 0
    (ดักกรณีเกือบ singular ตอนรวม Nino3.4 กับ SOI)
  - mwc ต้องไม่ลดลงเมื่อเพิ่มตัวแปรเข้าไปในชุด (คุณสมบัติแบบ R^2 ของถดถอยพหุ)
    — ข้อนี้ไม่ใช่บั๊ก แต่เป็นเหตุผลว่าทำไมต้องมี Q6 (ทดสอบดัชนีปลอม)
  - ค่าที่ได้ต้องอยู่ในช่วง [0, 1] ทุกจุดที่ไม่ใช่ NaN

เพิ่มจากที่วางแผนไว้ (ได้มาระหว่างเขียน)
  - Y ที่เป็นผลรวมของ X1 + X2 เป๊ะ ⇒ MWC = 1 ทุกจุด ทั้งที่ WTC รายตัว < 1
    (เป็นตัวอย่างที่ชัดที่สุดว่า MWC จับ "การอธิบายร่วม" ที่ WTC รายตัวมองไม่เห็น)
  - ดัชนีที่ซ้ำกันเป๊ะ (X2 = -X1) ⇒ NaN ทั้งระนาบ ไม่ใช่ตัวเลขที่ถูก regularize มาเงียบ ๆ
  - การ normalize ขอบแกนสเกลยังหารกันหายใน MWC (เหมือนที่พบใน WTC ตอน G1)

เขียนแล้ว 2026-09-30 (W5 ทำก่อนกำหนด)
"""
import numpy as np
import pytest

from wtc.coherence import (SpectraCache, coherency_matrix, mwc, mwc_cached, wtc)
from wtc.significance import ar1_surrogate
from wtc.transform import DJ, DT_MONTHLY, coi_mask, cwt

N = 480


@pytest.fixture(scope="module")
def series():
    """Y ที่มีส่วนร่วมกับ X1 และ X2 จริง + noise · X3 อิสระ"""
    rng = np.random.default_rng(7)
    x1, x2, x3 = (ar1_surrogate(N, a, np.sqrt(1 - a * a), rng) for a in (0.8, 0.5, 0.3))
    y = 0.6 * x1 + 0.4 * x2 + 0.7 * ar1_surrogate(N, 0.6, 0.8, rng)
    return y, x1, x2, x3


@pytest.fixture(scope="module")
def transforms(series):
    y, x1, x2, x3 = series
    Wy, sc, per, coi = cwt(y)
    return Wy, [cwt(x)[0] for x in (x1, x2, x3)], sc, per, coi


def test_q1_equals_wtc(transforms):
    Wy, Wx, sc, _, _ = transforms
    for W in Wx:
        a, _ = wtc(Wy, W, DT_MONTHLY, DJ, sc)
        b, cond = mwc(Wy, [W], DT_MONTHLY, DJ, sc)
        assert np.max(np.abs(a - b)) < 1e-10
        assert np.all(cond == 1)


def test_range_and_hermitian_positive_definite(transforms):
    Wy, Wx, sc, per, coi = transforms
    cache = SpectraCache({"y": Wy, 0: Wx[0], 1: Wx[1], 2: Wx[2]}, DT_MONTHLY, DJ, sc)
    R2, _ = mwc_cached(cache, "y", [0, 1, 2])
    ok = np.isfinite(R2)
    assert np.all((R2[ok] >= -1e-12) & (R2[ok] <= 1 + 1e-10))

    # Hermitian: คำนวณ (1, 0) แยกจาก (0, 1) ใน cache ใหม่ แล้วต้องเป็น conj กันเป๊ะ
    other = SpectraCache({0: Wx[0], 1: Wx[1]}, DT_MONTHLY, DJ, sc)
    assert np.allclose(other(1, 0), np.conj(cache(0, 1)), rtol=0, atol=1e-12)

    C = coherency_matrix(cache, [0, 1, 2])
    assert np.allclose(C, np.conj(np.swapaxes(C, -1, -2)))
    inside = coi_mask(per, coi)
    ev = np.linalg.eigvalsh(C[inside])
    assert ev.min() > 0


def test_never_decreases_when_adding_an_index(transforms):
    """เหมือน R^2 ของถดถอยพหุ — ตัวที่เพิ่มเข้าไปเป็น noise ล้วน (X3) ก็ยังดันค่าขึ้น"""
    Wy, Wx, sc, _, _ = transforms
    r1, _ = mwc(Wy, Wx[:1], DT_MONTHLY, DJ, sc)
    r2, _ = mwc(Wy, Wx[:2], DT_MONTHLY, DJ, sc)
    r3, _ = mwc(Wy, Wx[:3], DT_MONTHLY, DJ, sc)
    ok = np.isfinite(r3)
    assert np.all(r2[ok] >= r1[ok] - 1e-10)
    assert np.all(r3[ok] >= r2[ok] - 1e-10)
    assert np.nanmean(r3) > np.nanmean(r2)          # X3 อิสระจาก Y จริง แต่ค่ายังขึ้น


def test_order_of_indices_does_not_matter(transforms):
    Wy, Wx, sc, _, _ = transforms
    a, _ = mwc(Wy, Wx, DT_MONTHLY, DJ, sc)
    b, _ = mwc(Wy, Wx[::-1], DT_MONTHLY, DJ, sc)
    ok = np.isfinite(a)
    assert np.max(np.abs(a[ok] - b[ok])) < 1e-10


def test_exact_sum_is_fully_explained(series):
    """Y = X1 + X2 ⇒ W^Y = W^X1 + W^X2 ทุกจุด (CWT เป็นเชิงเส้น) ⇒ MWC = 1

    ส่วน WTC รายตัวต้องน้อยกว่า 1 ชัดเจน — MWC เห็นสิ่งที่ WTC รายตัวมองไม่เห็น
    """
    _, x1, x2, _ = series
    W1, sc, per, coi = cwt(x1)
    W2 = cwt(x2)[0]
    Wy = cwt(x1 + x2)[0]
    R2, _ = mwc(Wy, [W1, W2], DT_MONTHLY, DJ, sc)
    inside = coi_mask(per, coi)
    assert np.max(np.abs(R2[inside] - 1)) < 1e-10
    single, _ = wtc(Wy, W1, DT_MONTHLY, DJ, sc)
    assert np.mean(single[inside]) < 0.9


def test_identical_indices_become_nan_not_regularized(transforms):
    """X2 = -X1 ⇒ C singular ทุกจุด ⇒ ต้องได้ NaN ทั้งระนาบ

    ถ้าโค้ดแอบบวกค่าบนแนวทแยง (regularize) เทสต์นี้จะเห็นตัวเลขแทน NaN
    """
    Wy, Wx, sc, _, _ = transforms
    R2, cond = mwc(Wy, [Wx[0], -Wx[0]], DT_MONTHLY, DJ, sc)
    assert np.all(np.isnan(R2))
    assert np.all(cond > 1e8)


def test_duplicate_key_is_rejected(transforms):
    Wy, Wx, sc, _, _ = transforms
    cache = SpectraCache({"y": Wy, 0: Wx[0]}, DT_MONTHLY, DJ, sc)
    with pytest.raises(ValueError):
        mwc_cached(cache, "y", [0, 0])


def test_scale_edge_renormalization_cancels(transforms):
    """ข้อ 3 ของ G1: normalize ขอบแกนสเกลคูณทั้งแถวด้วยค่าเดียวกัน ⇒ หายไปใน MWC ด้วย

    compat=True เปลี่ยนแค่การจัดการขอบแกนสเกล (แกนเวลาเติมศูนย์เหมือนกัน)
    """
    Wy, Wx, sc, _, _ = transforms
    a, _ = mwc(Wy, Wx, DT_MONTHLY, DJ, sc)
    b, _ = mwc(Wy, Wx, DT_MONTHLY, DJ, sc, compat=True)
    ok = np.isfinite(a) & np.isfinite(b)
    assert np.max(np.abs(a[ok] - b[ok])) < 1e-12


def test_cache_reuses_pairs(transforms):
    """ชุด {0,1} แล้ว {0,1,2} ต้อง smooth เพิ่มแค่คู่ที่ยังไม่มี — ไม่ใช่ทั้งหมดใหม่"""
    Wy, Wx, sc, _, _ = transforms
    cache = SpectraCache({"y": Wy, 0: Wx[0], 1: Wx[1], 2: Wx[2]}, DT_MONTHLY, DJ, sc)
    mwc_cached(cache, "y", [0, 1])
    assert len(cache) == 1 + 2 + 3                    # yy · y0 y1 · 00 11 01
    mwc_cached(cache, "y", [0, 1, 2])
    assert len(cache) == 1 + 3 + 6                    # + y2 · 22 02 12


# ---------------------------------------------------------------------------
# threshold ของ MWC (significance.threshold_mwc / pasc_null_mwc)
# ---------------------------------------------------------------------------

from wtc.significance import pasc_null_mwc, threshold_mwc, threshold_wtc   # noqa: E402

A_X = (0.9, 0.2, 0.6)                    # ผู้สมัคร 3 ตัว ความแดงต่างกันมาก
S_X = tuple(np.sqrt(1 - a * a) for a in A_X)


@pytest.fixture(scope="module")
def mwc_thr():
    return threshold_mwc(N, 0.6, 0.8, A_X, S_X, qs=(1, 2, 3), nmc=60, seed=11)


def test_threshold_mwc_q1_exact_equals_threshold_wtc():
    """โหมด exact ที่ q=1 ต้องสุ่มลำดับเดียวกับ threshold_wtc ⇒ เลขเดียวกันทุกหลัก

    ยืนยันว่าเส้นทาง MWC (cache + mwc_cached + histogram) ไม่ได้เพี้ยนไปจากเส้นทาง WTC
    ที่ผ่าน G2 มาแล้ว — ถ้าต่างแม้แต่หลักเดียวแปลว่ามีอะไรไม่ตรงกัน
    """
    a = threshold_wtc(N, 0.6, 0.8, 0.3, np.sqrt(1 - 0.09), nmc=20, seed=4)
    b = threshold_mwc(N, 0.6, 0.8, [0.3], [np.sqrt(1 - 0.09)], qs=(1,), nmc=20, seed=4)[1]
    assert not b.pooled
    np.testing.assert_array_equal(a.per_scale, b.per_scale)


def test_threshold_rises_with_q(mwc_thr):
    """หัวใจของ Q6: noise ล้วน q ตัว ได้ rho^2 สูงขึ้นเรื่อย ๆ ตาม q"""
    mid = [np.nanmedian(mwc_thr[q].per_scale[30:70]) for q in (1, 2, 3)]
    assert mid[0] < mid[1] < mid[2]
    assert mwc_thr[1].pooled and mwc_thr[2].pooled and not mwc_thr[3].pooled


def test_pooled_null_gives_about_five_percent(mwc_thr):
    """threshold รวมต่อ q ต้องให้ PASC ของ null เฉลี่ยใกล้ 5% ทุก q (นิยามของเกณฑ์ 95%)"""
    null = pasc_null_mwc(mwc_thr, N, 0.8, S_X, nmc=30)
    for q in (1, 2, 3):
        assert 2.5 < np.mean(null[q]["ทั้งระนาบ"]) < 8.0, q


def test_parallel_gives_identical_numbers():
    """ผลขึ้นกับ (seed, nmc) เท่านั้น ไม่ขึ้นกับจำนวน worker (ก้อนละ MC_CHUNK ชุด ก้อน k ใช้ seed+k)"""
    kw = dict(n=240, a_y=0.5, s_y=0.87, a_x=A_X[:2], s_x=S_X[:2], qs=(2,), nmc=110, seed=2)
    a = threshold_mwc(**kw, workers=1)[2].per_scale
    b = threshold_mwc(**kw, workers=3)[2].per_scale
    np.testing.assert_array_equal(a, b)


def test_where_and_unchecked_paths_agree_with_default(transforms):
    """ทางลัดที่ W6 ใช้ (คำนวณเฉพาะในกรวย · ข้าม condition number) ต้องได้เลขเดียวกับทางปกติ"""
    Wy, Wx, sc, per, coi = transforms
    cache = SpectraCache({"y": Wy, 0: Wx[0], 1: Wx[1], 2: Wx[2]}, DT_MONTHLY, DJ, sc)
    inside = coi_mask(per, coi)
    full, cond = mwc_cached(cache, "y", [0, 1, 2])
    a, cond_a = mwc_cached(cache, "y", [0, 1, 2], where=inside)
    b, cond_b = mwc_cached(cache, "y", [0, 1, 2], where=inside, check_cond=False)
    assert np.all(np.isnan(a[~inside])) and np.all(np.isnan(b[~inside]))
    assert np.max(np.abs(a[inside] - full[inside])) < 1e-12
    assert np.max(np.abs(b[inside] - full[inside])) < 1e-12
    assert np.allclose(cond_a[inside], cond[inside]) and np.all(np.isnan(cond_b))


def test_with_series_reuses_index_pairs(transforms):
    """เปลี่ยน Y แล้ว spectrum ของคู่ดัชนี–ดัชนีต้องไม่ถูกคำนวณใหม่ และผลต้องเท่ากับสร้าง cache ใหม่"""
    Wy, Wx, sc, _, _ = transforms
    base = SpectraCache({"y": Wy, 0: Wx[0], 1: Wx[1]}, DT_MONTHLY, DJ, sc)
    mwc_cached(base, "y", [0, 1])
    other = base.with_series("y", Wx[2])
    assert set(other._store) == {(0, 0), (1, 1), (0, 1)}
    assert other(0, 1) is base(0, 1)
    a, _ = mwc_cached(other, "y", [0, 1])
    b, _ = mwc(Wx[2], Wx[:2], DT_MONTHLY, DJ, sc)
    assert np.nanmax(np.abs(a - b)) < 1e-12
