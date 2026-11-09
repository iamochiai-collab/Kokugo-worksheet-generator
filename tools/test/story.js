// 文章読解(漢字なし)の プリントを ぜんぶの 話で 作り、字を 大きく しても 1枚に 入るかを しらべる
//   node tools/test/story.js
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 1400 } });
  await p.goto('file://' + path.resolve(process.argv[2] || 'build/test.html')); await p.evaluate(() => document.fonts.ready);
  const r = await p.evaluate(() => {
    const T = window.__T, host = document.getElementById('sheets'); document.body.dataset.view = 'sheet';
    const mm = 96 / 25.4; const bad = []; const zs = {}; let n = 0;
    for (let g = 1; g <= 7; g++) for (const genre of T.genresOf(g).map((x) => x[0])) for (const furi of ['none', 'over', 'all']) {
      const cnt = T.storiesOf(g, genre).length;
      for (let seed = 1; seed <= cnt; seed++) for (const answer of [false, true]) {
        const s = T.buildSheet({ grade: g, gStory: g, kind: 'long', level: 2, seed, no: 1, nRead: 0, nWrite: 0, furi, genre });
        host.innerHTML = T.sheetHtml(s, { answer }); T.fixZoom(host);
        const el = host.querySelector('.sheet'); n++;
        const z = +el.querySelector('.st-zoom').dataset.z; (zs[g] = zs[g] || []).push(z);
        const top = el.getBoundingClientRect().top, right = el.getBoundingClientRect().right;
        const kids = [...el.querySelectorAll('.st-zoom *')].map((x) => x.getBoundingClientRect());
        const bottom = Math.max(...kids.map((x) => x.bottom)) - top;
        const foot = el.querySelector('.sheet-foot').getBoundingClientRect().top - top;
        const where = `小${g} ${genre} ${furi} seed${seed}${answer ? ' 答え' : ''}`;
        if (el.offsetHeight / mm > 297.6) bad.push(`${where}: ${(el.offsetHeight / mm).toFixed(1)}mm`);
        if (bottom > foot + 2) bad.push(`${where}: シードに かさなる`);
        if (Math.max(...kids.map((x) => x.right)) > right + 1) bad.push(`${where}: よこに はみ出し`);
      }
    }
    const st = Object.entries(zs).map(([g, a]) => `${g === 7 ? "中学" : "小" + g} ${Math.min(...a).toFixed(2)}〜${Math.max(...a).toFixed(2)}倍`).join(' / ');
    return { n, bad, st };
  });
  await b.close();
  console.log(`文章読解 ${r.n} 枚  字の 大きさ: ${r.st}`);
  if (r.bad.length) { console.log(`NG ${r.bad.length} 件`); r.bad.slice(0, 20).forEach((x) => console.log(' -', x)); process.exit(1); }
  console.log('OK 文章読解は どの 話も 1枚に 入ります');
})();
