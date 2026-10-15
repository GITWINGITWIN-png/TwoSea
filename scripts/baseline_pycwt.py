#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys, warnings
from pathlib import Path
import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wtc.loaders import read_psmsl, read_noaa_index  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
BAND = (2.0, 7.0)


def deseason(t: np.ndarray, y: np.ndarray) -> np.ndarray:
    A = np.column_stack([t - t.mean(), np.ones_like(t)] +
                        [f(2 * np.pi * k * t) for k in (1, 2) for f in (np.sin, np.cos)])
    r = y - A @ np.linalg.lstsq(A, y, rcond=None)[0]
    return (r - r.mean()) / r.std()


def ar1_params(z: np.ndarray) -> tuple[float, float]:
    a = float(np.corrcoef(z[:-1], z[1:])[0, 1])
    return a, float(z.std() * np.sqrt(1 - a ** 2))


def ar1_surrogate(n: int, a: float, s: float, rng) -> np.ndarray:
    e = rng.normal(0, s, n)
    z = np.empty(n); z[0] = e[0]
    for i in range(1, n):
        z[i] = a * z[i - 1] + e[i]
    return (z - z.mean()) / z.std()


def band_coherence(a: np.ndarray, b: np.ndarray, dt: float, n: int, dj: float) -> float:
    import pycwt
    W, _, coi, freq, _ = pycwt.wct(a, b, dt, dj=dj, s0=4 * dt, J=-1, sig=False)
    per = 1 / freq
    sel = (per >= BAND[0]) & (per <= BAND[1])
    inside = np.tile(per[:, None], (1, n)) <= np.tile(coi[None, :], (len(per), 1))
    return float(np.nanmean(W[sel][inside[sel]]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmc", type=int, default=60, help="จำนวน AR(1) surrogate (ของจริงควร >=1000)")
    ap.add_argument("--dj", type=float, default=1/6, help="ความละเอียดสเกล (เล็กลง = ละเอียดขึ้น = ช้าลง)")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    tn, vn = read_noaa_index(RAW / "indices" / "nino34.data")
    grid = np.arange(1948 + 1/24, 2025, 1/12)
    x = np.interp(grid, tn[~np.isnan(vn)], vn[~np.isnan(vn)])
    x = (x - x.mean()) / x.std()
    dt, n = 1/12, len(grid)

    print(f"หน้าต่าง 1948–2024 · {n} เดือน · surrogate {args.nmc} ชุด · dj={args.dj:.4f}")
    for key, label in [("ko_taphao_noi", "KO TAPHAO NOI (อันดามัน)"),
                       ("ko_lak", "KO LAK (อ่าวไทย)")]:
        ts, vs = read_psmsl(RAW / "psmsl" / f"{key}_monthly.rlrdata")
        g = ~np.isnan(vs)
        y = deseason(grid, np.interp(grid, ts[g], vs[g]))
        obs = band_coherence(y, x, dt, n, args.dj)
        ay, sy = ar1_params(y); ax, sx = ar1_params(x)
        null = np.array([band_coherence(ar1_surrogate(n, ay, sy, rng),
                                        ar1_surrogate(n, ax, sx, rng), dt, n, args.dj)
                         for _ in range(args.nmc)])
        p = (np.sum(null >= obs) + 1) / (args.nmc + 1)
        verdict = "✅ มีนัยสำคัญ" if p < 0.05 else "❌ ไม่ผ่าน"
        print(f"\n  {label}")
        print(f"    AR(1): ระดับน้ำ a={ay:.3f} · Niño3.4 a={ax:.3f}")
        print(f"    coherence แถบ {BAND[0]:.0f}–{BAND[1]:.0f} ปี = {obs:.4f}")
        print(f"    null: mean={null.mean():.4f} · p95={np.percentile(null,95):.4f}")
        print(f"    p = {p:.3f}  {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
