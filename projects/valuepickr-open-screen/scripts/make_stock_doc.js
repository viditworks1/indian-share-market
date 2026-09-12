// Usage: node make_stock_doc.js <data.json> <output.docx>
// Reuses the docx package installed for the original research project (read-only require).
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle
} = require(path.join(__dirname, "..", "..", "legacy-108-screen", "scripts", "node_modules", "docx"));

const [,, dataPath, outPath] = process.argv;
const d = JSON.parse(fs.readFileSync(dataPath, "utf8"));

const COLORS = {
  accent: "1F4E5F", muted: "666666", bull: "1E7A34", bear: "A32020",
  avoid: "A32020", highCaution: "B8860B", exclude: "6B2020",
};

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
function redFlagColor(tier) {
  if (tier === "AVOID") return COLORS.avoid;
  if (tier === "EXCLUDE") return COLORS.exclude;
  if (tier === "HIGH CAUTION") return COLORS.highCaution;
  return COLORS.bull;
}
function dataTable(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const mkCell = (txt, w, opts = {}) => new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: opts.head ? { type: ShadingType.CLEAR, fill: "F2F2F2" } : undefined,
    children: [new Paragraph({ children: [new TextRun({ text: String(txt == null ? "" : txt), bold: !!opts.head, size: 18 })] })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((hd, i) => mkCell(hd, widths[i], { head: true })) }),
      ...rows.map(r => new TableRow({ children: r.map((c, i) => mkCell(c, widths[i])) })),
    ],
  });
}
const STAGE_ORDINAL = { expectation: 1, action: 2, operational: 3, commercial: 4, financial: 5 };

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

if (d.red_flag_tier) {
  children.push(new Paragraph({
    shading: { type: ShadingType.CLEAR, fill: "FFF0F0" },
    spacing: { after: 200 },
    children: [
      new TextRun({ text: `RED FLAG TIER: ${d.red_flag_tier} — `, bold: true, size: 22, color: redFlagColor(d.red_flag_tier) }),
      new TextRun({ text: d.red_flag_reason || "", size: 20 }),
    ],
  }));
}

children.push(h("Business Overview"));
children.push(p(d.business_overview));

children.push(h("Fundamentals"));
if (d.fundamentals_table) children.push(kvTable(d.fundamentals_table));
if (d.fundamentals_narrative) { children.push(new Paragraph({ text: "", spacing: { after: 100 } })); children.push(p(d.fundamentals_narrative)); }

if (d.shareholding_pattern) {
  const sh = d.shareholding_pattern;
  children.push(h("Shareholding Pattern", HeadingLevel.HEADING_2));
  children.push(kvTable([
    ["As of", sh.as_of || "—"],
    ["Promoter", sh.promoter_pct != null ? `${sh.promoter_pct}% (${sh.promoter_trend || "unclear"})` : "—"],
    ["Pledge", sh.pledge_pct != null ? `${sh.pledge_pct}% of promoter holding (${sh.pledge_trend || "unclear"})` : "—"],
    ["FII", sh.fii_pct != null ? `${sh.fii_pct}% (${sh.fii_trend || "unclear"})` : "—"],
    ["DII", sh.dii_pct != null ? `${sh.dii_pct}% (${sh.dii_trend || "unclear"})` : "—"],
    ["Public", sh.public_pct != null ? `${sh.public_pct}%` : "—"],
  ]));
  if (sh.concurrent_red_flag) {
    children.push(p("RED FLAG: pledge rising while promoter holding is decreasing in the same window.",
      { bold: true, size: 20, color: COLORS.bear }));
  }
  if (sh.note) children.push(p(sh.note, { size: 18, color: COLORS.muted }));
}

