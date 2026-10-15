"""Prepare geo data for Blender (run with the PROJECT python, not Blender's).

    uv run python tools/blender/prep_geo.py

Why a separate step: Blender's bundled Python cannot import our project packages
(scipy, pyshp ...). So we turn the raw downloads into two plain files Blender can
read with only numpy + json:

  data/geo/elevation.npy      float32 [rows=lat south->north, cols=lon west->east], metres
  data/geo/elevation_meta.json  grid origin + step
  data/geo/coastlines.json    Natural Earth 10m land outlines, clipped to the map box
                              ("wide" = simplified for the far camera, "close" = detailed)

Sources (both public domain / free reuse):
  ETOPO1 via NOAA ERDDAP  https://coastwatch.pfeg.noaa.gov/erddap/griddap/etopo180
  Natural Earth 10m land   https://www.naturalearthdata.com/ (public domain)
"""
import json
import urllib.request
from pathlib import Path

import numpy as np
import shapefile  # pyshp
from scipy.io import netcdf_file

ROOT = Path(__file__).resolve().parents[2]
GEO = ROOT / "data" / "geo"
NC = GEO / "etopo180_indian_ocean.nc"
# stride 3 on the 1-arc-minute grid = 3 arc-minutes (0.05 deg), whole box in one request
URL = ("https://coastwatch.pfeg.noaa.gov/erddap/griddap/etopo180.nc"
       "?altitude%5B(-25):3:(30)%5D%5B(40):3:(140)%5D")
LAND_SHP = Path.home() / ".local/share/cartopy/shapefiles/natural_earth/physical/ne_10m_land"
LON0, LON1, LAT0, LAT1 = 40.0, 140.0, -25.0, 30.0


def rdp(pts: np.ndarray, tol: float) -> np.ndarray:
    """Douglas-Peucker line simplification (iterative, so long coastlines don't recurse)."""
    n = len(pts)
    if n < 3:
        return pts
    keep = np.zeros(n, bool)
    keep[0] = keep[-1] = True
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        seg = pts[b] - pts[a]
        rel = pts[a + 1:b] - pts[a]
        norm = np.hypot(*seg)
        # perpendicular distance of each point to the chord a-b
        d = np.hypot(*rel.T) if norm == 0 else np.abs(seg[0] * rel[:, 1] - seg[1] * rel[:, 0]) / norm
        i = int(d.argmax())
        if d[i] > tol:
            keep[a + 1 + i] = True
            stack += [(a, a + 1 + i), (a + 1 + i, b)]
    return pts[keep]


def clip_runs(pts: np.ndarray, margin=1.0):
    """Split a ring into runs that lie inside the (slightly enlarged) map box."""
    inside = ((pts[:, 0] > LON0 - margin) & (pts[:, 0] < LON1 + margin) &
              (pts[:, 1] > LAT0 - margin) & (pts[:, 1] < LAT1 + margin))
    if inside.all():
        return [pts]
    runs, start = [], None
    for i, ok in enumerate(inside):
        if ok and start is None:
            start = i
        if not ok and start is not None:
            runs.append(pts[start:i]); start = None
    if start is not None:
        runs.append(pts[start:])
    return [r for r in runs if len(r) > 1]


def main():
    GEO.mkdir(parents=True, exist_ok=True)
    if not NC.exists():
        print("downloading", URL)
        urllib.request.urlretrieve(URL, NC)

    f = netcdf_file(NC, mmap=False)
    alt = f.variables["altitude"].data.astype("float32")
    lat, lon = f.variables["latitude"].data, f.variables["longitude"].data
    assert lat[0] < lat[-1] and lon[0] < lon[-1]
    np.save(GEO / "elevation.npy", alt)
    meta = dict(lon0=float(lon[0]), lat0=float(lat[0]), step=float(lon[1] - lon[0]),
                rows=alt.shape[0], cols=alt.shape[1])
    (GEO / "elevation_meta.json").write_text(json.dumps(meta, indent=1))
    print("elevation", alt.shape, meta)

    out = {"wide": [], "close": []}
    r = shapefile.Reader(str(LAND_SHP))
    for shp in r.shapes():
        parts = list(shp.parts) + [len(shp.points)]
        for a, b in zip(parts[:-1], parts[1:]):
            ring = np.asarray(shp.points[a:b], float)
            for run in clip_runs(ring):
                w, c = rdp(run, 0.04), rdp(run, 0.01)
                if len(w) > 1:
                    out["wide"].append(np.round(w, 4).tolist())
                out["close"].append(np.round(c, 4).tolist())
    (GEO / "coastlines.json").write_text(json.dumps(out))
    print({k: (len(v), sum(map(len, v))) for k, v in out.items()})


if __name__ == "__main__":
    main()
