#!/usr/bin/env python3
"""🚦 ประตูตาย G1 — WTC ที่เขียนเองต้องให้ค่าเท่ากับ pycwt.wct

    uv run --group reference python scripts/validate_wtc.py

เกณฑ์ผ่าน (PLAN.md §5, §6)
  (ก) |R2 ของเรา − R2 ของ pycwt| <= 0.05 ในแถบ 2–7 ปี ที่ KO TAPHAO NOI (ในกรวย COI)
  (ข) ทำซ้ำข้อสรุปของ premise test ได้: อันดามัน **มี** สัญญาณ ENSO · อ่าวไทย **ไม่มี**
      (เลขเป้าเดิมจาก baseline_pycwt.py: p = 0.016 และ p = 0.984)

⚠️ สคริปต์นี้เป็นที่**เดียว**ในโปรเจกต์ที่อนุญาตให้เรียก pycwt.wct — เพราะหน้าที่ของมัน
คือการเทียบ ไม่ใช่การผลิตผล ตัวงานจริงทั้งหมดใช้ wtc.coherence.wtc()
เมื่อผ่านประตูนี้แล้ว ทุกที่อื่นเลิกพึ่ง pycwt.wct ถาวร (PLAN.md §5 W3)

⚠️ ห้ามใช้ KO LAK ตัดสินว่าโค้ดถูกหรือผิด — สถานีนั้นไม่มีสัญญาณจริง (p = 0.984)
จะได้ผลว่างแล้วสรุปผิดว่าโค้ดพัง

📌 **ผลที่ได้จริง 2026-09-20 ดีกว่าเกณฑ์มาก: ต่างกันระดับ 1e-14 ทั้งระนาบ ไม่ใช่ 0.05**
   แปลว่าไม่ใช่ "ใกล้เคียงพอ" แต่เป็นสูตรเดียวกันจริง ๆ ระหว่างทางเจอสามจุดที่ต่าง
   และแต่ละจุดคือของจริงที่ต้องรู้ (เขียนไว้ใน wtc/smoothing.py ครบ):
     1. หน้าต่างแกนสเกลเป็น **สี่เหลี่ยมคางหมู** ปลายนับครึ่งน้ำหนัก ไม่ใช่ boxcar ตรง ๆ
     2. การเติมศูนย์ของแกนเวลาต้องเติมถึง **กำลังสองถัดไป** (1024) ไม่ใช่ next_fast_len (875)
     3. การ normalize ขอบแกนสเกลไม่มีผลต่อ R^2 เลย เพราะเป็นการคูณทั้งแถวด้วยตัวเดียวกัน
        แล้วมันหารกันหายไปใน |Sxy|^2/(Sxx*Syy) — เรื่องนี้จริงกับ WTC และต้องตรวจซ้ำกับ MWC
"""
from __future__ import annotations
import argparse, json, sys, warnings
from pathlib import Path
import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wtc.transform import cwt, coi_mask, morlet_flambda, DJ, DT_MONTHLY, OMEGA0  # noqa: E402
from wtc.coherence import wtc                                                    # noqa: E402
from wtc.significance import fit_ar1, ar1_surrogate                              # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SERIES = ROOT / "data" / "processed" / "series.npz"
BAND = (2.0, 7.0)          # แถบ ENSO เป็นปี
GATE = 0.05                # เกณฑ์ประตู G1


def load():
    d = np.load(SERIES, allow_pickle=True)
    y_names = [str(s) for s in d["y_names"]]
    x_names = [str(s) for s in d["x_names"]]
    return d["t"], d["Y"], d["X"], y_names, x_names, json.loads(str(d["meta"]))


def our_wtc(y, x, dt=DT_MONTHLY, dj=DJ):
    """R2, คาบ, COI จากโค้ดของเราล้วน ๆ"""
    Wy, scales, periods, coi = cwt(y, dt, dj)
    Wx, _, _, _ = cwt(x, dt, dj)
    R2, _ = wtc(Wy, Wx, dt, dj, scales)
    return R2, periods, coi


def lib_wtc(y, x, dt=DT_MONTHLY, dj=DJ):
    """R2 จาก pycwt.wct โดยตั้งพารามิเตอร์ให้ตรงกับของเราทุกตัว

    normalize=False สำคัญ — ถ้าปล่อย default pycwt จะ normalize ให้อีกรอบ ทั้งที่
    อนุกรมผ่าน preprocess มาแล้ว ความต่างที่เห็นจะกลายเป็นความต่างของการเตรียมข้อมูล
    ไม่ใช่ของตัวสูตร ซึ่งทำให้ประตู G1 วัดผิดเรื่อง
    """
    import pycwt
    s0 = 2 * dt / morlet_flambda(OMEGA0)
    j = int(round(np.log2(len(y) * dt / s0) / dj))
    R2, _, coi, freq, _ = pycwt.wct(y, x, dt, dj=dj, s0=s0, J=j, sig=False,
                                    wavelet=pycwt.Morlet(OMEGA0), normalize=False)
    return R2, 1 / freq, coi


