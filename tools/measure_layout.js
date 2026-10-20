// 長文プリントの 土台(漢字の 問題 なし)の 高さを、学年ごとに 全部の 話で 組んで 実測し、
// 9割の 話が 入る 高さを src/data/layout.json に 書く(学年ごと・学年:ジャンルごと)。
//   python3 tools/build.py && node tools/measure_layout.js && python3 tools/build.py
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1100, height: 1400 } });
  await p.goto('file://' + path.resolve('build/test.html'));
  const res = await p.evaluate(() => {
    const T = window.__T;
    const host = document.getElementById('sheets');
    document.body.dataset.view = 'sheet';
    const mm = 96 / 25.4;
    const out = { longBase: {}, longBaseR: {}, storyH: {}, storyHR: {} };
    for (const [furi, baseKey, hKey] of [['none', 'longBase', 'storyH'], ['all', 'longBaseR', 'storyHR']])
    for (const g of Object.keys(T.READS).map(Number)) {
      const longBase = out[baseKey], storyH = out[hKey];
      const hs = [], byGenre = {};
      // 選択肢の ならびは シードで かわり、ならびに よって 折り返しが かわる。
      // 6通りの ならびを ぜんぶ 組んで、問いごとに いちばん 高い ものを 足しあわせる
      const PERMS = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];
      for (const st of T.READS[g]) {
        let h = 0;
        for (const answer of [false, true]) {
          let total0 = 0, sum0 = 0;
          const qmax = st.questions.map(() => 0);
          PERMS.forEach((perm, k) => {
            const s = T.longSheetFor(g, st, furi);
            s.story.questions = st.questions.map((q) => ({ q: q.q, c: perm.map((i) => q.c[i]), a: perm.indexOf(q.a) }));
            host.innerHTML = T.sheetHtml(s, { answer });
            const el = host.querySelector('.sheet');
            el.style.transform = '';
            el.style.minHeight = '0';
            el.style.setProperty('--row-extra', '0mm');
            const qs = [...el.querySelectorAll('.q-read .q-item')].map((q) => q.getBoundingClientRect().height / mm);
            qs.forEach((v, i) => { qmax[i] = Math.max(qmax[i], v); });
            if (k === 0) { total0 = el.scrollHeight / mm; sum0 = qs.reduce((x, y) => x + y, 0); }
          });
          h = Math.max(h, total0 - sum0 + qmax.reduce((x, y) => x + y, 0));
        }
        h = Math.ceil((h + 0.5) * 10) / 10;
        storyH[st.id] = h;
        hs.push(h);
        (byGenre[st.genre] = byGenre[st.genre] || []).push(h);
      }
      // 9割の 話が 入る 高さを、その 学年の 土台に する(長すぎる 話は、入らない ときだけ 使わない)
      const p90 = (xs) => { xs.sort((a, b) => a - b); return xs[Math.min(xs.length - 1, Math.ceil(xs.length * 0.9) - 1)]; };
      longBase[g] = p90(hs);
      // ジャンルを しぼった ときの 土台(「学年:ジャンル」)
      for (const [genre, xs] of Object.entries(byGenre)) longBase[`${g}:${genre}`] = p90(xs);
    }
    return out;
  });
  await b.close();
  const file = path.resolve('src/data/layout.json');
  fs.writeFileSync(file, JSON.stringify(res) + '\n');
  console.log('土台の 高さ(mm):', JSON.stringify(res.longBase));
  console.log('ふりがな あり :', JSON.stringify(res.longBaseR));
})();
