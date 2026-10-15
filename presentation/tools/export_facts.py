"""ดึงตัวเลขทุกตัวที่คลิปใช้ ออกจากโครงงาน DSP โดยตรง -> data/facts.json + data/derived.npz

ต้องรันด้วย Python ของโครงงาน DSP เอง (เพื่อใช้โค้ด wtc/ และ scripts/ ชุดเดียวกับที่สร้างรายงาน
ไม่ต้องเขียนสูตรซ้ำ ซึ่งเป็นจุดที่ตัวเลขจะเพี้ยนได้):

    PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python tools/export_facts.py

อ่านโครงงานอย่างเดียว — เขียนเฉพาะในโฟลเดอร์ production นี้

ทุก fact มี: value · unit · kind (data = คำนวณจากข้อมูล · literature = อ้างงานวิจัยผ่านรายงาน ·
method = ค่าตั้งของวิธี) · source (หัวข้อในรายงาน + ไฟล์/ฟังก์ชันที่ใช้)
"""

from __future__ import annotations

import json
import math
import sys
import tomllib
from pathlib import Path

import numpy as np
from scipy.signal import freqz

HERE = Path(__file__).resolve().parent.parent
# path ใน studio.toml สัมพัทธ์กับโฟลเดอร์ presentation/ (ปัจจุบัน ".." = repo โครงงาน)
DSP = (HERE / Path(tomllib.loads((HERE / "studio.toml").read_text())["sources"]["dsp_project"]).expanduser()).resolve()
PROC = DSP / "data" / "processed"
sys.path.insert(0, str(DSP))
sys.path.insert(0, str(DSP / "scripts"))

import make_infographics as I  # noqa: E402  (ไม่วาดอะไร แค่ใช้ฟังก์ชันช่วยชุดเดียวกับรูปในรายงาน)

FACTS: dict[str, dict] = {}


def fact(key, value, unit, kind, source):
    if isinstance(value, (np.floating, np.integer)):
        value = value.item()
    FACTS[key] = {"value": value, "unit": unit, "kind": kind, "source": source}


def load(name):
    return np.load(PROC / name, allow_pickle=True)


# --- ข้อมูลพื้นฐาน (SQ01–SQ02) ------------------------------------------------------------------------
series = load("series.npz")
meta = json.loads(str(series["meta"]))
fact("series.n_months", meta["n"], "เดือน", "data", "§2 ตาราง data · series.npz meta.n")
w0, w1 = meta["window"]
fact("series.start_year", int(w0), "ปี", "data", "§2 · series.npz meta.window")
fact("series.years", round(w1 - w0), "ปี", "data", "§8 'ข้อมูล 72 ปี' · series.npz meta.window")
fact("indices.n", len(series["x_names"]), "ดัชนี", "data", "§2 · series.npz x_names")
fact("series.end_year", int(w1), "ปี", "data", "§2 · series.npz meta.window")

(lat_a, lon_a), (lat_g, lon_g) = (I.STATION_LL["ko_taphao_noi"][::-1], I.STATION_LL["ko_lak"][::-1]) \
    if abs(I.STATION_LL["ko_taphao_noi"][0]) > 90 else (I.STATION_LL["ko_taphao_noi"], I.STATION_LL["ko_lak"])


def haversine_km(lat1, lon1, lat2, lon2, r=6371.0):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


fact("stations.distance_km", haversine_km(lat_a, lon_a, lat_g, lon_g), "กม.", "data",
     "ระยะเส้นตรง (great circle) ระหว่างพิกัดสถานีใน make_infographics.STATION_LL · รายงาน §5 เขียน 'ไม่ถึง 450 กม.'")
fact("stations.ktn_latlon", [lat_a, lon_a], "องศา", "data", "§2 ตาราง data · STATION_LL")
fact("stations.klk_latlon", [lat_g, lon_g], "องศา", "data", "§2 ตาราง data · STATION_LL")

