// Usage: node make_expectation_gap_ranking.js
// Reads data/expectation-gap-scores.json (written by compute_expectation_gap_score.py),
// writes docs/00d_EXPECTATION_GAP_RANKING.docx.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle
} = require(path.join(__dirname, "..", "..", "research", "scripts", "node_modules", "docx"));

const data = JSON.parse(fs.readFileSync(__dirname + "/../data/expectation-gap-scores.json", "utf8"));
const COLORS = { accent: "1F4E5F", muted: "666666", hi: "1E7A34", mid: "8A6D00", lo: "999999", flag: "A32020" };

function h(text, level = HeadingLevel.HEADING_1, color) {
  return new Paragraph({
    children: [new TextRun({ text, bold: true, color: color || COLORS.accent, size: level === HeadingLevel.HEADING_1 ? 30 : 24 })],
    heading: level, spacing: { before: 320, after: 140 },
  });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function scoreColor(s) {
  if (s >= 55) return COLORS.hi;
  if (s >= 30) return COLORS.mid;
  return COLORS.lo;
}
function cell(txt, w, opts = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: opts.fill ? { type: ShadingType.CLEAR, fill: opts.fill } : undefined,
    children: [new Paragraph({ children: [new TextRun({
      text: String(txt == null ? "" : txt), bold: !!opts.bold, italics: !!opts.italics,
      color: opts.color, size: opts.size || 18,
    })] })],
  });
}
function table(headers, widths, rows, headFill) {
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((t, i) => cell(t, widths[i], { bold: true, fill: headFill || "E8E8E8" })) }),
      ...rows.map(r => new TableRow({ children: r.map((c, i) => (c && c.__cell) ? c.render(widths[i]) : cell(c, widths[i])) })),
    ],
  });
}
// tiny wrapper so a row cell can carry its own formatting
function fc(txt, opts) { return { __cell: true, render: (w) => cell(txt, w, opts || {}) }; }

const fmtGap = (r) => {
  const mag = (typeof r.gap_magnitude_pct === "number") ? ` ${r.gap_magnitude_pct > 0 ? "+" : ""}${r.gap_magnitude_pct}%` : "";
  return `${r.gap_direction || "-"} / ${r.gap_type || "-"}${mag}`;
};
const fmtCatalyst = (r) => {
  if (!r.catalyst_event) return "— none identified —";
  const w = (typeof r.catalyst_window_months === "number") ? `~${r.catalyst_window_months}M` : "?";
  const dated = r.catalyst_is_dated ? "dated" : "undated";
  const st = r.catalyst_status_effective && r.catalyst_status_effective !== "pending" ? `, ${r.catalyst_status_effective}` : "";
  return `${r.catalyst_event}  (${w}, ${dated}${st})`;
};
const fmtRisk = (r) => {
  if (!r.risk_open_spof_count) return "no single point of failure named";
  return `${r.risk_open_spof_count} open: ${(r.risk_open_spofs || []).join("; ")}`;
};

const children = [];

children.push(new Paragraph({
  children: [new TextRun({ text: "Expectation-Gap Ranking", bold: true, size: 44, color: COLORS.accent })],
  spacing: { after: 100 },
}));
children.push(new Paragraph({
  children: [new TextRun({
    text: `Compiled ${data.date_compiled} · ${data.scored_count} guidance-assessed, `
      + `${data.not_assessed_count} researched but not yet assessed`,
    italics: true, color: COLORS.muted, size: 20,
  })],
  spacing: { after: 200 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 8 } },
}));

children.push(new Paragraph({
  shading: { type: ShadingType.CLEAR, fill: "EDE7F6" },
  spacing: { after: 240 },
  children: [new TextRun({
    text: "Ranks the mispricing, not the business. expectation_gap_score (0-100) = "
      + "Gap x Evidence x Catalyst x Timing x Risk, per playbook/guidance-and-expectation-gap.md. "
      + "It is orthogonal to conviction_score (business quality + endorsement) — a portfolio add "
      + "should clear a bar on BOTH. The 'No current edge' section is the quality-name watchlist: "
      + "good businesses whose guidance is already in the price. Implied paths are reverse-P/E "
      + "estimates (no broker consensus) — directional, not precise.",
    size: 20,
  })],
}));

