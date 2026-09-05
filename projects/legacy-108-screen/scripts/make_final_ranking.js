const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle
} = require("docx");

const data = JSON.parse(fs.readFileSync(__dirname + "/data/final-ranking.json", "utf8"));
const COLORS = { accent: "1F4E5F", muted: "666666", tierA: "1E7A34", tierB: "8A6D00", tierC: "A35A00", avoid: "A32020", userTier: "5B3A9E" };

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
function scenarioTable(rows) {
  const colW = [2600, 3200, 3200];
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: colW,
    rows: [
      new TableRow({ children: ["", "Average Case", "Best Case"].map((t, i) => new TableCell({
        width: { size: colW[i], type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: "EDE7F6" },
        children: [new Paragraph({ children: [new TextRun({ text: t, bold: true })] })],
      })) }),
      ...rows.map(r => new TableRow({
        children: [r.label, r.avg, r.best].map((t, i) => new TableCell({
          width: { size: colW[i], type: WidthType.DXA },
          children: [new Paragraph({ children: [new TextRun({ text: String(t), bold: i === 0 })] })],
        })),
      })),
    ],
  });
}
function exclTable(rows) {
  const colW = [3200, 1600, 4200];
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: colW,
    rows: [
      new TableRow({ children: ["Name", "Market Cap", "Reason"].map((t, i) => new TableCell({
        width: { size: colW[i], type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: "E8E8E8" },
        children: [new Paragraph({ children: [new TextRun({ text: t, bold: true })] })],
      })) }),
      ...rows.map(r => new TableRow({
        children: [r.name, r.cap, r.reason].map((t, i) => new TableCell({
          width: { size: colW[i], type: WidthType.DXA },
          children: [new Paragraph({ text: String(t), })],
        })),
      })),
    ],
  });
}

const children = [];

children.push(new Paragraph({ children: [new TextRun({ text: "Microcap/Midcap 10x-in-2-3-Years Research: Final Ranking", bold: true, size: 44, color: COLORS.accent })], spacing: { after: 100 } }));
children.push(new Paragraph({ children: [new TextRun({ text: `Compiled ${data.date_compiled} · ${data.total_researched} stocks researched from the source sheet`, italics: true, color: COLORS.muted, size: 20 })], spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 8 } } }));

children.push(new Paragraph({
  shading: { type: ShadingType.CLEAR, fill: "FFF4E5" },
  spacing: { after: 240 },
  children: [new TextRun({ text: "This is independent research and analysis for informational purposes only — it is NOT personalized financial or investment advice, and nothing here is a recommendation to buy, sell, or hold any security. Past multi-bagger performance, forum enthusiasm, and social-media conviction are not indicators of future returns. Market caps and financials were captured at research time (Aug 2026) and will have moved. Several names carry serious, independently-corroborated red flags (financial distress, active regulatory action) — these are flagged explicitly, not silently omitted. Always do your own due diligence, verify current data, and consult a licensed advisor before investing.", bold: true, size: 20 })],
}));

children.push(h("Methodology"));
children.push(p(data.methodology_intro));
data.scoring_dimensions.forEach(d => children.push(new Paragraph({ text: d, bullet: { level: 0 }, spacing: { after: 60 } })));
children.push(p(data.methodology_note));

if (data.userHoldings && data.userHoldings.length) {
  children.push(h("User-Requested Holdings (Outside the Screen)", HeadingLevel.HEADING_1, COLORS.userTier));
  children.push(p(data.userHoldings_intro, { italics: true, color: COLORS.muted }));
  data.userHoldings.forEach(s => {
    children.push(new Paragraph({ children: [new TextRun({ text: s.name, bold: true, size: 26, color: COLORS.userTier })], spacing: { before: 200, after: 40 } }));
    children.push(new Paragraph({ children: [new TextRun({ text: s.tagline, italics: true, color: COLORS.muted, size: 20 })], spacing: { after: 120 } }));
    children.push(p(s.summary));
    if (s.scenario_rows) {
      children.push(scenarioTable(s.scenario_rows));
      children.push(new Paragraph({ text: "", spacing: { after: 120 } }));
    }
    children.push(p(s.conclusion));
  });
}

children.push(h("Tier A — Highest Conviction Candidates", HeadingLevel.HEADING_1, COLORS.tierA));
children.push(p(data.tierA_intro, { italics: true, color: COLORS.muted }));
data.tierA.forEach((s, i) => children.push(rankItem(i + 1, s.name, s.tagline, s.rationale)));

children.push(h("Tier B — Moderate Conviction, Watch Closely", HeadingLevel.HEADING_1, COLORS.tierB));
children.push(p(data.tierB_intro, { italics: true, color: COLORS.muted }));
data.tierB.forEach((s, i) => children.push(rankItem(i + 1 + data.tierA.length, s.name, s.tagline, s.rationale)));

children.push(h("Tier C — Speculative / Low Conviction", HeadingLevel.HEADING_1, COLORS.tierC));
children.push(p(data.tierC_intro, { italics: true, color: COLORS.muted }));
data.tierC.forEach((s, i) => children.push(rankItem(i + 1 + data.tierA.length + data.tierB.length, s.name, s.tagline, s.rationale)));

children.push(h("AVOID — Serious Red Flags", HeadingLevel.HEADING_1, COLORS.avoid));
children.push(p(data.avoid_intro, { italics: true, color: COLORS.muted }));
data.avoid.forEach(s => children.push(new Paragraph({
  spacing: { after: 140 },
  children: [
    new TextRun({ text: `${s.name}`, bold: true, size: 22, color: COLORS.avoid }),
    new TextRun({ text: `  —  ${s.reason}`, size: 20 }),
  ],
})));

children.push(h("Watch but Excluded from Ranking"));
children.push(p(data.excluded_intro));
children.push(h("Too large (already midcap/large-cap/mega-cap)", HeadingLevel.HEADING_2));
children.push(exclTable(data.excluded_large));
children.push(new Paragraph({ text: "", spacing: { after: 160 } }));
children.push(h("Other exclusions (foreign, special-situation, unverifiable, confirmed fraud)", HeadingLevel.HEADING_2));
children.push(exclTable(data.excluded_other));

children.push(new Paragraph({
  spacing: { before: 300 },
  border: { top: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 8 } },
  children: [new TextRun({
    text: "This is independent research and analysis for informational purposes only, not personalized financial or investment advice. Past multi-bagger performance and forum/social sentiment are not indicators of future returns. Do your own due diligence before investing.",
    italics: true, size: 18, color: COLORS.muted,
  })],
}));

const doc = new Document({ sections: [{ properties: { page: { size: { width: 12240, height: 15840 } } }, children }] });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(__dirname + "/../../../portfolio/00_FINAL_RANKING.docx", buf); console.log("Wrote final ranking"); });
