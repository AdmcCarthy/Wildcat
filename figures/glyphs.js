// North Sea glyph map: one glyph per quarter-block (a Sodir block cut into four) and era.
//   rings  = exploration wellbores drilled there in the era (one ring each), coloured by success vs the North Sea average
//   centre = volume discovered (area), filled with a 3x3 bivariate colour:
//            across: technical success below / around / above the average (diverging, clay - grey - blue)
//            down:   volume per new discovery small / medium / large (pale -> deep)
// After Nadieh Bremer's rings-and-discs glyphs (Visual Cinnamon) and Joshua Stevens' bivariate guide.
// state: { era: 0..3, lic: true|false }
import { tok, tip, vol, pct, scheme, reducedMotion } from "./common.js";
import { paintCanvas } from "./relief.js";

const BIV = {  // [y][x]: y = volume class (0 small .. 2 large), x = success class (0 below .. 2 above)
  light: [["#f2be9c", "#babec2", "#9ad3f5"], ["#cb8a5d", "#8a9095", "#57a5d0"], ["#9c5313", "#585f64", "#00729f"]],
  dark: [["#663c1c", "#4f5356", "#134e6a"], ["#a46639", "#7e8489", "#2f80aa"], ["#e49b68", "#b4bcc1", "#61b9ea"]],
};
const ringCol = (x) => BIV[scheme()][1][x];

