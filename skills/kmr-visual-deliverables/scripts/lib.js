// ===== kmr-visual-deliverables: 政策説明スライドの部品（pptxgenjs） =====
// 使い方: const L = require("./lib.js");  設計値（尺度・色・余白）は references/design-system.md と同じ。
// 文字サイズは尺度（10.5/12/14/17/21/25/30/36/43/62/89/107/185）だけを使う。
// 太字は、タイトル・見出し・関門の札・表の見出しだけ（全体の4割以下に収めるため、帯や注のラベルは標準ウェイト）。
const pptxgen = require("pptxgenjs");
const W = 13.333, MX = 0.75, CT = 1.9, CB = 6.9, CW = W - 2 * MX;
const F = "Meiryo";                       // 本文・ラベル
const FD = { ja: "Yu Mincho", num: "Cambria" };   // 主役の大字（標準ウェイトで使う）
// 色。領域に合わせて main / main2 を差し替える（環境＝深緑 など）。朱は関門・Ask・推奨・期限だけ。
const P = { ink: "1B1D21", sub: "5F6672", line: "D5DAE1", panel: "F3F5F8", paper: "F4F6FA", night: "0B1730",
  main: "1F3A5F", main2: "E4EAF3", mid: "3F6C9E", accent: "B93A14", accent2: "F7E6DD",
  accentOnDark: "F28A62", textOnDark: "FFFFFF", subOnDark: "B7C4D9", ruleOnDark: "2C3E5E" };

