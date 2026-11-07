"""Build Wildcat's datasets from the raw Sodir tables in data/raw.

Definitions (stated on the page):
- Wildcat: Sodir purpose WILDCAT, not a re-entry, not CCS. Year = completion year (Sodir's convention for
  the volumes-discovered series).
- Technical success: the well proved oil or gas (content OIL, GAS, OIL/GAS, GAS/CONDENSATE or
  OIL/GAS/CONDENSATE); shows and dry count as dry.
- New discovery: Sodir marks the well as the discovery wellbore.
- Commercial success: the discovery is producing, has produced (shut down) or is approved for production,
  directly or through the field or discovery it was later included in.
- Time to first hydrocarbons: from the wildcat's completion to the first 'Producing' status of the field
  that produces it, or the date the discovery was included in that field if later.
- Distance to the nearest field: from the well to the nearest field outline whose plan for development
  (PDO) had been approved before the well was spudded.
Volumes discovered per year: Sodir gross resource growth (norskpetroleum.no), 1990 onwards.

Usage: python scripts/build_data.py [raw_dir] [out_dir]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import shapely
from pyproj import Transformer
from shapely.geometry import MultiPolygon, Point, box, shape
from shapely.geometry.polygon import orient
from shapely.ops import transform, unary_union

HC = {"OIL", "GAS", "OIL/GAS", "GAS/CONDENSATE", "OIL/GAS/CONDENSATE"}
DEVELOPED = {"Producing", "Shut down", "Approved for production"}
EVALUATING = {"Production likely but unclarified", "Production in clarification phase", "Production not evaluated"}
UNLIKELY = {"Production is unlikely"}
GROWTH_XLSX = "np/55-Brutto-ressurstilvekst-undersokelsesbronner-1990-2025-200226.xlsx"
TO_UTM = Transformer.from_crs(4326, 32633, always_xy=True).transform


def d(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, format="%d.%m.%Y", errors="coerce")


def d3_orient(g):
    if g.geom_type == "Polygon":
        return orient(g, sign=-1.0)
    if g.geom_type == "MultiPolygon":
        return MultiPolygon([orient(p, sign=-1.0) for p in g.geoms])
    return g


def discovery_status(disc: pd.DataFrame, field_status: dict[str, str]) -> pd.DataFrame:
    """Resolve each discovery to developed / evaluating / unlikely, following 'included in' chains."""
    by_name = disc.set_index("dscName")
    out = {}
    for name, r in by_name.iterrows():
        seen, cur = set(), r
        while True:
            if isinstance(cur.fldName, str):  # included in (or is) a field
                st = field_status.get(cur.fldName, "")
                cat = "developed" if st in DEVELOPED or st == "" or cur.dscCurrentActivityStatus in DEVELOPED else "evaluating"
                out[name] = (cat, cur.fldName)
                break
            s = cur.dscCurrentActivityStatus
            if s == "Included in other discovery" and isinstance(cur.dscResInclInDiscoveryName, str) and cur.dscResInclInDiscoveryName in by_name.index and cur.dscResInclInDiscoveryName not in seen:
                seen.add(cur.dscResInclInDiscoveryName)
                cur = by_name.loc[cur.dscResInclInDiscoveryName]
                continue
            cat = "developed" if s in DEVELOPED else "evaluating" if s in EVALUATING else "unlikely" if s in UNLIKELY else "evaluating"
            out[name] = (cat, None)
            break
    return pd.DataFrame.from_dict(out, orient="index", columns=["commercial_status", "field"])


def main(raw: Path, out: Path) -> None:
    w = pd.read_csv(raw / "wellbore_exploration_all.csv")
    disc = pd.read_csv(raw / "discovery.csv")
    fld = pd.read_csv(raw / "field.csv")
    st = pd.read_csv(raw / "field_activity_status_hst.csv")
    st["from"] = d(st.fldStatusFromDate)
    producing = st[st.fldStatus == "Producing"].groupby("fldName")["from"].min()
    pdo = st[st.fldStatus == "Approved for production"].groupby("fldName")["from"].min()
    prod = pd.read_csv(raw / "field_production_monthly.csv")
    prod = prod[prod.prfPrdOeNetMillSm3 > 0]
    first_month = prod.assign(dt=pd.to_datetime({"year": prod.prfYear, "month": prod.prfMonth, "day": 1})).groupby("prfInformationCarrier").dt.min()
    field_start = producing.combine_first(first_month)
    field_status = dict(zip(fld.fldName, fld.fldCurrentActivitySatus))

    wc = w[(w.wlbPurpose == "WILDCAT") & (w.wlbReentry != "YES") & (w.wlbCompletionYear >= 1966)].copy()  # 0 = still drilling
    wc["year"] = wc.wlbCompletionYear.astype(int)
    wc["spud"] = d(wc.wlbEntryDate)
    wc["completed"] = d(wc.wlbCompletionDate)
    wc["technical"] = wc.wlbContent.isin(HC)
    wc["new_discovery"] = wc.wlbDiscoveryWellbore == "YES"
    wc["apa"] = wc.wlbLicensingActivity.fillna("").str.match(r"^(TFO|APA)")
    wc["area"] = wc.wlbMainArea.str.title()
    # drilled from an existing installation: Sodir names such wells with a slot code, e.g. 31/4-A-15 B, 6506/12-PB-3 H
    wc["from_platform"] = wc.wlbWellboreName.str.match(r"^\d+/\d+-[A-Z]+-\d")

    ds = discovery_status(disc, field_status)
    dlink = disc.set_index("wlbNpdidWellbore")[["dscName", "dscDiscoveryYear", "dscDateFromInclInField", "dscHcType"]]
    wc = wc.join(dlink, on="wlbNpdidWellbore")
    wc = wc.join(ds, on="dscName")
    wc.loc[~wc.new_discovery, ["commercial_status", "field"]] = [None, None]
    wc["commercial"] = wc.commercial_status.eq("developed")
    # time to first hydrocarbons
    incl = d(wc.dscDateFromInclInField)
    fs = wc.field.map(field_start)
    first_hc = pd.concat([fs, incl.where(incl > fs)], axis=1).max(axis=1)
    first_hc = first_hc.where(wc.commercial & fs.notna())
    wc["first_hc"] = first_hc
    wc["lead_years"] = ((first_hc - wc.completed).dt.days / 365.25).clip(lower=0).round(2)  # inclusion can predate completion

    # distance to the nearest field with an approved PDO at spud
    geo = json.loads((raw / "fields.geojson").read_text())
    polys = {}
    for ft in geo["features"]:
        if ft.get("geometry"):
            polys.setdefault(ft["properties"]["fldName"], []).append(shape(ft["geometry"]).buffer(0))
    fpoly = {k: transform(TO_UTM, unary_union(v)) for k, v in polys.items()}
    fpdo = {k: pdo.get(k, field_start.get(k)) for k in fpoly}
    dist = []
    for r in wc.itertuples():
        if pd.isna(r.wlbNsDecDeg) or pd.isna(r.spud):
            dist.append(np.nan)
            continue
        p = Point(TO_UTM(r.wlbEwDecDeg, r.wlbNsDecDeg))
        ds_ = [g.distance(p) for k, g in fpoly.items() if pd.notna(fpdo[k]) and fpdo[k] <= r.spud]
        dist.append(round(min(ds_) / 1000, 1) if ds_ else np.nan)
    wc["dist_field_km"] = dist

    keep = ["wlbWellboreName", "year", "spud", "completed", "area", "wlbNsDecDeg", "wlbEwDecDeg", "wlbContent",
            "technical", "new_discovery", "dscName", "commercial_status", "commercial", "field", "first_hc",
            "lead_years", "wlbWaterDepth", "wlbTotalDepth", "wlbDrillingDays", "apa", "wlbLicensingActivity",
            "dist_field_km", "wlbDrillingOperator", "from_platform"]
    wells = wc[keep].rename(columns={"wlbWellboreName": "well", "wlbNsDecDeg": "lat", "wlbEwDecDeg": "lon",
                                     "wlbContent": "content", "dscName": "discovery", "wlbWaterDepth": "water_depth_m",
                                     "wlbTotalDepth": "total_depth_m", "wlbDrillingDays": "drilling_days",
                                     "wlbLicensingActivity": "licensing", "wlbDrillingOperator": "operator"})
    out.mkdir(parents=True, exist_ok=True)
    wells.sort_values(["year", "well"]).to_csv(out / "wildcats.csv", index=False, date_format="%Y-%m-%d")

    # volumes discovered per year (Sodir gross resource growth) and Sodir's completed-wildcat count
    gx = pd.read_excel(raw / GROWTH_XLSX, header=None).dropna(how="all").dropna(axis=1, how="all")
    gx = gx[pd.to_numeric(gx.iloc[:, 0], errors="coerce").between(1960, 2100)]
    growth = pd.DataFrame({"year": gx.iloc[:, 0].astype(int).values, "volume_msm3": gx.iloc[:, 2].astype(float).values,
                           "sodir_wildcats": gx.iloc[:, 3].astype(int).values})

    y = wells.groupby("year").agg(
        wildcats=("well", "size"), technical=("technical", "sum"), discoveries=("new_discovery", "sum"),
        commercial=("commercial", "sum"),
        evaluating=("commercial_status", lambda s: (s == "evaluating").sum()),
        unlikely=("commercial_status", lambda s: (s == "unlikely").sum()),
        median_days=("drilling_days", "median"), median_td=("total_depth_m", "median"),
        median_wd=("water_depth_m", "median"), apa_share=("apa", "mean"),
        median_dist_km=("dist_field_km", "median"),
        near_field_share=("dist_field_km", lambda s: (s <= 25).mean()),
        median_lead=("lead_years", "median"),
    ).reset_index()
    y = y.merge(growth, on="year", how="left")
    # time to first production without censoring bias: share of a year's new discoveries producing within
    # 5 / 10 years, only for years at least 5 / 10 years ago
    last_year = int(wells.year.max())
    disc_w = wells[wells.new_discovery]
    for k in (5, 10):
        share = disc_w.groupby("year").apply(lambda g, k=k: (g.lead_years <= k).sum() / len(g), include_groups=False)
        y[f"producing_within_{k}y"] = y.year.map(share).where(y.year <= last_year - k)
    y["from_platform"] = y.year.map(wells.groupby("year").from_platform.sum())
    y["technical_rate"] = y.technical / y.wildcats
    y["commercial_rate"] = y.commercial / y.wildcats
    y["volume_per_wildcat"] = y.volume_msm3 / y.wildcats
    y["volume_per_discovery"] = y.volume_msm3 / y.discoveries.replace(0, np.nan)
    # three-year centred rolling sums for the connected scatterplot (ratios of sums, not means of ratios)
    r = y.set_index("year")[["wildcats", "technical", "discoveries", "commercial", "volume_msm3"]].rolling(3, center=True, min_periods=2).sum()
    y["technical_rate_3y"] = (r.technical / r.wildcats).values
    y["commercial_rate_3y"] = (r.commercial / r.wildcats).values
    y["volume_per_wildcat_3y"] = (r.volume_msm3 / r.wildcats).values
    y["volume_per_discovery_3y"] = (r.volume_msm3 / r.discoveries).values
    y["wildcats_3y"] = (r.wildcats / 3).values
    y.round(4).to_csv(out / "yearly.csv", index=False)

    # map layers: last-decade wildcats, fields, land, boundaries
    last = wells[wells.year >= 2016]
    pts = [{"type": "Feature", "properties": {"well": r.well, "year": int(r.year), "technical": bool(r.technical),
                                              "commercial_status": r.commercial_status if isinstance(r.commercial_status, str) else None, "apa": bool(r.apa),
                                              "dist": None if pd.isna(r.dist_field_km) else r.dist_field_km},
            "geometry": {"type": "Point", "coordinates": [round(r.lon, 3), round(r.lat, 3)]}}
           for r in last.itertuples() if pd.notna(r.lat)]
    (out / "wells_recent.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": pts}))
    flds = [{"type": "Feature", "properties": {"name": k},
             "geometry": json.loads(json.dumps(d3_orient(shapely.set_precision(unary_union(v).simplify(0.01), 0.001)).__geo_interface__))}
            for k, v in polys.items()]
    (out / "fields.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": flds}))
    frame = box(-4, 54.0, 34, 75)
    land = unary_union([shape(ft["geometry"]).buffer(0) for ft in json.loads((raw / "land.geojson").read_text())["features"] if ft.get("geometry")])
    land = land.intersection(frame).simplify(0.06)
    land = MultiPolygon([g for g in getattr(land, "geoms", [land]) if g.area > 0.03])
    (out / "land.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": json.loads(json.dumps(d3_orient(shapely.set_precision(land, 0.01)).__geo_interface__))}]}))
    sb = json.loads((raw / "sea_boundaries.geojson").read_text())
    lines = [{"type": "Feature", "properties": {}, "geometry": json.loads(json.dumps(shapely.set_precision(shape(ft["geometry"]).intersection(frame).simplify(0.02), 0.01).__geo_interface__))}
             for ft in sb["features"] if ft.get("geometry")]
    (out / "borders.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [x for x in lines if x["geometry"].get("coordinates") or x["geometry"].get("geometries")]}))
    print(f"{len(wells)} wildcats {wells.year.min()}–{wells.year.max()}; {int(wells.new_discovery.sum())} discoveries; "
          f"{int(wells.commercial.sum())} developed; {len(pts)} recent wells mapped")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(Path(a[0]) if a else Path("data/raw"), Path(a[1]) if len(a) > 1 else Path("data"))
