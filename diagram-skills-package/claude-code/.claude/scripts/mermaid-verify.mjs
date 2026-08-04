#!/usr/bin/env node
/*
 * mermaid-verify.mjs — compile-verify mọi block ```mermaid trong 1 file .md qua mmdc.
 *
 * Dùng bởi /sequence /activity /erd /state SAU khi Write — mermaid không render trong chat
 * (Mermaid syntax safety, diagram-selection.md), nên lỗi cú pháp trước đây chỉ lộ ra khi user
 * tự mở IDE/Obsidian/GitHub. Script này bắt lỗi NGAY, trước khi skill báo "xong".
 *
 * Dùng:
 *   node .claude/scripts/mermaid-verify.mjs --file docs/{feature}/srs/flows.md
 *   node .claude/scripts/mermaid-verify.mjs --file docs/x/srs/x-erd.md --png /tmp/erd-review
 *
 * Output: mỗi block PASS/FAIL kèm heading gần nhất (## ...) để biết lỗi ở đâu trong file.
 * Exit code = số block FAIL (0 nếu tất cả pass).
 *
 * --png <dir>: ngoài compile-check, giữ lại ảnh PNG mỗi block ở <dir>/block-N.png để skill
 * TỰ Read xem hình soi lỗi nghiệp vụ (thiếu entity, sai cardinality) — compile-check chỉ bắt
 * lỗi cú pháp, không bắt lỗi nội dung. In path từng ảnh ra stdout.
 *
 * mmdc cần PUPPETEER_EXECUTABLE_PATH trỏ Chrome sẵn có (~/.puppeteer-cache) — mmdc mặc định
 * tìm Chrome ở ~/.cache/puppeteer (không có gì ở đó trên môi trường này) và fail ngay nếu thiếu.
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';

const argv = process.argv.slice(2);
const flag = (name) => { const i = argv.indexOf('--' + name); return i >= 0 ? argv[i + 1] : null; };
const FILE = flag('file');
const PNG_DIR = flag('png');
if (!FILE) {
  console.error('Thiếu --file <path.md>. Ví dụ: --file docs/authentication/srs/flows.md');
  process.exit(2);
}
if (!fs.existsSync(FILE)) {
  console.error(`Không thấy file: ${FILE}`);
  process.exit(2);
}

function findChrome() {
  const glob = path.join(os.homedir(), '.puppeteer-cache', 'chrome');
  if (!fs.existsSync(glob)) return null;
  for (const versionDir of fs.readdirSync(glob)) {
    const candidate = path.join(glob, versionDir, 'chrome-mac-arm64', 'Google Chrome for Testing.app', 'Contents', 'MacOS', 'Google Chrome for Testing');
    if (fs.existsSync(candidate)) return candidate;
    // linux/x64 layout fallback (best-effort — máy khác kiến trúc có thể cần path khác)
    const linuxCandidate = path.join(glob, versionDir, 'chrome-linux64', 'chrome');
    if (fs.existsSync(linuxCandidate)) return linuxCandidate;
  }
  return null;
}

const CHROME = findChrome();
if (!CHROME) {
  console.error('⚠️  Không tìm thấy Chrome for Testing ở ~/.puppeteer-cache/chrome — mmdc sẽ fail khi launch.');
  console.error('   Cài qua: npx puppeteer browsers install chrome-headless-shell (hoặc dùng bản Chrome D2 render.sh đã cài).');
  process.exit(2);
}

// ---------- extract ```mermaid blocks + heading gần nhất ----------
function extractBlocks(mdPath) {
  const lines = fs.readFileSync(mdPath, 'utf8').split('\n');
  const blocks = [];
  let heading = '(no heading)';
  let inBlock = false;
  let buf = [];
  for (const line of lines) {
    if (/^##\s+/.test(line)) heading = line.replace(/^##\s+/, '').trim();
    if (line.trim() === '```mermaid') { inBlock = true; buf = []; continue; }
    if (inBlock && line.trim() === '```') { inBlock = false; blocks.push({ heading, code: buf.join('\n') }); continue; }
    if (inBlock) buf.push(line);
  }
  return blocks;
}

const blocks = extractBlocks(FILE);
if (!blocks.length) {
  console.log(`Không có block \`\`\`mermaid nào trong ${FILE} — không có gì để verify.`);
  process.exit(0);
}

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'mermaid-verify-'));
if (PNG_DIR) fs.mkdirSync(PNG_DIR, { recursive: true });
let failCount = 0;
const results = [];

blocks.forEach((b, i) => {
  const mmdPath = path.join(tmpDir, `block-${i}.mmd`);
  // --png → xuất PNG (Read tool xem được như ảnh) vào PNG_DIR; else SVG vào tmp (compile-check thôi).
  const outPath = PNG_DIR
    ? path.join(PNG_DIR, `block-${i}.png`)
    : path.join(tmpDir, `block-${i}.svg`);
  fs.writeFileSync(mmdPath, b.code);
  const res = spawnSync('mmdc', ['-i', mmdPath, '-o', outPath, '-s', '2'], {
    encoding: 'utf8',
    env: { ...process.env, PUPPETEER_EXECUTABLE_PATH: CHROME },
  });
  const ok = res.status === 0 && fs.existsSync(outPath);
  if (!ok) failCount++;
  results.push({ index: i, heading: b.heading, ok, pngPath: PNG_DIR && ok ? outPath : null, stderr: (res.stderr || '').split('\n').slice(0, 6).join('\n') });
});

fs.rmSync(tmpDir, { recursive: true, force: true });

console.log(`\n=== mermaid-verify: ${FILE} (${blocks.length} block) ===`);
for (const r of results) {
  console.log(`${r.ok ? '✅' : '❌'} Block ${r.index + 1} — "${r.heading}"`);
  if (r.pngPath) console.log(`   🖼  ${r.pngPath}`);
  if (!r.ok) console.log(r.stderr.split('\n').map(l => '   ' + l).join('\n'));
}
console.log(`\n${blocks.length - failCount}/${blocks.length} block compile OK${failCount ? `, ${failCount} FAIL` : ''}`);
if (PNG_DIR && failCount === 0) console.log(`\n→ Ảnh PNG đã lưu ở ${PNG_DIR}. Read từng ảnh để tự soi thiếu entity/sai cardinality trước khi báo xong.`);
process.exit(failCount);
