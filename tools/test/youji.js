// ようじの プリントを ぜんぶ 作って、A4 1枚に 入るか・ことば あそびの 答えが 正しいかを しらべる
//   node tools/test/youji.js
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1100, height: 1400 } });
  await p.goto('file://' + path.resolve(process.argv[2] || 'build/test.html'));
  await p.evaluate(() => document.fonts.ready);
  const res = await p.evaluate(() => {
    const T = window.__T;
    const host = document.getElementById('sheets');
    document.body.dataset.view = 'sheet';
    const mm = 96 / 25.4;
    const bad = [];
    let n = 0, maxH = 0, worst = '';
    const words = new Set(T.YPOOL.map((x) => x.w));
    const SMALL = { 'ゃ': 'や', 'ゅ': 'ゆ', 'ょ': 'よ', 'っ': 'つ' };
    const last = (w) => SMALL[w[w.length - 1]] || w[w.length - 1];
    const jobs = [];
    T.YD.hira.forEach((_, i) => jobs.push({ ykind: 'hira', yrow: String(i), seed: 1 }));
    T.YD.kata.forEach((_, i) => jobs.push({ ykind: 'kata', yrow: String(i), seed: 1 }));
    T.YD.themes.forEach((_, i) => jobs.push({ ykind: 'word', ytheme: String(i), seed: 1 }));
    for (const yplay of ['shiri', 'search', 'miss', 'sort'])
      for (let seed = 1; seed <= 60; seed++) jobs.push({ ykind: 'play', yplay, seed });
    for (const j of jobs) {
      const s = T.buildYoujiSheet(Object.assign({ no: 1 }, j));
      const where = `${j.ykind} ${j.yrow || j.ytheme || j.yplay || ''} seed${j.seed}`;
      // 答えの しらべ
      if (s.play === 'shiri') {
        if (s.data.chains.length !== 4) bad.push(`${where}: しりとりが ${s.data.chains.length} つ`);
        for (const c of s.data.chains) for (let i = 1; i < c.length; i++)
          if (c[i][0] !== last(c[i - 1]) || c[i].endsWith('ん')) bad.push(`${where}: ${c[i - 1]}→${c[i]}`);
      } else if (s.play === 'search') {
        if (s.data.words.length !== 6) bad.push(`${where}: ことばが ${s.data.words.length}`);
        for (const w of s.data.words) if (w.cells.map(([y, x]) => s.data.grid[y][x]).join('') !== w.w) bad.push(`${where}: ${w.w} が ない`);
      } else if (s.play === 'miss') {
        if (s.data.items.length !== 8) bad.push(`${where}: ${s.data.items.length} 問`);
        for (const it of s.data.items) {
          if (it.choices[it.a] !== it.w[it.at]) bad.push(`${where}: ${it.w} の 答え`);
          it.choices.forEach((c, k) => { if (k !== it.a && words.has(it.w.slice(0, it.at) + c + it.w.slice(it.at + 1))) bad.push(`${where}: ${it.w} 答えが 2つ`); });
        }
      } else if (s.play === 'sort') {
        if (s.data.items.length !== 6) bad.push(`${where}: ${s.data.items.length} 問`);
        for (const it of s.data.items) if (it.letters.join('') === it.w || [...it.letters].sort().join('') !== [...it.w].sort().join('')) bad.push(`${where}: ${it.w}`);
      }
      for (const answer of [false, true]) {
        if (answer && j.ykind !== 'play') continue;
        host.innerHTML = T.youjiSheetHtml(s, { answer });
        const el = host.querySelector('.sheet');
        el.style.transform = '';
        const h = el.scrollHeight / mm;
        n++;
        if (h > maxH) { maxH = h; worst = where + (answer ? ' こたえ' : ''); }
        if (h > 297.5) bad.push(`${where}${answer ? ' こたえ' : ''}: ${h.toFixed(1)}mm`);
        if (el.scrollWidth > el.clientWidth + 2) bad.push(`${where}: よこに はみ出し`);
      }
    }
    return { n, maxH, worst, bad };
  });
  await b.close();
  console.log(`ようじ プリント ${res.n} 枚  いちばん 高い ${res.maxH.toFixed(1)}mm (${res.worst})`);
  if (res.bad.length) {
    console.log(`NG ${res.bad.length} 件`);
    res.bad.slice(0, 30).forEach((x) => console.log(' -', x));
    process.exit(1);
  }
  console.log('OK ようじの プリントは どれも 1枚に 入り、答えも 合っています');
})();
