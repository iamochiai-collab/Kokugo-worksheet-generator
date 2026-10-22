"""ローマ字の 単元(①〜⑫)を 作って src/data/kimari.txt の ローマ字の ところを 書きかえる。

  python3 tools/make_romaji.py && python3 tools/build.py

ことばは 下の WORDS(ひらがな)に 足すだけ。訓令式・ヘボン式の つづりは 自動で 作り、
つかって いる 音(行・にごる 音・ねじれる 音・つまる 音・のばす 音・はねる 音)で 単元に わける。
  ⑤ あ・か・さ・た・な行だけ  ⑥ は・ま・や・ら・わ行・ん まで  ⑦ にごる 音・半だく音
  ⑧ ねじれる 音  ⑨ のばす 音・つまる 音・はねる 音  ⑫ ぜんぶ
のばす 音は、お段+う・お段+お・う段+う・あ段+あ・い段+い・え段+え を ^ に する(えい は ei)。
"""
import pathlib, random, re

root = pathlib.Path(__file__).resolve().parent.parent

# ---- ことば(ひらがな)。名詞を 中心に、子どもが 知って いる ことば ----
WORDS = '''
あい あお いえ うえ おい えい あおい
かさ いけ あさ すいか たこ なつ ねこ いぬ きつね さかな くつ あし なす たね そと かき かお せき あき いか
うし おに かに くち こし さけ しか すし せなか たき たけ つくえ つの つな なか なし にく ぬの のき おかし
おなか かたな きのこ くさ こたつ えき いす うち おけ きく くき こい すな たいこ とけい にし いと うた
かいすいよく? おかき せかい そこ ちいさい? つき てつ とし なかま 
あたま うさぎ えのぐ おもち かえる きりん くじら けむし こいぬ さくら しろ すみれ せみ そら たぬき
ちず つばめ てがみ とり なべ にわとり ぬいぐるみ ねずみ のり はさみ ひよこ ふね へび ほし まめ みかん
むし めがね もも やま ゆき よる らくだ りす わに はな ひも ふえ へや ほん まど みみ むね めだか もり
やね ゆび よこ りんご ろば わなげ あめ うみ えほん かめ くま くも くり こま さる しま はし はち ひと
ふく へそ ほたる まくら みそ むかし もち やさい ゆめ りか れきし わた からす いのしし はなび ほたて
みなと めろん? さいふ たまねぎ にんじん れんこん からて てまり あみ いね おふろ かみ くわ さら
がっこう げた ごま ざる じてんしゃ ずかん ぜんまい ぞう だんご でんわ どんぐり ばった びん ぶた
べんとう ぼうし ぺんぎん かぎ ひざ かぜ まど ごはん かば えんぴつ てんぷら うで おでこ かがみ ぶどう
かぶとむし どんぶり かばん かいだん がけ ぎんなん すずめ ずぼん だるま でぐち どうぐ はなぢ みかづき
きゃべつ きゅうり きょうりゅう しゃしん しゅくだい ちゃわん ちょうちょ ひゃく りゅう りょかん
ぎゅうにゅう じゃんけん じゅんばん じょうろ びょういん きんぎょ おもちゃ いしゃ でんしゃ にんじゃ
きょり ちゅうしゃ しょくじ おちゃ じゃがいも きゃく さんしょ しゅみ りょうり みゃく? ひょう
てんいん ほんや きんえん げんいん まんいん こんや ぜんいん しんゆう きんようび げんかんや? さんいん?
おかあさん おとうさん おにいさん おねえさん こおり くうき ひこうき ゆうき きのう ほうき とうふ
ふうせん すうじ こうえん おおかみ とおり おうさま ろうか どうぶつ ようふく ほうたい ゆうがた
きって らっぱ にっき せっけん はっぱ しっぽ ねっこ きっぷ ざっし らっこ かっぱ ほっぺ がっき
しゃもじ ちゃいろ じゃり きょねん ちょきん しゃこ しゅるい にんぎょ おしゃれ かしゅ ぎゃく しゃち じゃま しゃみせん
きんじょ かいしゃ ひゃくえん ぎょうざ でんきゅう しょうゆ
ほっきょく きっさてん こっか さっか いっぱい しゅっぱつ はっけん びっくり まっか まっしろ まっくら けっこん
らっかせい いっしょ みっか
'''
WORDS = list(dict.fromkeys(w for w in WORDS.split() if '?' not in w))   # 重なりは 1つに

