"""長文の データに ふりがなを つけて src/data/ruby.json を 作る。

  pip install 'fugashi[unidic-lite]'      # 形態素解析(はじめに 1回)
  python3 tools/furigana.py

src/data/read*.json の 本文・問い・選択肢・語句を 形態素解析して、
漢字の ところに 読みを つける。結果は「もとの 文 → ふりがなつきの 文」の 表で、
ふりがなつきの 文は {漢字|かんじ} の 形で 書く。アプリは ふりがなを つける ときだけ これを 使う。

読みまちがいを 見つけたら、下の FIX に「語: 読み」を 足して もう一度 走らせる。
"""
import json, pathlib, re, sys

import fugashi

root = pathlib.Path(__file__).resolve().parent.parent
KANJI_CH = r'㐀-䶿一-鿿豈-﫿々〆ヶ'
HAS_KANJI = re.compile(f'[{KANJI_CH}]')
RUN = re.compile(f'([{KANJI_CH}]+|[^{KANJI_CH}]+)')

# 形態素解析が まちがえやすい 読み(この 教材の 文での 読み)
FIX = {
    '一日': 'いちにち', '何回': 'なんかい', '何度': 'なんど', '何日': 'なんにち', '何年': 'なんねん',
    '何人': 'なんにん', '何本': 'なんぼん', '何千': 'なんぜん', '何十': 'なんじゅう', '何時': 'なんじ',
    '一人': 'ひとり', '二人': 'ふたり', '大人': 'おとな', '今日': 'きょう', '明日': 'あした',
    '昨日': 'きのう', '今年': 'ことし', '上手': 'じょうず', '下手': 'へた', '一番': 'いちばん',
    'お兄さん': 'おにいさん', '兄さん': 'にいさん', '姉さん': 'ねえさん', '母さん': 'かあさん', '父さん': 'とうさん',
    '一人一人': 'ひとりひとり', '一つ一つ': 'ひとつひとつ', '大輔': 'だいすけ',
    '昔': 'むかし', '風流': 'ふうりゅう', '最中': 'さいちゅう', '目じるし': 'めじるし', '五色': 'ごしょく',
    '来なさい': 'きなさい', '「望」': '「ぼう」', '振り返': 'ふりかえ', '半月': 'はんげつ', '汚す': 'よごす',
    '一行も': 'いちぎょうも', '既読': 'きどく', '私': 'わたし',
    '七月七日': 'しちがつなのか', '四日': 'よっか', '四十日': 'よんじゅうにち', 'なん日': 'なんにち', '生日': 'じょうび',
    '一本': 'いっぽん', '三本': 'さんぼん', '四本': 'よんほん', '五本': 'ごほん', '六本': 'ろっぽん', '八本': 'はっぽん',
    '四つ': 'よっつ', '六つ': 'むっつ', '四かく': 'しかく', '一まわり': 'ひとまわり', '一さじ': 'ひとさじ', '下で': 'したで', '二本': 'にほん', 'なん本': 'なんぼん', '七がつ': 'しちがつ', '言う': 'いう', '丸い': 'まるい', '八つ': 'やっつ', '千本': 'せんぼん', '百本': 'ひゃっぽん', '十本': 'じっぽん', '米': 'こめ', 'つくえの 下': 'つくえの した', '日本': 'にほん', '七星': 'しちせい', '白色': 'しろいろ', '公みん館': 'こうみんかん', '発こう': 'はっこう', '立こうほ': 'りっこうほ', '五音': 'ごおん', '半日': 'はんにち', 'きん止': 'きんし', '法りつ': 'ほうりつ', '正しく': 'ただしく', '円つなぎ': 'えんつなぎ', '何位': 'なんい', '競ぎ': 'きょうぎ', '黒えん': 'こくえん', '便として': 'べんとして', '便を': 'べんを', 'ちょ金箱': 'ちょきんばこ', '塩水': 'しおみず', '中南米': 'ちゅうなんべい', '宝物': 'たからもの', '町中を': 'まちじゅうを', '絹糸': 'きぬいと', '中谷': 'なかや', '亮': 'りょう', '大樹': 'だいき', '素ぶり': 'すぶり', '家で飼': 'いえでか', '何千枚': 'なんぜんまい', '「希」': '「き」',
}


def hira(s):
    return ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s)


def align(surface, reading):
    """「読ん」+「よん」→ [('読', 'よ'), ('ん', None)] のように 漢字の ところだけに 読みを わりあてる"""
    runs = RUN.findall(surface)
    pat = ''.join('(.+?)' if HAS_KANJI.match(r) else re.escape(hira(r)) for r in runs)
    m = re.fullmatch(pat, reading)
    if not m:
        return [(surface, reading)]
    out, i = [], 0
    for r in runs:
        if HAS_KANJI.match(r):
            i += 1
            out.append((r, m.group(i)))
        else:
            out.append((r, None))
    return out


tagger = fugashi.Tagger()


def tokens(text):
    """FIX の 語を さきに さがして、のこりを 形態素解析する"""
    keys = sorted(FIX, key=len, reverse=True)
    pos, out = 0, []
    pat = re.compile('|'.join(map(re.escape, keys)))
    for m in pat.finditer(text):
        out += tag(text[pos:m.start()])
        out += align(m.group(0), FIX[m.group(0)])
        pos = m.end()
    out += tag(text[pos:])
    return out


def tag(text):
    out, pos = [], 0
    for w in tagger(text):
        s = w.surface
        # 形態素解析は 空白を 消すので、もとの 文を たどって 空白も そのまま のこす
        i = text.find(s, pos)
        if i < 0:
            continue
        if i > pos:
            out.append((text[pos:i], None))
        pos = i + len(s)
        k = getattr(w.feature, 'kana', None)
        if not HAS_KANJI.search(s) or not k or k == '*':
            out.append((s, None))
        else:
            out += align(s, hira(k))
    if pos < len(text):
        out.append((text[pos:], None))
    return out


def markup(text):
    segs = tokens(text)
    plain = ''.join(s for s, _ in segs)
    if plain != text:                     # 空白などが ずれたら、ふりがなを あきらめて もとの 文に する
        return None
    return ''.join(f'{{{s}|{r}}}' if r else s for s, r in segs)


table, lost = {}, []
for path in sorted(root.glob('src/data/read*.json')):
    for d in json.loads(path.read_text(encoding='utf-8')):
        texts = [d['passage']] + [q['q'] for q in d['questions']] + \
                [c for q in d['questions'] for c in q['c']] + d['vocab']
        for t in texts:
            if t in table or not HAS_KANJI.search(t):
                continue
            m = markup(t)
            if m is None:
                lost.append(t[:30])
            else:
                table[t] = m

pathlib.Path(root / 'src' / 'data' / 'ruby.json').write_text(
    json.dumps(table, ensure_ascii=False, indent=0) + '\n', encoding='utf-8')
print(f'ruby.json: {len(table)} 文に ふりがな', f'(あきらめた {len(lost)} 文)' if lost else '')
for t in lost[:10]:
    print('  -', t)