def band_mean(R2, periods, coi, band=BAND):
    """ค่าเฉลี่ย coherence ในแถบคาบที่กำหนด **เฉพาะจุดที่อยู่ในกรวย COI**"""
    sel = (periods >= band[0]) & (periods <= band[1])
    inside = coi_mask(periods, coi)
    return float(np.nanmean(R2[sel][inside[sel]]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmc", type=int, default=60, help="จำนวน surrogate (ของจริง >=1000)")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    t, Y, X, y_names, x_names, meta = load()
    n = len(t)
    nino = X[x_names.index("nino34")]
    print(f"หน้าต่าง {t[0]:.3f}–{t[-1]:.3f} · {n} เดือน · dj={DJ:.4f} · omega0={OMEGA0:.0f}")

    # --- (ก) ประตู G1: เทียบกับไลบรารี ------------------------------------
    print("\n" + "=" * 78)
    print("(ก) โค้ดเรา เทียบ pycwt.wct")
    print("=" * 78)
    worst = 0.0
    for key in y_names:
        y = Y[y_names.index(key)]
        R2_ours, per, coi = our_wtc(y, nino)
        R2_lib, per_lib, coi_lib = lib_wtc(y, nino)
        assert np.allclose(per, per_lib) and np.allclose(coi, coi_lib), "แกนไม่ตรงกัน"

        sel = (per >= BAND[0]) & (per <= BAND[1])
        inside = coi_mask(per, coi)
        d_band = np.abs(R2_ours - R2_lib)[sel][inside[sel]]
        d_all = np.abs(R2_ours - R2_lib)[inside]
        flag = "✅" if d_band.max() <= GATE else "❌"
        print(f"  {key:26s} แถบ {BAND[0]:.0f}–{BAND[1]:.0f} ปี: "
              f"ต่างสูงสุด {d_band.max():.3e} เฉลี่ย {d_band.mean():.3e}  {flag}")
        print(f"  {'':26s} ทั้งระนาบในกรวย:  ต่างสูงสุด {d_all.max():.3e} "
              f"เฉลี่ย {d_all.mean():.3e}")
        if key == "ko_taphao_noi":
            worst = d_band.max()

    # --- (ข) ทำซ้ำข้อสรุปของ premise test ----------------------------------
    print("\n" + "=" * 78)
    print(f"(ข) นัยสำคัญด้วย AR(1) surrogate {args.nmc} ชุด (seed {args.seed}) — ใช้โค้ดเราล้วน")
    print("=" * 78)
    rng = np.random.default_rng(args.seed)
    ax, sx = fit_ar1(nino)
    verdicts = {}
    for key in ("ko_taphao_noi", "ko_lak"):
        y = Y[y_names.index(key)]
        R2, per, coi = our_wtc(y, nino)
        obs = band_mean(R2, per, coi)
        ay, sy = fit_ar1(y)
        null = np.empty(args.nmc)
        for i in range(args.nmc):
            r2s, p_s, coi_s = our_wtc(ar1_surrogate(n, ay, sy, rng),
                                      ar1_surrogate(n, ax, sx, rng))
            null[i] = band_mean(r2s, p_s, coi_s)
        p = (np.sum(null >= obs) + 1) / (args.nmc + 1)
        verdicts[key] = p
        print(f"  {key:26s} AR(1) a={ay:.3f} · coherence แถบ {BAND[0]:.0f}–{BAND[1]:.0f} ปี = {obs:.4f}")
        print(f"  {'':26s} null mean={null.mean():.4f} p95={np.percentile(null,95):.4f} "
              f"⇒ p = {p:.3f}  {'✅ มีนัยสำคัญ' if p < 0.05 else '❌ ไม่ผ่าน'}")
    print(f"  (Niño3.4: AR(1) a={ax:.3f})")

    # --- สรุปประตู --------------------------------------------------------
    print("\n" + "=" * 78)
    gate_a = worst <= GATE
    gate_b = verdicts["ko_taphao_noi"] < 0.05 <= verdicts["ko_lak"]
    print(f"  (ก) ต่างจาก pycwt ที่ KO TAPHAO NOI = {worst:.3e} (เกณฑ์ <= {GATE}) "
          f"{'✅ ผ่าน' if gate_a else '❌ ไม่ผ่าน'}")
    print(f"  (ข) อันดามันมีสัญญาณ (p={verdicts['ko_taphao_noi']:.3f}) · "
          f"อ่าวไทยไม่มี (p={verdicts['ko_lak']:.3f}) "
          f"{'✅ ผ่าน' if gate_b else '❌ ไม่ผ่าน'}")
    ok = gate_a and gate_b
    print(f"\n  🚦 ประตู G1: {'✅ ผ่าน — เดินต่อได้' if ok else '❌ ยังไม่ผ่าน — ห้ามเดินต่อจนกว่าจะรู้สาเหตุ'}")
    print("=" * 78)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