ROW = {}
for row, chars in {'': 'あいうえお', 'k': 'かきくけこ', 's': 'さしすせそ', 't': 'たちつてと', 'n': 'なにぬねの',
                   'h': 'はひふへほ', 'm': 'まみむめも', 'y': 'やゆよ', 'r': 'らりるれろ', 'w': 'わを',
                   'g': 'がぎぐげご', 'z': 'ざじずぜぞ', 'd': 'だぢづでど', 'b': 'ばびぶべぼ', 'p': 'ぱぴぷぺぽ'}.items():
    for c in chars:
        ROW[c] = row
VOWEL = {}
for v, chars in zip('aiueo', ['あかさたなはまやらわがざだばぱ', 'いきしちにひみりぎじぢびぴ', 'うくすつぬふむゆるぐずづぶぷ',
                               'えけせてねへめれげぜでべぺ', 'おこそとのほもよろをごぞどぼぽ']):
    for c in chars:
        VOWEL[c] = v
KUN = {'し': 'si', 'ち': 'ti', 'つ': 'tu', 'ふ': 'hu', 'じ': 'zi', 'ぢ': 'zi', 'づ': 'zu', 'を': 'o', 'ん': 'n'}
HEP = {'し': 'shi', 'ち': 'chi', 'つ': 'tsu', 'ふ': 'fu', 'じ': 'ji', 'ぢ': 'ji', 'づ': 'zu', 'を': 'o', 'ん': 'n'}
CIRC = {'a': 'â', 'i': 'î', 'u': 'û', 'e': 'ê', 'o': 'ô'}


def syll(c, hep):
    t = HEP if hep else KUN
    if c in t: return t[c]
    return ROW[c] + VOWEL[c]


def morae(w):
    """「きゃ」のような ねじれる 音を 1つに まとめた 音の ならび"""
    out, i = [], 0
    while i < len(w):
        if i + 1 < len(w) and w[i + 1] in 'ゃゅょ':
            out.append(w[i:i + 2]); i += 2
        else:
            out.append(w[i]); i += 1
    return out


def mora_roman(m, hep):
    if len(m) == 2:                     # ねじれる 音
        base = syll(m[0], hep)          # ki / si(shi) / ti(chi) / zi(ji)
        y = {'ゃ': 'a', 'ゅ': 'u', 'ょ': 'o'}[m[1]]
        if hep and base in ('shi', 'chi', 'ji'):
            return base[:-1] + y        # sha / cha / ja
        return base[:-1] + 'y' + y      # kya / sya / tya / zya
    return syll(m, hep)


def roman(w, hep=False):
    ms = morae(w)
    out, i = '', 0
    while i < len(ms):
        m = ms[i]
        if m == 'っ':
            nxt = mora_roman(ms[i + 1], hep)
            out += 't' if (hep and nxt.startswith('ch')) else nxt[0]
            i += 1
            continue
        r = mora_roman(m, hep)
        if m == 'ん' and i + 1 < len(ms):
            n0 = mora_roman(ms[i + 1], hep)
            if n0[0] in 'aiueoy':
                r = "n'"
        # のばす 音
        if i + 1 < len(ms) and r[-1] in 'aiueo':
            v, nx = r[-1], ms[i + 1]
            if (v == 'o' and nx in 'うお') or (v == 'u' and nx == 'う') or (v == 'a' and nx == 'あ') \
               or (v == 'i' and nx == 'い') or (v == 'e' and nx == 'え'):
                out += r[:-1] + CIRC[v]
                i += 2
                continue
        out += r
        i += 1
    return out


def roman_hyphen(w, hep=False):
    """のばす 音を - に(ノート → no-to)、「ん」の 区切りも - に(てんいん → ten-in)"""
    r = roman(w, hep)
    for a, b in CIRC.items():
        r = r.replace(b, a + '-')
    return r.replace("'", '-')


