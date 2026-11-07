---
title: Still striking, finding less
short_title: "Still striking, finding less"
dek: Norway's wildcat wells still find oil or gas about half the time. They do it by drilling close to what is already there, and each find is a fraction of what it used to be.
kicker: NCS · Exploration wells 1966–2026 · Sodir
byline: Adam McCarthy
date: 2026-11-07
arc: reveal
register: section
palette: tide
surface: nordic-cool
units: sm3
horizon: true
kpis:
  - { metric: tech_last, filter: pct, label: "of wildcats found oil or gas, 2016–2025" }
  - { metric: vol_disc_last, filter: volume, label: "found per new discovery since 2016" }
  - { metric: near_last, filter: pct, label: "drilled within 25 km of a field" }
  - { metric: dev_2010s, filter: pct, label: "of 2010s discoveries developed so far" }
sources:
  sodir:
    name: Sodir FactPages and FactMaps
    url: https://factpages.sodir.no
    accessed: 2026-11-07
    note: Exploration wellbores, discoveries, fields, field status and production; field outlines, land and maritime boundaries. NLOD 2.0.
  np:
    name: Sodir, gross resource growth and wildcats completed, 1990–2025 (norskpetroleum.no)
    url: https://www.norskpetroleum.no/en/exploration/exploration-activity/
    accessed: 2026-11-07
    note: Volume discovered each year, million Sm³ o.e.; 2025 is preliminary
data:
  wildcats: data/wildcats.csv
  yearly: data/yearly.csv
  wells: data/wells_recent.geojson
  fields: data/fields.geojson
  land: data/land.geojson
  borders: data/borders.geojson
  ns_quarters: data/ns_quarters.json
  land_ns: data/land_ns.geojson
  fields_ns: data/fields_ns.geojson
  licences_ns: data/licences_ns.geojson
---

A wildcat is the first well drilled on a new idea: a structure nobody has tested. Sodir, the
Norwegian Offshore Directorate, records every one: where it was drilled, how long it took, and what it
found. {{ n_wildcats }} wildcats have been completed on the Norwegian shelf since 1966. Put the years
side by side and two measures tell most of the story: how often a wildcat finds oil or gas, and how
much each new discovery holds.

::: step {beat=claim kicker="1990–1999" layout=wide}
### Four in ten, and big

Each point is a year, averaged with its neighbours. Across: the share of wildcats that found oil or
gas. Up: the volume found per new discovery, on a log scale. In the 1990s {{ tech_1990s | pct }} of
wildcats struck, and each new discovery held {{ vol_disc_1990s | volume }} on average.

```chart
id: journey
export: true
type: custom
module: figures/connected.js
data: journey
register: outcrop
state: { upto: 1999 }
title: Wildcats find oil or gas about as often as ever; each find holds far less
subtitle: Technical success rate against volume per new discovery, three-year averages, 1990–2025
source: np
confidence: derived
unit: share of wildcats; million Sm³ o.e. per discovery
notes: Success from Sodir's wellbore results (oil or gas proven; shows count as dry). Volumes are Sodir's gross resource growth for each year divided by new discoveries that year.
exception: { rule: log-scale, reason: "Volume per discovery spans more than an order of magnitude; a log axis keeps the last decade readable. Gridlines are labelled with real values." }
```
:::

::: step {beat=claim kicker="2000–2015"}
### More hits, then a giant

The 2000s pushed the hit rate up to {{ tech_2000s | pct }}, while each discovery shrank to
{{ vol_disc_2000s | volume }}. Then 2010 stands out: Johan Sverdrup
lifted the volume per discovery that year to {{ vol_2010_disc | volume }}. A drilling boom followed,
with up to {{ peak_wildcats }} wildcats completed in a year.

```chart
use: journey
upto: 2015
```
:::

::: step {beat=claim kicker="2016–2025"}
### Still about half

In the last decade {{ n_last }} wildcats were completed and {{ tech_last | pct }} of them found oil or
gas: {{ disc_last }} new discoveries. Sodir calls that high by international standards, and it has
held for twenty years.

```chart
use: journey
upto: 2025
highlight: [2016, 2025]
```
:::

## How the hit rate holds up

::: step {beat=evidence kicker="Where they drill"}
### Close to home

The wildcats of the last decade, in green where they found oil or gas. Almost all sit among the fields
that already produce.

```chart
id: map
type: custom
module: figures/map.js
data: [wells, fields, land, borders]
state: { colour: result }
title: Most of the last decade's wildcats were drilled next to existing fields
subtitle: Wildcats completed 2016–2025, with field outlines
source: sodir
confidence: observed
notes: Distance is to the nearest field whose development plan was approved before the well was spudded.
exception: { rule: north-up, reason: "Map rotated so the shelf runs up the panel; a north arrow marks the turn." }
```
:::