# --- SQ03: ตัวกรองและการลดอัตราสุ่ม ------------------------------------------------------------------------
dec = load("decimation.npz")
spec = json.loads(str(dec["spec"]))
res = json.loads(str(dec["results"]))
taps = dec["taps"]
fact("fir.taps", len(taps), "taps", "data", "§3 กล่อง Q7 · decimation.npz taps")
fact("fir.spec_db", spec["atten_db"], "dB", "method", "§3 กล่อง Q7 · decimation.npz spec")
fact("fir.beta", 0.1102 * (spec["atten_db"] - 8.7), "", "method", "§3 กล่อง Q7 · สูตร Kaiser β = 0.1102(A − 8.7)")
fs = spec["fs"]  # ตัวอย่างต่อวัน (รายชั่วโมง = 24)
w, h = freqz(taps, worN=1 << 16, fs=fs)
stop = w >= spec["f_stop"]
fact("fir.measured_db", -20 * np.log10(np.abs(h[stop]).max()), "dB", "data",
     "§3 กล่อง Q7 · ความลดทอนต่ำสุดในแถบหยุดของ taps จริง (freqz)")
# ความเร็วเชิงมุมมาตรฐานขององค์ประกอบน้ำขึ้นน้ำลง (รอบ/วัน)
TIDES = {"M2": 1.9322736, "S2": 2.0, "N2": 1.8959820, "K2": 2.0054758,
         "K1": 1.0027379, "O1": 0.9295357, "P1": 0.9972621, "Q1": 0.8932441}
supp = {}
for name, f0 in TIDES.items():
    _, hk = freqz(taps, worN=[f0], fs=fs)
    supp[name] = float(-20 * np.log10(abs(hk[0])))
fact("fir.tide_suppression_db", supp, "dB", "data", "§3 กล่อง Q7 · |H| ที่ความถี่องค์ประกอบน้ำขึ้นน้ำลง")
fact("fir.tide_suppression_min_db", min(supp.values()), "dB", "data", "§3 กล่อง Q7 (77–99 dB)")
fact("fir.tide_suppression_max_db", max(supp.values()), "dB", "data", "§3 กล่อง Q7 (77–99 dB)")


def alias_period_days(f_cpd, fs_cpd=1.0):
    """ความถี่ที่ถูกพับเมื่อสุ่มวันละครั้ง -> คาบ (วัน)"""
    fa = abs(f_cpd - round(f_cpd / fs_cpd) * fs_cpd)
    return 1.0 / fa


fact("alias.K1_days", alias_period_days(TIDES["K1"]), "วัน", "method", "§3 กล่อง Q7 · K1 สุ่มรายวัน")
fact("alias.P1_days", alias_period_days(TIDES["P1"]), "วัน", "method", "§3 กล่อง Q7 · P1 สุ่มรายวัน")
fact("alias.K2_days", alias_period_days(TIDES["K2"]), "วัน", "method", "§3 กล่อง Q7 · K2 สุ่มรายวัน")
fact("decim.daily_rms_mm", res["daily_vs_uhslc"]["rms"], "มม.", "data", "§3 กล่อง Q7 · decimation results daily_vs_uhslc")
mon = [v["median_abs"] for k, v in res.items() if k.startswith("monthly ") and ("1988" in k or "2015" in k)]
fact("decim.monthly_median_mm", [min(mon), max(mon)], "มม.", "data",
     "§3 กล่อง Q7 · มัธยฐาน |ต่าง| ช่วง datum นิ่ง 1988–2005 และ 2015–2019")
fact("hourly.n_points", 306785, "จุด/สถานี", "data", "README โครงงาน (UHSLC รายชั่วโมง)")

st = meta["stats"]
fact("season.share_gulf", 100 * st["ko_lak"]["frac_season"], "%", "data", "§3.1 · series meta stats.frac_season")
fact("season.share_andaman", 100 * st["ko_taphao_noi"]["frac_season"], "%", "data", "§3.1 · series meta stats.frac_season")
fact("season.amp_gulf_mm", st["ko_lak"]["annual_amp"], "มม.", "data", "§3.1 · series meta stats.annual_amp")
fact("season.amp_andaman_mm", st["ko_taphao_noi"]["annual_amp"], "มม.", "data", "§3.1 · series meta stats.annual_amp")

# --- SQ04: สหสัมพันธ์ทั้งอนุกรม + เหตุการณ์ --------------------------------------------------------------------
t = series["t"]
yn, xn = [str(s) for s in series["y_names"]], [str(s) for s in series["x_names"]]
running, monthly = {}, {}
for sta in ("ko_taphao_noi", "ko_lak"):
    i = yn.index(sta)
    mm = np.where(series["Y_fill"][i], np.nan, series["Y"][i]) * st[sta]["resid_std"]
    monthly[sta] = mm  # รายเดือน (มม.) ตัดแนวโน้ม+ฤดูกาลแล้ว — เส้นคลื่นข้อมูลจริงบนปกและ SQ02_S010 (บท v4)
    running[sta] = I._running(mm)