def roman_sep(w, hep=False):
    """1音ずつ 区切る(てんいん → te n i n、きって → ki t te、おかあさん → o ka a sa n)"""
    ms = morae(w)
    out = []
    for i, m in enumerate(ms):
        if m == 'っ':
            nxt = mora_roman(ms[i + 1], hep) if i + 1 < len(ms) else 't'
            out.append('t' if (hep and nxt.startswith('ch')) else nxt[0])
        elif m in (' ', '　'):
            out.append('　')
        else:
            out.append(mora_roman(m, hep))
    return ' '.join(out).replace(' 　 ', '　')


def M(w, hep=False, capital=False):
    """3つの 書き方を «教科書¦ハイフン¦1音ずつ» に まとめる(アプリが えらぶ)"""
    words = w.split(' ')
    def cp(x):
        return x[:1].upper() + x[1:] if capital else x
    a = ' '.join(cp(roman(x, hep)) for x in words)
    b = ' '.join(cp(roman_hyphen(x, hep)) for x in words)
    c = '　'.join(cp(roman_sep(x, hep)) for x in words)
    return f'«{a}¦{b}¦{c}»'


def feats(w):
    ms = morae(w)
    r = roman(w)
    rows = {ROW[c] for c in w if c in ROW}
    return {
        'rows': rows,
        'daku': bool(rows & set('gzdbp')),
        'you': any(len(m) == 2 for m in ms),
        'soku': 'っ' in w,
        'long': any(c in r for c in 'âîûêô'),
        'apos': "'" in r,
        'n': 'ん' in w,
    }


def unit_of(w):
    f = feats(w)
    if f['long'] or f['soku'] or f['apos']: return 9
    if f['you']: return 8
    if f['daku']: return 7
    if f['n'] or f['rows'] & set('hmyrw'): return 6
    if f['rows'] <= {'', 'k', 's', 't', 'n'}: return 5 if f['rows'] - {''} else 4
    return 12


def rows_for(unit):
    return [w for w in WORDS if unit_of(w) == unit]


# ---- ⑪ ヘボン式: 訓令式と ちがう つづりの ことば(のばす 音は つかわない) ----
HEPW = [w for w in WORDS if roman(w) != roman(w, True) and not feats(w)['long'] and len(roman(w, True)) <= 10]
PLACES = [('ちば', 'Chiba'), ('つくば', 'Tsukuba'), ('しが', 'Shiga'), ('ふくおか', 'Fukuoka'), ('ひろしま', 'Hiroshima'),
          ('しずおか', 'Shizuoka'), ('ふくしま', 'Fukushima'), ('いしかわ', 'Ishikawa'), ('ぎふ', 'Gifu'), ('かごしま', 'Kagoshima'),
          ('しまね', 'Shimane'), ('とちぎ', 'Tochigi'), ('やまぐち', 'Yamaguchi'), ('やまなし', 'Yamanashi'), ('しんじゅく', 'Shinjuku'),
          ('しぶや', 'Shibuya'), ('ふじさん', 'Fujisan')]

# ---- ⑩ 大文字: 地名(訓令式で si・ti・tu・hu・zi を ふくまない もの)と 人の 名前 ----
TOWNS = 'なごや きょうと おおさか さっぽろ せんだい よこはま なら こうべ くまもと ながさき おきなわ かながわ おかやま ' \
        'やまがた あきた あおもり いわて みやぎ かがわ えひめ さが みやざき とっとり とやま ながの さいたま いばらき ぐんま みえ ' \
        'わかやま ひょうご'.split()
FAMILY = 'やまだ たなか さとう すずき いとう わたなべ なかむら かとう やまもと ささき きむら もり いけだ あべ まえだ おかだ ' \
         'はせがわ むらかみ こんどう さかもと えんどう あおき おおた みうら おかもと なかがわ なかの はらだ おの たむら かねこ ' \
         'わだ なかやま うえだ もりた さかい くどう よこやま みやざき みやもと'.split()
GIVEN = 'たろう はなこ けんた ゆい はると さくら りく みお そうた ひな れん あおい ゆうと めい かいと りん みなと ゆな だいき なな'.split()
cap = lambda s: ' '.join(x[:1].upper() + x[1:] for x in s.split(' '))


NV = {'あ': 'な', 'い': 'に', 'う': 'ぬ', 'え': 'ね', 'お': 'の', 'や': 'にゃ', 'ゆ': 'にゅ', 'よ': 'にょ'}
BIG = {'ゃ': 'や', 'ゅ': 'ゆ', 'ょ': 'よ'}


