// Usage: node make_max_returns_ranking.js
// Reads data/max-returns-ranking.json, writes docs/00c_MAX_RETURNS_RANKING.docx
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle
} = require(path.join(__dirname, "..", "..", "legacy-108-screen", "scripts", "node_modules", "docx"));

const data = JSON.parse(fs.readFileSync(__dirname + "/../data/max-returns-ranking.json", "utf8"));
const COLORS = { accent: "1F4E5F", muted: "666666", high: "1E7A34", medhigh: "3D7A1E", med: "8A6D00", low: "999999", flagged: "A32020" };

function h(text, level = HeadingLevel.HEADING_1, color) {
  return new Paragraph({ children: [new TextRun({ text, bold: true, color: color || COLORS.accent, size: level === HeadingLevel.HEADING_1 ? 30 : 26 })], heading: level, spacing: { before: 320, after: 140 } });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function convColor(c) {
  if (c === "High") return COLORS.high;
  if (c === "Medium-High") return COLORS.medhigh;
  if (c === "Medium") return COLORS.med;
  return COLORS.low;
}
function rankedTable(rows) {
  const colW = [2400, 1400, 1800, 1600, 1800];
  const headers = ["Stock", "Conviction", "Thesis fit (info only)", "Size", "Why"];
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: colW,
    rows: [
      new TableRow({ children: headers.map((t, i) => new TableCell({
        width: { size: colW[i], type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: "E8E8E8" },
        children: [new Paragraph({ children: [new TextRun({ text: t, bold: true, size: 18 })] })],
      })) }),
      ...rows.map(r => new TableRow({
        children: [
          new TableCell({ width: { size: colW[0], type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: r.name, size: 18, bold: true })] })] }),
          new TableCell({ width: { size: colW[1], type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: r.conviction, size: 18, color: convColor(r.conviction), bold: true })] })] }),
          new TableCell({ width: { size: colW[2], type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: r.thesis_fit || "-", size: 18, italics: true, color: COLORS.muted })] })] }),
          new TableCell({ width: { size: colW[3], type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: r.market_cap_tier || "-", size: 18 })] })] }),
          new TableCell({ width: { size: colW[4], type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: r.reason || "", size: 18 })] })] }),
        ],
      })),
    ],
  });
}
function flaggedTable(rows) {
  const colW = [2600, 1800, 4600];
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: colW,
    rows: [
      new TableRow({ children: ["Stock", "Red flag", "Reason"].map((t, i) => new TableCell({
        width: { size: colW[i], type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: "FCE8E8" },
        children: [new Paragraph({ children: [new TextRun({ text: t, bold: true, size: 18 })] })],
      })) }),
      ...rows.map(r => new TableRow({
        children: [r.name, r.red_flag_tier, r.reason].map((t, i) => new TableCell({
          width: { size: colW[i], type: WidthType.DXA },
          children: [new Paragraph({ children: [new TextRun({ text: String(t || ""), size: 18, bold: i < 2, color: i < 2 ? COLORS.flagged : undefined })] })],
        })),
      })),
    ],
  });
}

const children = [];

children.push(new Paragraph({ children: [new TextRun({ text: "Max Returns Ranking (No Thesis Filter)", bold: true, size: 44, color: COLORS.accent })], spacing: { after: 100 } }));
children.push(new Paragraph({ children: [new TextRun({ text: `Compiled ${data.date_compiled} · ${data.total_researched} researched stocks, ranked by conviction alone`, italics: true, color: COLORS.muted, size: 20 })], spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 8 } } }));

children.push(new Paragraph({
  shading: { type: ShadingType.CLEAR, fill: "EDE7F6" },
  spacing: { after: 240 },
  children: [new TextRun({ text: data.intro, size: 20 })],
}));

children.push(h("Ranked by Conviction (no return-magnitude gate applied)"));
children.push(rankedTable(data.ranked || []));

children.push(h("Kept Separate — Red-Flagged", HeadingLevel.HEADING_1, COLORS.flagged));
children.push(p(data.flagged_intro || "", { italics: true, color: COLORS.muted }));
children.push(flaggedTable(data.flagged || []));

children.push(new Paragraph({
  spacing: { before: 300 },
  border: { top: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 8 } },
  children: [new TextRun({
    text: "This is independent research and analysis for informational purposes only, not personalized financial or investment advice. This document deliberately omits the main screen's 10x/100x return-magnitude filter - conviction here reflects business/fundamental quality, not a promise of any specific return. Do your own due diligence before investing.",
    italics: true, size: 18, color: COLORS.muted,
  })],
}));

const doc = new Document({ sections: [{ properties: { page: { size: { width: 12240, height: 15840 } } }, children }] });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(__dirname + "/../docs/00c_MAX_RETURNS_RANKING.docx", buf); console.log("Wrote max-returns ranking"); });