for k in ("nino34", "dmi"):
    running["neg_" + k] = -I._running(series["X"][xn.index(k)])
for sta, short in (("ko_taphao_noi", "andaman"), ("ko_lak", "gulf")):
    for k in ("nino34", "dmi"):
        a, b = running[sta], running["neg_" + k]
        ok = np.isfinite(a) & np.isfinite(b)
        fact(f"corr.{short}.neg_{k}", np.corrcoef(a[ok], b[ok])[0, 1], "", "data",
             "§4 fig11 · ค่าเฉลี่ยเคลื่อนที่ 12 เดือน (make_infographics._running)")
j97 = (t >= 1997.5) & (t < 1998.5)
fact("event.andaman_9798_min_mm", np.nanmin(running["ko_taphao_noi"][j97]), "มม.", "data",
     "§4 · ต่ำสุดของค่าเฉลี่ย 12 เดือน ก.ค. 97 – มิ.ย. 98")
fact("event.phuket_drop_cm", 29, "ซม.", "literature", "§4 · Brown et al. (2019) — ต่ำกว่าปกติราว 29 ซม. นาน 7 เดือน")
fact("event.phuket_drop_months", 7, "เดือน", "literature", "§4 · Brown et al. (2019)")
fact("event.dmcr_low_years", [1997, 2006, 2019], "ปี", "literature", "§4 · กรมทรัพยากรทางทะเลและชายฝั่ง (2564)")

# --- SQ05–SQ06: เวฟเล็ตและ coherence --------------------------------------------------------------------------
q1 = load("wtc_q1.npz")
sc = q1["scales"]
fact("cwt.scales_per_octave", round(1 / np.median(np.diff(np.log2(sc)))), "สเกล/octave", "method", "§3.2 · wtc_q1.npz scales")
fact("cwt.morlet_w0", 6, "", "method", "§3.2 · Morlet ω0 = 6")
fact("wtc.vs_pycwt_max_diff", 1.4e-15, "", "data", "README โครงงาน · scripts/validate_wtc.py (ต่างจาก pycwt.wct ทั้งระนาบ)")
st_q1, ix_q1 = [str(s) for s in q1["stations"]], [str(s) for s in q1["indices"]]
bands_q1 = [str(b) for b in q1["bands"]]
si = st_q1.index("ko_taphao_noi")
nul = q1["null"][si, :, bands_q1.index("ทั้งระนาบ"), :]
fact("null.n_pairs", q1["null"].shape[-1], "คู่", "data", "§3.3 · wtc_q1.npz null (คู่ AR(1) ต่อกรณี)")
fact("noise.pasc_mean_plane", float(nul.mean()), "%", "data", "§3.3 · wtc_q1.npz null (ทุกดัชนี) ค่าเฉลี่ย")
fact("noise.pasc_p95_plane", float(np.mean(np.percentile(nul, 95, axis=-1))), "%", "data", "§3.3 · wtc_q1.npz null quantile 95%")
nulb = q1["null"][si, :, bands_q1.index("2–7 ปี"), :]
p95b = np.percentile(nulb, 95, axis=-1)
fact("noise.pasc_p95_band", [float(p95b.min()), float(p95b.max())], "%", "data", "§3.3 · null quantile 95% แถบ 2–7 ปี")

# --- SQ07: PASC + MWC -------------------------------------------------------------------------------------------
S, M = I.load_sens()
base = S["baseline"]
for sta, short in (("ko_taphao_noi", "andaman"), ("ko_lak", "gulf")):
    for band, bshort in (("ทั้งระนาบ", "plane"), ("2–7 ปี", "band")):
        for k, v in base[sta]["bands"][band]["single"].items():
            fact(f"pasc.{short}.{bshort}.{k}", v["pasc"], "%", "data", f"§4/§5 · sens_baseline summary {sta} {band} single")
            fact(f"p.{short}.{bshort}.{k}", v["p"], "", "data", f"§4/§5 · sens_baseline summary {sta} {band} single")