def spell_wrong(w):
    """まちがえやすい 書き方を かなで 作る(っを わすれる・のばす 音を わすれる・「ん」の 区切りを わすれる・ゃを や に)"""
    c = []
    if 'っ' in w: c.append(w.replace('っ', '', 1))
    ms = morae(w)
    for i in range(len(ms) - 1):          # のばす 音を おとす(おかあさん → おかさん)
        if ms[i] in ('っ', 'ん') or ms[i + 1] in ('っ', 'ん'):
            continue
        r = mora_roman(ms[i], False)
        if r[-1] in 'aiueo' and roman(ms[i] + ms[i + 1]) != r + mora_roman(ms[i + 1], False):
            c.append(''.join(ms[:i + 1] + ms[i + 2:])); break
    for i in range(len(w) - 1):           # てんいん → てにん
        if w[i] == 'ん' and w[i + 1] in NV:
            c.append(w[:i] + NV[w[i + 1]] + w[i + 2:]); break
    for i in range(len(w) - 1):           # きゃべつ → きやべつ
        if w[i + 1] in BIG and w[i] not in 'ん':
            c.append(w[:i + 1] + BIG[w[i + 1]] + w[i + 2:]); break
    return [x for x in dict.fromkeys(c) if x != w]


def kana_choice_items(chars):
    """1つの 音の ローマ字を えらぶ(か → {*ka|ki|ko})と、その ぎゃく(ka → {*か|き|こ})"""
    out = []
    rnd = random.Random(7)
    pool = [c for c in chars]
    for c in pool:
        r = mora_roman(c, False)
        same = [mora_roman(x, False) for x in pool if x != c and mora_roman(x, False)[:-1] == r[:-1]]
        other = [mora_roman(x, False) for x in pool if x != c and mora_roman(x, False) not in same]
        opts = rnd.sample(same, min(2, len(same)))
        opts += rnd.sample(other, 2 - len(opts))
        out.append(f'{c}　{{*{r}|{"|".join(opts)}}}')
        ks = [x for x in pool if x != c]
        out.append(f'{r}　{{*{c}|{"|".join(rnd.sample(ks, 2))}}}')
    return out


def topic(tid, name, desc, sections):
    lines = [f'@ {tid} | 3 | {name} | {desc}']
    for head, items in sections:
        lines.append('== ' + head)
        lines += items
    return '\n'.join(lines) + '\n'


# 4本線に 書く ことば(2れつ)は、1音ずつ 区切っても 列に 入る 長さまで
fits = lambda w, hep=False: len(roman(w, hep)) <= 9 and len(roman_sep(w, hep)) <= 10


def word_sections(words, n_write=4, n_read=4):
    w2 = [w for w in words if len(roman(w)) <= 9]
    ww = [w for w in w2 if fits(w)]
    return [
        (f'ことばを 書く | つぎの ことばを ローマ字で 書きましょう。 | {n_write} | cols=2', [f'{w}　[={M(w)}] #{w}' for w in ww]),
        (f'ことばを 読む | ローマ字で 書いた ことばを ひらがなで 書きましょう。 | {n_read} | cols=2', [f'{M(w)}　[{w}] #{w}' for w in w2]),
    ]


ROWS5 = [('か き く け こ', 'ka ki ku ke ko'), ('さ し す せ そ', 'sa si su se so'), ('た ち つ て と', 'ta ti tu te to'), ('な に ぬ ね の', 'na ni nu ne no')]
ROWS6 = [('は ひ ふ へ ほ', 'ha hi hu he ho'), ('ま み む め も', 'ma mi mu me mo'), ('や ゆ よ', 'ya yu yo'), ('ら り る れ ろ', 'ra ri ru re ro'), ('わ を ん', 'wa o n')]
ROWS7 = [('が ぎ ぐ げ ご', 'ga gi gu ge go'), ('ざ じ ず ぜ ぞ', 'za zi zu ze zo'), ('だ ぢ づ で ど', 'da zi zu de do'), ('ば び ぶ べ ぼ', 'ba bi bu be bo'), ('ぱ ぴ ぷ ぺ ぽ', 'pa pi pu pe po')]
YOU = 'きしちにひみりぎじびぴ'
ROWS8 = [(' '.join(c + s for s in 'ゃゅょ'), ' '.join(mora_roman(c + s, False) for s in 'ゃゅょ')) for c in YOU]
trace = lambda rows: [f'{k} (({r}))' for k, r in rows]

