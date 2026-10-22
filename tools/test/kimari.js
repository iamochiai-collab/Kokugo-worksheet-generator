// ことばの きまりの プリントを ぜんぶ 作って、A4 1枚に 入るか・問題の 数・答えが 正しく 出るかを しらべる
//   node tools/test/kimari.js
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
    // ローマ字は 大文字(rcase: upper)でも しらべる
    // ふりがな(すべて)・ひらがな(習って いない 漢字)でも しらべる(シードは 少なめ)
    const jobs = [];
    for (const t of T.KM) for (const g of t.grades) {
      for (const rcase of t.id.startsWith('romaji') ? ['lower', 'upper'] : ['lower']) for (let seed = 1; seed <= 40; seed++) jobs.push([t, g, rcase, 'normal', seed, 'std']);
      // ローマ字の 書き方(ハイフン・1音ずつ)
      if (t.id.startsWith('romaji')) for (const rstyle of ['hyp', 'sep']) for (let seed = 1; seed <= 30; seed++) jobs.push([t, g, 'upper', 'normal', seed, rstyle]);
      if (!t.nofuri) for (const kfuri of ['all', 'kana']) for (let seed = 1; seed <= 12; seed++) jobs.push([t, g, 'lower', kfuri, seed, 'std']);
    }
    for (const [t, g, rcase, kfuri, seed, rstyle] of jobs) {
      const s = T.buildKimariSheet({ grade: g, ktopic: t.id, seed, no: 1, rcase, kfuri, klearn: 'prev', rstyle });
      const where = `${t.id} 小${g}${rcase === 'upper' ? ' 大文字' : ''}${kfuri && kfuri !== 'normal' ? ' ' + kfuri : ''}${rstyle && rstyle !== 'std' ? ' ' + rstyle : ''} seed${seed}`;
      // «»が のこって いないか・えらぶ ものが 同じに なって いないか
      for (const sec of s.sections) for (const it of sec.items) for (const q of it.parts || []) {
        if (JSON.stringify(q).includes('«')) bad.push(`${where}: «» が のこって いる`);
        if (q[0] === 'c' && new Set(q[1]).size !== q[1].length) bad.push(`${where}: えらぶ ものが 同じ ${q[1].join('/')}`);
      }
      // 大問を こえて 同じ 問題(答えが わかって しまう もの)が 出て いないか
      const keyOf = (parts) => {
        const k = parts.find((p) => p[0] === 'k');
        if (k) return '#' + k[1];
        const br = parts.findIndex((p) => p[0] === 'br');
        return (br < 0 ? parts : parts.slice(0, br)).map((p) => (p[0] === 't' || p[0] === 'u' || p[0] === 'w' || p[0] === 'wl' ? p[1] : p[0] === 'c' ? p[1][p[2]] : p[0] === 'tr' ? p[1].join(' ') : '')).join('').replace(/[\s　。、]/g, '');
      };
      const seen = new Set();
      for (const sec of s.sections) for (const it of sec.items) if (it.parts) {
        const k = keyOf(it.parts);
        if (seen.has(k)) bad.push(`${where}: 同じ 問題が 2回 (${k})`);
        seen.add(k);
      }
      s.sections.forEach((sec, i) => {
        if (sec.items.length !== t.sections[i].n) bad.push(`${where}: 大問${i + 1} が ${sec.items.length} 問`);
        for (const it of sec.items) {
          if (it.order && it.show.every((v, k) => v === k)) bad.push(`${where}: じゅんばんが まざって いない`);
          for (const q of it.parts || []) if (q[0] === 'c' && !(q[2] >= 0 && q[2] < q[1].length)) bad.push(`${where}: ○の 答えが ない`);
        }
        if (sec.bank) for (const it of sec.items) for (const q of it.parts || [])
          if (q[0] === 'w' && !sec.bank.includes(q[1])) bad.push(`${where}: 語群に ${q[1]} が ない`);
      });
      for (const answer of [false, true]) {
        host.innerHTML = T.kimariSheetHtml(s, { answer });
        const el = host.querySelector('.sheet');
        el.style.transform = '';
        const h = el.scrollHeight / mm;
        n++;
        if (h > maxH) { maxH = h; worst = where + (answer ? ' 答え' : ''); }
        if (h > 297.5) bad.push(`${where}${answer ? ' 答え' : ''}: ${h.toFixed(1)}mm`);
        if (el.scrollWidth > el.clientWidth + 2) bad.push(`${where}: よこに はみ出し`);
        // 大問の 中で 問題が はみ出して いないか
        el.querySelectorAll('.km-sec, .km-items').forEach((box) => { if (box.scrollHeight > box.clientHeight + 2) bad.push(`${where}: 大問の 中が つまって いる`); });
        const secs = [...el.querySelectorAll('.km-sec')];
        for (let k = 1; k < secs.length; k++) if (secs[k].getBoundingClientRect().top < secs[k - 1].getBoundingClientRect().bottom - 1) bad.push(`${where}: 大問が かさなって いる`);
        if (answer) {
          const want = s.sections.flatMap((sec) => sec.items.flatMap((it) => it.order ? it.order : (it.parts || []).filter((q) => q[0] === 'w' || q[0] === 'wl' || q[0] === 'c' || (q[0] === 'b' && q[1])))).length;
          const got = el.querySelectorAll('.ans, .km-ch .o.ok').length;
          if (got !== want) bad.push(`${where}: 答えが ${got}/${want}`);
        } else if (el.querySelector('.ans')) bad.push(`${where}: 問題の ページに 答えが ある`);
      }
    }
    return { n, maxH, worst, bad };
  });
  await b.close();
  console.log(`ことばの きまり ${res.n} 枚  いちばん 高い ${res.maxH.toFixed(1)}mm (${res.worst})`);
  if (res.bad.length) {
    console.log(`NG ${res.bad.length} 件`);
    const by = {};
    for (const x of res.bad) { const k = x.split(' ')[0] + ' ' + x.split(': ')[1].replace(/[\d.]+mm/, 'mm'); by[k] = (by[k] || 0) + 1; }
    console.log(Object.entries(by).map(([k, v]) => `   ${k} ×${v}`).join('\n'));
    [...new Set(res.bad)].slice(0, 30).forEach((x) => console.log(' -', x));
    process.exit(1);
  }
  console.log('OK ことばの きまりの プリントは どれも 1枚に 入り、答えも そろっています');
})();