if (d.working_capital) {
  const wc = d.working_capital;
  children.push(h("Working Capital", HeadingLevel.HEADING_2));
  children.push(kvTable([
    ["As of", wc.as_of || "—"],
    ["Inventory / receivable / payable days", [wc.inventory_days, wc.receivable_days, wc.payable_days]
      .map(v => v != null ? v : "—").join(" / ")],
    ["Cash conversion cycle", wc.cash_conversion_cycle_days != null ? `${wc.cash_conversion_cycle_days} days` : "—"],
    ["Trend", wc.nwc_trend || "—"],
    ["Intensity vs sector", wc.working_capital_intensity || "—"],
  ]));
  if (wc.note) children.push(p(wc.note, { size: 18, color: COLORS.muted }));
}

if (d.sector_kpis && d.sector_kpis.kpis && d.sector_kpis.kpis.length) {
  const sk = d.sector_kpis;
  children.push(h(`Sector KPIs${sk.sector_label ? " — " + sk.sector_label : ""}`, HeadingLevel.HEADING_2));
  children.push(dataTable(
    ["Metric", "Value", "Trend", "Peer comparison"],
    sk.kpis.map(k => [k.metric, k.value, k.trend || "—", k.peer_comparison || "—"]),
    [2000, 1600, 1400, 4000]
  ));
  if (sk.note) children.push(p(sk.note, { size: 18, color: COLORS.muted }));
}

if (d.scenario_analysis && (d.scenario_analysis.bear || d.scenario_analysis.base || d.scenario_analysis.bull)) {
  const sa = d.scenario_analysis;
  children.push(h("Scenario Analysis", HeadingLevel.HEADING_2));
  children.push(p(`As of ${sa.as_of || "—"}`, { italics: true, color: COLORS.muted, size: 18 }));
  const scRows = ["bear", "base", "bull"]
    .filter(k => sa[k])
    .map(k => [
      k[0].toUpperCase() + k.slice(1),
      sa[k].revenue_cagr_fy26_28_pct != null ? `${sa[k].revenue_cagr_fy26_28_pct}%` : "—",
      sa[k].fy28_margin_pct != null ? `${sa[k].fy28_margin_pct}%` : "—",
      sa[k].fy28_eps != null ? sa[k].fy28_eps : "—",
      sa[k].exit_multiple != null ? `${sa[k].exit_multiple}x` : "—",
      sa[k].implied_price != null ? `Rs ${sa[k].implied_price}` : "—",
      sa[k].vs_cmp_pct != null ? `${sa[k].vs_cmp_pct > 0 ? "+" : ""}${sa[k].vs_cmp_pct}%` : "—",
    ]);
  children.push(dataTable(
    ["Scenario", "Rev CAGR FY26-28", "FY28 margin", "FY28 EPS", "Exit multiple", "Implied price", "vs CMP"],
    scRows,
    [1000, 1400, 1200, 1000, 1200, 1300, 900]
  ));
  ["bear", "base", "bull"].forEach(k => {
    if (sa[k] && sa[k].key_assumption) {
      children.push(p(`${k[0].toUpperCase() + k.slice(1)}: ${sa[k].key_assumption}`, { size: 18, color: COLORS.muted }));
    }
  });
  if (sa.note) children.push(p(sa.note, { size: 18, color: COLORS.muted }));
}

