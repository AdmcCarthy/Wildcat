// Wildcat figure helpers: palette (eucalyptus and clay, shared with Tulip), theme, units, tooltip, styles.
import { token, tooltip as ssTooltip, units, UNITS, onSchemeChange, reducedMotion } from "../runtime/js/subscout.js";

const PAL = {
  light: { path: "#9bb4b1", early: "#7ea6a3", late: "#b5786a", lateSoft: "#dfb7aa", dry: "#c9d1d6", hit: "#5f8f8b", accent: "#a5624f" },
  dark: { path: "#4f6b68", early: "#7ea6a3", late: "#e0a596", lateSoft: "#8a5f55", dry: "#3a4650", hit: "#8fbcb7", accent: "#eab3a4" },
};
export function scheme() {
  const a = document.documentElement.getAttribute("data-colour-scheme");
  if (a === "light" || a === "dark") return a;
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}
export const pal = () => PAL[scheme()];
export const tok = (n) => token(n);
export { onSchemeChange, reducedMotion };
export const unit = () => UNITS[units.get()];
export const fmt0 = d3.format(",.0f");
export const fmt1 = d3.format(",.1f");
export const pct = d3.format(".0%");
export const vol = (msm3, digits = 1) => { const u = unit(); return `${(digits ? fmt1 : fmt0)(msm3 * u.factor)} million ${u.short}${u.short === "Sm³" ? " o.e." : ""}`; };
let tipInst = null;
export const tip = () => (tipInst ??= ssTooltip());

const CSS = `
.wc-axis,.wc-note{font:400 11px var(--ss-font-body);fill:var(--ss-text-muted)}
.wc-title{font:600 12px var(--ss-font-body);fill:var(--ss-text)}
.wc-label{font:600 11.5px var(--ss-font-body);fill:var(--ss-text);paint-order:stroke;stroke:var(--ss-surface);stroke-width:3px;stroke-linejoin:round;pointer-events:none}
.wc-year{font:500 11px var(--ss-font-mono);fill:var(--ss-text);paint-order:stroke;stroke:var(--ss-surface);stroke-width:3px}
.wc-hint{font:italic 400 12.5px var(--ss-font-display);fill:var(--ss-text-muted)}
.wc-legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12px;margin:0 0 8px;color:var(--ss-text)}
.wc-legend i{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:5px;vertical-align:-1px}
`;
if (!document.getElementById("wc-css")) { const s = document.createElement("style"); s.id = "wc-css"; s.textContent = CSS; document.head.append(s); }
