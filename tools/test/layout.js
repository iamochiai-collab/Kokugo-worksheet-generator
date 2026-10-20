// プリントの はみ出し・問題数・答えを しらべる
// node tools/test/layout.js [build/test.html]
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const file = 'file://' + path.resolve(process.argv[2] || 'build/test.html');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1100, height: 1400 } });
  const bad = [];
  await page.goto(file);
  const grades = await page.evaluate(() => window.__T.BANKS.length);

  for (let g = 1; g <= grades; g++) {
    for (const kind of ['both', 'read', 'write', 'long']) {
      for (const level of [1, 2, 3]) {
        for (const seed of [1, 7, 23, 99]) {
          const r = await page.evaluate(([g, kind, level, seed]) => {
            const T = window.__T;
            if (kind === 'long' && !T.hasLong(g)) return null;
            const count = kind === 'write' ? 12 : 16;
            const opt = { grade: g, kind, level, count, seed, no: 1 };
            if (kind === 'long') [opt.nRead, opt.nWrite] = T.defaultCounts('long', g);
            const sheet = T.buildSheet(opt);
            const host = document.getElementById('sheets');
            host.innerHTML = T.sheetHtml(sheet, {}) + T.sheetHtml(sheet, { answer: true });
            document.body.dataset.view = 'sheet';
            for (const el of host.querySelectorAll('.sheet')) el.style.transform = '';
            const mm = 96 / 25.4;
            const els = [...host.querySelectorAll('.sheet')];
            const over = els.map((el) => Math.round(el.scrollHeight / mm));
            const items = host.querySelectorAll('.sheet:first-child .item').length;
            const nos = [...host.querySelectorAll('.sheet:first-child .item .n')].map((e) => e.textContent);
            const reads = host.querySelectorAll('.sheet:first-child .q-read .q-item').length;
            const vocab = host.querySelectorAll('.sheet:first-child .vocab .v').length;
            const answers = [...host.querySelectorAll('.sheet.answer .ans')].length;
            const empty = sheet.groups.some((grp) => grp.items.length === 0);
            const want = kind === 'long' ? opt.nRead + opt.nWrite : count;
            const wantQ = sheet.story ? sheet.story.questions.length : 0;
            const wantV = sheet.story ? sheet.story.vocab.length : 0;
            return { over, items, nos, answers, empty, reads, vocab, want, wantQ, wantV };
          }, [g, kind, level, seed]);
          if (!r) continue;
          const where = `学年${g} ${kind} ★${level} seed${seed}`;
          for (const h of r.over) if (h > 297) bad.push(`${where}: 紙から はみ出し ${h}mm`);
          if (r.items !== r.want) bad.push(`${where}: 問題が ${r.items} 問(${r.want} 問の はず)`);
          if (r.empty) bad.push(`${where}: 空の 大問が ある`);
          if (!r.answers) bad.push(`${where}: 答えが 出ていない`);
          if (kind === 'long') {
            if (r.reads !== r.wantQ) bad.push(`${where}: 長文の問いが ${r.reads} 問(${r.wantQ} 問の はず)`);
            if (r.vocab !== r.wantV) bad.push(`${where}: 言葉の意味が ${r.vocab} 問(${r.wantV} 問の はず)`);
          }
          const expect = Array.from({ length: r.items }, (_, i) => `(${i + 1})`);
          if (r.nos.join() !== expect.join()) bad.push(`${where}: 番号が ずれている -> ${r.nos.join(' ')}`);
        }
      }
    }
  }
  await browser.close();
  if (bad.length) {
    console.log(`NG ${bad.length} 件`);
    for (const b of bad.slice(0, 40)) console.log(' -', b);
    process.exit(1);
  }
  console.log('OK すべての くみあわせで はみ出し・番号のずれは ありません');
})();