if (d.deep_dive) {
  const dd = d.deep_dive;
  children.push(h("Deep-Dive: Primary Documents (Annual Reports, Quarterly Results, Exchange Filings)"));
  children.push(p(
    `Pass ${dd.pass || 1}${dd.date ? " — " + dd.date : ""}. `
    + "Built from the company's own filings (3 years of annual reports, ~4 quarters of "
    + "results/concalls, and 6 months of BSE/NSE announcements), read via the web — a "
    + "deeper layer than the forum-sentiment read below.",
    { italics: true, color: COLORS.muted, size: 18 }
  ));
  if (dd.sources_reviewed && dd.sources_reviewed.length) {
    children.push(p("Sources reviewed this pass:", { bold: true, size: 20 }));
    dd.sources_reviewed.forEach(s => children.push(bullet(s)));
  }
  const ddSection = (title, arr) => {
    if (!arr || !arr.length) return;
    children.push(p(title, { bold: true, size: 20 }));
    arr.forEach(x => children.push(bullet(x)));
  };
  ddSection("Annual-report findings (3-year view):", dd.annual_report_findings);
  ddSection("Quarterly trend (last ~4 quarters + concall commentary):", dd.quarterly_trend);
  ddSection("Exchange announcements (last 6 months):", dd.recent_announcements);
  ddSection("Key new facts vs. the prior write-up:", dd.key_new_facts);
  ddSection("Open questions / what to watch:", dd.open_questions);
  if (dd.conviction_update) {
    children.push(new Paragraph({
      spacing: { before: 120, after: 120 },
      children: [
        new TextRun({ text: "Conviction impact: ", bold: true, size: 20 }),
        new TextRun({ text: dd.conviction_update, size: 20 }),
      ],
    }));
  }
  if (dd.history && dd.history.length) {
    children.push(p("Earlier deep-dive passes:", { bold: true, size: 18, color: COLORS.muted }));
    dd.history.forEach(hst => children.push(p(
      `Pass ${hst.pass} (${hst.date}): ${hst.summary}`,
      { size: 18, color: COLORS.muted }
    )));
  }
}

if ((d.commitments && d.commitments.length) || d.earnings_chain || d.market_expectation || d.catalyst) {
  children.push(h("Guidance & Expectation Gap"));
  children.push(p(
    "Management guidance decoded into commitments, graded on the "
    + "expectation → action → operational → commercial → financial ladder, then compared "
    + "to what the current price appears to assume. Method: playbook/guidance-and-expectation-gap.md.",
    { italics: true, color: COLORS.muted, size: 18 }
  ));

  if (d.commitments && d.commitments.length) {
    children.push(p("Commitment ladder (most-proven first):", { bold: true, size: 20 }));
    const sorted = d.commitments.slice().sort((a, b) => {
      if (!!b.thesis_critical - !!a.thesis_critical) return !!b.thesis_critical - !!a.thesis_critical;
      return (STAGE_ORDINAL[b.quality_stage] || 0) - (STAGE_ORDINAL[a.quality_stage] || 0);
    });
    children.push(dataTable(
      ["Area", "Commitment", "Specifics", "By when", "Stage", "Thesis-critical"],
      sorted.map(c => [
        c.area, c.text, c.specifics || "—", c.timeline_bucket || "—",
        c.quality_stage || "—", c.thesis_critical ? "yes" : "",
      ]),
      [1100, 2600, 2400, 900, 1200, 800]
    ));
  }

  if (d.earnings_chain && d.earnings_chain.chain && d.earnings_chain.chain.length) {
    const ec = d.earnings_chain;
    children.push(new Paragraph({
      spacing: { before: 120, after: 60 },
      children: [
        new TextRun({ text: "Earnings chain: ", bold: true, size: 20 }),
        ...ec.chain.flatMap((link, i) => {
          const isBottleneck = link === ec.bottleneck_link;
          const runs = [new TextRun({ text: link, size: 20, bold: isBottleneck,
            color: isBottleneck ? COLORS.bear : undefined })];
          if (i < ec.chain.length - 1) runs.push(new TextRun({ text: " → ", size: 20, color: COLORS.muted }));
          return runs;
        }),
      ],
    }));
    if (ec.bottleneck_link) children.push(p(`Bottleneck link: ${ec.bottleneck_link}.`, { size: 18, color: COLORS.muted }));
    if (ec.operating_leverage) children.push(p(`Operating leverage: ${ec.operating_leverage}`, { size: 18, color: COLORS.muted }));
    if ((ec.evidenced_links && ec.evidenced_links.length) || (ec.assumed_links && ec.assumed_links.length)) {
      children.push(p(
        `Evidenced: ${(ec.evidenced_links || []).join("; ") || "none"}. `
        + `Still assumed: ${(ec.assumed_links || []).join("; ") || "none"}.`,
        { size: 18, color: COLORS.muted }
      ));
    }
  }

  if (d.market_expectation) {
    const m = d.market_expectation;
    children.push(p("Market expectation vs. our path:", { bold: true, size: 20 }));
    const meRows = [
      ["As of", m.as_of || "—"],
      ["Price / multiple", [m.price != null ? `Rs ${m.price}` : null,
        m.current_pe != null ? `${m.current_pe}x P/E` : null,
        m.current_ev_ebitda != null ? `${m.current_ev_ebitda}x EV/EBITDA` : null]
        .filter(Boolean).join(" · ") || "—"],
      ["Right valuation lens", m.valuation_tool || "—"],
      ["Price implies", m.implied_growth_cagr || "—"],
      ["Our FY27", m.our_fy27_estimate || "—"],
      ["Our FY28", m.our_fy28_estimate || "—"],
      ["Gap direction", m.gap_direction || "—"],
      ["Gap type", m.gap_type || "—"],
      ["Gap magnitude", m.gap_magnitude_pct != null ? `${m.gap_magnitude_pct}% (our FY28 PAT vs implied)` : "not estimable"],
      ["Gap basis", m.gap_basis || "—"],
      ["Evidence quality", m.evidence_quality || "—"],
    ];
    children.push(kvTable(meRows));
    if (m.data_caveat) children.push(p(m.data_caveat, { italics: true, size: 16, color: COLORS.muted }));
  }

  if (d.catalyst && (d.catalyst.event || d.catalyst.expected_window_months != null)) {
    const c = d.catalyst;
    children.push(new Paragraph({
      spacing: { before: 120, after: 120 },
      children: [
        new TextRun({ text: "Catalyst: ", bold: true, size: 20 }),
        new TextRun({ text: c.event || "—", size: 20 }),
        new TextRun({
          text: ` (window ~${c.expected_window_months != null ? c.expected_window_months + "M" : "?"}`
            + `${c.window_start ? " from " + c.window_start : ""}; `
            + `${c.is_dated ? "dated" : "undated"}; evidence ${c.evidence_quality || "?"}; ${c.status || "pending"})`,
          size: 18, color: COLORS.muted,
        }),
      ],
    }));
  }
}

