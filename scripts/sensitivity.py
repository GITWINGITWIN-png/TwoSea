#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wtc.metrics import BANDS  # noqa: E402
from wtc.search import (all_subsets, best_per_q, evaluate_subsets, gains,  # noqa: E402
                        prepare_station, search_null, within_of_max)
from wtc.series import VARIANTS, build_series  # noqa: E402
from wtc.significance import empirical_p, fit_ar1, pasc_null_mwc, threshold_mwc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
REPORTED = ("ko_taphao_noi", "ko_lak")
SEED_INDEX = {"ko_taphao_noi": 0, "ko_lak": 1, "fort_phrachula_chomklao": 2}
THR_SEED, NULL_SEED = 20261001, 20261002
QS = (1, 2, 3, 4, 5)
PAPER6 = ("nino34", "pdo", "nao", "soi", "amo", "tpi")
PRIMARY = ("ทั้งระนาบ", "2–7 ปี")
GAIN_RULE = 5.0


def pval(obs: float, null: np.ndarray) -> float:
    return float((np.sum(null >= obs - 1e-9) + 1) / (len(null) + 1))


def run_station(d, st, variant, nmc, nrep, workers):
    x_names = [str(s) for s in d["x_names"]]
    y_names = [str(s) for s in d["y_names"]]
    iy = y_names.index(st)
    n = d["Y"].shape[1]
    a_y, s_y = fit_ar1(d["Y"][iy], d["Y_fill"][iy])
    ar = [fit_ar1(x, f) for x, f in zip(d["X"], d["X_fill"])]
    a_x, s_x = [a for a, _ in ar], [s for _, s in ar]

    t0 = time.perf_counter()
    thr_obj = threshold_mwc(n, a_y, s_y, a_x, s_x, qs=QS, nmc=nmc,
                            seed=THR_SEED + 100_000 * SEED_INDEX[st], workers=workers)
    pnull = pasc_null_mwc(thr_obj, n, s_y, s_x, nmc=nmc, workers=workers)
    thr = {q: thr_obj[q].per_scale for q in QS}
    t1 = time.perf_counter()

    subsets = all_subsets(x_names, max(QS))
    cache, periods, coi, scales, inside, ok = prepare_station(d, st, variant.max_filled)
    tab = evaluate_subsets(cache, "y", subsets, thr, periods, inside, ok)
    bands = list(BANDS)
    p = np.array([[empirical_p(tab.pasc[i, k], pnull[int(tab.q[i])][b]) for k, b in enumerate(bands)]
                  for i in range(len(subsets))])
    t2 = time.perf_counter()

    nul, nul_fixed, n_bad = search_null(d, st, thr, "fake_y", nrep,
                                        NULL_SEED + 1_000_000 * SEED_INDEX[st] + 100_000, workers,
                                        variant.max_filled)
    t3 = time.perf_counter()

    q = tab.q
    in6 = np.array([set(s) <= set(PAPER6) for s in subsets])
    summ = {"n": int(n), "a_y": float(a_y), "n_nan": int(tab.n_nan.sum()), "n_bad": int(n_bad),
            "cond_max": float(np.nanmax(tab.cond_max)),
            "thr_mid": [float(np.nanmedian(thr[k][(periods >= 0.5) & (periods <= 16)])) for k in QS],
            "seconds": {"threshold": t1 - t0, "search": t2 - t1, "null": t3 - t2}, "bands": {}}
    for b in PRIMARY:
        k = bands.index(b)
        v = tab.pasc[:, k]
        nmax_all = np.nanmax(nul[:, :, k], axis=1)
        best = best_per_q(q, v)
        g = gains(best)
        q_enough = 1
        for qq in sorted(g):
            if g[qq] >= GAIN_RULE and qq == q_enough + 1:
                q_enough = qq
        top, pars = int(np.nanargmax(v)), within_of_max(v, q, 1.0)
        o_gain = float(np.nanmax(v) - np.nanmax(v[in6]))
        n_gain = np.nanmax(nul[:, :, k], axis=1) - np.nanmax(nul[:, in6, k], axis=1)
        summ["bands"][b] = {
            "single": {x_names[i]: {"pasc": float(v[i]), "p": float(p[i, k]),
                                    "p_family": pval(v[i], nmax_all)}
                       for i in range(len(subsets)) if q[i] == 1},
            "best": {int(qq): {"subset": list(subsets[j]), "pasc": val,
                               "p_family_q": pval(val, np.nanmax(nul[:, q == qq, k], axis=1))}
                     for qq, (j, val) in best.items()},
            "gain": {int(a): float(b_) for a, b_ in g.items()}, "q_enough": q_enough,
            "top": {"subset": list(subsets[top]), "pasc": float(v[top]),
                    "p_family": pval(v[top], nmax_all)},
            "parsimonious": {"subset": list(subsets[pars]), "pasc": float(v[pars]),
                             "p_family": pval(v[pars], nmax_all)},
            "n_family_sig": int(sum(pval(x, nmax_all) < 0.05 for x in v)),
            "null_max_p95": float(np.percentile(nmax_all, 95)),
            "q5_gain": {"observed": o_gain, "p": pval(o_gain, n_gain),
                        "best6": list(subsets[int(np.flatnonzero(in6)[np.nanargmax(v[in6])])])},
            "fixed_best": {int(qq): float(np.nanmax(tab.pasc_fixed[q == qq, k])) for qq in QS},
        }
    arrays = dict(pasc=tab.pasc, pasc_fixed=tab.pasc_fixed, awc=tab.awc, p=p,
                  null=nul, threshold=np.array([thr[k] for k in QS]), periods=periods)
    return summ, arrays, subsets


