#!/usr/bin/env python3
"""Q6 — การค้นหาทั้งดุ้นให้ผลอะไรเมื่อ **ไม่มีความสัมพันธ์จริงเลย**

    uv run python scripts/null_control.py              # 500 รอบ × 2 แบบ × 3 สถานี
    uv run python scripts/null_control.py --nrep 50    # ตอนพัฒนา

ต้องรัน run_mwc_null.py (threshold) และ run_mwc.py (ผลจริง) มาก่อน

ทำไมต้องมี: Q3–Q5 เลือก "ชุดที่ดีที่สุด" จาก 218 ชุด ค่าสูงสุดของหลายสิบชุดย่อมสูงกว่าค่าของชุดเดียว
แม้ทุกชุดเป็น noise ⇒ p-value ต่อชุดใน run_mwc.py ใช้ตัดสิน "ชุดที่ดีที่สุด" ไม่ได้
ที่นี่สร้างข้อมูลที่รู้แน่ว่าไม่มีความสัมพันธ์ แล้ว **ส่งผ่านการค้นหาเดียวกันทุกขั้น**
(threshold เดียวกัน · พื้นที่ที่นับเดียวกัน · คำนวณด้วย wtc.search.FastSearch ซึ่งมีเทสต์บังคับว่า
ได้ PASC เท่ากับ evaluate_subsets ที่ใช้กับผลจริง — และสคริปต์นี้ตรวจซ้ำกับผลจริงก่อนเริ่มทุกครั้ง)

null สองแบบ — ตอบคำถามเดียวกันด้วยสมมติฐานคนละชุด
  fake_x  **ดัชนีปลอม** (แบบที่ proposal ประกาศ): Y จริง + ดัชนี AR(1) อิสระ 8 ตัว ความแดงเท่าของจริง
          ⇒ พื้นค่าเท็จของ "ดัชนี 8 ตัวอะไรก็ได้ที่ไม่เกี่ยวกับระดับน้ำ"
  fake_y  **Y ปลอม**: Y เป็น AR(1) ความแดงเท่าของจริง + ดัชนีจริงทั้ง 8 ตัว
          ⇒ เก็บโครงสร้างจริงของดัชนีไว้ครบ (สหสัมพันธ์ระหว่างกัน เช่น Niño3.4–SOI–TPI และ
            spectrum ที่ไม่ใช่ AR(1)) สมมติแค่เรื่อง Y — เข้มกว่าในแง่ที่ดัชนีจริงซ้ำซ้อนกัน
            การค้น 218 ชุดจึง "เลือกได้น้อยกว่า" ที่ดูเหมือน

ผลต่อรอบ: PASC ของทุกชุด (ปรับ q และไม่ปรับ) ⇒ สถิติอะไรก็คำนวณทีหลังได้ เช่น
  - ค่าสูงสุดต่อ q        เทียบกับชุดที่ดีที่สุดต่อ q ของข้อมูลจริง (Q3 · Q4)
  - ค่าสูงสุดทั้ง 218 ชุด  = p ที่คุมความผิดพลาดทั้งตระกูลการทดสอบ (max-statistic)
  - (สูงสุดจาก 8 ตัว) − (สูงสุดจาก 6 ตัวของเปเปอร์)   เทียบกับ Q5

ผล -> data/processed/null_control.npz
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")          # ก่อน import numpy — worker ละเธรดเดียว (บทเรียน W4)

import argparse, json, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wtc.search import search_null_chunk                                 # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SERIES = ROOT / "data" / "processed" / "series.npz"
NULL = ROOT / "data" / "processed" / "mwc_null.npz"
SEARCH = ROOT / "data" / "processed" / "mwc_search.npz"
OUT = ROOT / "data" / "processed" / "null_control.npz"
MAIN = "ko_taphao_noi"
DESIGNS = ("fake_x", "fake_y")
CHUNK = 25                       # รอบต่อหนึ่งงาน — งานที่ k ใช้ seed + k ⇒ ผลไม่ขึ้นกับจำนวน worker


def run_chunk(station: str, design: str, nrep: int, seed: int):
    """-> (pasc, pasc_fixed, n_bad) — ตัวงานอยู่ใน wtc.search.search_null_chunk (ย้ายไปเมื่อ W7)"""
    d = np.load(SERIES, allow_pickle=True)
    nul = np.load(NULL, allow_pickle=True)
    si = [str(s) for s in nul["stations"]].index(station)
    thr = {int(q): nul["threshold"][si, i] for i, q in enumerate(nul["qs"])}
    return search_null_chunk(dict(d={k: d[k] for k in d.files}, station=station, thr=thr,
                                  design=design, nrep=nrep, seed=seed))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nrep", type=int, default=500)
    ap.add_argument("--seed", type=int, default=20261002)
    ap.add_argument("--workers", type=int, default=min(16, (os.cpu_count() or 2) // 2))   # คอร์จริง
    ap.add_argument("--stations", nargs="*", default=None)
    args = ap.parse_args()

    srch = np.load(SEARCH, allow_pickle=True)
    stations = [str(s) for s in srch["stations"]]
    if args.stations:
        stations = [s for s in stations if s in args.stations]
    bands = [str(b) for b in srch["bands"]]
    subsets = [tuple(s) for s in json.loads(str(srch["subsets"]))]
    q = srch["q"]
    in6 = srch["in_paper6"]
    smeta = json.loads(str(srch["meta"]))
    all_stations = [str(s) for s in srch["stations"]]

    sizes = [CHUNK] * (args.nrep // CHUNK) + ([args.nrep % CHUNK] if args.nrep % CHUNK else [])
    print(f"{len(stations)} สถานี × {len(DESIGNS)} แบบ × {args.nrep} รอบ × {len(subsets)} ชุด · "
          f"{args.workers} workers · seed {args.seed}")
    # ด่านตรวจก่อนเริ่ม: ข้อมูลจริงผ่านเส้นทางเร็วต้องได้ PASC เท่ากับที่ run_mwc.py บันทึกไว้
    for st in stations:
        p, pf, bad = run_chunk(st, "check", 1, 0)
        sj = all_stations.index(st)
        assert bad == 0
        np.testing.assert_allclose(p[0], srch["pasc"][sj], atol=1e-4, equal_nan=True)
        np.testing.assert_allclose(pf[0], srch["pasc_fixed"][sj], atol=1e-4, equal_nan=True)
    print("✅ เส้นทางเร็วให้ PASC ของข้อมูลจริงตรงกับ run_mwc.py ทุกสถานี ทุกชุด ทุกแถบ")

    t0 = time.perf_counter()
    parts: dict = {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = {}
        for si, st in enumerate(stations):
            for di, design in enumerate(DESIGNS):
                for k, size in enumerate(sizes):
                    seed = args.seed + 1_000_000 * all_stations.index(st) + 100_000 * di + k
                    futs[pool.submit(run_chunk, st, design, size, seed)] = (st, design, k)
        for n_done, fut in enumerate(as_completed(futs), 1):
            parts[futs[fut]] = fut.result()
            if n_done % 20 == 0 or n_done == len(futs):
                print(f"  งาน {n_done}/{len(futs)} ({time.perf_counter() - t0:.0f} s)", flush=True)

    P = np.array([[np.concatenate([parts[(st, de, k)][0] for k in range(len(sizes))])
                   for de in DESIGNS] for st in stations])            # (สถานี, แบบ, รอบ, ชุด, แถบ)
    PF = np.array([[np.concatenate([parts[(st, de, k)][1] for k in range(len(sizes))])
                    for de in DESIGNS] for st in stations])

    # --- สรุป ---------------------------------------------------------------
    qs = sorted(set(int(v) for v in q))
    pval = lambda obs, null: float((np.sum(null >= obs - 1e-9) + 1) / (len(null) + 1))
    summary = {}
    for i, st in enumerate(stations):
        sj = all_stations.index(st)
        obs = srch["pasc"][sj]                                          # (ชุด, แถบ)
        summary[st] = {}
        print(f"\n{'=' * 100}\n{st}{'  ← รายงานหลัก' if st == MAIN else '  (สำรอง)'}")
        for b in smeta["primary_bands"]:
            kb = bands.index(b)
            print(f"\n  ── แถบ {b} ── PASC (%) · threshold ปรับตาม q")
            print(f"  {'q':>2s} │ {'จริง: ดีที่สุด':>14s} │ " + " │ ".join(
                f"{de + ': เฉลี่ยทุกชุด · สูงสุด (95%) · p':^44s}" for de in DESIGNS) +
                  " │ ไม่ปรับ q: เฉลี่ยทุกชุด (fake_x)")
            rec = {"per_q": {}, "overall": {}, "q5_gain": {}}
            for k in qs:
                m = q == k
                o = float(np.nanmax(obs[m, kb]))
                cells, rq = [], {"observed_best": o}
                for di, de in enumerate(DESIGNS):
                    nmax = np.nanmax(P[i, di][:, m, kb], axis=1)
                    nmean = float(np.nanmean(P[i, di][:, m, kb]))
                    rq[de] = {"null_mean_all": nmean, "null_max_mean": float(nmax.mean()),
                              "null_max_p95": float(np.percentile(nmax, 95)), "p": pval(o, nmax)}
                    cells.append(f"{nmean:5.1f} · {nmax.mean():5.1f} ({np.percentile(nmax, 95):5.1f}) · {pval(o, nmax):.3f}")
                rq["fixed_mean_fake_x"] = float(np.nanmean(PF[i, 0][:, m, kb]))
                rec["per_q"][k] = rq
                print(f"  {k:2d} │ {o:14.1f} │ " + " │ ".join(f"{c:^44s}" for c in cells) +
                      f" │ {rq['fixed_mean_fake_x']:6.1f}")
            # ค่าสูงสุดทั้ง 218 ชุด = p ที่คุมทั้งตระกูล
            o_all = float(np.nanmax(obs[:, kb]))
            line = []
            for di, de in enumerate(DESIGNS):
                nall = np.nanmax(P[i, di][:, :, kb], axis=1)
                rec["overall"][de] = {"null_p95": float(np.percentile(nall, 95)), "p": pval(o_all, nall)}
                line.append(f"{de}: 95% ของ null {np.percentile(nall, 95):.1f} · p = {pval(o_all, nall):.3f}")
            rec["overall"]["observed"] = o_all
            print(f"  สูงสุดจากทั้ง {len(subsets)} ชุด: จริง {o_all:.1f}   |   " + "   |   ".join(line))
            # Q5: (สูงสุดจาก 8 ตัว) − (สูงสุดจาก 6 ตัวของเปเปอร์) ทุก q รวมกัน
            o_gain = float(np.nanmax(obs[:, kb]) - np.nanmax(obs[in6, kb]))
            line = []
            for di, de in enumerate(DESIGNS):
                ng = np.nanmax(P[i, di][:, :, kb], axis=1) - np.nanmax(P[i, di][:, in6, kb], axis=1)
                rec["q5_gain"][de] = {"null_p95": float(np.percentile(ng, 95)), "p": pval(o_gain, ng)}
                line.append(f"{de}: 95% ของ null {np.percentile(ng, 95):+.1f} · p = {pval(o_gain, ng):.3f}")
            rec["q5_gain"]["observed"] = o_gain
            print(f"  Q5 ส่วนที่ 8 ตัวชนะ 6 ตัว: จริง {o_gain:+.1f} จุด   |   " + "   |   ".join(line))
            summary[st][b] = rec

    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT, stations=np.array(stations), designs=np.array(DESIGNS), bands=np.array(bands),
        n_bad=np.array([[sum(parts[(st, de, k)][2] for k in range(len(sizes))) for de in DESIGNS]
                        for st in stations]),
        subsets=json.dumps([list(s) for s in subsets]), q=q, in_paper6=in6,
        pasc=P, pasc_fixed=PF, summary=json.dumps(summary, ensure_ascii=False),
        meta=json.dumps({"nrep": args.nrep, "seed": args.seed, "chunk": CHUNK}))
    print(f"\n✅ เขียนแล้ว {OUT.relative_to(ROOT)} · ใช้เวลารวม {time.perf_counter() - t0:.0f} วินาที")
    return 0


if __name__ == "__main__":
    sys.exit(main())