if (d.value_chain || d.earnings_quality || d.growth_trajectory || d.management_quality || d.quality_metrics || d.track_record || d.global_signal_check) {
  children.push(h("Ishmohit-Lens Checks (value chain · earnings quality · growth trajectory · management · quality metrics · track record · global-signal check)"));
  children.push(p(
    "Extra checks drawn from @ishmohit1 / SOIC methodology (playbook/ishmohit-soic-style.md): "
    + "where the company sits in its value chain and what the supply side is doing, whether a "
    + "margin/PAT inflection is structural or a cyclical peak, the rate-of-change of growth vs. "
    + "what the multiple demands, and management quality as a positive attribute.",
    { italics: true, color: COLORS.muted, size: 18 }
  ));

  if (d.value_chain) {
    const v = d.value_chain;
    children.push(p("Value chain & supply side:", { bold: true, size: 20 }));
    children.push(kvTable([
      ["Theme", v.theme || "—"],
      ["This company's position", v.position || "—"],
      ["Bottleneck node (pricing power)", v.bottleneck_node || "—"],
      ["Supply-side status", v.supply_side_status || "—"],
      ["Adjacent-node peers", (v.adjacent_peers && v.adjacent_peers.length) ? v.adjacent_peers.join(", ") : "—"],
    ]));
    if (v.note) children.push(p(v.note, { size: 18, color: COLORS.muted }));
  }

  if (d.earnings_quality) {
    const e = d.earnings_quality;
    children.push(new Paragraph({
      spacing: { before: 120, after: 60 },
      children: [
        new TextRun({ text: "Earnings quality: ", bold: true, size: 20 }),
        new TextRun({ text: `margin driver ${e.margin_driver || "unclear"}`, size: 20 }),
        new TextRun({
          text: e.peak_margin_risk ? "  — PEAK-MARGIN RISK: do not capitalise current margins" : "",
          size: 20, bold: true, color: COLORS.bear,
        }),
      ],
    }));
    if (e.drivers && e.drivers.length) children.push(p(`Drivers: ${e.drivers.join("; ")}.`, { size: 18, color: COLORS.muted }));
    if (e.normalised_note) children.push(p(e.normalised_note, { size: 18, color: COLORS.muted }));
  }

  if (d.growth_trajectory) {
    const g = d.growth_trajectory;
    children.push(new Paragraph({
      spacing: { before: 120, after: 60 },
      children: [
        new TextRun({ text: "Growth trajectory: ", bold: true, size: 20 }),
        new TextRun({
          text: `YoY growth rate is ${g.yoy_trend || "unclear"}`, size: 20,
          bold: g.yoy_trend === "decelerating", color: g.yoy_trend === "decelerating" ? COLORS.bear : undefined,
        }),
      ],
    }));
    if (g.last_quarters_note) children.push(p(g.last_quarters_note, { size: 18, color: COLORS.muted }));
    if (g.reverse_pe_note) children.push(p(`Reverse P/E: ${g.reverse_pe_note}`, { size: 18, color: COLORS.muted }));
  }

  if (d.management_quality) {
    const mq = d.management_quality;
    children.push(p("Management quality (TVGP's \"P\"):", { bold: true, size: 20 }));
    children.push(kvTable([
      ["Assessment", mq.assessment || "—"],
      ["Capital allocation", mq.capital_allocation_track_record
        ? `${mq.capital_allocation || "—"} (${mq.capital_allocation_track_record})`
        : (mq.capital_allocation || "—")],
      ["Related-party trend", mq.rpt_trend || "—"],
      ["Guidance credibility", mq.guidance_credibility || "—"],
      ["Shareholder returns", mq.shareholder_returns || "—"],
      ["Capability ladder / VAP", mq.capability_ladder_note || "—"],
    ]));
  }

  if (d.quality_metrics) {
    const qm = d.quality_metrics;
    children.push(p("Quality metrics (ROCE · debt · FCF · margin · capex):", { bold: true, size: 20 }));
    children.push(kvTable([
      ["Assessment", qm.assessment || "—"],
      ["ROCE", qm.roce_pct != null ? `${qm.roce_pct}% (${qm.roce_trend || "unclear"})` : "—"],
      ["Leverage", qm.net_debt_to_ebitda != null ? `Net debt/EBITDA ${qm.net_debt_to_ebitda}x`
        : (qm.interest_coverage != null ? `Interest coverage ${qm.interest_coverage}x` : "—")],
      ["FCF conversion", qm.fcf_conversion_pct != null ? `${qm.fcf_conversion_pct}%` : "—"],
      ["Margin trend", qm.margin_trend || "—"],
      ["Capex efficiency", qm.capex_efficiency || "—"],
    ]));
  }

  if (d.track_record) {
    const tr = d.track_record;
    const pct = (tr.years_checked >= 3 && typeof tr.years_cleared === "number")
      ? ` (consistency_score ${Math.round(100 * tr.years_cleared / tr.years_checked)})` : "";
    children.push(new Paragraph({
      spacing: { before: 120, after: 60 },
      children: [
        new TextRun({ text: "Track record (Coffee Can persistence check): ", bold: true, size: 20 }),
        new TextRun({
          text: tr.years_checked >= 3
            ? `cleared revenue growth ≥10% AND ROCE ≥15% in ${tr.years_cleared} of the last ${tr.years_checked} years${pct}`
            : "not yet 3 fiscal years of history — not assessed",
          size: 20,
        }),
      ],
    }));
    if (tr.note) children.push(p(tr.note, { size: 18, color: COLORS.muted }));
  }

  if (d.global_signal_check) {
    const gs = d.global_signal_check;
    const alignBear = gs.alignment === "diverging" || gs.alignment === "not-yet-visible";
    children.push(new Paragraph({
      spacing: { before: 120, after: 60 },
      children: [
        new TextRun({ text: "Global-signal check: ", bold: true, size: 20 }),
        new TextRun({
          text: `Indian-name alignment with the ${gs.theme || "global"} tailwind is ${gs.alignment || "unclear"}`,
          size: 20, bold: gs.alignment === "diverging",
          color: alignBear ? COLORS.bear : (gs.alignment === "confirmed" ? COLORS.bull : undefined),
        }),
      ],
    }));
    children.push(kvTable([
      ["Bellwether / theme", gs.bellwether ? `${gs.bellwether} — ${gs.theme || ""}`.replace(/ — $/, "") : (gs.theme || "—")],
      ["Global tailwind", gs.global_tailwind || "—"],
      ["Signal looked for", gs.signal_hypothesis || "—"],
      ["Found in the Indian name", gs.india_datapoint || "—"],
      ["Checked on", gs.checked_date || "—"],
    ]));
    if (gs.note) children.push(p(gs.note, { size: 18, color: COLORS.muted }));
  }
}