# อ่าวไทย: จำนวน (ดัชนี × แบบ) ที่ p < 0.05 ทั้งระนาบ
gulf_sig = sum(v["p"] < 0.05 for var in S.values() for v in var["ko_lak"]["bands"]["ทั้งระนาบ"]["single"].values())
fact("gulf.n_sig_index_variant", gulf_sig, "ครั้ง", "data", "§5 · ทุกแบบทดสอบความไว sens_*.npz")
fact("sens.n_variants", len(S), "แบบ", "data", "§3.4 · sens_*.npz")
fact("mwc.threshold_mid", base["ko_taphao_noi"]["thr_mid"], "ρ²", "data", "§7 · sens_baseline thr_mid (q = 1…5)")
gain = json.loads(base["ko_taphao_noi"]["bands"]["ทั้งระนาบ"]["gain"].replace("'", '"')) \
    if isinstance(base["ko_taphao_noi"]["bands"]["ทั้งระนาบ"]["gain"], str) else base["ko_taphao_noi"]["bands"]["ทั้งระนาบ"]["gain"]
fact("mwc.max_gain_plane", max(gain.values()), "จุด", "data", "§7 · ส่วนเพิ่มสูงสุดของชุดที่ดีที่สุดเทียบดัชนีเดี่ยว")
srch = load("mwc_search.npz")
nc = load("null_control.npz")
qv = srch["q"]
qs = sorted(set(int(v) for v in qv))
kb = [str(b) for b in srch["bands"]].index("ทั้งระนาบ")
dx = [str(x) for x in nc["designs"]].index("fake_x")
for sta, short in (("ko_taphao_noi", "andaman"), ("ko_lak", "gulf")):
    s_i = [str(x) for x in srch["stations"]].index(sta)
    n_i = [str(x) for x in nc["stations"]].index(sta)
    mean_q = lambda a: [float(np.nanmean(a[..., qv == k])) for k in qs]  # noqa: E731
    fact(f"mwc.{short}.fake_unadjusted", mean_q(nc["pasc_fixed"][n_i, dx][:, :, kb]), "%", "data", "§7 fig06 · null_control pasc_fixed")
    fact(f"mwc.{short}.real_unadjusted", mean_q(srch["pasc_fixed"][s_i][:, kb]), "%", "data", "§7 fig06 · mwc_search pasc_fixed")
    fact(f"mwc.{short}.fake_adjusted", mean_q(nc["pasc"][n_i, dx][:, :, kb]), "%", "data", "§7 fig06 · null_control pasc")
    fact(f"mwc.{short}.real_adjusted", mean_q(srch["pasc"][s_i][:, kb]), "%", "data", "§7 fig06 · mwc_search pasc")
from make_figures import PAPER_PASC  # noqa: E402
fact("paper.pasc_by_q", {str(k): v for k, v in PAPER_PASC.items()}, "%", "literature",
     "§7 · Song & Chen (2022) · make_figures.PAPER_PASC")

# --- SQ08: เฟส -------------------------------------------------------------------------------------------------
phase = json.loads((PROC / "phase_summary.json").read_text())
for k, v in phase.items():
    fact(f"phase.{k}.theta", v["theta"], "องศา", "data", "§4 fig12 · phase_summary.json")
    fact(f"phase.{k}.R", v["R"], "", "data", "§4 fig12 · phase_summary.json")
    fact(f"phase.{k}.lag_months", v["lag"], "เดือน", "data", "§4 fig12 · phase_summary.json (+ = ระดับน้ำนำ)")
    fact(f"phase.{k}.inside_expected", v["inside"], "", "data", "§4 fig12 · ตกในช่วงที่กลไกทำนาย")
    # ที่มาของความล่าช้า (หน้า SQ08_S050 · ผู้ใช้ 10-15 ขอภาพอธิบาย): สูตรเดียวกับ make_infographics.fig12_phase
    #   ห่างจากทิศหลัก (0° หรือ ±180°) กี่องศา → สัดส่วนของรอบ × คาบกลาง (เดือน) = ความล่าช้า (เดือน)
    ref = 0 if abs(v["theta"]) < 90 else (180 if v["theta"] > 0 else -180)
    fact(f"phase.{k}.offset_deg", v["theta"] - ref, "องศา", "data", "§4 fig12 · θ − ทิศหลักที่ใกล้สุด (0° หรือ ±180°)")
    fact(f"phase.{k}.period_months", v["period"] * 12, "เดือน", "data", "§4 fig12 · คาบกลาง (มัธยฐาน) ของจุดที่มีนัยสำคัญ แถบ 2–7 ปี")
