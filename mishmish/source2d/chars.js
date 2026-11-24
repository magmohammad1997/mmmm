// 2D cut-out cartoon characters with clean outlines (original designs: "Leen" the girl and "Mishmish" the cat)
const OUT = '#3b2216';
function P(g){g.beginPath()}
function fs(g, fill, lw = 7){ g.fillStyle = fill; g.fill(); g.lineWidth = lw; g.strokeStyle = OUT; g.lineJoin = 'round'; g.lineCap = 'round'; g.stroke() }
function ellipseP(g, x, y, rx, ry, rot = 0){ g.beginPath(); g.ellipse(x, y, Math.max(.1, rx), Math.max(.1, ry), rot, 0, Math.PI * 2) }
function shade(g, pathFn, fill, sx, sy, base){ // cel-shade: dark crescent on the far side, inside the shape
  g.save(); pathFn(); g.clip(); g.fillStyle = fill; g.fillRect(-2000, -2000, 4000, 4000); g.translate(-sx, -sy); pathFn(); g.fillStyle = base; g.fill(); g.restore();
  pathFn(); g.lineWidth = 7; g.strokeStyle = OUT; g.stroke() }
function glint(g, x, y, r){ g.beginPath(); g.arc(x, y, r, 0, 7); g.fillStyle = '#fff'; g.fill() }
function star5(g, x, y, r, rot = 0, inner = .48){ g.beginPath(); for (let i = 0; i < 10; i++){ const a = rot + i * Math.PI / 5 - Math.PI / 2, rr = i % 2 ? r * inner : r; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr) } g.closePath() }

function eyes(g, o, ex, ey, rx, ry){
  for (const s of [-1, 1]){
    const x = s * ex, kind = (o.eyes === 'wink' && s > 0) ? 'happy' : o.eyes;
    if (kind === 'happy'){ g.beginPath(); g.arc(x, ey + ry * .35, rx * 1.15, Math.PI * 1.12, Math.PI * 1.88); g.lineWidth = 9; g.strokeStyle = OUT; g.lineCap = 'round'; g.stroke(); continue }
    if (kind === 'closed'){ g.beginPath(); g.arc(x, ey - ry * .1, rx * 1.1, Math.PI * .12, Math.PI * .88); g.lineWidth = 8; g.strokeStyle = OUT; g.stroke(); continue }
    const bl = o.blink || 0; const sy = ry * (1 - bl * .9);
    if (kind === 'surprised'){ ellipseP(g, x, ey, rx * 1.35, sy * 1.25); fs(g, '#fff', 6); ellipseP(g, x + (o.lookX || 0) * 4, ey + (o.lookY || 0) * 4, rx * .55, sy * .6); g.fillStyle = '#1d120c'; g.fill(); glint(g, x - rx * .2, ey - sy * .3, rx * .22); continue }
    ellipseP(g, x + (o.lookX || 0) * 3, ey + (o.lookY || 0) * 3, rx, sy); g.fillStyle = '#1d120c'; g.fill();
    if (bl < .6){ glint(g, x - rx * .32 + (o.lookX || 0) * 3, ey - sy * .38, rx * .42); glint(g, x + rx * .35, ey + sy * .35, rx * .18) }
  }
}
function mouth(g, o, mx, my, w){
  const m = Math.max(0, Math.min(1, o.mouth || 0)), shape = o.mouthShape || 'smile';
  if (m < .08){
    if (shape === 'grin'){ g.beginPath(); g.moveTo(mx - w, my - 4); g.quadraticCurveTo(mx, my + w * 1.1, mx + w, my - 4); g.closePath(); fs(g, '#7a1f2b', 6); g.save(); g.clip(); g.fillStyle = '#fff'; g.fillRect(mx - w, my - 6, w * 2, 12); g.restore(); return }
    g.beginPath(); g.arc(mx, my - w * .55, w * .85, Math.PI * .2, Math.PI * .8); g.lineWidth = 7; g.strokeStyle = OUT; g.lineCap = 'round'; g.stroke(); return }
  const h = 8 + m * w * 1.25, ww = w * (shape === 'o' ? .55 : .9) + m * 6;
  g.beginPath(); g.moveTo(mx - ww, my - 4); g.bezierCurveTo(mx - ww, my + h, mx + ww, my + h, mx + ww, my - 4); g.quadraticCurveTo(mx, my + 2, mx - ww, my - 4); g.closePath();
  fs(g, '#7a1f2b', 6);
  g.save(); g.clip(); ellipseP(g, mx, my + h * .9, ww * .7, h * .45); g.fillStyle = '#ff7f93'; g.fill(); g.fillStyle = '#fff'; g.fillRect(mx - ww, my - 6, ww * 2, 9); g.restore();
}
function limb(g, x, y, a1, l1, a2, l2, w, fill, end){ // two-segment limb with rounded caps (outlined)
  const x1 = x + Math.sin(a1) * l1, y1 = y + Math.cos(a1) * l1, x2 = x1 + Math.sin(a1 + a2) * l2, y2 = y1 + Math.cos(a1 + a2) * l2;
  g.lineCap = 'round'; g.lineJoin = 'round';
  g.beginPath(); g.moveTo(x, y); g.lineTo(x1, y1); g.lineTo(x2, y2); g.strokeStyle = OUT; g.lineWidth = w + 14; g.stroke(); g.strokeStyle = fill; g.lineWidth = w; g.stroke();
  if (end) end(x2, y2, a1 + a2);
  return [x2, y2];
}