def check_baseline(st, arrays, subsets):
    srch = np.load(PROC / "mwc_search.npz", allow_pickle=True)
    nc = np.load(PROC / "null_control.npz", allow_pickle=True)
    assert [tuple(s) for s in json.loads(str(srch["subsets"]))] == subsets
    si = [str(s) for s in srch["stations"]].index(st)
    np.testing.assert_array_equal(arrays["pasc"], srch["pasc"][si])
    np.testing.assert_array_equal(arrays["p"], srch["p"][si])
    ni = [str(s) for s in nc["stations"]].index(st)
    di = [str(s) for s in nc["designs"]].index("fake_y")
    if arrays["null"].shape == nc["pasc"][ni, di].shape:
        np.testing.assert_array_equal(arrays["null"], nc["pasc"][ni, di])
    print(f"    ✅ baseline ตรงกับ mwc_search.npz / null_control.npz ทุกหลัก")


def run_variant(name, nmc, nrep, workers):
    v = VARIANTS[name]
    d = build_series(v)
    stations = [s for s in REPORTED if s in [str(x) for x in d["y_names"]]]
    print(f"\n{'=' * 100}\n{name}: {v.label}   ·   {d['t'][0]:.2f}–{d['t'][-1]:.2f} ({len(d['t'])} เดือน) · "
          f"ดัชนี {len(d['x_names'])} ตัว\n  {v.why}", flush=True)
    out, store = {}, {}
    for st in stations:
        summ, arrays, subsets = run_station(d, st, v, nmc, nrep, workers)
        out[st] = summ
        store[st] = arrays
        sec = summ["seconds"]
        print(f"  {st}  a_Y {summ['a_y']:.3f} · threshold q=1..5 {', '.join(f'{x:.2f}' for x in summ['thr_mid'])} · "
              f"({sec['threshold']:.0f}+{sec['search']:.0f}+{sec['null']:.0f} s)", flush=True)
        for b in PRIMARY:
            r = summ["bands"][b]
            singles = sorted(r["single"].items(), key=lambda kv: -kv[1]["pasc"])[:3]
            print(f"    {b:9s} ดัชนีเดี่ยว: " + " · ".join(f"{k} {x['pasc']:.1f} (p {x['p']:.3f})" for k, x in singles)
                  + f" | ดีที่สุด/q: " + " ".join(f"{r['best'][qq]['pasc']:.1f}" for qq in QS)
                  + f" | พอที่ {r['q_enough']} ตัว | ประหยัดสุด {'+'.join(r['parsimonious']['subset'])} "
                  f"p_fam {r['parsimonious']['p_family']:.3f} | 8−6 {r['q5_gain']['observed']:+.1f} (p {r['q5_gain']['p']:.3f})",
                  flush=True)
        if name == "baseline" and nmc == 1000:
            check_baseline(st, arrays, subsets)

    path = PROC / f"sens_{name}.npz"
    np.savez_compressed(
        path, stations=np.array(stations), indices=d["x_names"], bands=np.array(list(BANDS)),
        subsets=json.dumps([list(s) for s in subsets]), t=d["t"],
        **{f"{st}__{k}": a for st in stations for k, a in store[st].items()},
        summary=json.dumps(out, ensure_ascii=False),
        meta=json.dumps({"variant": name, "label": v.label, "why": v.why, "nmc": nmc, "nrep": nrep,
                         "window": d["meta"]["window"], "n": len(d["t"]),
                         "max_filled": v.max_filled, "max_interp": v.max_interp,
                         "exclude": v.exclude, "y_source": v.y_source}, ensure_ascii=False))
    print(f"  ✅ เขียนแล้ว {path.relative_to(ROOT)}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--nmc", type=int, default=1000)
    ap.add_argument("--nrep", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=min(16, (os.cpu_count() or 2) // 2))
    args = ap.parse_args()
    names = list(VARIANTS) if args.all else args.variant
    if not names or any(n not in VARIANTS for n in names):
        ap.error(f"เลือกแบบจาก {list(VARIANTS)}")
    t0 = time.perf_counter()
    for name in names:
        run_variant(name, args.nmc, args.nrep, args.workers)
    print(f"\nรวม {time.perf_counter() - t0:.0f} วินาที")
    return 0


if __name__ == "__main__":
    sys.exit(main())
