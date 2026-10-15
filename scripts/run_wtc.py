#!/usr/bin/env python3
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse, json, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wtc.coherence import wtc  # noqa: E402
from wtc.metrics import BANDS, significance, summarize, valid_mask  # noqa: E402
from wtc.significance import empirical_p, fit_ar1, pasc_null, threshold_wtc  # noqa: E402
from wtc.transform import DJ, DT_MONTHLY, cwt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SERIES = ROOT / "data" / "processed" / "series.npz"
OUT = ROOT / "data" / "processed" / "wtc_q1.npz"
MAIN = "ko_taphao_noi"
LABEL = {"ko_taphao_noi": "KO TAPHAO NOI (อันดามัน)", "ko_lak": "KO LAK (อ่าวไทย)",
         "fort_phrachula_chomklao": "FORT PHRACHULA (อ่าวไทยตอนบน)"}


def one_pair(y, y_fill, x, x_fill, nmc, seed):
    n = len(y)
    a_y, s_y = fit_ar1(y, y_fill)
    a_x, s_x = fit_ar1(x, x_fill)
    Wy, scales, periods, coi = cwt(y)
    Wx, _, _, _ = cwt(x)
    R2, phase = wtc(Wy, Wx, DT_MONTHLY, DJ, scales)
    thr = threshold_wtc(n, a_y, s_y, a_x, s_x, nmc=nmc, seed=seed)
    null = pasc_null(thr, n, s_y, s_x, nmc=nmc, seed=seed + 500_000)
    valid = valid_mask(periods, coi, scales, DT_MONTHLY, y_fill, x_fill)
    sig = significance(R2, thr.per_scale)
    summ = summarize(R2, sig, valid, periods)
    for b in BANDS:
        summ[b]["p"] = empirical_p(summ[b]["pasc"], null[b])
        summ[b]["null_p95"] = float(np.nanpercentile(null[b], 95))
        summ[b]["null_mean"] = float(np.nanmean(null[b]))
    return dict(R2=R2.astype(np.float32), phase=phase.astype(np.float32), sig=sig,
                valid=valid, threshold=thr.per_scale, a_y=a_y, a_x=a_x,
                null=np.array([null[b] for b in BANDS]), summary=summ,
                scales=scales, periods=periods, coi=coi)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmc", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20260930)
    ap.add_argument("--workers", type=int, default=min(24, (os.cpu_count() or 2) - 2))
    args = ap.parse_args()

    d = np.load(SERIES, allow_pickle=True)
    t, Y, X = d["t"], d["Y"], d["X"]
    Yf, Xf = d["Y_fill"], d["X_fill"]
    y_names = [str(s) for s in d["y_names"]]
    x_names = [str(s) for s in d["x_names"]]
    stations = [MAIN] + [s for s in y_names if s != MAIN]
    print(f"{len(stations)} สถานี × {len(x_names)} ดัชนี · surrogate {args.nmc}+{args.nmc} ชุด/คู่ · "
          f"{args.workers} workers · seed {args.seed}")

    jobs, results = {}, {}
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for i, s in enumerate(stations):
            iy = y_names.index(s)
            for j, k in enumerate(x_names):
                seed = args.seed + 1000 * i + j
                fut = pool.submit(one_pair, Y[iy], Yf[iy], X[j], Xf[j], args.nmc, seed)
                jobs[fut] = (s, k)
        for n_done, fut in enumerate(as_completed(jobs), 1):
            results[jobs[fut]] = fut.result()
            s, k = jobs[fut]
            print(f"  [{n_done:2d}/{len(jobs)}] {s:24s} × {k:7s} "
                  f"PASC {results[(s, k)]['summary']['ทั้งระนาบ']['pasc']:5.1f}% "
                  f"({time.perf_counter() - t0:5.0f} s)", flush=True)

    bands = list(BANDS)
    for s in stations:
        tag = "  ← รายงานหลัก" if s == MAIN else "  (สำรอง)"
        print(f"\n{LABEL[s]}{tag}   a_Y = {results[(s, x_names[0])]['a_y']:.3f}")
        print(f"  {'ดัชนี':8s} {'a_X':>6s} │ " + " │ ".join(f"{b:^27s}" for b in bands))
        print(f"  {'':8s} {'':6s} │ " + " │ ".join(f"{'PASC%':>7s} {'p':>6s} {'null95':>6s} {'AWC':>5s}"
                                                  for _ in bands))
        order = sorted(x_names, key=lambda k: -results[(s, k)]["summary"]["ทั้งระนาบ"]["pasc"])
        for k in order:
            r = results[(s, k)]
            cells = []
            for b in bands:
                m = r["summary"][b]
                star = "*" if m["p"] < 0.05 else " "
                cells.append(f"{m['pasc']:6.1f}{star} {m['p']:6.3f} {m['null_p95']:6.1f} "
                             f"{m['awc']:5.2f}" if np.isfinite(m["awc"]) else
                             f"{m['pasc']:6.1f}{star} {m['p']:6.3f} {m['null_p95']:6.1f}   —  ")
            print(f"  {k:8s} {r['a_x']:6.3f} │ " + " │ ".join(cells))
    print("\n  * = PASC สูงกว่าที่ noise ทำได้ (p < 0.05 เทียบการกระจายของ PASC ใน null)")

    first = results[(MAIN, x_names[0])]
    stack = lambda key: np.array([[results[(s, k)][key] for k in x_names] for s in stations])
    summary = {s: {k: results[(s, k)]["summary"] for k in x_names} for s in stations}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT, t=t, stations=np.array(stations), indices=np.array(x_names),
        bands=np.array(bands), scales=first["scales"], periods=first["periods"],
        coi=first["coi"], R2=stack("R2"), phase=stack("phase"), sig=stack("sig"),
        valid=stack("valid"), threshold=stack("threshold"), null=stack("null"),
        a_y=stack("a_y"), a_x=stack("a_x"),
        summary=json.dumps(summary, ensure_ascii=False),
        meta=json.dumps({"nmc": args.nmc, "seed": args.seed, "level": 0.95,
                         "max_filled_fraction": 0.5}))
    print(f"\n✅ เขียนแล้ว {OUT.relative_to(ROOT)} · ใช้เวลารวม {time.perf_counter() - t0:.0f} วินาที")
    return 0


if __name__ == "__main__":
    sys.exit(main())