::: step {beat=evidence kicker="Near-field"}
### Within reach of a platform

{{ near_last | pct }} of those wildcats were drilled within {{ 25 | param }} km of a field already
approved for development, up from {{ near_1990s | pct }} in the 1990s. A find there can be tied back
to a platform that is already paid for.

```chart
use: map
colour: near
```
:::

::: step {beat=evidence kicker="Licences"}
### Mature acreage by design

{{ apa_last | pct }} were in licences from the APA rounds, the annual awards in mature areas around
existing infrastructure.

```chart
use: map
colour: apa
```
:::

::: step {beat=evidence kicker="Speed"}
### Quicker wells

Wells are faster too. The median wildcat since 2016 took {{ days_last | round:0 }} days to drill,
against {{ days_2006_15 | round:0 }} in the ten years before.

```chart
id: days
type: line
data: days
x: year
y: median_days
series: series
title: The median wildcat now takes about a month to drill
subtitle: Median drilling days per wildcat, by completion year
source: sodir
confidence: observed
unit: days
```
:::

## The twist

::: step {beat=twist kicker="Size"}
### Each find is smaller

The same path, with the last decade picked out. It has moved right and down: as many hits, much less
oil and gas in each. Since 2016 a new discovery has held {{ vol_disc_last | volume }} on average,
{{ vol_disc_fall | pct }} less than in the 1990s. Per wildcat drilled, that is
{{ vol_wc_last | volume }} against {{ vol_wc_1990s | volume }}.

```chart
id: journey2
type: custom
module: figures/connected.js
data: journey
state: { upto: 2025, highlight: [2016, 2025] }
title: Since 2016 each new discovery has held {{ vol_disc_fall | pct }} less than in the 1990s
subtitle: Technical success rate against volume per new discovery, three-year averages
source: np
confidence: derived
unit: share of wildcats; million Sm³ o.e. per discovery
notes: As above. Recent volumes are early estimates and tend to change as discoveries are appraised.
exception: { rule: log-scale, reason: "As in the first view of this figure." }
```
:::

::: step {beat=twist kicker="Outcome"}
### Fewer reach production

Of the discoveries made in the 2010s, {{ dev_2010s | pct }} are producing or approved,
{{ eval_2010s | pct }} are still being evaluated and {{ unlikely_2010s | pct }} are unlikely ever to
produce. For discoveries since 2020, {{ dev_2020s | pct }} are producing or approved so far and
{{ eval_2020s | pct }} are still under evaluation.

```chart
id: outcomes
type: stack
data: outcomes
x: period
y: share
series: outcome
colours: [data-seq-fjord-6, data-seq-fjord-4, data-seq-fjord-2, border, data-context]
title: Commercial success has fallen even as technical success held
subtitle: What became of every wildcat, by five-year period of completion, per cent
source: sodir
confidence: derived
unit: per cent of wildcats
notes: Commercial = the discovery is producing, has produced or is approved for production, directly or through the field it joined. Recent periods are incomplete by nature.
```
:::

::: step {beat=twist kicker="Time"}
### Slower, unless the platform is next door

Developed discoveries also take longer to come on stream. {{ p10_2010s | pct }} of discoveries made
from 2010 onwards were producing within ten years, against {{ p10_2000s | pct }} of those from the
2000s. The exception is new: {{ platform_2020s }} wildcats since 2020 were drilled from an existing
platform, and several produced almost at once.

```chart
id: lead
type: custom
module: figures/lead.js
data: lead
title: Most discoveries take years to produce; wildcats drilled from platforms produce at once
subtitle: Years from discovery to first production, for every discovery developed so far, by discovery year
source: sodir
confidence: derived
unit: years
notes: First production is the producing field's start, or the date the discovery was included in it if later. Discoveries that have not produced yet are not shown, so recent years show only the fast ones.
exception: { rule: sqrt-scale, reason: "Square-root axis spreads the many short lead times while keeping the 30-year ones in view." }
```
:::

## Where the North Sea still pays

The national averages hide a map. Cut every North Sea block into four equal quarters, ten minutes of
longitude by seven and a half of latitude, and each of the {{ ns_quarters }} quarters has its own record: how many wildcats, how often they
struck, how much they found. Across {{ ns_wells }} North Sea wildcats, one glyph per quarter and era: a ring for every wildcat drilled, and at
the centre a disc whose area is the volume discovered. Colour says how the quarter did: clay below
the North Sea's long-run hit rate of {{ ns_avg | pct }}, grey around it, blue above; pale for small
finds, deep for large ones.

