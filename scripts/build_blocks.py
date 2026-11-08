"""North Sea performance by quarter-block and era, for the bivariate glyph map.

Unit: each Sodir block (an exact 20' x 15' rectangle in ED50) cut into four equal quarters (10' x 7.5',
about 9 x 14 km). Quarters are stable through time, unlike licences, which are awarded, split and
relinquished. Wells are assigned by their ED50 coordinates (Sodir's datum for wellbore positions).

Per quarter and era:
- wells:      wildcats completed
- hits:       wildcats that proved oil or gas (technical success)
- rate_adj:   technical success shrunk towards the North Sea average, (hits + K * avg) / (wells + K),
              so one lucky or unlucky well does not paint a quarter as an outlier (empirical Bayes)
- volume:     volume attributed to the quarter's new discoveries: Sodir's estimate for discoveries not
              yet developed; the field's recoverable volume for the discovery that founded a field (split
              equally if a field has two); discoveries later included in another are counted in that one.
              Discoveries Sodir rates 'production unlikely' have no published volume and count as zero.
- vol_per_disc: volume / new discoveries
Classes for the bivariate colour: x = rate_adj below / around / above the average (+-BAND);
y = volume per discovery small / medium / large (log decades, MSm3 o.e.).

Usage: python scripts/build_blocks.py [raw_dir] [out_dir]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from shapely.geometry import box, shape

ERAS = [(1966, 1985), (1986, 2005), (2006, 2015), (2016, 2025)]
K = 3  # prior weight, in wells
BAND = 0.10  # +-10 percentage points around the average counts as 'around'
VOL_BREAKS = [5.0, 50.0]  # MSm3 o.e. per discovery: small < 5 (about 30 MMboe) <= medium < 50 <= large


def discovery_volumes(raw: Path) -> dict[str, float]:
    d = pd.read_csv(raw / "discovery.csv")
    dr = pd.read_csv(raw / "discovery_reserves.csv")
    fr = pd.read_csv(raw / "field_reserves.csv")
    fr = fr[fr.fldVersion == fr.fldVersion.max()].set_index("fldName").fldRecoverableOE
    vol = {r.dscName: float(r.dscRecoverableOe) for r in dr.itertuples()}
    own = d[(d.dscCurrentActivityStatus != "Included in other discovery") & d.fldName.notna()]
    share = own.groupby("fldName").size()
    for r in own.itertuples():
        if r.dscName not in vol and r.fldName in fr.index:
            vol[r.dscName] = float(fr[r.fldName]) / share[r.fldName]
    return vol


def main(raw: Path, out: Path) -> None:
    w = pd.read_csv(out / "wildcats.csv")
    w = w[(w.area == "North Sea") & (w.year <= ERAS[-1][1]) & w.lat.notna()].copy()
    vol = discovery_volumes(raw)
    w["volume"] = np.where(w.new_discovery, w.discovery.map(vol).fillna(0.0), 0.0)
    avg = float(w.technical.mean())

    blocks = json.loads((raw / "blocks_ns_ed50.geojson").read_text())["features"]
    quarters = []
    for ft in blocks:
        x0, y0, x1, y1 = shape(ft["geometry"]).bounds
        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
        name = ft["properties"]["blcName"]
        for q, (a, b, c, e) in zip(["NW", "NE", "SW", "SE"], [(x0, ym, xm, y1), (xm, ym, x1, y1), (x0, y0, xm, ym), (xm, y0, x1, ym)], strict=True):
            quarters.append({"id": f"{name} {q}", "block": name, "box": (a, b, c, e)})
    # assign wells to quarters (grid lookup on block bounds)
    idx = {}
    for i, qd in enumerate(quarters):
        a, b, c, e = qd["box"]
        idx.setdefault((round(a, 4), round(b, 4)), i)
    def find(lon, lat):
        for i, qd in enumerate(quarters):
            a, b, c, e = qd["box"]
            if a <= lon < c and b <= lat < e:
                return i
        return None
    w["q"] = [find(r.lon, r.lat) for r in w.itertuples()]
    unassigned = int(w.q.isna().sum())
    w = w[w.q.notna()]
    w["q"] = w.q.astype(int)

    era = np.full(len(w), -1)
    for k, (a, b) in enumerate(ERAS):
        era[(w.year >= a).values & (w.year <= b).values] = k
    w["era"] = era
    g = w.groupby(["q", "era"]).agg(wells=("well", "size"), hits=("technical", "sum"), discoveries=("new_discovery", "sum"),
                                     volume=("volume", "sum"), first=("year", "min"), last=("year", "max"),
                                     names=("discovery", lambda s: [x for x in s.dropna()][:4])).reset_index()
    g["rate_raw"] = g.hits / g.wells
    g["rate_adj"] = (g.hits + K * avg) / (g.wells + K)
    g["xcls"] = np.select([g.rate_adj < avg - BAND / 2, g.rate_adj > avg + BAND / 2], [0, 2], 1)
    g["vol_per_disc"] = np.where(g.discoveries > 0, g.volume / g.discoveries.clip(lower=1), np.nan)
    g["ycls"] = np.where(g.discoveries > 0, np.digitize(g.vol_per_disc, VOL_BREAKS), -1)

    feats = []
    for r in g.itertuples():
        qd = quarters[r.q]
        a, b, c, e = qd["box"]
        feats.append({"q": qd["id"], "lon": round((a + c) / 2, 4), "lat": round((b + e) / 2, 4), "era": int(r.era),
                      "wells": int(r.wells), "hits": int(r.hits), "disc": int(r.discoveries), "vol": round(float(r.volume), 2),
                      "rate": round(float(r.rate_adj), 3), "raw": round(float(r.rate_raw), 3), "x": int(r.xcls), "y": int(r.ycls),
                      "names": r.names, "span": [int(r.first), int(r.last)]})
    grid = [[round(v, 4) for v in qd["box"]] for qd in quarters]
    summary = {
        "eras": [f"{a}–{b}" for a, b in ERAS], "avg": round(avg, 4), "band": BAND, "k": K, "vol_breaks": VOL_BREAKS,
        "n_wells": len(w), "unassigned": unassigned,
        "era_rate": [round(float(w[w.era == k].technical.mean()), 4) for k in range(len(ERAS))],
        "era_wells": [int((w.era == k).sum()) for k in range(len(ERAS))],
        "era_quarters": [int((g.era == k).sum()) for k in range(len(ERAS))],
        "era_volume": [round(float(w[w.era == k].volume.sum()), 1) for k in range(len(ERAS))],
        "era_above": [int(((g.era == k) & (g.xcls == 2)).sum()) for k in range(len(ERAS))],
        "era_below": [int(((g.era == k) & (g.xcls == 0)).sum()) for k in range(len(ERAS))],
        "repeat_quarters": int((w.groupby("q").era.nunique() == len(ERAS)).sum()),
    }
    (out / "ns_quarters.json").write_text(json.dumps({"cells": feats, "grid": grid, "summary": summary}, ensure_ascii=False))
    # a clipped North Sea land and field set for the detail map
    frame = box(0.5, 55.6, 9.5, 62.5)
    for name in ("land", "fields"):
        fc = json.loads((out / f"{name}.geojson").read_text())
        keep = [f for f in fc["features"] if f.get("geometry") and shape(f["geometry"]).intersects(frame)]
        (out / f"{name}_ns.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": keep}))
    # present-day licences in the North Sea frame, simplified, as a context outline layer
    import shapely
    from shapely.ops import unary_union
    lic = json.loads((raw / "licences_active.geojson").read_text())["features"]
    geoms = [shape(f["geometry"]).buffer(0) for f in lic if f.get("geometry") and shape(f["geometry"]).intersects(frame)]
    merged = shapely.set_precision(unary_union(geoms).simplify(0.005), 0.001)
    (out / "licences_ns.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"n": len(geoms)}, "geometry": json.loads(json.dumps(merged.__geo_interface__))}]}))
    summary["n_licences"] = len(geoms)
    (out / "ns_quarters.json").write_text(json.dumps({"cells": feats, "grid": grid, "summary": summary}, ensure_ascii=False))
    print(f"North Sea: {len(w)} exploration wellbores in {len(quarters)} quarters ({unassigned} unassigned); average {avg:.3f}; "
          f"cells per era {summary['era_quarters']}")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(Path(a[0]) if a else Path("data/raw"), Path(a[1]) if len(a) > 1 else Path("data"))