// ---------------- Leen (girl) ----------------
const SK = '#ffd3b4', SKD = '#f3b392', HR = '#4b2a1b', HRD = '#36190f', DR = '#36c7b0', DRD = '#22a593';
function drawGirl(g, o){
  g.save(); g.translate(o.x, o.y); const s = o.s || 1; const sq = o.squash || 0;
  g.scale(s * (o.flip ? -1 : 1) * (1 + sq * .08), s * (1 - sq * .08)); g.rotate(o.rot || 0);
  const step = o.step || 0; // walking phase
  // legs
  for (const sd of [-1, 1]){
    const lift = Math.max(0, Math.sin(step + (sd > 0 ? Math.PI : 0))) * 18 * (o.walk || 0);
    limb(g, sd * 36, -112, sd * .04, 50, 0, 46, 38, SK, (x, y) => { ellipseP(g, x + sd * 6, y + 6 - lift, 34, 21); fs(g, '#ff6f91', 7); g.fillStyle = '#fff'; g.fillRect(x - 19, y - 26 - lift, 38, 13) });
  }
  g.translate(0, 52);
  // back arm
  const arm = (sd, a) => limb(g, sd * 62, -305, a[0] * sd, 72, a[1] * sd, 66, 26, SK, (x, y) => { g.beginPath(); g.arc(x, y, 21, 0, 7); fs(g, SK, 6) });
  // dress
  const dress = () => { g.beginPath(); g.moveTo(-58, -330); g.bezierCurveTo(-80, -280, -130, -210, -138, -158); g.quadraticCurveTo(-70, -138, 0, -150); g.quadraticCurveTo(70, -138, 138, -158); g.bezierCurveTo(130, -210, 80, -280, 58, -330); g.closePath() };
  dress(); fs(g, DR); shade(g, dress, DRD, 26, 0, DR);
  g.beginPath(); g.moveTo(-138, -158); g.quadraticCurveTo(-70, -138, 0, -150); g.quadraticCurveTo(70, -138, 138, -158); g.lineWidth = 10; g.strokeStyle = '#fff'; g.stroke();
  star5(g, 0, -255, 24, Math.sin((o.t || 0) * 2) * .2); fs(g, '#ffd23f', 5);
  // arms (both in front)
  const aL = o.armL || [.35, .25], aR = o.armR || [.35, .25];
  arm(-1, aL); arm(1, aR);
  for (const sd of [-1, 1]){ ellipseP(g, sd * 62, -312, 30, 26); fs(g, DR, 6) }
  // collar
  for (const sd of [-1, 1]){ g.beginPath(); g.moveTo(0, -330); g.quadraticCurveTo(sd * 50, -335, sd * 48, -305); g.quadraticCurveTo(sd * 22, -300, 0, -318); g.closePath(); fs(g, '#fff', 5) }
  // head group
  g.save(); g.translate(0, -470); g.rotate(o.tilt || 0);
  // back hair + pigtails
  for (const sd of [-1, 1]){ const sw = Math.sin((o.t || 0) * 4 + sd) * .08; g.save(); g.translate(sd * 150, -40); g.rotate(sd * (.5 + sw));
    ellipseP(g, sd * 20, 55, 42, 80); fs(g, HR); g.restore() }
  const back = () => { ellipseP(g, 0, -8, 168, 160) }; back(); fs(g, HR);
  // face
  const face = () => { ellipseP(g, 0, 18, 150, 138) }; face(); fs(g, SK); shade(g, face, SKD, 16, 10, SK);
  for (const sd of [-1, 1]){ ellipseP(g, sd * 148, 22, 20, 28); fs(g, SK, 6) }
  // bangs
  const bangs = () => { g.beginPath(); g.moveTo(-160, 0); g.bezierCurveTo(-170, -140, 170, -140, 160, 0); for (let i = 5; i >= 0; i--){ const x0 = -160 + i * 64, x1 = x0 - 64; g.quadraticCurveTo((x0 + x1) / 2 + 8, -40 + (i % 2) * 10, x1 < -160 ? -160 : x1 + 0, i === 0 ? 0 : -20) } g.closePath() };
  g.beginPath(); g.moveTo(-162, 10); g.bezierCurveTo(-178, -150, 178, -150, 162, 10); g.quadraticCurveTo(130, -60, 70, -45); g.quadraticCurveTo(30, -70, -10, -50); g.quadraticCurveTo(-60, -75, -100, -45); g.quadraticCurveTo(-140, -40, -162, 10); g.closePath(); fs(g, HR);
  g.beginPath(); g.moveTo(-90, -105); g.quadraticCurveTo(-40, -125, 10, -112); g.lineWidth = 9; g.strokeStyle = 'rgba(255,255,255,.35)'; g.stroke();
  for (const sd of [-1, 1]){ star5(g, sd * 128, -92, 28, sd * .3); fs(g, '#ffd23f', 5) }
  // features
  eyes(g, o, 55, 20, 21, 30);
  for (const sd of [-1, 1]){ g.beginPath(); g.arc(sd * 55, -28, 22, Math.PI * 1.2, Math.PI * 1.8); g.lineWidth = 6; g.strokeStyle = OUT; g.stroke() }
  for (const sd of [-1, 1]){ ellipseP(g, sd * 98, 62, 26, 15); g.fillStyle = 'rgba(255,110,130,.45)'; g.fill() }
  g.beginPath(); g.arc(0, 48, 9, Math.PI * .1, Math.PI * .9); g.lineWidth = 5; g.strokeStyle = OUT; g.stroke();
  mouth(g, o, 0, 86, 30);
  g.restore(); g.restore();
}