out = []
LOWER = 'abcdefghijklmnopqrstuvwxyz'
out.append(topic('romaji01', 'ローマ字① アルファベット(小文字)', 'a〜z の 小文字を、4本の 線に 合わせて なぞって 書く。', [
    ('小文字を なぞる | 黒い 字を よく 見て、うすい 字を なぞりましょう。あいて いる ところにも 書きましょう。 | 26 | seq | cols=2 | nonum',
     [f'((!{c} {c} {c}))' for c in LOWER])]))
out.append(topic('romaji02', 'ローマ字② アルファベット(大文字)', 'A〜Z の 大文字を、4本の 線に 合わせて なぞって 書く。', [
    ('大文字を なぞる | 黒い 字を よく 見て、うすい 字を なぞりましょう。あいて いる ところにも 書きましょう。 | 26 | seq | cols=2 | nonum',
     [f'((!{c.upper()} {c.upper()} {c.upper()}))' for c in LOWER])]))

# ③ 大文字と 小文字: まぎらわしい 字を まぜる
CONF = {'a': 'deo', 'b': 'dpq', 'c': 'eoa', 'd': 'bpq', 'e': 'acf', 'f': 'tel', 'g': 'qjy', 'h': 'nkb', 'i': 'ljt', 'j': 'igy',
        'k': 'hxr', 'l': 'itj', 'm': 'nwu', 'n': 'mhu', 'o': 'acq', 'p': 'qbd', 'q': 'pgd', 'r': 'nkv', 's': 'zcx', 't': 'fli',
        'u': 'nvw', 'v': 'uwy', 'w': 'mvu', 'x': 'kyz', 'y': 'vgj', 'z': 'sxn'}
rnd = random.Random(3)
up_lo = [f'{c.upper()}　{{*{c}|{"|".join(rnd.sample(CONF[c], 2))}}} #{c}' for c in LOWER]
lo_up = [f'{c}　{{*{c.upper()}|{"|".join(x.upper() for x in rnd.sample(CONF[c], 2))}}} #{c}' for c in LOWER]
out.append(topic('romaji03', 'ローマ字③ 大文字と 小文字', 'A と a、B と b。大文字と 小文字を むすびつける。', [
    ('小文字を えらぶ | 大文字に 合う 小文字を ○で かこみましょう。 | 6 | cols=2', up_lo),
    ('大文字を えらぶ | 小文字に 合う 大文字を ○で かこみましょう。 | 4 | cols=2', lo_up),
    ('小文字で 書く | 大文字を 小文字で 書きましょう。 | 4 | cols=2', [f'{c.upper()}　[={c}] #{c}' for c in LOWER]),
    ('大文字で 書く | 小文字を 大文字で 書きましょう。 | 4 | cols=2', [f'{c}　[={c.upper()}] #{c}' for c in LOWER]),
]))

