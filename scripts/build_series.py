#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wtc.series import BASELINE, STATIONS, build_series  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "processed" / "series.npz"


def main() -> int:
    d = build_series(BASELINE, verbose=True)
    start, stop = d["meta"]["window"]
    grid = d["t"]
    print(f"หน้าต่างร่วมของดัชนี {len(d['x_names'])} ตัว: {start:.3f} – {stop:.3f}")
    print(f"กริดรายเดือน {len(grid)} จุด  ({grid[0]:.3f} – {grid[-1]:.3f})  dt = 1/12 ปี\n")
    print(f"  {'อนุกรม':32s} {'มีจริง':>8s} {'เติม':>6s} {'แนวโน้ม/ปี':>12s} "
          f"{'วงรอบปี':>9s} {'%แนวโน้ม':>9s} {'%ฤดูกาล':>9s}")
    print("  " + "-" * 92)
    for name, info in d["stats"].items():
        label = STATIONS.get(name, name)
        print(f"  {label:32s} {info['n_used']:8d} {info['n_filled']:6d} "
              f"{info['slope']:12.3f} {info['annual_amp']:9.3f} "
              f"{info['frac_trend']:8.1%} {info['frac_season']:9.1%}")

    Y, X = d["Y"], d["X"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, t=grid, Y=Y, Y_fill=d["Y_fill"], X=X, X_fill=d["X_fill"],
                        y_names=d["y_names"], x_names=d["x_names"],
                        meta=json.dumps(d["meta"], ensure_ascii=False))
    print(f"\n✅ เขียนแล้ว {OUT.relative_to(ROOT)}  "
          f"({OUT.stat().st_size/1024:.0f} kB · Y {Y.shape} · X {X.shape})")

    worst = max(float(m.mean()) for m in list(d["Y_fill"]) + list(d["X_fill"]))
    print(f"   สัดส่วนของเติมสูงสุดในบรรดาอนุกรมทั้งหมด = {worst:.1%}")
    if worst > 0.15:
        print("   ⚠️ เกิน 15% — ต้องอธิบายในรายงานว่ากระทบผลตรงไหน")
    return 0


if __name__ == "__main__":
    sys.exit(main())
