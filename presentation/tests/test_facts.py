"""ตัวเลขที่คลิปใช้ (data/facts.json) ต้องตรงกับที่รายงานเขียนไว้ — ภายในความละเอียดที่รายงานพิมพ์

รัน:  uv run pytest
ถ้าเทสต์แดง: อย่าแก้เลขในเทสต์ให้ผ่าน — หาก่อนว่ารายงานหรือข้อมูลเปลี่ยน แล้วตัดสินว่าคลิปควรพูดอะไร
"""

import json
from pathlib import Path

import pytest

FACTS = json.loads((Path(__file__).resolve().parent.parent / "data" / "facts.json").read_text())


def v(key):
    return FACTS[key]["value"]


# (fact, ค่าตามที่รายงานพิมพ์, ความคลาดเคลื่อนที่ยอมได้ = ครึ่งหนึ่งของหลักสุดท้ายที่พิมพ์)
REPORT = [
    ("series.n_months", 865, 0),
    ("fir.taps", 261, 0),
    ("fir.spec_db", 70, 0),
    ("fir.beta", 6.7553, 0.00005),
    ("fir.measured_db", 70.07, 0.005),
    ("fir.tide_suppression_min_db", 77, 0.5),
    ("fir.tide_suppression_max_db", 99, 0.5),
    ("alias.K1_days", 365.2, 0.05),
    ("alias.P1_days", 365.2, 0.05),
    ("alias.K2_days", 182.6, 0.05),
    ("decim.daily_rms_mm", 3.0, 0.05),
    ("season.share_gulf", 81, 0.5),
    ("season.share_andaman", 30, 0.5),
    ("season.amp_gulf_mm", 213, 0.5),
    ("season.amp_andaman_mm", 87, 0.5),
    ("corr.andaman.neg_nino34", 0.30, 0.005),
    ("corr.andaman.neg_dmi", 0.10, 0.005),
    ("event.andaman_9798_min_mm", -210, 5),          # รายงาน: "ราว 210 มม."
    ("cwt.scales_per_octave", 12, 0),
    ("noise.pasc_mean_plane", 5, 0.5),               # "เฉลี่ยราว 5%"
    ("noise.pasc_p95_plane", 9, 0.5),                # "ราว 9%"
    ("pasc.andaman.plane.soi", 14.3, 0.05),
    ("pasc.andaman.plane.dmi", 13.6, 0.05),
    ("pasc.andaman.plane.wnpmi", 13.3, 0.05),
    ("pasc.andaman.plane.nino34", 10.0, 0.05),
    ("pasc.andaman.band.wnpmi", 32.2, 0.05),
    ("pasc.andaman.band.dmi", 17.7, 0.05),
    ("pasc.andaman.band.soi", 16.1, 0.05),
    ("gulf.n_sig_index_variant", 0, 0),
    ("sens.n_variants", 8, 0),
    ("mwc.max_gain_plane", 0.6, 0.05),
    ("phase.soi.theta", -28, 0.5),
    ("phase.nino34.theta", 156, 0.5),
    ("phase.dmi.theta", -150, 0.5),
    ("phase.wnpmi.theta", 56, 0.5),
    ("phase.n_match", 4, 0),
    ("phase.soi.lag_months", -3, 0.5),               # "ตามหลังราว 3 เดือน"
    ("phase.nino34.lag_months", -3, 0.5),
    ("phase.dmi.lag_months", 5, 0.5),                # "ลดก่อน DMI ถึงจุดสูงสุดราว 5 เดือน"
    ("phase.wnpmi.lag_months", 6, 0.5),              # "นำราว 6 เดือน"
    ("phase.dmi.R", 0.55, 0.005),
    ("archive.wnpmi.psmsl", 70.5, 0.05),
    ("archive.wnpmi.uhslc", 34.9, 0.05),
    ("archive.soi.psmsl", 49.7, 0.05),
    ("archive.soi.uhslc", 50.3, 0.05),
]

REPORT_LISTS = [
    ("decim.monthly_median_mm", [1.1, 1.2], 0.05),
    ("noise.pasc_p95_band", [13, 15], 0.5),
    ("mwc.threshold_mid", [0.59, 0.77, 0.87, 0.93, 0.96], 0.005),
    ("mwc.andaman.fake_unadjusted", [4.8, 25.7, 59.8, 86.4, 97.2], 0.05),
    ("mwc.andaman.real_unadjusted", [9.3, 35.1, 67.5, 90.2, 98.5], 0.05),
]


@pytest.mark.parametrize("key, expected, tol", REPORT)
def test_number_matches_report(key, expected, tol):
    assert abs(v(key) - expected) <= tol + 1e-9, f"{key} = {v(key)} แต่รายงานพิมพ์ {expected}"


@pytest.mark.parametrize("key, expected, tol", REPORT_LISTS)
def test_series_matches_report(key, expected, tol):
    got = v(key)
    assert len(got) == len(expected)
    for g, e in zip(got, expected):
        assert abs(g - e) <= tol + 1e-9, f"{key} = {got} แต่รายงานพิมพ์ {expected}"


def test_robustness_counts_match_report():
    counts = [r["n_pass"] for r in v("robust.rows")]
    assert counts == [8, 8, 8, 8, 5, 6, 4]


def test_paper_curve_matches_report():
    assert [round(x) for x in v("paper.pasc_by_q").values()] == [14, 50, 81, 96]


def test_station_distance_is_about_470_km():
    # รายงาน §5 เขียน "ไม่ถึง 450 กม." แต่ระยะเส้นตรงจากพิกัดสถานีที่รายงานใช้เองคือ ~466 กม.
    # คลิปจึงพูดว่า "ราว 470 กม." (แจ้งผู้ใช้ให้แก้รายงานแล้ว 2026-10-08)
    assert 460 < v("stations.distance_km") < 470
