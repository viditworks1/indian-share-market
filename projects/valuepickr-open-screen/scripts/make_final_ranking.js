// Usage: node make_final_ranking.js
// Reads data/screen-ranking.json, writes docs/00_SCREEN_RANKING.docx
// Reuses the docx package installed for the original research project (read-only require).
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle
} = require(path.join(__dirname, "..", "..", "research", "scripts", "node_modules", "docx"));

const data = JSON.parse(fs.readFileSync(__dirname + "/../data/screen-ranking.json", "utf8"));
const COLORS = {
  accent: "1F4E5F", muted: "666666", tierA: "1E7A34", tierB: "8A6D00", tierC: "A35A00",
  avoid: "A32020", highCaution: "B8860B", exclude: "6B2020",
};

function h(text, level = HeadingLevel.HEADING_1, color) {
  return new Paragraph({ children: [new TextRun({ text, bold: true, color: color || COLORS.accent, size: level === HeadingLevel.HEADING_1 ? 30 : 26 })], heading: level, spacing: { before: 320, after: 140 } });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function rankItem(rank, name, tagline, rationale) {
  return new Paragraph({
    spacing: { after: 160 },
    children: [
      new TextRun({ text: `${rank}. ${name}`, bold: true, size: 24 }),
      new TextRun({ text: `  —  ${tagline}`, italics: true, color: COLORS.muted, size: 20 }),
      new TextRun({ text: `\n${rationale}`, size: 20, break: 1 }),
    ],
  });
}
function flagTable(rows, color) {
  const colW = [2600, 6400];
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: colW,
    rows: [
      new TableRow({ children: ["Name", "Reason"].map((t, i) => new TableCell({
        width: { size: colW[i], type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: "E8E8E8" },
        children: [new Paragraph({ children: [new TextRun({ text: t, bold: true })] })],
      })) }),
      ...rows.map(r => new TableRow({
        children: [r.name, r.reason].map((t, i) => new TableCell({
          width: { size: colW[i], type: WidthType.DXA },
          children: [new Paragraph({ children: [new TextRun({ text: String(t), color: i === 0 ? color : undefined, bold: i === 0 })] })],
        })),
      })),
    ],
  });
}

const children = [];

children.push(new Paragraph({ children: [new TextRun({ text: "ValuePickr Open Screen: Ranking", bold: true, size: 44, color: COLORS.accent })], spacing: { after: 100 } }));
children.push(new Paragraph({ children: [new TextRun({ text: `Updated ${data.date_compiled} · ${data.total_researched} stocks researched from the ongoing ValuePickr-wide screen (separate from, and does not modify, the original 108-stock docs/00_FINAL_RANKING.docx)`, italics: true, color: COLORS.muted, size: 20 })], spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 8 } } }));

children.push(new Paragraph({
  shading: { type: ShadingType.CLEAR, fill: "FFF4E5" },
  spacing: { after: 240 },
  children: [new TextRun({ text: "This is independent research and analysis for informational purposes only — it is NOT personalized financial or investment advice, and nothing here is a recommendation to buy, sell, or hold any security. Past multi-bagger performance, forum enthusiasm, and social-media conviction are not indicators of future returns. Market caps and financials were captured at research time and will have moved. Always do your own due diligence, verify current data, and consult a licensed advisor before investing.", bold: true, size: 20 })],
}));

children.push(h("Methodology"));
children.push(p(data.methodology_intro));
(data.scoring_dimensions || []).forEach(d => children.push(new Paragraph({ text: d, bullet: { level: 0 }, spacing: { after: 60 } })));
children.push(p(data.methodology_note));

children.push(h("Tier A — Highest Conviction Candidates", HeadingLevel.HEADING_1, COLORS.tierA));
children.push(p(data.tierA_intro, { italics: true, color: COLORS.muted }));
(data.tierA || []).forEach((s, i) => children.push(rankItem(i + 1, s.name, s.tagline, s.rationale)));

children.push(h("Tier B — Moderate Conviction, Watch Closely", HeadingLevel.HEADING_1, COLORS.tierB));
children.push(p(data.tierB_intro, { italics: true, color: COLORS.muted }));
(data.tierB || []).forEach((s, i) => children.push(rankItem(i + 1 + (data.tierA||[]).length, s.name, s.tagline, s.rationale)));

children.push(h("Tier C — Speculative / Low Conviction", HeadingLevel.HEADING_1, COLORS.tierC));
children.push(p(data.tierC_intro, { italics: true, color: COLORS.muted }));
(data.tierC || []).forEach((s, i) => children.push(rankItem(i + 1 + (data.tierA||[]).length + (data.tierB||[]).length, s.name, s.tagline, s.rationale)));

children.push(h("HIGH CAUTION — Promoter-Holding Collapse or Similar", HeadingLevel.HEADING_1, COLORS.highCaution));
children.push(p("Flagged, not silently dropped — a sharp, unexplained promoter-holding decline (the AVI Polymers pattern) or comparable red flag, weighed against any momentum.", { italics: true, color: COLORS.muted }));
children.push(flagTable(data.highCaution || [], COLORS.highCaution));

children.push(h("AVOID — Negative Net Worth / Going-Concern Doubts", HeadingLevel.HEADING_1, COLORS.avoid));
children.push(p("Financial distress serious enough (negative net worth, going-concern audit language — the JITF pattern) to disqualify regardless of any short-term price action.", { italics: true, color: COLORS.muted }));
children.push(flagTable(data.avoid || [], COLORS.avoid));

children.push(h("EXCLUDE — Active SEBI/Regulatory Action", HeadingLevel.HEADING_1, COLORS.exclude));
children.push(p("Confirmed active regulatory/SEBI action (the Darjeeling Industries pattern) — hard exclusion.", { italics: true, color: COLORS.muted }));
children.push(flagTable(data.exclude || [], COLORS.exclude));

children.push(h("Screened Out — Sound Fundamentals, Doesn't Fit the Return Bar", HeadingLevel.HEADING_1, COLORS.muted));
children.push(p(data.screenedOut_intro || "", { italics: true, color: COLORS.muted }));
children.push(flagTable(data.screenedOut || [], COLORS.muted));

children.push(new Paragraph({
  spacing: { before: 300 },
  border: { top: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 8 } },
  children: [new TextRun({
    text: "This is independent research and analysis for informational purposes only, not personalized financial or investment advice. Past multi-bagger performance and forum/social sentiment are not indicators of future returns. Do your own due diligence before investing.",
    italics: true, size: 18, color: COLORS.muted,
  })],
}));

const doc = new Document({ sections: [{ properties: { page: { size: { width: 12240, height: 15840 } } }, children }] });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(__dirname + "/../docs/00_SCREEN_RANKING.docx", buf); console.log("Wrote screen ranking"); });
