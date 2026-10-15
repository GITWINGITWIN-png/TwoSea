"""ทดสอบ wtc/series.py — การสร้างอนุกรมแบบมาตรฐานและแบบทดสอบความไว (W7)

เกณฑ์ผ่าน
  - **แบบมาตรฐานต้องได้เลขเดียวกับ data/processed/series.npz ทุกหลัก** — ย้ายโค้ดแล้วผลต้องไม่ขยับ
  - แต่ละแบบเปลี่ยนเฉพาะสิ่งที่ประกาศ (ตัดปี 2004–2005 ⇒ ช่วงนั้นเป็นของเติมทั้งหมด · ตัด AMO ⇒ 7 ดัชนี
    และยาวขึ้น · interp ทุกช่องว่าง ⇒ mask เดิมแต่ค่าในช่องว่างยาวไม่ใช่ 0)
  - คู่เทียบ short_1985 กับ y_q7 ต้องอยู่บนกริดเดียวกันเป๊ะ (ไม่งั้นแยกผลของ "แหล่ง" กับ "ความยาว" ไม่ได้)

เขียนแล้ว 2026-10-07 (W7)
"""
from pathlib import Path

import numpy as np
import pytest

from wtc.series import BASELINE, VARIANTS, build_series

SERIES = Path(__file__).resolve().parent.parent / "data" / "processed" / "series.npz"


@pytest.fixture(scope="module")
def base():
    return build_series(BASELINE)


@pytest.mark.skipif(not SERIES.exists(), reason="ต้องรัน scripts/build_series.py ก่อน")
def test_baseline_matches_saved_file(base):
    saved = np.load(SERIES, allow_pickle=True)
    for k in ("t", "Y", "Y_fill", "X", "X_fill", "y_names", "x_names"):
        np.testing.assert_array_equal(base[k], saved[k], err_msg=k)


def test_cut_2004_marks_both_years_as_filled(base):
    d = build_series(VARIANTS["cut_2004"])
    cut = (d["t"] >= 2004) & (d["t"] < 2006)
    assert cut.sum() == 24
    assert d["Y_fill"][:, cut].all()
    np.testing.assert_array_equal(d["X"], base["X"])              # ดัชนีไม่ถูกแตะ
    assert d["Y_fill"].sum() > base["Y_fill"].sum()


def test_no_amo_drops_one_index_and_extends_window(base):
    d = build_series(VARIANTS["no_amo"])
    assert "amo" not in d["x_names"] and len(d["x_names"]) == 7
    assert d["t"][-1] > base["t"][-1] + 1                         # ยาวขึ้นอย่างน้อยหนึ่งปี
    assert d["t"][0] == base["t"][0]


def test_interp_all_keeps_mask_but_changes_long_gaps(base):
    d = build_series(VARIANTS["interp_all"])
    np.testing.assert_array_equal(d["Y_fill"], base["Y_fill"])   # อะไรเป็นของเติมไม่เปลี่ยน
    changed = np.abs(d["Y"] - base["Y"]) > 1e-12
    assert changed.any() and np.all(d["Y_fill"][changed])         # เปลี่ยนได้เฉพาะตำแหน่งของเติม


def test_short_and_q7_share_the_same_grid():
    a = build_series(VARIANTS["short_1985"])
    b = build_series(VARIANTS["y_q7"])
    np.testing.assert_array_equal(a["t"], b["t"])
    assert list(a["y_names"]) == list(b["y_names"]) == ["ko_taphao_noi", "ko_lak"]
    assert 1985 <= a["t"][0] < 1985.1 and 2019.9 < a["t"][-1] < 2020
    # Y ต่างแหล่งแต่ความสัมพันธ์ต้องสูง (KO LAK สองแหล่งตรงกันเกือบสมบูรณ์ — ตรวจแล้วตอนสร้างแบบนี้)
    lak = list(a["y_names"]).index("ko_lak")
    real = ~a["Y_fill"][lak] & ~b["Y_fill"][lak]
    assert np.corrcoef(a["Y"][lak][real], b["Y"][lak][real])[0, 1] > 0.95
