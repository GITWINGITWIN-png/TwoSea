from __future__ import annotations
import re
from pathlib import Path
import numpy as np

PSMSL_MISSING = -99999.0
NOAA_MISSING = -90.0
UHSLC_MISSING = -32767


def read_psmsl(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    t, v = [], []
    for line in Path(path).read_text().splitlines():
        parts = [p.strip() for p in line.split(";")]
        if len(parts) < 2:
            continue
        val = float(parts[1])
        t.append(float(parts[0]))
        v.append(np.nan if val == PSMSL_MISSING else val)
    return np.asarray(t), np.asarray(v)


def read_noaa_index(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    lines = [l.rstrip() for l in Path(path).read_text().splitlines() if l.strip()]
    t, v = [], []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) != 13 or not re.fullmatch(r"\d{4}", parts[0]):
            continue
        year = int(parts[0])
        for month, raw in enumerate(parts[1:]):
            x = float(raw)
            t.append(year + (month + 0.5) / 12)
            v.append(np.nan if x < NOAA_MISSING else x)
    return np.asarray(t), np.asarray(v)


def read_uhslc(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    import datetime as dt
    t, v = [], []
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        y, mo, d, h, val = (int(x) for x in line.split(","))
        doy = dt.date(y, mo, d).timetuple().tm_yday
        t.append(y + ((doy - 1) * 24 + h) / (365.25 * 24))
        v.append(np.nan if val == UHSLC_MISSING else float(val))
    return np.asarray(t), np.asarray(v)


def read_uhslc_grid(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    raw = np.loadtxt(path, delimiter=",", dtype=np.int64, ndmin=2)
    days = np.array([f"{y:04d}-{m:02d}-{d:02d}" for y, m, d in raw[:, :3]],
                    dtype="datetime64[D]")
    t = days.astype("datetime64[h]") + raw[:, 3].astype("timedelta64[h]")
    step = np.diff(t).astype(int)
    if not np.all(step == 1):
        bad = int(np.flatnonzero(step != 1)[0])
        raise ValueError(f"กริดรายชั่วโมงไม่ต่อเนื่องที่แถว {bad}: {t[bad]} -> {t[bad + 1]}")
    v = raw[:, 4].astype(float)
    v[raw[:, 4] == UHSLC_MISSING] = np.nan
    return t, v


def read_uhslc_daily(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    raw = np.loadtxt(path, delimiter=",", dtype=np.int64, ndmin=2)
    days = np.array([f"{y:04d}-{m:02d}-{d:02d}" for y, m, d in raw[:, :3]],
                    dtype="datetime64[D]")
    v = raw[:, 3].astype(float)
    v[raw[:, 3] == UHSLC_MISSING] = np.nan
    return days, v


def read_wnpmi(indices_dir: str | Path) -> tuple[np.ndarray, np.ndarray]:
    d = Path(indices_dir)
    ts, vs = read_noaa_index(d / "u850_box_south.data")
    tn, vn = read_noaa_index(d / "u850_box_north.data")
    if len(ts) != len(tn) or not np.allclose(ts, tn):
        raise ValueError("แกนเวลาของสองกล่องไม่ตรงกัน — โหลดมาคนละช่วงปีหรือเปล่า")
    return ts, vs - vn


def to_monthly_grid(t: np.ndarray, v: np.ndarray,
                    start: float, stop: float) -> tuple[np.ndarray, np.ndarray]:
    grid = np.arange(start + 1 / 24, stop, 1 / 12)
    out = np.full_like(grid, np.nan)
    good = ~np.isnan(v)
    tg, vg = t[good], v[good]
    if len(tg) == 0:
        return grid, out
    hi = np.clip(np.searchsorted(tg, grid), 0, len(tg) - 1)
    lo = np.clip(hi - 1, 0, len(tg) - 1)
    pick = np.where(np.abs(tg[lo] - grid) <= np.abs(tg[hi] - grid), lo, hi)
    near = np.abs(tg[pick] - grid) < 1 / 24
    out[near] = vg[pick][near]
    return grid, out
