# Data

Sodir (Norwegian Offshore Directorate), Norwegian Licence for Open Government Data (NLOD 2.0).
`data/raw/` comes from `scripts/fetch_sodir.py` (FactPages tables `wellbore_exploration_all`, `discovery`,
`discovery_reserves`, `field`, `field_reserves`, `field_activity_status_hst`, `field_production_monthly`;
FactMaps fields, discoveries, land, maritime boundaries) plus two norskpetroleum.no spreadsheets saved in
`data/raw/np/` (gross resource growth and completed wildcats 1990–2025; exploration wells spudded).
Everything else is built by `scripts/build_data.py`. Accessed 2026-11-07.

| File | What |
|---|---|
| `wildcats.csv` | One row per wildcat: year, area, result, discovery, commercial status, producing field, first production, lead time, depths, drilling days, APA flag, distance to nearest approved field, platform-drilled flag |
| `yearly.csv` | Per completion year: counts, technical and commercial rates, Sodir volumes and wildcat count, medians, three-year centred ratios for the connected scatterplot, producing-within-5/10-years cohort shares |
| `wells_recent.geojson`, `fields.geojson`, `land.geojson`, `borders.geojson` | Map layers |

Definitions: see the module docstring of `scripts/build_data.py` and the page appendix. Check: wildcat
counts per year match Sodir's own completed-wildcat series within two wells (tests).
Caveats: volumes per year are today's estimates of what each year found (2025 preliminary); commercial
status of recent discoveries is incomplete by nature; "drilled from a platform" is inferred from
slot-coded wellbore names.