// ---------------- Mishmish (cat) ----------------
const CO = '#ffa83f', COD = '#f0862a', CR = '#fff1d8';
function drawCat(g, o){
  g.save(); g.translate(o.x, o.y); const s = o.s || 1, sq = o.squash || 0;
  g.scale(s * (o.flip ? -1 : 1) * (1 + sq * .08), s * (1 - sq * .08)); g.rotate(o.rot || 0);
  const t = o.t || 0;
  // tail
  const tw = Math.sin(t * 3) * 30;
  g.beginPath(); g.moveTo(60, -70); g.bezierCurveTo(170, -60, 160 + tw * .4, -190, 120 + tw, -230); g.lineCap = 'round'; g.lineWidth = 44; g.strokeStyle = OUT; g.stroke(); g.lineWidth = 30; g.strokeStyle = CO; g.stroke();
  // feet
  for (const sd of [-1, 1]){ const lift = Math.max(0, Math.sin((o.step || 0) + (sd > 0 ? Math.PI : 0))) * 14 * (o.walk || 0); ellipseP(g, sd * 48, -18 - lift, 38, 24); fs(g, CO); ellipseP(g, sd * 48, -12 - lift, 18, 10); g.fillStyle = '#ffc4cf'; g.fill() }
  // body
  const body = () => { ellipseP(g, 0, -105, 92, 96) }; body(); fs(g, CO); shade(g, body, COD, 20, 0, CO);
  ellipseP(g, 0, -88, 52, 62); g.fillStyle = CR; g.fill();
  // arms
  const aL = o.armL || [.3, .2], aR = o.armR || [.3, .2];
  for (const [sd, a] of [[-1, aL], [1, aR]]) limb(g, sd * 66, -150, a[0] * sd + Math.PI * 0 , 52, a[1] * sd, 40, 30, CO, (x, y) => { g.beginPath(); g.arc(x, y, 19, 0, 7); fs(g, CR, 6) });
  if (o.holdStar){ star5(g, 0, -120, 52, Math.sin(t * 2) * .2); fs(g, '#ffd23f', 7); glint(g, -14, -130, 7) }
  // head
  g.save(); g.translate(0, -265); g.rotate(o.tilt || 0);
  for (const sd of [-1, 1]){ g.beginPath(); g.moveTo(sd * 40, -88); g.quadraticCurveTo(sd * 92, -178, sd * 118, -70); g.closePath(); fs(g, CO); g.beginPath(); g.moveTo(sd * 58, -88); g.quadraticCurveTo(sd * 90, -146, sd * 102, -82); g.closePath(); g.fillStyle = '#ffa3b8'; g.fill() }
  const head = () => { ellipseP(g, 0, 0, 132, 112) }; head(); fs(g, CO); shade(g, head, COD, 16, 8, CO);
  for (const dx of [-30, 0, 30]){ g.beginPath(); g.moveTo(dx, -108); g.lineTo(dx * 1.1, -72); g.lineWidth = 11; g.strokeStyle = COD; g.lineCap = 'round'; g.stroke() }
  ellipseP(g, 0, 50, 66, 44); g.fillStyle = CR; g.fill();
  eyes(g, o, 52, -2, 18, 26);
  for (const sd of [-1, 1]){ ellipseP(g, sd * 88, 40, 22, 13); g.fillStyle = 'rgba(255,110,130,.45)'; g.fill() }
  g.beginPath(); g.moveTo(-13, 26); g.lineTo(13, 26); g.lineTo(0, 40); g.closePath(); fs(g, '#ff8aa3', 5);
  g.strokeStyle = OUT; g.lineWidth = 4; for (const sd of [-1, 1]) for (const k of [-1, 1]){ g.beginPath(); g.moveTo(sd * 70, 50 + k * 9); g.lineTo(sd * 140, 42 + k * 20); g.stroke() }
  if ((o.mouth || 0) > .08) mouth(g, o, 0, 52, 22);
  else { g.lineWidth = 6; g.beginPath(); g.arc(-11, 44, 11, 0, Math.PI); g.stroke(); g.beginPath(); g.arc(11, 44, 11, 0, Math.PI); g.stroke() }
  g.restore(); g.restore();
}
