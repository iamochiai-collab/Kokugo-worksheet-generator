#!/usr/bin/env python3
"""漢字練習帳の 漢字の じょうほう(画数・音読み・訓読み)を つくる。

もとの データ: npm の joyo-kanji-counts(MIT、https://github.com/tkd-org/joyo-kanji)の db/chars.json
(常用漢字表の 音訓。カタカナ=音読み、ひらがな=訓読み、「-」の あとが 送りがな)。

  npm pack joyo-kanji-counts && tar xzf joyo-kanji-counts-*.tgz
  python3 tools/make_kanji_info.py package/db/chars.json

出力: src/data/kanji_info.json  {"漢": [画数, ["カン"], ["…"]], …}(小学校の 1026字だけ)
"""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
src = json.load(open(sys.argv[1], encoding='utf-8'))
grades = json.load(open(root / 'src/data/kanji_grades.json', encoding='utf-8'))
strokes = json.load(open(root / 'src/data/kanji_strokes.json', encoding='utf-8'))
out, miss = {}, []
for g in sorted(grades, key=int):
    for k in grades[g]:
        c = src.get(k)
        if not c:
            miss.append(k)
            continue
        # （　）つきは 常用漢字表で まれな 読み(上の「うわ」など)。練習帳には 出さない
        rs = [r for r in c['pronounce'].split('|') if r and not r.startswith(('（', '('))]
        on = [r for r in rs if '゠' <= r[0] <= 'ヿ']
        kun = [r for r in rs if not ('゠' <= r[0] <= 'ヿ')]
        n = int(c['stroke_count'])
        if k in strokes and len(strokes[k]) != n:
            print(f'  画数が ちがう: {k} {n} / 線 {len(strokes[k])}')
        out[k] = [n, on, kun]
# 熟語の れい:漢字の ドリル(words*.tsv)と 文章の ふりがな(ruby.json の {漢字|よみ})から、
# その 漢字の 学年までに 習う 漢字だけで 書ける 2字いじょうの ことばを 3つまで
import re
kg = {k: int(g) for g, ks in grades.items() for k in ks}
cand, freq, drill = {}, {}, set()
for f in sorted((root / 'src/data').glob('words*.tsv')):
    for line in open(f, encoding='utf-8'):
        if line.startswith('#') or '\t' not in line:
            continue
        w, r = line.rstrip('\n').split('\t')[:2]
        cand.setdefault(w, r)
        drill.add(w)
for v in json.load(open(root / 'src/data/ruby.json', encoding='utf-8')).values():
    for w, r in re.findall(r'\{([^|{}]+)\|([^{}]+)\}', v):
        cand.setdefault(w, r)
        freq[w] = freq.get(w, 0) + 1
# 文章の ふりがなは 区切りが ずれて いる ことが ある(右上がり → 右上|みぎあ)ので、
# 読みが 1字ずつの 音・訓(にごる・つまる も)で 組み立てられる ことばだけに する
K2H = str.maketrans({chr(c): chr(c - 0x60) for c in range(0x30A1, 0x30F7)})
DAKU = dict(zip('かきくけこさしすせそたちつてとはひふへほ', 'がぎぐげござじずぜぞだぢづでどばびぶべぼ'))
HANDAKU = dict(zip('はひふへほ', 'ぱぴぷぺぽ'))
# 文章から とる ことばは 音読みだけで 読める 熟語に する(訓どうしの ことばは 人の 名前や 送りがなの きれた もの が まじる)
def yomi(k):
    v = out.get(k)
    if not v:
        return set()
    base = {r.translate(K2H) for r in v[1]}
    more = set()
    for r in base:
        if r[0] in DAKU: more.add(DAKU[r[0]] + r[1:])
        if r[0] in HANDAKU: more.add(HANDAKU[r[0]] + r[1:])
        if len(r) >= 2 and r[-1] in 'つくちき': more.add(r[:-1] + 'っ')
    return base | more
def ok(w, r, i=0):
    if i == len(w):
        return r == ''
    return any(r.startswith(y) and ok(w, r[len(y):], i + 1) for y in yomi(w[i]))
NG = {'海王', '起死', '望気'}   # 話の 中の 名前・ことばの 一部
words = [(w, r) for w, r in cand.items() if w not in NG and len(w) >= 2 and all(c in kg for c in w) and (w in drill or ok(w, r))]
cnt = 0
for k, v in out.items():
    g = kg[k]
    ex = [(w, r) for w, r in words if k in w and max(kg[c] for c in w) <= g]
    # ドリルの ことば → 文章に よく 出る ことば(2回いじょう) → 2字の ことば の じゅん
    ex = [x for x in ex if x[0] in drill or freq.get(x[0], 0) >= 3]
    ex.sort(key=lambda x: (x[0] not in drill, -freq.get(x[0], 0), len(x[0]) != 2, x[0]))
    v.append([f'{w}|{r}' for w, r in ex[:3]])
    cnt += bool(ex)
print('熟語の れいが ある 字:', cnt)
json.dump(out, open(root / 'src/data/kanji_info.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('kanji_info.json:', len(out), '字', '/ ない:', ''.join(miss))