::: step {beat=twist kicker="1966–1985" layout=wide}
### The frontier

The first twenty years were a lottery with huge prizes. Only {{ ns_rate_0 | pct }} of wildcats struck,
so clay rings dominate, but {{ ns_large_0 }} quarters held finds of more than {{ 50 | param }} million
Sm³ o.e. each: Troll, Statfjord, Ekofisk, Oseberg. Together that era found {{ ns_vol_0 | volume }}.

```chart
id: glyphs
export: true
type: custom
module: figures/glyphs.js
data: [quarters, land_ns, fields_ns, licences_ns]
register: outcrop
state: { era: 0 }
title: Big finds belong to the North Sea's first decades; the last ten years drilled more accurately and found little
subtitle: Wildcats by quarter-block and era; rings = wells, disc = volume found, colour = success and size
source: sodir
confidence: derived
unit: wells; million Sm³ o.e.
notes: Success is shrunk towards the North Sea average (three-well prior) so one well does not make an outlier. Volume is attributed to the well that made each discovery (field volumes to the founding discovery); discoveries rated production unlikely have no published volume and count as zero.
exception: { rule: direct-labels, reason: "Hundreds of glyphs: a bivariate legend, ring key and hover replace labels. Colour is bivariate (3 x 3, corners labelled); rings and disc area carry count and volume as well." }
```
:::

::: step {beat=twist kicker="1986–2005"}
### Filling in

The hit rate climbed and the glyphs gathered around the fields already found: Tampen, Oseberg,
Sleipner. Most discs turn pale. Only {{ ns_large_1 }} quarters held a large find, and the era found
{{ ns_vol_1 | volume }}.

```chart
use: glyphs
era: 1
```
:::

::: step {beat=twist kicker="2006–2015"}
### One giant in a mature basin

More of the same, with one exception that stands out on the whole map: the large blue disc on the Utsira
High is Johan Sverdrup.

```chart
use: glyphs
era: 2
```
:::

::: step {beat=twist kicker="2016–2025"}
### Busy, accurate, small

The hit rate has risen to {{ ns_rate_3 | pct }} and blue rings are now common: {{ ns_above_3 }} of the {{ ns_cells_3 }} quarters drilled beat the
average, and {{ ns_multi_3 }} were drilled three times or more. But every disc is pale. The best
quarter of the decade found {{ ns_top_last | volume }}; the whole North Sea found {{ ns_vol_3 | volume }}.

```chart
use: glyphs
era: 3
```
:::

::: step {beat=twist kicker="Licences today"}
### Inside today's licences

With the {{ ns_licences }} present-day licences drawn in, the pattern is plain: the last decade's
wildcats sit almost entirely inside acreage that is already licensed around producing fields.

```chart
use: glyphs
era: 3
lic: true
```
:::

## What the next decade looks like

The pattern is consistent. Norway keeps its hit rate by drilling where it knows the rocks and already
has the pipes, and that brings smaller finds. Small finds are worth developing mainly when a platform
is close and has spare capacity, and that capacity shrinks as fields age and shut down.

The coming decade will likely look the same: about half of wildcats finding something, most of it
small, and the best of it produced quickly through existing platforms while they last. A large new
find, as Johan Sverdrup was in 2010, remains possible but cannot be planned for. *Interpreted.*

::: appendix
### Definitions

- **Wildcat**: Sodir purpose *wildcat*, not a re-entry and not a CO₂ storage well. Counted in the year
  it was completed, as in Sodir's own series; 2026 is partial and only shown, never averaged.
- **Technical success**: the well proved oil or gas. Shows count as dry.
- **New discovery**: Sodir records the well as the discovery wellbore.
- **Commercial success**: the discovery is producing, has produced or is approved for production,
  directly or through the field or discovery it was later included in.
- **Near a field**: within {{ 25 | param }} km of the outline of a field whose development plan was
  approved before the well was spudded.
- **APA**: Awards in Predefined Areas, Norway's annual licensing in mature areas.
- **Drilled from a platform**: wellbore names with an installation slot code, such as the A in Brage's A-wells.
- **Volume per discovery**: Sodir's gross resource growth for the year divided by that year's new
  discoveries. These are today's estimates of what was found.

### Glossary

- **Sm³ o.e.**: standard cubic metres of oil equivalent; one is {{ 6.29 | param }} barrels of oil equivalent.
- **PDO**: plan for development and operation, the sanction step on the Norwegian shelf.
- **Tie-back**: a field produced through another field's platform or vessel.
:::