fact("phase.n_match", sum(v["inside"] for v in phase.values()), "ดัชนี", "data", "§4 · ทิศตรงกลไก")
fact("gulf.depth_m", 40, "ม.", "literature", "§5 · ความลึกเฉลี่ยอ่าวไทย")
fact("gulf.wind_r", -0.84, "", "literature", "§5 · Anutaliya (2023) ระดับน้ำตาม curl ของลม ไม่มีความหน่วง")
fact("mech.kelvin_weeks", 2, "สัปดาห์", "literature", "§6 · อนุมาน: คลื่นจากสุมาตราถึงภูเก็ตไม่ถึงสองสัปดาห์")
fact("mech.han_webster_r", 0.95, "", "literature", "§6 · Han & Webster (2002) ลมศูนย์สูตรอธิบายระดับน้ำขอบตะวันออกอ่าวเบงกอล")
fact("mech.local_wind_r", 0.28, "", "literature", "§6 · Han & Webster (2002) ลมท้องถิ่นอย่างเดียวอธิบายได้เพียงเท่านี้")
fact("gulf.season_grace_cm", 20, "ซม.", "literature", "§5 กล่อง · GRACE (Wouters & Chambers 2010) วงรอบรายปีราว 20 ซม.")
fact("gulf.enso_cm", [3, 5], "ซม.", "literature", "§5 กล่อง · Luu et al. (2015) ENSO ±3–5 ซม. ชายฝั่งตะวันออกมาเลเซีย")
# หน้า SQ08_S030 ใช้หน่วย มม. ทั้งหน้า (ผู้ใช้ 10-14) — ค่าเดียวกันแปลงจาก ซม. ของงานวิจัย
fact("gulf.season_grace_mm", 200, "มม.", "literature", "§5 กล่อง · GRACE (Wouters & Chambers 2010) ราว 20 ซม. = 200 มม.")
fact("gulf.enso_mm", [30, 50], "มม.", "literature", "§5 กล่อง · Luu et al. (2015) ±3–5 ซม. = ±30–50 มม.")

# --- SQ09: ความแข็งแรง + คลังข้อมูล --------------------------------------------------------------------------------
rows = I.robustness_rows(S)
names = list(S)
fact("robust.rows", [{"label": lab, "n_pass": sum(f(n) == 2 for n in names)} for lab, f in rows],
     "แบบ", "data", "§8 fig13 · make_infographics.robustness_rows")
fact("robust.n_pass", [sum(f(n) == 2 for n in names) for _, f in rows], "แบบ", "data", "§8 fig13 · จำนวนแบบที่ผ่านต่อข้อสรุป")
src = {k: (S["short_1985"]["ko_taphao_noi"]["bands"]["2–7 ปี"]["single"][k]["pasc"],
           S["y_q7"]["ko_taphao_noi"]["bands"]["2–7 ปี"]["single"][k]["pasc"]) for k in ("soi", "nino34", "wnpmi")}
for k, (ps, uh) in src.items():
    fact(f"archive.{k}.psmsl", ps, "%", "data", "§8 ตาราง source · sens_short_1985")
    fact(f"archive.{k}.uhslc", uh, "%", "data", "§8 ตาราง source · sens_y_q7")
fact("archive.events", {"uhslc_radar": "2005-10-12", "datum_fix_before": "2012-04-01",
                        "datum_fix_cm": 10, "platform_destroyed": "2013-07"}, "", "literature",
     "§8 · UHSLC qa148a (2020), PSMSL 446")

# --- ผลลัพธ์ -------------------------------------------------------------------------------------------------------
out = HERE / "data"
out.mkdir(exist_ok=True)
(out / "facts.json").write_text(json.dumps(FACTS, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
np.savez_compressed(out / "derived.npz", t=t,
                    andaman_mm_12m=running["ko_taphao_noi"], gulf_mm_12m=running["ko_lak"],
                    andaman_mm=monthly["ko_taphao_noi"], gulf_mm=monthly["ko_lak"],
                    neg_nino34_12m=running["neg_nino34"], neg_dmi_12m=running["neg_dmi"],
                    fir_taps=taps, fir_w=w, fir_h_db=20 * np.log10(np.maximum(np.abs(h), 1e-12)))
print(f"facts: {len(FACTS)} -> {out / 'facts.json'}")
