// Usage: node make_portfolio.js
// Reads data/portfolio.json, writes docs/00b_PORTFOLIO.docx
// Reuses the docx package installed for the original research project (read-only require).
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle
} = require(path.join(__dirname, "..", "..", "research", "scripts", "node_modules", "docx"));

const data = JSON.parse(fs.readFileSync(__dirname + "/../data/portfolio.json", "utf8"));
const COLORS = { accent: "1F4E5F", muted: "666666", high: "1E7A34", medhigh: "3D7A1E", med: "8A6D00" };

function h(text, level = HeadingLevel.HEADING_1, color) {
  return new Paragraph({ children: [new TextRun({ text, bold: true, color: color || COLORS.accent, size: level === HeadingLevel.HEADING_1 ? 30 : 26 })], heading: level, spacing: { before: 320, after: 140 } });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function convColor(level) {
  if (!level) return COLORS.med;
  if (level.startsWith("High")) return COLORS.high;
  if (level.startsWith("Medium-High")) return COLORS.medhigh;
  return COLORS.med;
}
function stockBlock(s, alloc) {
  const out = [];
  out.push(new Paragraph({
    spacing: { before: 240, after: 40 },
    children: [
      new TextRun({ text: s.name, bold: true, size: 26 }),
      new TextRun({ text: `  —  ${alloc.weight}% allocation  |  Conviction: ${alloc.conviction}`, bold: true, size: 20, color: convColor(alloc.conviction) }),
    ],
  }));
  out.push(new Paragraph({ children: [new TextRun({ text: s.tagline, italics: true, color: COLORS.muted, size: 20 })], spacing: { after: 100 } }));
  out.push(p(s.thesis));
  out.push(new Paragraph({ children: [new TextRun({ text: "Why this weight: ", bold: true, size: 20 }), new TextRun({ text: s.sizing_rationale, size: 20 })], spacing: { after: 100 } }));
  out.push(new Paragraph({ children: [new TextRun({ text: "Watch for (thesis-breakers): ", bold: true, size: 20, color: "A32020" }), new TextRun({ text: s.watch_for, size: 20 })], spacing: { after: 160 } }));
  return out;
}
function allocTable(rows) {
  const colW = [2600, 1400, 1400, 1200, 1200, 1200];
  const headers = ["Stock", "Weight", "Amount (Rs)", "Approx Price (Rs)", "Approx Shares", "Conviction"];
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
        children: [r.name, r.weight + "%", r.amount, r.price, r.shares, r.conviction].map((t, i) => new TableCell({
          width: { size: colW[i], type: WidthType.DXA },
          children: [new Paragraph({ children: [new TextRun({ text: String(t), size: 18 })] })],
        })),
      })),
    ],
  });
}

const children = [];

children.push(new Paragraph({ children: [new TextRun({ text: "ValuePickr Open Screen: Portfolio Allocation", bold: true, size: 44, color: COLORS.accent })], spacing: { after: 100 } }));
children.push(new Paragraph({ children: [new TextRun({ text: `Compiled ${data.date_compiled} — built from the ongoing ValuePickr-wide open screen (separate from the original 108-stock project's docs/00b_PORTFOLIO_Rs1L_Allocation.docx)`, italics: true, color: COLORS.muted, size: 20 })], spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 8 } } }));

children.push(new Paragraph({
  shading: { type: ShadingType.CLEAR, fill: "FFF4E5" },
  spacing: { after: 240 },
  children: [new TextRun({ text: "I am not a licensed financial advisor, and this is not personalized investment advice. This is an illustrative, research-based allocation model, built to be transparent about assumptions so you can judge and adjust it. Prices are approximate and dated - verify live prices before acting. Do your own due diligence and consider a licensed advisor before investing real money.", bold: true, size: 20 })],
}));

children.push(h("Thesis & Sizing Philosophy"));
children.push(p(data.philosophy));

children.push(h("Final Allocation"));
children.push(allocTable(data.allocation));
children.push(new Paragraph({ text: "", spacing: { after: 100 } }));
children.push(p(data.allocation_note, { italics: true, color: COLORS.muted, size: 20 }));

children.push(h("Per-Stock Detail"));
data.stocks.forEach(s => {
  const alloc = data.allocation.find(a => a.name === s.name || s.name.startsWith(a.name) || a.name.startsWith(s.name));
  stockBlock(s, alloc || { weight: "?", conviction: "Medium" }).forEach(el => children.push(el));
});

children.push(h("Risk Management"));
(data.risk_management || []).forEach(r => children.push(new Paragraph({ text: r, bullet: { level: 0 }, spacing: { after: 80 } })));

children.push(new Paragraph({
  spacing: { before: 300 },
  border: { top: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 8 } },
  children: [new TextRun({
    text: "This is independent research and analysis for informational purposes only, not personalized financial or investment advice. Do your own due diligence, verify all current prices and filings, and consult a licensed advisor before investing.",
    italics: true, size: 18, color: COLORS.muted,
  })],
}));

const doc = new Document({ sections: [{ properties: { page: { size: { width: 12240, height: 15840 } } }, children }] });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(__dirname + "/../docs/00b_PORTFOLIO.docx", buf); console.log("Wrote portfolio doc"); });
