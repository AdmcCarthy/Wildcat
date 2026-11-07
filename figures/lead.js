// Time from discovery to first production, for every discovery that has been developed.
// Wells drilled from an existing installation are marked. Recent years are shaded: many of their
// discoveries have not had time to come on stream, so the dots there are only the fast ones.
import { pal, tok, tip, fmt1 } from "./common.js";

export default function create(el, { lead: L }, opts = {}) {
  if (opts.legendEl) {
    const C = pal();
    opts.legendEl.innerHTML = `<div class="wc-legend"><span><i style="background:${C.early}"></i>Developed discovery</span><span><i style="background:${C.late}"></i>Wildcat drilled from an existing platform</span></div>`;
  }
  el.innerHTML = "";
  const svg = d3.select(el).append("svg").style("display", "block").style("width", "100%");
  let W = 0;
  function draw(width) {
    W = width;
    const C = pal(), narrow = W < 560;
    const H = Math.round(Math.max(300, Math.min(W * 0.55, 460))), m = { t: 30, r: 14, b: 32, l: 44 };
    svg.attr("viewBox", [0, 0, W, H]).attr("role", "img").attr("aria-label", "Years from discovery to first production against discovery year");
    svg.selectAll("*").remove();
    const x = d3.scaleLinear([1966, 2026], [m.l, W - m.r]);
    const y = d3.scaleSqrt([0, Math.max(36, d3.max(L.points, (p) => p.lead) * 1.04)], [H - m.b, m.t]);
    const g = svg.append("g");
    g.append("rect").attr("x", x(2016)).attr("width", x(2026) - x(2016)).attr("y", m.t).attr("height", H - m.b - m.t).attr("fill", tok("surface-raised"));
    g.append("text").attr("class", "wc-note").attr("x", x(2021)).attr("y", m.t + 12).attr("text-anchor", "middle").text(narrow ? "too recent" : "too recent to judge");
    [0, 1, 2, 5, 10, 20, 30, 40, 50].filter((v) => v <= y.domain()[1]).forEach((v) => {
      g.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(v)).attr("y2", y(v)).attr("stroke", tok("grid"));
      g.append("text").attr("class", "wc-axis").attr("x", m.l - 6).attr("y", y(v)).attr("dy", "0.35em").attr("text-anchor", "end").text(v);
    });
    d3.range(1970, 2030, 10).forEach((v) => g.append("text").attr("class", "wc-axis").attr("x", x(v)).attr("y", H - 10).attr("text-anchor", "middle").text(v));
    g.append("text").attr("class", "wc-title").attr("x", m.l - 36).attr("y", 12).text("↑ Years from discovery to first production");
    const pts = [...L.points].sort((a, b) => a.platform - b.platform);
    svg.append("g").selectAll("circle").data(pts).join("circle")
      .attr("cx", (p) => x(p.year + 0.5)).attr("cy", (p) => y(p.lead)).attr("r", (p) => (p.platform ? 4.6 : 3.4))
      .attr("fill", (p) => (p.platform ? C.late : C.early)).attr("fill-opacity", (p) => (p.platform ? 1 : 0.75)).attr("stroke", tok("surface")).attr("stroke-width", 1)
      .on("pointermove", (ev, p) => tip().show(`<b>${p.name}</b><br><span class="ss-k">Found ${p.year}${p.field ? ` · produced via ${p.field.split(" ").map((w) => w[0] + w.slice(1).toLowerCase()).join(" ")}` : ""}</span><br>${fmt1(p.lead)} years to first production${p.platform ? "<br><span class='ss-k'>Drilled from an existing platform</span>" : ""}`, ev.clientX, ev.clientY))
      .on("pointerleave", () => tip().hide());
  }
  return { draw, repaint() { if (W) draw(W); } };
}
