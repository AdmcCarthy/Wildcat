# Wildcat

**Still striking, finding less: fifty years of Norwegian wildcat wells.**
Live page: https://admccarthy.github.io/Wildcat/

"Wildcat" is the repository's name; the page is titled *Still striking, finding less*. Every
exploration wildcat on the Norwegian continental shelf since 1966, from Sodir's public data: how often
wildcats find oil or gas (technical success), how much each discovery holds, how many discoveries are
developed (commercial success) and how long they take to produce. The key figure is a connected
scatterplot of success rate against volume per discovery, 1990–2025. The story follows SubScout's
`reveal` arc: the hit rate has held at about half, near-field drilling in mature acreage explains it,
and the twist is that each find holds a fraction of what it used to.

A [SubScout](https://github.com/AdmcCarthy/SubScout) story (v0.4.0): `story.md`, `story.py` (every
quoted number with method, source and confidence) and `figures/` (connected scatterplot, map,
time-to-production chart, North Sea quarter-block glyph map with a bivariate colour scale).

```
uv sync --all-groups
uv run python scripts/fetch_sodir.py   # -> data/raw (Sodir FactPages, FactMaps; not committed)
uv run python scripts/build_data.py    # -> data/
uv run python scripts/build_blocks.py  # -> data/ns_quarters.json (North Sea glyph map)
uv run subscout build . --out _site    # -> the page
uv run pytest                          # checks against Sodir's series + every quoted number
```

Data: Sodir (Norwegian Offshore Directorate), NLOD 2.0; definitions in [`data/README.md`](data/README.md)
and on the page under "How we know". Code: MIT.
