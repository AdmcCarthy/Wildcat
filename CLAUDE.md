# Wildcat: working rules

A SubScout story (github.com/AdmcCarthy/SubScout, pinned tag) on Norwegian exploration wildcats.
"Wildcat" is only the repo name; the page is titled *Still striking, in smaller pieces*.
Owner: Adam McCarthy, petroleum geoscience domain expert. Follow SubScout's CLAUDE.md and styleguide.

- Arc `reveal`: claim (hit rate ~half) -> evidence (near-field, APA, faster wells) -> twist (smaller
  finds, lower commercial success, longer to production except platform-drilled wells).
- Key figure: connected scatterplot (figures/connected.js), technical success vs volume per discovery,
  three-year centred ratios of sums, 1990–2025; last decade = 2016–2025; 2026 partial, never averaged.
- Technical success = oil or gas proven (shows = dry). Commercial = discovery producing, shut down or
  approved, following 'included in' chains. Lead time = completion to producing-field start.
- Palette: Tulip's eucalyptus and clay (figures/common.js); built-in charts use fjord/neutral tokens.
- Numbers in prose come from story.py and are tested in tests/test_wildcat.py. Build must have 0 warnings.
- North Sea section (figures/glyphs.js, scripts/build_blocks.py): quarter-blocks x four eras; glyph = rings
  (wells) + disc (volume, area) with a 3x3 diverging bivariate fill (x: success vs North Sea average,
  clay-grey-blue; y: volume per discovery, pale-deep). Base map and licences on canvas, one SVG layer per
  era prepared only near view in idle time (perf gate). Phones: compact legend, map <= vh - 530.
- Print plates: `export: true` figures are rendered by Plate (github.com/AdmcCarthy/Plate, pinned by tag) in the Pages workflow: PDF at A3 and A1 and PNG, listed on `/plates/` by `scripts/build_plates_index.py`. SubScout >= 0.6 no longer renders (`subscout export` only points to Plate).

