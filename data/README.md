# Data

Sodir (Norwegian Offshore Directorate), Norwegian Licence for Open Government Data (NLOD 2.0).
`data/raw/` comes from `scripts/fetch_sodir.py` (FactPages tables `wellbore_exploration_all`, `discovery`,
`discovery_reserves`, `field`, `field_reserves`, `field_activity_status_hst`, `field_production_monthly`;
FactMaps fields, discoveries, active licences, North Sea blocks in ED50, land, maritime boundaries) plus two norskpetroleum.no spreadsheets saved in
`data/raw/np/` (gross resource growth and completed wildcats 1990–2025; exploration wells spudded).
Everything else is built by `scripts/build_data.py`. Accessed 2026-11-07.

| File | What |
|---|---|
| `wildcats.csv` | One row per wildcat: year, area, result, discovery, commercial status, producing field, first production, lead time, depths, drilling days, APA flag, distance to nearest approved field, platform-drilled flag |
| `yearly.csv` | Per completion year: counts, technical and commercial rates, Sodir volumes and wildcat count, medians, three-year centred ratios for the connected scatterplot, producing-within-5/10-years cohort shares |
| `wells_recent.geojson`, `fields.geojson`, `land.geojson`, `borders.geojson` | Map layers |
| `ns_quarters.json` | North Sea glyph map: every Sodir block cut into four equal quarters (ED50, 10' x 7.5'); per quarter and era wells, hits, adjusted success, new discoveries, attributed volume and bivariate classes (`scripts/build_blocks.py`) |
| `land_ns.geojson`, `fields_ns.geojson`, `licences_ns.geojson` | North Sea base map; present-day licences merged into one outline |

Definitions: see the module docstring of `scripts/build_data.py` and the page appendix. Check: wildcat
counts per year match Sodir's own completed-wildcat series within two wells (tests).
Caveats: volumes per year are today's estimates of what each year found (2025 preliminary); commercial
status of recent discoveries is incomplete by nature; "drilled from a platform" is inferred from
slot-coded wellbore names.

North Sea glyph map: success is shrunk towards the North Sea average with a three-well prior
((hits + 3 x avg) / (wells + 3)) and classed below / around / above at +-5 points; volume per discovery is
classed small < 5, medium 5-50, large >= 50 million Sm3 o.e. Volume is attributed to the discovering well
(Sodir's estimate for undeveloped discoveries; field recoverable volume for the discovery that founded a
field); discoveries rated 'production unlikely' have no published volume and count as zero. Attributed
volumes cover 67-93 % of Sodir's gross resource growth per decade.