out.append(topic('romaji04', 'ローマ字④ あ行(a i u e o)', 'ローマ字の もとに なる 母音 a・i・u・e・o。', [
    ('あ行を なぞる | 黒い 字を よく 見て、うすい 字を なぞりましょう。 | 5 | seq', [f'{k}　((!{r} {r} {r} {r}))' for k, r in zip('あいうえお', 'aiueo')]),
    ('あ行の ローマ字 | 合う ほうを ○で かこみましょう。 | 4 | cols=2', kana_choice_items(list('あいうえお'))),
] + word_sections(rows_for(4), 4, 2)))
out.append(topic('romaji05', 'ローマ字⑤ か行・さ行・た行・な行', 'k・s・t・n に a・i・u・e・o を 組み合わせる。', [
    ('行を なぞる | うすい 字を なぞりましょう。 | 3 | seq', trace(ROWS5)),
    ('合う ローマ字 | 合う ものを ○で かこみましょう。 | 4 | cols=2', kana_choice_items(list('かきくけこさしすせそたちつてとなにぬねの'))),
] + word_sections(rows_for(5))))
out.append(topic('romaji06', 'ローマ字⑥ は行・ま行・や行・ら行・わ行・ん', 'h・m・y・r・w と、「ん」の n。', [
    ('行を なぞる | うすい 字を なぞりましょう。 | 3 | seq', trace(ROWS6)),
    ('合う ローマ字 | 合う ものを ○で かこみましょう。 | 4 | cols=2', kana_choice_items(list('はひふへほまみむめもやゆよらりるれろわん'))),
] + word_sections(rows_for(6))))
out.append(topic('romaji07', 'ローマ字⑦ が行・ざ行・だ行・ば行・ぱ行', 'にごる 音(g・z・d・b)と、半だく音(p)。', [
    ('行を なぞる | うすい 字を なぞりましょう。 | 3 | seq', trace(ROWS7)),
    ('合う ローマ字 | 合う ものを ○で かこみましょう。 | 4 | cols=2', kana_choice_items(list('がぎぐげござずぜぞだでどばびぶべぼぱぴぷぺぽ'))),
] + word_sections(rows_for(7))))
you_items = []
for c in YOU:
    for s in 'ゃゅょ':
        r = mora_roman(c + s, False)
        you_items.append(f'{c}{s}　{{*{r}|{r[0]}i{r[1:]}|{r[0]}{r[2]}}}')
out.append(topic('romaji08', 'ローマ字⑧ きゃ・しゅ・ちょ(ねじれる 音)', '小さい「ゃ・ゅ・ょ」の つく 音は y を 入れる。', [
    ('ねじれる 音を なぞる | うすい 字を なぞりましょう。 | 3 | seq', trace(ROWS8)),
    ('合う ローマ字 | 合う ものを ○で かこみましょう。 | 4 | cols=2', you_items),
] + word_sections(rows_for(8))))
w9 = rows_for(9)
longw = [w for w in w9 if feats(w)['long']]
sokuw = [w for w in w9 if feats(w)['soku'] and not feats(w)['long']]
aposw = [w for w in w9 if feats(w)['apos']]
nonap = 'ほんだな みかん ぶんか せんせい たんぽぽ さんぽ えんそく おんがく'.split()
choice = lambda w: f'{w}　{{*{M(w)}|{M(spell_wrong(w)[0])}}} #{w}'
out.append(topic('romaji09', 'ローマ字⑨ のばす 音・つまる 音・はねる 音',
                 'のばす 音・小さい「っ」・「ん」の 書き方。(教科書では のばす 音は ^、「ん」の 区切りは \')', [
    ('のばす 音 | 正しい ほうを ○で かこみましょう。 | 4 | cols=2', [choice(w) for w in longw]),
    ('つまる 音 | つぎの ことばを ローマ字で 書きましょう。 | 4 | cols=2', [f'{w}　[={M(w)}] #{w}' for w in sokuw if fits(w)]),
    ('はねる 音 | 正しい ほうを ○で かこみましょう。 | 4 | cols=2', [choice(w) for w in aposw] +
     [f'{w}　{{*{M(w)}|«{roman(w).replace("n", "n\'", 1)}¦{roman(w).replace("n", "n-", 1)}¦{roman_sep(w.replace("ん", "ぬ", 1))}»}} #{w}' for w in nonap]),
]))
towns = [f'(地名){t}　[={M(t, capital=True)}] #{t}' for t in TOWNS]
rnd = random.Random(5)
names = sorted({(f, g) for f in FAMILY for g in GIVEN}, key=lambda x: rnd.random())[:40]
name_items = [f'(人の 名前){f} {g}　[={M(f + " " + g, capital=True)}] #{f}{g}' for f, g in names]
cap_choice = [f'(地名){t}　{{*{M(t, capital=True)}|{M(t)}}} #{t}' for t in TOWNS] + \
             [f'(人の 名前){f} {g}　{{*{M(f + " " + g, capital=True)}|{M(f + " " + g)}}} #{f}{g}' for f, g in names[:12]] + \
             [f'(ふつうの ことば){w}　{{*{M(w)}|{M(w, capital=True)}}} #{w}' for w in 'いぬ さくら やま ねこ うみ はな ほん そら'.split()]
