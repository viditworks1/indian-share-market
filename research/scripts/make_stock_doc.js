// Usage: node make_stock_doc.js <data.json> <output.docx>
// data.json shape: see bottom of file for an example.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle
} = require("docx");

const [,, dataPath, outPath] = process.argv;
const d = JSON.parse(fs.readFileSync(dataPath, "utf8"));

const COLORS = { accent: "1F4E5F", muted: "666666", bull: "1E7A34", bear: "A32020" };

function h(text, level = HeadingLevel.HEADING_1) {
  return new Paragraph({ text, heading: level, spacing: { before: 280, after: 120 } });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function bullet(text) {
  return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 60 } });
}
function kvTable(rows) {
  const colW = [3200, 5800];
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: colW,
    rows: rows.map(([k, v]) => new TableRow({
      children: [
        new TableCell({
          width: { size: colW[0], type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, fill: "F2F2F2" },
          children: [new Paragraph({ children: [new TextRun({ text: k, bold: true })] })],
        }),
        new TableCell({
          width: { size: colW[1], type: WidthType.DXA },
          children: [new Paragraph({ text: String(v) })],
        }),
      ],
    })),
  });
}

const children = [];

children.push(new Paragraph({
  children: [new TextRun({ text: d.name, bold: true, size: 44, color: COLORS.accent })],
  spacing: { after: 60 },
}));
children.push(new Paragraph({
  children: [new TextRun({ text: d.tagline || "", italics: true, color: COLORS.muted, size: 22 })],
  spacing: { after: 200 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 8 } },
}));

children.push(h("Business Overview"));
children.push(p(d.business_overview));

children.push(h("Source / Conviction Notes (from original sheet)"));
children.push(p(d.source_notes));

children.push(h("Fundamentals"));
if (d.fundamentals_table) children.push(kvTable(d.fundamentals_table));
if (d.fundamentals_narrative) { children.push(new Paragraph({ text: "", spacing: { after: 100 } })); children.push(p(d.fundamentals_narrative)); }

children.push(h("Technical Read (Weekly / Monthly)"));
children.push(p(d.technical_read));

children.push(h("ValuePickr + X Sentiment"));
children.push(p(d.sentiment_summary));

children.push(h("BSE Corporate Actions / Red Flags"));
children.push(p(d.bse_notes));

children.push(h("Bull Case"));
(d.bull_case || []).forEach(b => children.push(bullet(b)));

children.push(h("Bear Case / Key Risks"));
(d.bear_case || []).forEach(b => children.push(bullet(b)));

children.push(h("Market-Cap Tier"));
children.push(p(d.market_cap_tier, { bold: true }));

children.push(h("10x-in-2-3-Years Plausibility Verdict"));
children.push(p(d.verdict_headline, { bold: true, size: 24 }));
(d.verdict_reasoning || []).forEach(b => children.push(bullet(b)));

children.push(new Paragraph({
  spacing: { before: 300 },
  border: { top: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 8 } },
  children: [new TextRun({
    text: "This is independent research and analysis for informational purposes only, not personalized financial or investment advice. Past multi-bagger performance and forum/social sentiment are not indicators of future returns. Do your own due diligence before investing.",
    italics: true, size: 18, color: COLORS.muted,
  })],
}));

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 } } },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outPath, buf);
  console.log("Wrote", outPath);
});