children.push(h("Ranked by expectation gap (highest opportunity first)"));
if ((data.ranked || []).length) {
  const widths = [1900, 850, 850, 2100, 3000, 2500, 2400];
  children.push(table(
    ["Stock", "Gap score", "Conv. score", "Gap (dir / type / mag)", "Catalyst", "Risk (open SPOF)", "Flags"],
    widths,
    data.ranked.map(r => [
      fc(r.name, { bold: true }),
      fc(r.expectation_gap_score, { bold: true, color: scoreColor(r.expectation_gap_score) }),
      fc(r.conviction_score == null ? "-" : String(r.conviction_score), { color: COLORS.muted }),
      fmtGap(r),
      fmtCatalyst(r),
      fmtRisk(r),
      fc((r.flags || []).join(", ") || "-", { italics: true, color: (r.flags || []).length ? COLORS.mid : COLORS.muted }),
    ]),
  ));
} else {
  children.push(p("No stocks have a populated market_expectation block yet — run deepdive-top100.", { italics: true, color: COLORS.muted }));
}

children.push(h("No current edge — quality-name watchlist", HeadingLevel.HEADING_1, COLORS.flag));
children.push(p(
  "Researched and guidance-assessed, but the gap is already priced in, the price is ahead of "
  + "our path (over-optimistic), the catalyst has lapsed, or a hard red flag zeroes it. Hold / "
  + "watch — do not add on this signal. Cross-check conviction_score before dismissing.",
  { italics: true, color: COLORS.muted }
));
if ((data.no_edge || []).length) {
  const widths = [2400, 1000, 2200, 2600, 3400];
  children.push(table(
    ["Stock", "Conv. score", "Gap direction", "Flags", "Why (gap type / catalyst)"],
    widths,
    data.no_edge.map(r => [
      fc(r.name, { bold: true }),
      fc(r.conviction_score == null ? "-" : String(r.conviction_score), { color: COLORS.muted }),
      r.gap_direction || "-",
      fc((r.flags || []).join(", ") || "-", { color: COLORS.flag }),
      `${r.gap_type || "-"} · ${r.catalyst_event || "no catalyst"}`,
    ]),
    "FCE8E8",
  ));
} else {
  children.push(p("None.", { italics: true, color: COLORS.muted }));
}

children.push(h("Not yet guidance-assessed"));
children.push(p(
  `${data.not_assessed_count} researched stocks have no market_expectation block yet — `
  + "deepdive-top100 populates these in rank order. Listed by conviction_score so the highest-"
  + "conviction gaps get assessed first.",
  { italics: true, color: COLORS.muted }
));
if ((data.not_assessed || []).length) {
  const widths = [3200, 1400, 2200, 2600];
  children.push(table(
    ["Stock", "Conv. score", "Conviction", "Thesis fit"],
    widths,
    data.not_assessed.slice(0, 120).map(r => [
      fc(r.name, { bold: true }),
      fc(r.conviction_score == null ? "-" : String(r.conviction_score), { color: COLORS.muted }),
      r.conviction || "-",
      fc(r.thesis_fit || "-", { italics: true, color: COLORS.muted }),
    ]),
  ));
  if (data.not_assessed.length > 120) {
    children.push(p(`… and ${data.not_assessed.length - 120} more.`, { italics: true, color: COLORS.muted }));
  }
}

children.push(new Paragraph({
  spacing: { before: 300 },
  border: { top: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 8 } },
  children: [new TextRun({
    text: "Independent research for informational purposes only, not investment advice. "
      + "expectation_gap_score is a mechanical ranking signal built on approximated market "
      + "expectations (reverse-P/E, no broker consensus) — it flags where to look, it does not "
      + "size positions. Do your own due diligence.",
    italics: true, size: 18, color: COLORS.muted,
  })],
}));

const doc = new Document({ sections: [{ properties: { page: { size: { width: 12240, height: 15840 } } }, children }] });
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(__dirname + "/../docs/00d_EXPECTATION_GAP_RANKING.docx", buf);
  console.log("Wrote expectation-gap ranking");
});
