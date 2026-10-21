// 読み・書きの 数の くみあわせを ぜんぶ 作って、A4 1枚に 入るか・問題数が 合うかを しらべる
// node tools/test/counts.js [build/test.html]
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const file = 'file://' + path.resolve(process.argv[2] || 'build/test.html');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1100, height: 1400 } });
  await page.goto(file);
  const res = await page.evaluate(() => {
    const T = window.__T;
    const host = document.getElementById('sheets');
    document.body.dataset.view = 'sheet';
    const mm = 96 / 25.4;
    const bad = [];
    let n = 0, maxH = 0, worst = '', combos = 0;
    const jobs = [];
    for (const kind of ['both', 'tk', 'long']) {  // tk = 大きい 字(1れつ)
      const grades = kind === 'long' ? Object.keys(T.READS).map(Number) : [1, 2, 3, 4, 5, 6, 7];
      // 長文は ふりがな なし と すべての 漢字に ふりがな(いちばん 高く なる)の 両方を 調べる
      for (const furi of kind === 'long' ? ['none', 'all'] : ['none'])
      for (const g of grades)
      // 長文は ジャンル(すべて・物語・説明文・評論)ごとにも 調べる
      for (const genre of kind === 'long' ? T.genresOf(g).map(([k]) => k) : ['all']) {
        const L = T.layoutOf(kind, g, furi, genre);
        for (let r = 0; r <= L.top; r += 2)
          for (let w = 0; w <= L.top; w += 2)
            if ((kind === 'long' || r + w > 0) && T.fits(kind, r, w, g, furi, genre)) {
              // 長文は いちばん きびしい(どちらも これ以上 ふやせない)くみあわせと 0・0 だけ 全部の 話で 調べる
              const edge = !T.fits(kind, r + 2, w, g, furi, genre) && !T.fits(kind, r, w + 2, g, furi, genre);
              if (kind !== 'long' || edge || (r === 0 && w === 0)) jobs.push([kind, g, r, w, furi, genre]);
            }
      }
    }
    combos = jobs.length;
    for (const [kind, g, r, w, furi, genre] of jobs) {
      // 長文は 話が いくつも あるので、シードを 全部の 話に 回す
      const seeds = kind === 'long' ? Array.from({ length: T.storiesOf(g, genre).length }, (_, i) => i + 1) : [1, 2];
      for (const level of kind === 'long' ? [2] : [1, 3]) for (const seed of seeds) {
        // 子どもの 学年は 1(ふりがなが いちばん 多く つく)、長文の 学年は g
        const s = T.buildSheet({ grade: furi === 'none' ? g : 1, gRead: g, gWrite: g, gStory: g, furi,
                                 kind: kind === 'tk' ? 'both' : kind, tk: kind === 'tk', level, seed, no: 1, nRead: r, nWrite: w, genre });
        if (kind === 'long' && genre !== 'all' && s.story.genre !== genre)
          bad.push(`${kind} 学年${g} ${genre} seed${seed}: ジャンルが ${s.story.genre}`);
        for (const answer of [false, true]) {
          host.innerHTML = T.sheetHtml(s, { answer });
          const el = host.querySelector('.sheet');
          el.style.transform = '';
          const h = el.scrollHeight / mm;
          n++;
          const where = `${kind} 学年${g} ${genre} ふりがな${furi} 読み${r} 書き${w} seed${seed}${answer ? ' 答え' : ''}`;
          if (h > maxH) { maxH = h; worst = where; }
          if (h > 297.5) bad.push(`${where}: ${h.toFixed(1)}mm`);
          const items = el.querySelectorAll('.item').length;
          if (items !== r + w) bad.push(`${where}: 問題が ${items} 問`);
        }
      }
    }
    return { n, combos, maxH, worst, bad };
  });
  await browser.close();
  console.log(`学年×くみあわせ ${res.combos} 通り / プリント ${res.n} 枚  いちばん 高い ${res.maxH.toFixed(1)}mm (${res.worst})`);
  if (res.bad.length) {
    console.log(`NG ${res.bad.length} 件`);
    res.bad.slice(0, 30).forEach((b) => console.log(' -', b));
    process.exit(1);
  }
  console.log('OK どの くみあわせも 1枚に 入り、問題数も 合っています');
})();
