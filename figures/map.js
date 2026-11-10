// Exploration wellbores completed 2016–2025 on a map rotated so the shelf runs along a wide panel (north to the left) or up a
// phone's (north arrow shows the turn).
// state: { colour: "result" | "near" | "apa" }
import { pal, tok, tip, scheme } from "./common.js";
import { paintSvg } from "./relief.js";

const ANGLE_WIDE = 108, ANGLE_NARROW = 18; // wide: the shelf runs along the panel (2 : 1); a phone keeps it running up
export default function create(el, { wells: WL, fields: FL, relief: R, land: LAND, borders: B }, opts = {}) {
  el.innerHTML = "";
  const svg = d3.select(el).append("svg").style("display", "block").style("width", "100%").style("overflow", "hidden");
  let W = 0, cur = {};
  const legend = (state) => {
    if (!opts.legendEl) return;
    const C = pal(), k = state.colour ?? "result";
    const items = k === "near" ? [[C.hit, "Within 25 km of a field"], [C.dry, "Farther away"]]
      : k === "apa" ? [[C.hit, "APA licence (mature areas)"], [C.dry, "Numbered licensing round"]]
      : [[C.hit, "Found oil or gas"], [C.dry, "Dry"]];
    opts.legendEl.innerHTML = `<div class="wc-legend">${items.map(([c, t]) => `<span><i style="background:${c}"></i>${t}</span>`).join("")}</div>`;
  };
  function draw(width, state = {}, { animate = false } = {}) {
    state = { colour: "result", ...state }; W = width; cur = state; legend(state);
    const C = pal(), vh = window.innerHeight || 800;
    const narrow = W < 560, ANGLE = narrow ? ANGLE_NARROW : ANGLE_WIDE;
    const H = Math.round(narrow ? Math.max(240, vh * 0.36) : Math.max(360, Math.min(W / 2, vh * (opts.vhShare ?? 0.66))));
    svg.attr("viewBox", [0, 0, W, H]).attr("role", "img").attr("aria-label", "Map of exploration wellbores completed 2016 to 2025");
    const frame = { type: "FeatureCollection", features: [...WL.features, { type: "Feature", geometry: { type: "MultiPoint", coordinates: [[3.0, 56.0], [8.0, 55.6], [10.6, 57.7]] } }] };
    const proj = d3.geoConicConformal().parallels([60, 72]).rotate([-12, 0]).angle(ANGLE).fitExtent([[10, 10], [W - 10, H - 10]], frame);
    const path = d3.geoPath(proj);
    if (!svg.select("g.base").node() || svg.attr("data-w") !== String(W) || svg.attr("data-s") !== scheme()) {
      svg.selectAll("*").remove(); svg.attr("data-w", W).attr("data-s", scheme());
      const base = svg.append("g").attr("class", "base");
      paintSvg(base, R, path, { width: W, height: H, land: LAND, seaCap: 500 });
      base.append("path").datum(B).attr("d", path).attr("fill", "none").attr("stroke", tok("text-muted")).attr("stroke-width", 0.7).attr("stroke-dasharray", "3 2");
      base.append("g").selectAll("path").data(FL.features).join("path").attr("d", path).attr("fill", tok("text-muted")).attr("fill-opacity", 0.18).attr("stroke", tok("text-muted")).attr("stroke-width", 0.5);
      svg.append("g").attr("class", "wells").selectAll("circle").data(WL.features).join("circle")
        .attr("cx", (f) => proj(f.geometry.coordinates)[0]).attr("cy", (f) => proj(f.geometry.coordinates)[1]).attr("r", 4).attr("stroke", tok("text-muted")).attr("stroke-width", 0.8)
        .on("pointermove", (ev, f) => { const p = f.properties; tip().show(`<b>${p.well}</b> <span class="ss-k">${p.year}</span><br>${p.technical ? "Found oil or gas" : "Dry"}${p.commercial_status ? ` · ${p.commercial_status === "developed" ? "developed or approved" : p.commercial_status === "evaluating" ? "being evaluated" : "development unlikely"}` : ""}<br><span class="ss-k">${p.dist == null ? "" : `${p.dist} km from the nearest field · `}${p.apa ? "APA licence" : "licensing round"}</span>`, ev.clientX, ev.clientY); })
        .on("pointerleave", () => tip().hide());
      const na = svg.append("g").attr("transform", `translate(${W - 24},28) rotate(${-ANGLE})`); // d3's angle turns the map counter-clockwise
      na.append("path").attr("d", "M0,-10 L4,6 L0,2 L-4,6 Z").attr("fill", tok("text-muted"));
      na.append("text").attr("class", "wc-note").attr("y", -13).attr("text-anchor", "middle").text("N");
    }
    const on = (f) => (state.colour === "near" ? f.properties.dist != null && f.properties.dist <= 25 : state.colour === "apa" ? f.properties.apa : f.properties.technical);
    svg.select("g.wells").selectAll("circle").transition().duration(animate ? 500 : 0).attr("fill", (f) => (on(f) ? C.hit : C.dry));
  }
  return { draw, repaint() { if (W) { svg.selectAll("*").remove(); draw(W, cur); } } };
}
