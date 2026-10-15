import numpy as np
import pytest

from wtc.coherence import SpectraCache, mwc_cached
from wtc.metrics import BANDS, pasc, significance, valid_mask
from wtc.search import (all_subsets, best_per_q, evaluate_subsets, fill_ok, gains,
                        reduce_per_q, within_of_max)
from wtc.significance import ar1_surrogate, threshold_mwc
from wtc.transform import DJ, DT_MONTHLY, coi_mask, cwt

N = 480
NAMES = ["x0", "x1", "x2", "x3"]
A_X = (0.8, 0.5, 0.3, 0.6)
S_X = tuple(np.sqrt(1 - a * a) for a in A_X)


def test_all_subsets_counts():
    s = all_subsets(list("abcdefgh"), 5)
    assert len(s) == 8 + 28 + 56 + 70 + 56 == 218
    assert len(set(s)) == 218 and s[0] == ("a",) and len(s[-1]) == 5


@pytest.fixture(scope="module")
def setup():
    rng = np.random.default_rng(3)
    xs = [ar1_surrogate(N, a, s, rng) for a, s in zip(A_X, S_X)]
    y = xs[0] + xs[1] + 0.4 * ar1_surrogate(N, 0.5, 0.87, rng)
    y = (y - y.mean()) / y.std()
    y_fill = np.zeros(N, bool)
    y_fill[200:260] = True
    Wy, sc, per, coi = cwt(y)
    W = {"y": Wy, **{k: cwt(x)[0] for k, x in zip(NAMES, xs)}}
    cache = SpectraCache(W, DT_MONTHLY, DJ, sc)
    thr = {q: t.per_scale for q, t in
           threshold_mwc(N, 0.7, 0.7, A_X, S_X, qs=(1, 2, 3), nmc=50, seed=1).items()}
    inside = coi_mask(per, coi)
    ok = {"y": fill_ok(y_fill, sc, DT_MONTHLY, Wy.shape),
          **{k: fill_ok(None, sc, DT_MONTHLY, Wy.shape) for k in NAMES}}
    subsets = all_subsets(NAMES, 3)
    tab = evaluate_subsets(cache, "y", subsets, thr, per, inside, ok)
    return dict(cache=cache, thr=thr, per=per, coi=coi, sc=sc, inside=inside, ok=ok,
                y_fill=y_fill, subsets=subsets, tab=tab)


def test_matches_the_slow_checked_path(setup):
    s = setup
    for i in (0, 5, len(s["subsets"]) - 1):
        sub = s["subsets"][i]
        R2, _ = mwc_cached(s["cache"], "y", sub)
        valid = valid_mask(s["per"], s["coi"], s["sc"], DT_MONTHLY, s["y_fill"]) & np.isfinite(R2)
        sig = significance(R2, s["thr"][len(sub)])
        for b, band in enumerate(BANDS.values()):
            assert s["tab"].pasc[i, b] == pytest.approx(pasc(sig, valid, s["per"], band), nan_ok=True)
        assert s["tab"].mean_r2[i] == pytest.approx(R2[valid].mean())


def test_unchecked_path_gives_same_table(setup):
    s = setup
    fast = evaluate_subsets(s["cache"], "y", s["subsets"], s["thr"], s["per"], s["inside"],
                            s["ok"], check_cond=False)
    np.testing.assert_allclose(fast.pasc, s["tab"].pasc, equal_nan=True)
    np.testing.assert_allclose(fast.pasc_fixed, s["tab"].pasc_fixed, equal_nan=True)


def test_fixed_threshold_equals_adjusted_at_q1_and_inflates_after(setup):
    t = setup["tab"]
    np.testing.assert_array_equal(t.pasc[t.q == 1], t.pasc_fixed[t.q == 1])
    assert np.all(t.pasc_fixed[t.q > 1] >= t.pasc[t.q > 1] - 1e-9)


def test_search_recovers_the_true_pair(setup):
    t = setup["tab"]
    best = best_per_q(t.q, t.pasc[:, 0])
    assert setup["subsets"][best[2][0]] == ("x0", "x1")
    assert best[2][1] > 60
    g = gains(best)
    assert g[2] > 5 and g[3] < 5
    assert setup["subsets"][within_of_max(t.pasc[:, 0], t.q, 1.0)] == ("x0", "x1")


def test_gap_in_y_is_excluded_from_counted_area(setup):
    t = setup["tab"]
    no_gap = dict(setup["ok"], y=np.ones_like(setup["ok"]["y"]))
    t2 = evaluate_subsets(setup["cache"], "y", setup["subsets"][:1], setup["thr"], setup["per"],
                          setup["inside"], no_gap)
    assert t.n_valid[0, 0] < t2.n_valid[0, 0]


def test_reduce_and_selection_rules_on_known_numbers():
    q = np.array([1, 1, 2, 2, 3])
    v = np.array([[10.0], [12.0], [20.0], [19.5], [20.4]])
    mx, mean = reduce_per_q(q, v)
    assert mx[:, 0].tolist() == [12.0, 20.0, 20.4] and mean[0, 0] == 11.0
    best = best_per_q(q, v[:, 0])
    assert best == {1: (1, 12.0), 2: (2, 20.0), 3: (4, 20.4)}
    assert gains(best) == {2: 8.0, 3: pytest.approx(0.4)}
    assert within_of_max(v[:, 0], q, 1.0) == 2
    allowed = np.array([True, False, False, True, True])
    assert best_per_q(q, v[:, 0], allowed)[1] == (0, 10.0)


def test_fast_search_matches_checked_path(setup):
    from wtc.search import FastSearch
    s = setup
    for block in (4096, 1000):
        fs = FastSearch(NAMES, s["subsets"], s["thr"], s["per"], s["inside"], s["ok"], block=block)
        p, pf, n_bad = fs.run(s["cache"])
        assert n_bad == 0
        np.testing.assert_array_equal(fs.n_valid, s["tab"].n_valid)
        np.testing.assert_allclose(p, s["tab"].pasc, rtol=0, atol=1e-9, equal_nan=True)
        np.testing.assert_allclose(pf, s["tab"].pasc_fixed, rtol=0, atol=1e-9, equal_nan=True)


def test_fast_search_flags_singular_points(setup):
    from wtc.search import FastSearch
    s = setup
    W = dict(s["cache"].W, dup=-s["cache"].W["x0"])
    cache = SpectraCache(W, DT_MONTHLY, DJ, s["sc"])
    ok = dict(s["ok"], dup=s["ok"]["x0"])
    fs = FastSearch(["x0", "dup"], [("x0",), ("dup",), ("x0", "dup")], s["thr"], s["per"], s["inside"], ok)
    p, _, n_bad = fs.run(cache)
    assert n_bad == int(s["inside"].sum())
    assert p[2, 0] == 0.0 and p[0, 0] == pytest.approx(p[1, 0])
