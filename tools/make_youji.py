"""ようじ(幼児)の プリントの データ src/data/youji.json を 作る。

  python3 tools/make_youji.py

ここに 書いた 表を 直して 走らせれば、データが かわる。
  hira / kata : 行ごとの 字と、その 字の ことば(なぞり書きの 右に 出る)
  themes      : ことば なぞりの テーマと ことば(1テーマ 7語・5字まで)
  extra       : ことば あそび(しりとり など)に だけ 使う ことば
  pics        : え を みて かこう の ことばと 絵(assets/pics/<名前>.svg)。
                絵は Microsoft の Fluent Emoji(フラット。MIT ライセンス)。
                新しい 絵を 足す ときは、fluentui-emoji の icons/flat/ から assets/pics/ に コピーする
"""
import json, pathlib

root = pathlib.Path(__file__).resolve().parent.parent

def rows(spec):
    out = []
    for line in spec.strip().split('\n'):
        name, rest = line.split(':', 1)
        pairs = [p.split('=') for p in rest.split()]
        out.append({'name': name, 'chars': [c for c, _ in pairs], 'words': [w for _, w in pairs]})
    return out

HIRA = rows('''
あ行:あ=あり い=いぬ う=うし え=えび お=おに
か行:か=かさ き=きつね く=くも け=けむし こ=こま
さ行:さ=さる し=しか す=すいか せ=せみ そ=そら
た行:た=たこ ち=ちず つ=つき て=てがみ と=とけい
な行:な=なす に=にじ ぬ=ぬりえ ね=ねこ の=のり
は行:は=はな ひ=ひよこ ふ=ふね へ=へび ほ=ほし
ま行:ま=まめ み=みかん む=むし め=めだか も=もも
や行:や=やま ゆ=ゆき よ=よる
ら行:ら=らくだ り=りす る=るすばん れ=れもん ろ=ろうそく
わ行:わ=わに を=えをかく ん=ほん
が行:が=がっこう ぎ=かぎ ぐ=ぐみ げ=げた ご=ごま
ざ行:ざ=ざる じ=ひじ ず=ずかん ぜ=かぜ ぞ=ぞう
だ行:だ=だんご ぢ=はなぢ づ=みかづき で=でんわ ど=どんぐり
ば行:ば=ばなな び=くび ぶ=ぶた べ=べんとう ぼ=ぼうし
ぱ行:ぱ=ぱん ぴ=えんぴつ ぷ=きっぷ ぺ=てっぺん ぽ=たんぽぽ
''')

KATA = rows('''
ア行:ア=アイス イ=イルカ ウ=ウクレレ エ=エプロン オ=オムレツ
カ行:カ=カメラ キ=キウイ ク=クッキー ケ=ケーキ コ=コアラ
サ行:サ=サラダ シ=シャツ ス=スキー セ=セーター ソ=ソース
タ行:タ=タオル チ=チーズ ツ=ツリー テ=テレビ ト=トマト
ナ行:ナ=ナイフ ニ=ニット ヌ=ヌードル ネ=ネクタイ ノ=ノート
ハ行:ハ=ハート ヒ=ヒーロー フ=フォーク ヘ=ヘリ ホ=ホテル
マ行:マ=マスク ミ=ミルク ム=ムース メ=メロン モ=モップ
ヤ行:ヤ=ヤギ ユ=ユリ ヨ=ヨット
ラ行:ラ=ラジオ リ=リボン ル=ルビー レ=レモン ロ=ロボット
ワ行:ワ=ワニ ヲ=- ン=パン
ガ行:ガ=ガム ギ=ギター グ=グミ ゲ=ゲーム ゴ=ゴリラ
ザ行:ザ=ザリガニ ジ=ジャム ズ=ズボン ゼ=ゼリー ゾ=ゾウ
ダ行:ダ=ダンス ヂ=- ヅ=- デ=デパート ド=ドア
バ行:バ=バス ビ=ビル ブ=ブランコ ベ=ベッド ボ=ボール
パ行:パ=パン ピ=ピアノ プ=プール ペ=ペン ポ=ポスト
''')

THEMES = [
    ('どうぶつ', 'いぬ ねこ うさぎ ぞう きりん さる くま'),
    ('くだもの', 'りんご みかん ぶどう いちご すいか もも なし'),
    ('やさい', 'なす だいこん にんじん きゃべつ ねぎ かぶ ごぼう'),
    ('のりもの', 'くるま ふね ひこうき でんしゃ じてんしゃ きしゃ そり'),
    ('からだ', 'あたま め みみ はな くち て あし'),
    ('むし', 'あり ちょう とんぼ せみ ばった かぶとむし かたつむり'),
    ('うみの いきもの', 'さかな たこ いか かに くじら いるか えび'),
    ('いろ', 'あか あお きいろ みどり しろ くろ ちゃいろ'),
    ('てんき', 'はれ くもり あめ ゆき かみなり にじ かぜ'),
    ('はる', 'さくら たんぽぽ つくし ひなまつり こいのぼり おはなみ うぐいす'),
    ('なつ', 'うみ はなび あさがお ひまわり たなばた かきごおり おまつり'),
    ('あき', 'もみじ どんぐり つきみ くり きのこ いもほり さんま'),
    ('ふゆ', 'ゆき こたつ ゆきだるま おもち てぶくろ たこあげ こま'),
    ('いえの なか', 'つくえ いす とけい まど ふとん はし おさら'),
    ('かぞく', 'おかあさん おとうさん あかちゃん おにいさん おねえさん おじいさん おばあさん'),
    ('ようちえん', 'ほん かばん ぼうし はさみ のり つみき えほん'),
]

