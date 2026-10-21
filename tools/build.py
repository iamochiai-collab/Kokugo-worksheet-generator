"""国語プリントを 1つの HTML に まとめる。

  python3 tools/build.py   → docs/index.html(公開用) と build/test.html(検査用)

src/template.html の つぎの ところを おきかえる。
  {{DATA}}            src/data/words*.tsv を JavaScript の データに して 入れる
  {{CHARA:名前}}      assets/chara/名前.webp を data URI で 入れる
  {{ICON:大きさ}}      assets/icon/icon-大きさ.png を data URI で 入れる
  {{VENDOR:ファイル}} vendor/ の ファイルを そのまま 入れる
  {{FONT:ファイル}}   vendor/ の フォント(woff2)を data URI で 入れる
"""
import base64, json, pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
tpl = (root / 'src' / 'template.html').read_text(encoding='utf-8')

LABELS = {1: '小1', 2: '小2', 3: '小3', 4: '小4', 5: '小5', 6: '小6', 7: '中学'}


def load(path):
    rows = []
    for line in path.read_text(encoding='utf-8').split('\n'):
        if not line.strip() or line.startswith('#'):
            continue
        f = line.split('\t')
        if len(f) != 4:
            sys.exit(f'{path.name}: 列が {len(f)} つ -> {line!r}')
        rows.append({'w': f[0], 'r': f[1], 's': f[2], 'lv': int(f[3])})
    return rows


blocks, total = [], 0
for path in sorted(root.glob('src/data/words*.tsv')):
    grade = int(re.search(r'words(\d+)', path.name).group(1))
    rows = load(path)
    total += len(rows)
    body = ',\n    '.join(json.dumps(r, ensure_ascii=False) for r in rows)
    blocks.append(
        f'  var words{grade} = {{ grade: {grade}, '
        f'label: {json.dumps(LABELS[grade], ensure_ascii=False)}, entries: [\n    {body}\n  ] }};')

# --- 読解(長文)の データ ---
reads = []
for path in sorted(root.glob('src/data/read*.json')):
    grade = re.search(r'read(\d+)', path.name).group(1)
    data = json.loads(path.read_text(encoding='utf-8'))
    reads.append(f'  var read{grade} = {json.dumps(data, ensure_ascii=False)};')
    print(f'  {path.name}: {len(data)} 話')
blocks += reads

# --- 長文プリントの 土台の 高さ(tools/measure_layout.js が 書く) ---
lay = root / 'src' / 'data' / 'layout.json'
if lay.exists():
    blocks.append(f'  var layoutData = {lay.read_text(encoding="utf-8").strip()};')

# --- ふりがな(tools/furigana.py が 作る)と 学年別漢字配当表 ---
for name, var in [('ruby.json', 'rubyData'), ('kanji_grades.json', 'kanjiGrades'), ('youji.json', 'youjiData')]:
    f = root / 'src' / 'data' / name
    if f.exists():
        blocks.append(f'  var {var} = {json.dumps(json.loads(f.read_text(encoding="utf-8")), ensure_ascii=False)};')

# --- ようじの「え を みて かこう」の 絵(assets/pics/*.svg。Fluent Emoji フラット・MIT。ビルドで 白黒に する) ---
sys.path.insert(0, str(root / 'tools'))
from lineart import to_mono   # 色つきの 絵を、白黒でも わかる 絵(うすい 灰色 + 黒い りんかく)に する
pics = {f.stem: 'data:image/svg+xml;base64,' + base64.b64encode(to_mono(f.read_text(encoding='utf-8')).encode()).decode()
        for f in sorted((root / 'assets' / 'pics').glob('*.svg'))}
blocks.append(f'  var youjiPics = {json.dumps(pics)};')

assert tpl.count('{{DATA}}') == 1
out = tpl.replace('{{DATA}}', '\n'.join(blocks).strip())

out = re.sub(r'\{\{CHARA:(\w+)\}\}',
             lambda m: 'data:image/webp;base64,' + base64.b64encode(
                 (root / 'assets' / 'chara' / f'{m.group(1)}.webp').read_bytes()).decode(), out)
# {{ICON:大きさ}} は assets/icon/icon-大きさ.png を data URI で 入れる(タブや ホーム画面の アイコン)
out = re.sub(r'\{\{ICON:(\d+)\}\}',
             lambda m: 'data:image/png;base64,' + base64.b64encode(
                 (root / 'assets' / 'icon' / f'icon-{m.group(1)}.png').read_bytes()).decode(), out)
# {{FONT:ファイル}} は vendor/ の フォントを data URI で 入れる(ようじの なぞり書き用 Klee One の かなだけ)
out = re.sub(r'\{\{FONT:([\w.\-]+)\}\}',
             lambda m: 'data:font/woff2;base64,' + base64.b64encode((root / 'vendor' / m.group(1)).read_bytes()).decode(), out)
out = re.sub(r'\{\{VENDOR:([\w.\-]+)\}\}',
             lambda m: (root / 'vendor' / m.group(1)).read_text(encoding='utf-8'), out)
assert '{{' not in out, out[out.index('{{'):out.index('{{') + 60]

(root / 'docs').mkdir(exist_ok=True)
(root / 'docs' / 'index.html').write_text(out, encoding='utf-8')

hook = ('  window.__T = { BANKS, READS, hasLong, buildSheet, sheetHtml, makeRng, splitWord, pickEntries, LAYOUT, fits, maxFor, estHeight, layoutOf, defaultCounts, labelsFor, longSheetFor, rubyHtml, learned, storiesOf, genresOf, genreFor, buildYoujiSheet, youjiSheetHtml, YD, YPOOL };\n'
        '  renderHome();')
assert out.count('  renderHome();') == 1
(root / 'build').mkdir(exist_ok=True)
(root / 'build' / 'test.html').write_text(out.replace('  renderHome();', hook, 1), encoding='utf-8')

print(f'built docs/index.html ({len(out.encode()) / 1e6:.2f} MB) 語い {total} 語')