out.append(topic('romaji10', 'ローマ字⑩ 大文字の 使い方', '人の 名前や 地名は、はじめの 字を 大文字で 書く。', [
    ('大文字で 書き始める もの | 正しい ほうを ○で かこみましょう。 | 4', cap_choice),
    ('地名や 人の 名前を 書く | 地名や 人の 名前を ローマ字で 書きましょう。 | 4', towns + name_items),
]))
HROWS = [('し ち つ ふ じ', 'shi chi tsu fu ji'), ('しゃ しゅ しょ', 'sha shu sho'), ('ちゃ ちゅ ちょ', 'cha chu cho'), ('じゃ じゅ じょ', 'ja ju jo')]
hep_syl = []
for k in ['し', 'ち', 'つ', 'ふ', 'じ', 'しゃ', 'しゅ', 'しょ', 'ちゃ', 'ちゅ', 'ちょ', 'じゃ', 'じゅ', 'じょ']:
    hep_syl.append(f'{k}　{{*{mora_roman(k, True)}|{mora_roman(k, False)}}} #{k}')
hep_words = [f'{w}　[={M(w, True)}] #{w}' for w in HEPW if fits(w, True)] + [f'(地名){k}　[={M(k, True, True)}] #{k}' for k, v in PLACES if fits(k, True)]
hep_conv = [f'{M(w)}　→　[={M(w, True)}] #{w}' for w in HEPW if fits(w, True)]
out.append(topic('romaji11', 'ローマ字⑪ ヘボン式', '駅や 看板で 見る 書き方。し→shi、ち→chi、つ→tsu、ふ→fu、じ→ji。', [
    ('ヘボン式を なぞる | うすい 字を なぞりましょう。 | 2 | seq', trace(HROWS)),
    ('ヘボン式は どちら | ヘボン式で 書くと どちらですか。○で かこみましょう。 | 4 | cols=2', hep_syl),
    ('ヘボン式で 書く | ヘボン式で 書きましょう。 | 4 | cols=2', hep_words),
    ('｜訓令式《くんれいしき》を ヘボン式に | ｜訓令式《くんれいしき》の つづりを ヘボン式に 直しましょう。 | 2 | cols=2', hep_conv),
]))
allw = [w for w in WORDS if len(roman(w)) <= 9]
wrongs = [w for w in allw if spell_wrong(w)]
out.append(topic('romaji12', 'ローマ字⑫ 読む・書く(まとめ)', 'これまでの ローマ字を ぜんぶ つかって、ことばを 読んだり 書いたり する。', [
    ('ローマ字を 読む | ローマ字で 書いた ことばを ひらがなで 書きましょう。 | 6 | cols=2', [f'{M(w)}　[{w}] #{w}' for w in allw]),
    ('ローマ字で 書く | つぎの ことばを ローマ字で 書きましょう。 | 4 | cols=2', [f'{w}　[={M(w)}] #{w}' for w in allw if fits(w)]),
    ('正しい つづり | 正しい つづりを ○で かこみましょう。 | 4 | cols=2', [f'{w}　{{*{M(w)}|{M(spell_wrong(w)[0])}}} #{w}' for w in wrongs]),
]))

block = '\n'.join(out)
p = root / 'src' / 'data' / 'kimari.txt'
s = p.read_text(encoding='utf-8')
START, END = '# ==== ローマ字(tools/make_romaji.py が 作る。ここは 手で 直さない) ====', '# ==== ローマ字 ここまで ===='
if START in s:
    i, j = s.index(START), s.index(END) + len(END)
else:
    i = s.index('@ romaji01 |'); j = s.index('@ kosoado |')
s = s[:i] + START + '\n' + block + END + '\n\n' + s[j:].lstrip('\n')
p.write_text(s, encoding='utf-8')
for u in (4, 5, 6, 7, 8, 9):
    print(f'単元{u}: {len(rows_for(u))} 語', ' '.join(f'{w}={roman(w)}' for w in rows_for(u)))
print('ヘボン式:', ' '.join(f'{w}={roman(w, True)}' for w in HEPW))
print('のこり(どこにも 入らない):', [w for w in WORDS if unit_of(w) == 12])
for w in ['てんいん', 'おかあさん', 'きって', 'きゃべつ', 'ほんや', 'こおり', 'ちょうちょ']:
    print(w, M(w), [M(x) for x in spell_wrong(w)])
print(M('やまだ たろう', capital=True), M('しんじゅく', True, True))
