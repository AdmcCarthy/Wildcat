"""Wildcat: datasets for the figures and every number the prose quotes.

Volumes in Sm³ o.e. for SubScout's `volume` filter; shares 0–1. Periods: 1990s = 1990–1999,
2000s = 2000–2009, last decade = 2016–2025 (2026 is partial and only shown, never averaged).
"""

from __future__ import annotations

import pandas as pd

from subscout import metric

M = 1e6
LAST = (2016, 2025)
NEAR_KM = 25


def _sum_ratio(y: pd.DataFrame, a: int, b: int, num: str, den: str) -> float:
    s = y[(y.year >= a) & (y.year <= b)]
    return float(s[num].sum() / s[den].sum())


def datasets(d):
    y, w = d["yearly"], d["wildcats"]
    j = y[(y.year >= 1990) & (y.year <= 2025)]
    journey = {
        "points": [{"year": int(r.year), "x": round(r.technical_rate_3y, 4), "y": round(r.volume_per_discovery_3y, 3),
                    "wildcats": round(r.wildcats_3y, 1)} for r in j.itertuples()],
        "last": list(LAST),
        "labels": {"1990": "1990", "1997": "1997", "2005": "2005", "2010": "2010: Johan Sverdrup", "2016": "2016", "2025": "2025"},
    }
    # outcomes of every wildcat, five-year bins
    w = w[w.year <= 2025].copy()
    w["bin"] = (w.year // 5 * 5).astype(int)
    w["outcome"] = "Dry"
    w.loc[w.technical, "outcome"] = "Oil or gas, no new discovery"
    w.loc[w.commercial_status == "developed", "outcome"] = "Developed or approved"
    w.loc[w.commercial_status == "evaluating", "outcome"] = "Still being evaluated"
    w.loc[w.commercial_status == "unlikely", "outcome"] = "Development unlikely"
    order = ["Developed or approved", "Still being evaluated", "Development unlikely", "Oil or gas, no new discovery", "Dry"]
    oc = w.groupby(["bin", "outcome"]).size().unstack(fill_value=0).reindex(columns=order, fill_value=0)
    oc = oc.div(oc.sum(axis=1), axis=0).stack().rename("share").reset_index()
    oc["period"] = oc.bin.astype(str) + "–" + (oc.bin + 4).astype(str).str[2:]
    oc["share"] = (oc.share * 100).round(1)
    days = y[(y.year >= 1990) & (y.year <= 2025)][["year", "median_days"]].assign(series="Median drilling days")
    dev = w[w.commercial & w.lead_years.notna()]
    lead = {
        "points": [{"year": int(r.year), "lead": float(r.lead_years), "name": r.discovery if isinstance(r.discovery, str) else "", "platform": bool(r.from_platform), "field": r.field if isinstance(r.field, str) else None}
                   for r in dev.itertuples()],
        "cohort": [{"year": int(r.year), "p5": None if pd.isna(r.producing_within_5y) else round(r.producing_within_5y, 3),
                    "p10": None if pd.isna(r.producing_within_10y) else round(r.producing_within_10y, 3)} for r in y.itertuples() if 1966 <= r.year <= 2025],
    }
    return {"journey": journey, "outcomes": oc[["period", "outcome", "share"]], "days": days, "lead": lead}


def metrics(d):
    y, w = d["yearly"], d["wildcats"]
    w = w[w.year <= 2025]
    a, b = LAST
    m, fp, np_ = metric, "sodir", "np"
    lw = w[(w.year >= a) & (w.year <= b)]
    w90 = w[(w.year >= 1990) & (w.year <= 1999)]
    disc = w[w.new_discovery]
    d10 = disc[(disc.year >= 2010) & (disc.year <= 2019)]
    d20 = disc[disc.year >= 2020]
    co = y.set_index("year")

    def cohort(col, y0, y1):
        s = co.loc[y0:y1, col].dropna()
        num = sum(co.loc[k, "discoveries"] * s[k] for k in s.index)
        return float(num / co.loc[s.index, "discoveries"].sum())

    vd90 = _sum_ratio(y, 1990, 1999, "volume_msm3", "discoveries")
    vdl = _sum_ratio(y, a, b, "volume_msm3", "discoveries")
    return {
        "n_wildcats": m(len(w), "Wildcats completed 1966–2025 (not re-entries or CCS)", fp, "observed"),
        "n_last": m(len(lw), "Wildcats completed 2016–2025", fp, "observed"),
        "tech_last": m(_sum_ratio(y, a, b, "technical", "wildcats"), "Technical success 2016–2025: wells proving oil or gas over all wildcats", fp, "derived"),
        "tech_1990s": m(_sum_ratio(y, 1990, 1999, "technical", "wildcats"), "Technical success 1990–1999", fp, "derived"),
        "tech_2000s": m(_sum_ratio(y, 2000, 2009, "technical", "wildcats"), "Technical success 2000–2009", fp, "derived"),
        "disc_last": m(int(lw.new_discovery.sum()), "New discoveries from wildcats completed 2016–2025", fp, "observed"),
        "vol_disc_1990s": m(vd90 * M, "Volume discovered per new discovery, 1990–1999 (Sodir gross resource growth / discoveries)", np_, "derived", "Sm³ o.e."),
        "vol_disc_2000s": m(_sum_ratio(y, 2000, 2009, "volume_msm3", "discoveries") * M, "Volume per new discovery, 2000–2009", np_, "derived", "Sm³ o.e."),
        "vol_disc_last": m(vdl * M, "Volume per new discovery, 2016–2025", np_, "derived", "Sm³ o.e."),
        "vol_disc_fall": m(1 - vdl / vd90, "Fall in volume per discovery, 1990s to 2016–2025", np_, "derived"),
        "vol_wc_1990s": m(_sum_ratio(y, 1990, 1999, "volume_msm3", "wildcats") * M, "Volume discovered per wildcat, 1990–1999", np_, "derived", "Sm³ o.e."),
        "vol_wc_last": m(_sum_ratio(y, a, b, "volume_msm3", "wildcats") * M, "Volume discovered per wildcat, 2016–2025", np_, "derived", "Sm³ o.e."),
        "vol_2010_disc": m(float(co.loc[2010, "volume_per_discovery"]) * M, "Volume per new discovery in 2010, the year Johan Sverdrup was found", np_, "derived", "Sm³ o.e."),
        "near_last": m(float((lw.dist_field_km <= NEAR_KM).mean()), f"Share of 2016–2025 wildcats within {NEAR_KM} km of a field approved before spud", fp, "derived"),
        "near_1990s": m(float((w90.dist_field_km <= NEAR_KM).mean()), f"Share of 1990s wildcats within {NEAR_KM} km of a field", fp, "derived"),
        "apa_last": m(float(lw.apa.mean()), "Share of 2016–2025 wildcats in licences from the APA rounds", fp, "observed"),
        "days_2006_15": m(float(w[(w.year >= 2006) & (w.year <= 2015)].drilling_days.median()), "Median drilling days, wildcats 2006–2015", fp, "observed"),
        "days_last": m(float(lw.drilling_days.median()), "Median drilling days, wildcats 2016–2025", fp, "observed"),
        "platform_2020s": m(int(w[w.year >= 2020].from_platform.sum()), "Wildcats drilled from an existing installation since 2020 (slot-coded wellbore names)", fp, "derived"),
        "dev_2010s": m(float((d10.commercial_status == "developed").mean()), "2010s discoveries producing, produced or approved for production", fp, "derived"),
        "eval_2010s": m(float((d10.commercial_status == "evaluating").mean()), "2010s discoveries still being evaluated", fp, "derived"),
        "unlikely_2010s": m(float((d10.commercial_status == "unlikely").mean()), "2010s discoveries where production is unlikely", fp, "derived"),
        "dev_2020s": m(float((d20.commercial_status == "developed").mean()), "2020–2025 discoveries producing or approved", fp, "derived"),
        "eval_2020s": m(float((d20.commercial_status == "evaluating").mean()), "2020–2025 discoveries still being evaluated", fp, "derived"),
        "p10_2000s": m(cohort("producing_within_10y", 2000, 2009), "Share of 2000s discoveries producing within ten years", fp, "derived"),
        "p10_2010s": m(cohort("producing_within_10y", 2010, 2019), "Share of 2010–2015 discoveries producing within ten years (later years too recent)", fp, "derived"),
        "peak_wildcats": m(int(co.loc[1990:2025, "wildcats"].max()), "Most wildcats completed in one year since 1990", fp, "observed"),
    }