children.push(h("Technical Read (Weekly / Monthly MACD + Bollinger Bands, or RSI/CCI/Williams %R proxy)"));
children.push(p(d.technical_read));

children.push(h("ValuePickr Community Signal"));
children.push(p(d.sentiment_summary));
if (d.community_signal) {
  children.push(new Paragraph({
    children: [
      new TextRun({ text: "High-conviction call from a top contributor: ", bold: true, size: 20 }),
      new TextRun({ text: d.community_signal, size: 20 }),
    ],
    spacing: { after: 120 },
  }));
}

if (d.trusted_signals && d.trusted_signals.length) {
  children.push(h("Trusted-User Signals (Ongoing)"));
  children.push(p("Every time a trusted user expresses clear conviction on this stock, most recent first — this section accumulates over time, it isn't a one-time snapshot.", { italics: true, color: COLORS.muted, size: 18 }));
  d.trusted_signals.slice().reverse().forEach(sig => {
    children.push(new Paragraph({
      spacing: { after: 100 },
      children: [
        new TextRun({ text: `${sig.date} — ${sig.username}`, bold: true, size: 20 }),
        new TextRun({ text: sig.thread ? ` (${sig.thread})` : "", italics: true, color: COLORS.muted, size: 18 }),
        new TextRun({ text: `: ${sig.note}`, size: 20, break: 1 }),
      ],
    }));
  });
}

children.push(h("BSE Corporate Actions / Other Red Flags"));
children.push(p(d.bse_notes));

children.push(h("Bull Case"));
(d.bull_case || []).forEach(b => children.push(bullet(b)));

children.push(h("Bear Case / Key Risks"));
(d.bear_case || []).forEach(b => children.push(bullet(b)));

children.push(h("Market-Cap Tier (informational — not a gate in this project)"));
children.push(p(d.market_cap_tier, { bold: true }));

children.push(h("Thesis Fit"));
children.push(p(d.thesis_fit || "Not yet assessed", { bold: true, size: 24 }));
if (d.four_box) {
  const fb = d.four_box;
  children.push(p(
    `4-box gate — tailwind: ${fb.tailwind || "?"} · TAM: ${fb.tam || "?"} · moat: ${fb.moat || "?"} · valuation: ${fb.valuation || "?"}  (score ${fb.score ?? "?"} / 4)`,
    { size: 20, color: COLORS.muted },
  ));
  if (fb.note) children.push(p(fb.note, { size: 20, italics: true, color: COLORS.muted }));
}

children.push(h("Verdict"));
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