function newDeck(title, o = {}) {          // o.paper=true で紙色の地（投影向け）。既定は白（印刷・回覧向け）
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; pres.title = title;
  const num = { x: W - MX - 0.6, y: 7.05, w: 0.6, h: 0.3, fontFace: F, fontSize: 10.5, color: P.sub, align: "right" };
  pres.defineSlideMaster({ title: "BODY", background: { color: o.paper ? P.paper : "FFFFFF" },
    objects: [{ placeholder: { options: { name: "title", type: "title", x: MX, y: 0.7, w: CW, h: 1.1,
      fontFace: F, fontSize: 30, bold: true, color: P.ink, align: "left", valign: "top", margin: 0 }, text: "" } }],
    slideNumber: num });
  pres.defineSlideMaster({ title: "DARK", background: { color: P.night },
    slideNumber: Object.assign({}, num, { color: P.subOnDark }) });
  return pres;
}
function T(s, text, o) { s.addText(text, Object.assign({ fontFace: F, isTextBox: true, margin: 0, valign: "top", color: P.ink, fontSize: 14 }, o)); }
function frame(pres, tag, title, source) {            // 標準フレーム：章名＋結論のタイトル＋出典
  const s = pres.addSlide({ masterName: "BODY" });
  T(s, tag, { x: MX, y: 0.36, w: 8, h: 0.3, fontSize: 12, color: P.main });
  s.addText(title, { placeholder: "title" });
  if (source) T(s, source, { x: MX, y: 7.05, w: CW - 1, h: 0.3, fontSize: 10.5, color: P.sub });
  return s;
}
function dark(pres) { return pres.addSlide({ masterName: "DARK" }); }   // 全面濃色（表紙・山場・Ask。3枚まで）
function hero(s, text, o = {}) {                       // 主役の大字。num=true で数字・欧文の書体
  s.addText(text, Object.assign({ fontFace: o.num ? FD.num : FD.ja, fontSize: 89, bold: false, color: P.ink,
    isTextBox: true, margin: 0, valign: "top", align: "left", wrap: false }, o));
}
function box(pres, s, x, y, w, h, text, o = {}) {      // 箱（図の基本部品）
  s.addText(text, Object.assign({ shape: o.round === false ? pres.ShapeType.rect : pres.ShapeType.roundRect, rectRadius: 0.06,
    x, y, w, h, fontFace: F, fontSize: 14, color: P.ink, align: "center", valign: "middle", margin: 0.08,
    fill: { color: P.panel }, line: { color: P.line, width: 0.75 } }, o));
}
function arrow(pres, s, x1, y1, x2, y2, o = {}) {      // 直線の矢印（向きは自動）
  s.addShape(pres.ShapeType.line, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
    flipH: x2 < x1, flipV: y2 < y1,
    line: { color: o.color || P.sub, width: o.width || 1.5, endArrowType: o.head === false ? undefined : "triangle" } });
}
function elbow(pres, s, x1, y1, x2, y2, o = {}) {      // 親→子のL字連結（x方向に折れる）
  const mx = (x1 + x2) / 2;
  arrow(pres, s, x1, y1, mx, y1, { ...o, head: false });
  arrow(pres, s, mx, y1, mx, y2, { ...o, head: false });
  arrow(pres, s, mx, y2, x2, y2, o);
}
function badge(pres, s, x, y, n, d = 0.42, fill = P.main) {  // 番号バッジ
  s.addText(String(n), { shape: pres.ShapeType.ellipse, x, y, w: d, h: d, fontFace: F, fontSize: 14, bold: true,
    color: "FFFFFF", fill: { color: fill }, align: "center", valign: "middle", margin: 0 });
}
// 期限札：全頁で同じ語・30pt・同じ大きさ（幅3.1×高さ0.74）。onDark=濃色面
function plate(pres, s, x, y, text, onDark = false, w = 3.1, h = 0.74) {
  const fill = onDark ? P.accentOnDark : P.accent, tx = onDark ? P.night : "FFFFFF";
  s.addText(text, { shape: pres.ShapeType.rect, x, y, w, h, fontFace: F, fontSize: 30, bold: true, color: tx,
    fill: { color: fill }, line: { color: fill, width: 0 }, align: "center", valign: "middle", margin: 0, isTextBox: true, charSpacing: 1 });
  s.addShape(pres.ShapeType.rect, { x: x + 0.05, y: y + 0.05, w: w - 0.1, h: h - 0.1,
    fill: { color: fill, transparency: 100 }, line: { color: tx, width: 0.75, transparency: 55 } });
}
// 確定／未確定の札：実線＋塗り＝確定、破線＝未確定・目標
function tag(pres, s, x, y, w, text, solid = true) {
  s.addText(text, { shape: pres.ShapeType.rect, x, y, w, h: 0.32, fontFace: F, fontSize: 12, bold: true,
    color: solid ? "FFFFFF" : P.main, fill: { color: solid ? P.main : "FFFFFF" },
    line: { color: P.main, width: 1.5, dashType: solid ? "solid" : "dash" }, align: "center", valign: "middle", margin: 0, isTextBox: true });
}
// 数字と単位を別の箱で置き、下端をそろえる。parts=[{t,fs,num}]  yb=下端のy
function numline(s, x, yb, parts, color = P.ink) {
  const wd = p => (p.num ? 0.56 * p.t.length : p.t.length) * p.fs / 72; let cx = x;
  parts.forEach(p => {
    const w = wd(p) * (p.num ? 1.15 : 1) + 0.12, h = p.fs / 72 * 1.25, raise = p.num ? 0 : (0.21 * parts[0].fs - 0.12 * p.fs) / 72;
    s.addText(p.t, { x: cx - 0.02, y: yb - h - raise, w, h, fontFace: p.num ? FD.num : F, fontSize: p.fs, bold: false, color,
      margin: 0, valign: "bottom", align: "left", wrap: false, isTextBox: true });
    cx += wd(p);
  });
}
// 施策体系図：目的 → 施策の柱 → 事業 → 指標（左から右へ）
function tree(pres, s, d) {
  const cols = [[MX, 2.2], [3.35, 2.6], [6.35, 3.7], [10.45, 2.13]];
  const heads = ["目的", "施策の柱", "事業（具体的方策）", "成果指標"];
  heads.forEach((h, i) => T(s, h, { x: cols[i][0], y: CT, w: cols[i][1], h: 0.3, fontSize: 12, color: P.sub, align: "center" }));
  const top = CT + 0.45, avail = CB - top;
  const n = d.pillars.length, gap = 0.2, ph = (avail - gap * (n - 1)) / n;
  box(pres, s, cols[0][0], top, cols[0][1], avail, d.purpose, { fill: { color: P.main }, color: "FFFFFF", fontSize: 17, line: { color: P.main } });
  d.pillars.forEach((p, i) => {
    const y = top + i * (ph + gap);
    box(pres, s, cols[1][0], y, cols[1][1], ph, [{ text: p.no + "  ", options: { bold: true, color: P.main } }, { text: p.name, options: { bold: true } }],
      { fill: { color: P.main2 }, line: { color: P.main2 }, fontSize: 14 });
    elbow(pres, s, cols[0][0] + cols[0][1], top + avail / 2, cols[1][0], y + ph / 2);
    T(s, p.projects.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < p.projects.length - 1 } })),
      { x: cols[2][0] + 0.1, y, w: cols[2][1] - 0.1, h: ph, fontSize: 14, valign: "middle", paraSpaceAfter: 3 });
    arrow(pres, s, cols[1][0] + cols[1][1], y + ph / 2, cols[2][0], y + ph / 2);
    box(pres, s, cols[3][0], y, cols[3][1], ph, p.kpi, { fill: { color: "FFFFFF" }, line: { color: P.main, width: 0.75 }, fontSize: 14 });
    arrow(pres, s, cols[2][0] + cols[2][1], y + ph / 2, cols[3][0], y + ph / 2);
  });
}
// 施策フロー（スイムレーン）：主体×フェーズ。tasks=[{lane,phase,text,key?}], links=[[i,j]]
function swimlane(pres, s, d) {
  const lx = MX, lw = 1.7, gx = lx + lw, gw = CW - lw, top = CT, hh = 0.45;
  const pw = gw / d.phases.length, lh = (CB - top - hh) / d.lanes.length;
  d.phases.forEach((p, i) => box(pres, s, gx + i * pw + 0.03, top, pw - 0.06, hh, p, { fill: { color: P.main }, color: "FFFFFF", fontSize: 14, line: { color: P.main } }));
  d.lanes.forEach((l, i) => {
    const y = top + hh + i * lh;
    s.addShape(pres.ShapeType.rect, { x: lx, y: y + 0.03, w: CW, h: lh - 0.06, fill: { color: i % 2 ? "FFFFFF" : P.panel }, line: { color: P.line, width: 0.75 } });
    T(s, l, { x: lx + 0.1, y, w: lw - 0.2, h: lh, fontSize: 14, bold: true, color: P.main, valign: "middle" });
  });
  const pos = d.tasks.map(t => {
    const bw = pw - 0.3, bh = Math.min(lh - 0.3, 0.9);
    const x = gx + t.phase * pw + 0.15, y = top + hh + t.lane * lh + (lh - bh) / 2;
    box(pres, s, x, y, bw, bh, t.text, Object.assign({ fontSize: 14, fill: { color: "FFFFFF" }, line: { color: P.main, width: 0.75 } }, t.key ? { fill: { color: P.accent2 }, line: { color: P.accent, width: 1.5 } } : {}));
    return { x, y, bw, bh };
  });
  (d.links || []).forEach(([a, b]) => {
    const A = pos[a], B = pos[b];
    if (A.x === B.x) {                                   // 同じ列：縦の矢印（上下の辺どうしを結ぶ）
      const down = B.y > A.y;
      arrow(pres, s, A.x + A.bw / 2, down ? A.y + A.bh : A.y, B.x + B.bw / 2, down ? B.y : B.y + B.bh);
    } else if (A.y === B.y) arrow(pres, s, A.x + A.bw, A.y + A.bh / 2, B.x, B.y + B.bh / 2);
    else elbow(pres, s, A.x + A.bw, A.y + A.bh / 2, B.x, B.y + B.bh / 2);
  });
}
// ステップ・フロー（1行）：[{h, b, who}]
function flow(pres, s, steps, y = CT + 0.6, h = 3.2) {
  const n = steps.length, g = 0.35, w = (CW - g * (n - 1)) / n;
  steps.forEach((st, i) => {
    const x = MX + i * (w + g);
    box(pres, s, x, y, w, h, "", { fill: { color: P.panel } });
    badge(pres, s, x + 0.15, y + 0.15, i + 1);
    T(s, st.h, { x: x + 0.15, y: y + 0.7, w: w - 0.3, h: 0.65, fontSize: 17, bold: true });
    T(s, st.b, { x: x + 0.15, y: y + 1.4, w: w - 0.3, h: h - 1.55, fontSize: 14, color: P.ink });
    if (st.who) box(pres, s, x, y + h + 0.15, w, 0.42, st.who, { fill: { color: P.main2 }, line: { color: P.main2 }, fontSize: 12, color: P.main });
    if (i < n - 1) arrow(pres, s, x + w + 0.03, y + h / 2, x + w + g - 0.03, y + h / 2, { color: P.main, width: 2 });
  });
}
// ロードマップ（ガント）：periods=["R8下",...], rows=[{name,from,to,gate?,label?,plan?}]  plan=true は未確定（破線）
function roadmap(pres, s, d) {
  const nw = 2.9, gx = MX + nw, gw = CW - nw, top = CT, hh = 0.45, n = d.periods.length, pw = gw / n;
  const rh = Math.min(0.62, (CB - top - hh) / d.rows.length);
  d.periods.forEach((p, i) => box(pres, s, gx + i * pw + 0.02, top, pw - 0.04, hh, p, { fill: { color: P.main }, color: "FFFFFF", fontSize: 12, line: { color: P.main } }));
  d.rows.forEach((r, i) => {
    const y = top + hh + 0.08 + i * rh, c = r.gate ? P.accent : P.main;
    if (i % 2 === 0) s.addShape(pres.ShapeType.rect, { x: MX, y, w: CW, h: rh, fill: { color: P.panel }, line: { color: P.panel, width: 0 } });
    T(s, r.name, { x: MX + 0.1, y, w: nw - 0.2, h: rh, fontSize: 14, valign: "middle", bold: !!r.head });
    s.addShape(pres.ShapeType.roundRect, { x: gx + r.from * pw + 0.05, y: y + rh * 0.2, w: (r.to - r.from + 1) * pw - 0.1, h: rh * 0.6, rectRadius: 0.05,
      fill: { color: r.plan ? "FFFFFF" : c }, line: { color: c, width: r.plan ? 1.5 : 0, dashType: r.plan ? "dash" : "solid" } });
    if (r.label) T(s, r.label, { x: gx + r.from * pw + 0.15, y: y + rh * 0.2, w: (r.to - r.from + 1) * pw - 0.3, h: rh * 0.6, fontSize: 12, color: r.plan ? c : "FFFFFF", valign: "middle" });
  });
}
// 選択肢の比較表：criteria=[...], options=[{name, vals:[...], rec?}]
function options(pres, s, d) {
  const hdr = [{ text: "評価軸", options: { fill: { color: P.main }, color: "FFFFFF", bold: true } }].concat(
    d.options.map(o => ({ text: o.name + (o.rec ? "（推奨）" : ""), options: { fill: { color: o.rec ? P.accent : P.main }, color: "FFFFFF", bold: true, align: "center" } })));
  const rows = d.criteria.map((c, i) => [{ text: c, options: { bold: true, fill: { color: P.panel } } }].concat(
    d.options.map(o => ({ text: o.vals[i], options: { align: "center", fill: { color: o.rec ? P.accent2 : "FFFFFF" } } }))));
  const cw0 = 2.3, cw = (CW - cw0) / d.options.length;
  s.addTable([hdr, ...rows], { x: MX, y: CT, w: CW, colW: [cw0].concat(d.options.map(() => cw)), fontFace: F, fontSize: 14, color: P.ink,
    border: { type: "solid", color: P.line, pt: 0.75 }, valign: "middle", rowH: Math.min(0.95, (CB - CT) / (d.criteria.length + 1)), margin: [0.05, 0.1, 0.05, 0.1] });
}
module.exports = { pptxgen, W, MX, CT, CB, CW, F, FD, P, newDeck, T, frame, dark, hero, box, arrow, elbow, badge,
  plate, tag, numline, tree, swimlane, flow, roadmap, options };
