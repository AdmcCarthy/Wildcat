// Connected scatterplot: one point per year (three-year centred), technical success (x) against volume
// found per new discovery (y, log), joined in time order. After the d3 connected scatterplot example.
// state: { upto: year, highlight: [from, to] | null, emphasis: "x" | "y" | null }
import { pal, tok, tip, vol, pct, unit, reducedMotion } from "./common.js";

export default function create(el, { journey: J }, opts = {}) {
  el.innerHTML = "";
  const svg = d3.select(el).append("svg").style("display", "block").style("width", "100%");
  const P = J.points;
  let W = 0, cur = {};
  function draw(width, state = {}, { animate = false } = {}) {
    state = { upto: P.at(-1).year, highlight: null, emphasis: null, ...state };
    const prevUpto = cur.upto ?? (animate ? P[0].year : state.upto);
    W = width; cur = state;
    const narrow = W < 560, vh = window.innerHeight || 800;
    const H = opts.export ? Math.round(opts.height()) : Math.round(Math.max(narrow ? 240 : 320, Math.min(W * 0.72, vh * (narrow ? 0.36 : 0.62))));
    const m = { t: 22, r: narrow ? 14 : 30, b: 44, l: narrow ? 44 : 58 };
    svg.attr("viewBox", [0, 0, W, H]).attr("role", "img").attr("aria-label", "Connected scatterplot of technical success rate against volume per discovery, 1990 to 2025");
    svg.selectAll("*").remove();
    const C = pal(), f = unit().factor;
    const x = d3.scaleLinear([0.2, 0.75], [m.l, W - m.r]);
    const y = d3.scaleLog([0.8, 45], [H - m.b, m.t]);
    const g = svg.append("g");
    x.ticks(6).forEach((v) => {
      g.append("line").attr("x1", x(v)).attr("x2", x(v)).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", tok("grid"));
      g.append("text").attr("class", "wc-axis").attr("x", x(v)).attr("y", H - m.b + 16).attr("text-anchor", "middle").text(pct(v));
    });
    [1, 2, 5, 10, 20, 40].forEach((v) => {
      g.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(v)).attr("y2", y(v)).attr("stroke", tok("grid"));
      g.append("text").attr("class", "wc-axis").attr("x", m.l - 8).attr("y", y(v)).attr("dy", "0.35em").attr("text-anchor", "end").text(d3.format(",")(Math.round(v * f)));
    });
    g.append("text").attr("class", "wc-title").attr("x", W - m.r).attr("y", H - 6).attr("text-anchor", "end").text("Technical success rate: exploration wellbores that found oil or gas →");
    g.append("text").attr("class", "wc-title").attr("x", m.l - (narrow ? 36 : 50)).attr("y", m.t - 8).text(`↑ Volume per new discovery, million ${unit().short}${unit().short === "Sm³" ? " o.e." : ""} (log)`);
    if (!narrow) {
      g.append("text").attr("class", "wc-hint").attr("x", W - m.r - 4).attr("y", m.t + 14).attr("text-anchor", "end").text("big finds, often");
      g.append("text").attr("class", "wc-hint").attr("x", W - m.r - 4).attr("y", H - m.b - 8).attr("text-anchor", "end").text("small finds, often");
      g.append("text").attr("class", "wc-hint").attr("x", m.l + 6).attr("y", H - m.b - 8).text("small finds, rarely");
    }
    const hl = state.highlight, inHl = (yr) => hl && yr >= hl[0] && yr <= hl[1];
    const vis = P.filter((p) => p.year <= state.upto);
    const seg = svg.append("g").attr("fill", "none").attr("stroke-linecap", "round");
    vis.slice(1).forEach((p, i) => {
      const a = vis[i];
      const line = seg.append("line").attr("x1", x(a.x)).attr("y1", y(a.y)).attr("x2", x(p.x)).attr("y2", y(p.y))
        .attr("stroke", inHl(p.year) ? C.late : hl ? C.path : C.early).attr("stroke-width", inHl(p.year) ? 2.6 : 1.6).attr("opacity", hl && !inHl(p.year) ? 0.55 : 1);
      if (animate && !reducedMotion() && p.year > prevUpto) {
        const k = p.year - prevUpto;
        line.attr("x2", x(a.x)).attr("y2", y(a.y)).transition().delay((k - 1) * 90).duration(90).ease(d3.easeLinear).attr("x2", x(p.x)).attr("y2", y(p.y));
      }
    });
    const dots = svg.append("g").selectAll("circle").data(vis).join("circle")
      .attr("cx", (p) => x(p.x)).attr("cy", (p) => y(p.y)).attr("r", (p) => (inHl(p.year) ? 4.6 : 3.4))
      .attr("fill", (p) => (inHl(p.year) ? C.late : tok("surface"))).attr("stroke", (p) => (inHl(p.year) ? tok("surface") : hl ? C.path : C.early)).attr("stroke-width", 1.6);
    if (animate && !reducedMotion()) dots.filter((p) => p.year > prevUpto).attr("opacity", 0).transition().delay((p) => (p.year - prevUpto) * 90).duration(120).attr("opacity", 1);
    const lab = svg.append("g"), placed = [];
    [...vis].reverse().forEach((p) => {  // latest first, so the current year wins a collision
      const t = J.labels[String(p.year)] ?? (p.year === state.upto ? String(p.year) : null);
      if (!t || (narrow && t.length > 6 && p.year !== 2010)) return;
      const lx = x(p.x) + 8, ly = y(p.y) - 6, wdt = (narrow ? 4 : t.length) * 6.5;
      if (placed.some((q) => Math.abs(q[1] - ly) < 13 && lx < q[0] + q[2] && q[0] < lx + wdt)) return;
      placed.push([lx, ly, wdt]);
      lab.append("text").attr("class", "wc-year").attr("x", x(p.x) + 8).attr("y", y(p.y) - 6).text(narrow ? String(p.year) : t);
    });
    svg.append("g").selectAll("circle").data(vis).join("circle").attr("cx", (p) => x(p.x)).attr("cy", (p) => y(p.y)).attr("r", 12).attr("fill", "transparent")
      .on("pointermove", (ev, p) => tip().show(`<b>${p.year}</b> <span class="ss-k">(${p.year - 1}–${p.year + 1} average)</span><br>Technical success ${pct(p.x)}<br>Per new discovery ${vol(p.y)}<br><span class="ss-k">${p.wildcats} exploration wellbores a year</span>`, ev.clientX, ev.clientY))
      .on("pointerleave", () => tip().hide());
  }
  return { draw, repaint() { if (W) draw(W, cur); } };
}