export default function create(el, { quarters: Q, relief_ns: R, fields_ns: FL, licences_ns: LIC }, opts = {}) {
  const S = Q.summary;
  el.innerHTML = "";
  const wrap = d3.select(el).append("div").attr("class", "wcg-wrap").classed("is-export", !!opts.export);
  const mapBox = wrap.append("div").attr("class", "wcg-map");
  const side = wrap.append("div").attr("class", "wcg-side");
  const head = side.append("div").attr("class", "wcg-head");
  const legEl = side.append("div").node();
  const legend = () => {
    const B = BIV[scheme()], avg = pct(S.avg), [v1, v2] = S.vol_breaks;
    const cell = (y, x) => `<i style="background:${B[y][x]}" title="${["Below", "Around", "Above"][x]} average, ${["small", "medium", "large"][y]} finds"></i>`;
    const rows = [[2, `large ≥ ${v2}`], [1, `medium ${v1}–${v2}`], [0, `small < ${v1}`]];
    const disc = (v) => { const r = geo ? Math.max(1.8, geo.rVol(v)) : 6; return `<svg width="${2 * r + 2}" height="${2 * r + 2}"><circle cx="${r + 1}" cy="${r + 1}" r="${r}" fill="none" stroke="currentColor" stroke-width=".8"/></svg>`; };
    legEl.innerHTML = `<div class="wcg-legend">
      <div class="wcg-bivt">
        <div class="wcg-ylab">Volume per discovery<br><span>million Sm³ o.e.</span></div>
        ${rows.map(([y, t]) => `<span class="wcg-rl">${t}</span>${[0, 1, 2].map((x) => cell(y, x)).join("")}`).join("")}
        <span></span><span class="wcg-cl">below</span><span class="wcg-cl">around</span><span class="wcg-cl">above</span>
        <div class="wcg-xlab">Technical success vs the ${avg} North Sea average</div>
      </div>
      <div class="wcg-compact"><span class="wcg-mini">${[2, 1, 0].map((y) => [0, 1, 2].map((x) => cell(y, x)).join("")).join("")}</span><span>↑ bigger finds per discovery<br>→ above the ${avg} average</span></div>
      <div class="wcg-keys">
        <div class="wcg-key"><svg width="116" height="40" aria-hidden="true">${[1, 3, 6].map((n, k) => `<g transform="translate(${16 + k * 42},18)">${Array.from({ length: n }, (_, i) => `<circle r="${3.5 + i * 2}" fill="none" stroke="currentColor" stroke-width=".8" opacity=".75"/>`).join("")}<text y="21" text-anchor="middle" font-size="10" fill="currentColor">${n}</text></g>`).join("")}</svg><span>Rings: exploration wellbores drilled</span></div>
        <div class="wcg-key wcg-discs">${[10, 100, 1000].map((v) => `<span class="wcg-d">${disc(v)}<small>${v.toLocaleString("en-GB")}</small></span>`).join("")}<span>Disc area: volume found, million Sm³ o.e.</span></div>
      </div>
      <p class="wcg-how">Each glyph is one quarter of a Sodir block in one era. No disc means no new discovery there; the ring colour still shows whether its wells beat the average.</p>
    </div>`;
  };
  // static base map (land, quarter grid, fields) and licence outlines are painted once to canvases;
  // era glyphs are SVG layers above them, so a step or a scroll never repaints the map
  const baseCv = mapBox.append("canvas").style("display", "block").node();
  const licCv = mapBox.append("canvas").style("position", "absolute").style("left", 0).style("top", 0)
    .style("transition", "opacity 450ms ease").style("pointer-events", "none").node();
  let W = 0, geo = null, cur = {};

  function build(width) {
    const narrow = width < 640, vh = window.innerHeight || 800;
    wrap.classed("is-narrow", narrow);
    // desktop: the map takes the full height left under the figure title; era line and legend sit beside it
    const fig = el.closest(".ss-figure"), above = fig ? el.getBoundingClientRect().top - fig.getBoundingClientRect().top : 0;
    const room = narrow || !fig ? Infinity : vh - 56 - above - 30;
    // phones: leave room below the pinned panel for the step text (about 330 px on a 740 px screen)
    let H = opts.export ? Math.round(opts.height()) : Math.round(narrow ? Math.max(130, Math.min(vh * 0.27, vh - 625)) : Math.max(420, Math.min(room, 920)));
    // the drilled North Sea: Ekofisk (56.3N) to Tampen (61.6N), west of the empty Skagerrak
    const frame = { type: "MultiPoint", coordinates: [[1.7, 56.25], [7.0, 56.25], [7.0, 61.9], [1.7, 61.9]] };
    const proj = d3.geoConicConformal().parallels([56, 62]).rotate([-5, 0]);
    const maxW = narrow ? width : Math.max(260, width - (opts.export ? 420 : 300));
    proj.fitHeight(H - 12, frame);
    let [[bx0], [bx1]] = d3.geoPath(proj).bounds(frame);
    if (bx1 - bx0 > maxW - 12) { proj.fitWidth(maxW - 12, frame); const b = d3.geoPath(proj).bounds(frame); H = Math.round(b[1][1] - b[0][1] + 12); [[bx0], [bx1]] = b; }
    const mapW = narrow ? width : Math.round(bx1 - bx0 + 12);
    proj.fitExtent([[6, 6], [mapW - 6, H - 6]], frame);
    width = mapW;
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    [baseCv, licCv].forEach((c) => { c.width = mapW * dpr; c.height = H * dpr; c.style.width = `${mapW}px`; c.style.height = `${H}px`; });
    const path = d3.geoPath(proj);
    // pixel size of one quarter, for glyph scaling
    const [ax, ay] = proj([5, 59]), [bx] = proj([5 + 1 / 6, 59]), [, cy] = proj([5, 59 + 1 / 8]);
    const cellW = Math.abs(bx - ax), cellH = Math.abs(cy - ay);
    const unit = Math.min(cellW, cellH);
    // glyphs may outgrow their 9 x 14 km quarter (as in Bremer's design); largest are drawn first
    const vmax = d3.max(Q.cells, (c) => c.vol) || 1, k = Math.max(0.55, Math.min(1.2, H / 760));
    return { W: width, H, narrow, proj, path, unit,
      rVol: d3.scaleSqrt([0, vmax], [0, 22 * k]).clamp(true),
      r0min: 3.2 * k, gap: Math.max(1.1, 2 * k), ring: Math.max(0.6, 0.9 * k) };
  }

  function base() {
    mapBox.selectAll("svg.wcg-era").remove();
    const dpr = baseCv.width / geo.W;
    const ctx = baseCv.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, geo.W, geo.H);
    const path = d3.geoPath(geo.proj, ctx);
    paintCanvas(ctx, R, path);
    ctx.beginPath();
    Q.grid.forEach(([a, b, c, e]) => { const p = [[a, b], [c, b], [c, e], [a, e]].map((q) => geo.proj(q)); ctx.moveTo(...p[0]); p.slice(1).forEach((q) => ctx.lineTo(...q)); ctx.closePath(); });
    ctx.strokeStyle = tok("grid"); ctx.lineWidth = 0.35; ctx.stroke();
    ctx.beginPath(); path(FL); ctx.globalAlpha = 0.1; ctx.fillStyle = tok("text-muted"); ctx.fill(); ctx.globalAlpha = 1;
    const lc = licCv.getContext("2d");
    lc.setTransform(dpr, 0, 0, dpr, 0, 0); lc.clearRect(0, 0, geo.W, geo.H);
    const lp = d3.geoPath(geo.proj, lc);
    lc.beginPath(); lp(LIC); lc.setLineDash([3, 2]); lc.strokeStyle = tok("text-muted"); lc.lineWidth = 0.8; lc.stroke();
    geo.groups = new Map();
  }

  // One group per era, drawn once (earlier eras' wells as faint dots, then this era's glyphs) and
  // prepared ahead in idle time; a step only fades between groups, so scrolling stays smooth.
  function eraGroup(e) {
    if (geo.groups.has(e)) return geo.groups.get(e);
    const B = BIV[scheme()], gap = geo.gap;
    // its own <svg> layered over the base map: fading an HTML element is compositor work, not a repaint
    const layer = mapBox.append("svg").attr("class", "wcg-era").attr("viewBox", [0, 0, geo.W, geo.H])
      .style("position", "absolute").style("left", 0).style("top", 0).style("width", `${geo.W}px`).style("height", `${geo.H}px`)
      .style("overflow", "hidden").style("opacity", 0).style("transition", "opacity 450ms ease").style("will-change", "opacity");
    const g = layer.append("g");
    const P = (c) => geo.proj([c.lon, c.lat]);
    let html = "";
    Q.cells.filter((c) => c.era < e).forEach((c) => { const [x, y] = P(c); html += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="1.2" fill="${tok("text-muted")}" opacity="0.35"/>`; });
    const size = (c) => (c.disc ? geo.rVol(c.vol) : 0) + c.wells * gap;
    const cells = Q.cells.filter((c) => c.era === e).sort((a, b) => size(b) - size(a));
    cells.forEach((c, i) => {
      const [x, y] = P(c), rv = c.disc > 0 ? Math.max(1.8, geo.rVol(c.vol)) : 0, r0 = Math.max(rv + gap * 0.7, geo.r0min);
      html += `<g transform="translate(${x.toFixed(1)},${y.toFixed(1)})" data-i="${i}">`;
      for (let k = 0; k < c.wells; k++) html += `<circle r="${(r0 + k * gap).toFixed(2)}" fill="none" stroke="${ringCol(c.x)}" stroke-width="${geo.ring}"/>`;
      if (rv) html += `<circle r="${rv.toFixed(2)}" fill="${B[Math.max(0, c.y)][c.x]}" stroke="${tok("surface")}" stroke-width="0.5"/>`;
      html += `<circle r="${Math.max(r0 + c.wells * gap, 7).toFixed(1)}" fill="transparent"/></g>`;
    });
    g.html(html);
    g.on("pointermove", (ev) => {
      const t = ev.target.closest("g[data-i]"); if (!t) return;
      const c = cells[+t.dataset.i], cls = ["below", "around", "above"][c.x];
      tip().show(`<b>Quarter ${c.q}</b> <span class="ss-k">${S.eras[c.era]}</span><br>${c.wells} exploration wellbore${c.wells > 1 ? "s" : ""}, ${c.hits} found oil or gas<br>
        <span class="ss-k">Success ${cls} the ${pct(S.avg)} average (adjusted ${pct(c.rate)})</span>
        ${c.disc ? `<br>${c.disc} new discover${c.disc > 1 ? "ies" : "y"}: ${vol(c.vol)}${c.names.length ? `<br><span class="ss-k">${c.names.join(", ")}</span>` : ""}` : "<br><span class='ss-k'>No new discovery</span>"}`, ev.clientX, ev.clientY);
    }).on("pointerleave", () => tip().hide());
    geo.groups.set(e, layer);
    return layer;
  }
  // Prepare the other eras only when the figure is within about a screen of view, and only in real idle
  // time: building a layer costs tens of ms on a slow phone and must not land while the reader scrolls
  // through earlier sections.
  let idleId = null, near = false;
  new IntersectionObserver(([en]) => { near = en.isIntersecting; if (near && geo) prepareAhead(); }, { rootMargin: "100% 0px" }).observe(el);
  function prepareAhead() {
    if (idleId || !near) return;
    const ric = window.requestIdleCallback ?? ((f) => setTimeout(() => f({ timeRemaining: () => 50 }), 120));
    const step = (dl) => {
      idleId = null;
      if (!near) return;
      const e = S.eras.map((_, k) => k).find((k) => !geo.groups.has(k));
      if (e == null) return;
      if (dl.timeRemaining() > 20) eraGroup(e);
      idleId = ric(step);
    };
    idleId = ric(step);
  }

  function draw(width, state = {}, { animate = false } = {}) {
    state = { era: S.eras.length - 1, lic: false, ...state };
    const rebuild = !geo || width !== W || geo.sch !== scheme();
    W = width;
    if (opts.legendEl) opts.legendEl.innerHTML = "";
    if (rebuild) { idleId = null; geo = build(width); geo.sch = scheme(); base(); legend(); }
    cur = state;
    const e = state.era, dur = animate && !reducedMotion() ? 500 : 0;
    head.html(geo.narrow ? `<b>${S.eras[e]}</b> <span>${S.era_wells[e]} exploration wellbores · ${pct(S.era_rate[e])} struck</span>`
      : `<b>${S.eras[e]}</b> <span>${S.era_wells[e]} exploration wellbores · ${pct(S.era_rate[e])} found oil or gas · ${vol(S.era_volume[e], 0)} discovered</span>`);
    licCv.style.transitionDuration = `${dur}ms`;
    licCv.style.opacity = state.lic ? 0.9 : 0.25;
    const show = eraGroup(e);
    geo.groups.forEach((g) => g.style("transition-duration", `${dur}ms`).style("opacity", g === show ? 1 : 0).style("pointer-events", g === show ? null : "none"));
    prepareAhead();
  }
  return { draw, repaint() { if (W) { geo = null; draw(W, cur); } } };
}

const CSS = `
.wcg-wrap{display:flex;gap:24px;align-items:flex-start}
.wcg-map{flex:none;position:relative}
.wcg-side{flex:1 1 auto;min-width:0;display:flex;flex-direction:column;gap:14px;padding-top:6px}
.wcg-wrap.is-narrow{flex-direction:column-reverse;gap:4px} .wcg-wrap.is-narrow .wcg-side{gap:4px;padding-top:0}
.wcg-head{font-size:13px;color:var(--ss-text);line-height:1.45} .wcg-head b{display:block;font:500 26px/1.1 var(--ss-font-display);margin-bottom:4px} .wcg-head span{color:var(--ss-text-muted)}
.wcg-wrap.is-narrow .wcg-head b{display:inline;font-size:15px;margin-right:6px}
.wcg-legend{display:flex;flex-direction:column;gap:14px;font-size:11px;color:var(--ss-text-muted)}
.wcg-wrap.is-narrow .wcg-legend{flex-direction:row;flex-wrap:wrap;gap:4px 12px}
.wcg-bivt{display:grid;grid-template-columns:auto repeat(3,40px);gap:3px;align-items:center;width:max-content}
.wcg-bivt i{width:40px;height:24px;border-radius:3px;display:block}
.wcg-ylab{grid-column:1/-1;font-size:11.5px;color:var(--ss-text);font-weight:600;margin-bottom:2px} .wcg-ylab span{font-weight:400;color:var(--ss-text-muted)}
.wcg-rl{font-size:10.5px;text-align:right;padding-right:6px;white-space:nowrap}
.wcg-cl{font-size:9.5px;text-align:center}
.wcg-xlab{grid-column:1/-1;font-size:11.5px;color:var(--ss-text);font-weight:600;margin-top:2px}
.wcg-keys{display:flex;flex-direction:column;gap:10px;color:var(--ss-text)}
.wcg-key{display:flex;align-items:center;justify-content:flex-start;gap:10px;font-size:11px} .wcg-key>svg,.wcg-d svg{flex:none;width:auto !important;height:auto !important} .wcg-key>span:last-child{color:var(--ss-text-muted);flex:0 1 auto}
.wcg-discs{flex-wrap:wrap} .wcg-d{display:inline-flex;flex-direction:column;align-items:center;gap:1px} .wcg-d small{font-size:9.5px;color:var(--ss-text-muted)}
.wcg-how{margin:0;font-size:11.5px;line-height:1.45;color:var(--ss-text-muted);max-width:30ch}
.wcg-compact{display:none}
.wcg-wrap.is-export{justify-content:center;gap:56px}
.wcg-wrap.is-export .wcg-side{flex:0 1 380px;gap:22px}
.wcg-wrap.is-export .wcg-head{font-size:17px} .wcg-wrap.is-export .wcg-head b{font-size:40px}
.wcg-wrap.is-export .wcg-legend{font-size:14px;gap:22px} .wcg-wrap.is-export .wcg-key{font-size:14px}
.wcg-wrap.is-export .wcg-bivt{grid-template-columns:auto repeat(3,56px);gap:4px} .wcg-wrap.is-export .wcg-bivt i{width:56px;height:34px}
.wcg-wrap.is-export .wcg-rl{font-size:13px} .wcg-wrap.is-export .wcg-cl{font-size:12px} .wcg-wrap.is-export .wcg-ylab,.wcg-wrap.is-export .wcg-xlab{font-size:14px}
.wcg-wrap.is-export .wcg-how{font-size:14px;max-width:34ch}
.wcg-wrap.is-narrow .wcg-how,.wcg-wrap.is-narrow .wcg-discs,.wcg-wrap.is-narrow .wcg-bivt{display:none}
.wcg-wrap.is-narrow .wcg-compact{display:flex;gap:8px;align-items:center;font-size:10.5px;line-height:1.3}
.wcg-mini{display:grid;grid-template-columns:repeat(3,12px);gap:1px} .wcg-mini i{width:12px;height:12px;border-radius:2px;display:block}
.wcg-wrap.is-narrow .wcg-keys{display:none}
.wcg-wrap.is-narrow .wcg-key>span{display:none}
`;
if (!document.getElementById("wcg-css")) { const s = document.createElement("style"); s.id = "wcg-css"; s.textContent = CSS; document.head.append(s); }