# ことば あそびに だけ 使う ことば(しりとりが つながりやすいように 多めに)
EXTRA = '''
あひる いのしし うま かめ からす きつね しか すずめ たぬき つる とら にわとり ねずみ はと ひつじ
ぶた へび らくだ りす わに めだか もぐら こども たいこ かさ くつ ふく まめ やま かわ そら ほし
つき くも えき みち はこ いし いけ たまご すし だんご あめ おにぎり ことり こけし けいと とまと
はがき きって てがみ みかづき すいとう うちわ わなげ げた たけ けむし しまうま まくら らくがき
きもの のはら らいおん かき きく くるみ みそ そば ばけつ つばめ めがね ねこじゃらし いちょう
うし しお おに にもつ つの のこぎり りぼん さかなつり いちじく くさ さる るす すな なべ べにしょうが
'''.split()

# え を みて かこう:テーマ ことば 絵 。ひらがなの ことばと カタカナの ことばを べつに もつ
PICS_HIRA = '''
どうぶつ こあら koala|いぬ dog-face|ねこ cat-face|ぞう elephant|きりん giraffe|さる monkey-face|くま bear|うさぎ rabbit-face
どうぶつ ぶた pig-face|うし cow-face|うま horse-face|ひつじ ewe|らいおん lion|とら tiger-face|ぱんだ panda|かめ turtle
どうぶつ へび snake|かえる frog|ねずみ mouse-face|きつね fox|しか deer|わに crocodile|かば hippopotamus|らくだ camel
どうぶつ りす chipmunk|はりねずみ hedgehog
いきもの さかな fish|たこ octopus|かに crab|えび shrimp|いか squid|くじら spouting-whale|いるか dolphin|ぺんぎん penguin
いきもの にわとり rooster|ひよこ baby-chick|あひる duck|ふくろう owl|はと dove|はち honeybee|ちょう butterfly|あり ant
いきもの てんとうむし lady-beetle|かたつむり snail|くも spider|さめ shark
たべもの りんご red-apple|みかん tangerine|ぶどう grapes|いちご strawberry|すいか watermelon|もも peach|ばなな banana|めろん melon
たべもの さくらんぼ cherries|なし pear|くり chestnut|なす eggplant|にんじん carrot|とまと tomato|きのこ mushroom|たまねぎ onion
たべもの じゃがいも potato|おにぎり rice-ball|すし sushi|ぱん bread|たまご egg|あめ candy|だんご dango
のりもの くるま automobile|ばす bus|でんしゃ railway-car|ふね sailboat|ひこうき airplane|じてんしゃ bicycle|ろけっと rocket
もの とけい alarm-clock|かぎ key|ほん open-book|えんぴつ pencil|はさみ scissors|めがね glasses|くつ running-shoe|くつした socks
もの てぶくろ gloves|てがみ envelope|でんわ telephone|たいこ drum|ふうせん balloon|かさ umbrella|かばん backpack|たこ kite
しぜん やま mountain|つき crescent-moon|ほし star|たいよう sun|にじ rainbow|ゆき snowflake|くも cloud|かみなり high-voltage
しぜん さくら cherry-blossom|ひまわり sunflower|もみじ maple-leaf|ゆきだるま snowman|はな tulip|き deciduous-tree|いえ house|はなび fireworks
からだ め eye|みみ ear-default|はな nose-default|くち mouth|て raised-hand-default|あし leg-default
'''
PICS_KATA = '''
どうぶつ コアラ koala|ライオン lion|パンダ panda|ペンギン penguin|ゴリラ gorilla|カンガルー kangaroo|フラミンゴ flamingo|インコ parrot
どうぶつ ハムスター hamster|イルカ dolphin|ラッコ otter
たべもの バナナ banana|メロン melon|トマト tomato|ケーキ shortcake|パン bread|レモン lemon|キウイ kiwi-fruit|ピーマン bell-pepper
たべもの ドーナツ doughnut|クッキー cookie|アイス ice-cream|ピザ pizza|プリン custard|ミルク glass-of-milk|チョコ chocolate-bar
のりもの バス bus|ロケット rocket|トラック delivery-truck|タクシー taxi|バイク motorcycle|ヨット sailboat
もの テレビ television|カメラ camera|ピアノ musical-keyboard|ギター guitar|ボール soccer-ball|ベッド bed|ペン pen|ノート notebook
もの クレヨン crayon|ベル bell|スプーン spoon|コップ cup-with-straw|フォーク fork-and-knife|シャツ t-shirt|ネクタイ necktie|ラッパ trumpet
もの バイオリン violin
'''


def pics(spec):
    out = []
    for line in spec.strip().split('\n'):
        cat, rest = line.split(' ', 1)
        for item in rest.split('|'):
            item = item.strip()
            if not item or item.endswith('?'):
                continue
            w, f = item.split()
            assert (root / 'assets' / 'pics' / f'{f}.svg').exists(), f'絵が ない: {f}'
            assert len(w) <= 6, w
            out.append({'w': w, 'cat': cat, 'pic': f})
    return out


def boxes(w):
    return len(w)

data = {'hira': HIRA, 'kata': KATA, 'themes': [{'name': n, 'words': ws.split()} for n, ws in THEMES],
        'extra': EXTRA, 'pics': {'hira': pics(PICS_HIRA), 'kata': pics(PICS_KATA)}}
for t in data['themes']:
    assert len(t['words']) == 7, t
    for w in t['words']:
        assert len(w) <= 5, w
for r in HIRA + KATA:
    for w in r['words']:
        assert w == '-' or len(w) <= 5, w
(root / 'src' / 'data' / 'youji.json').write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
print('youji.json: ひらがな', len(HIRA), '行 / カタカナ', len(KATA), '行 / テーマ', len(THEMES), '/ あそびの ことば', len(EXTRA),
      '/ 絵', len(data['pics']['hira']), '+', len(data['pics']['kata']))
