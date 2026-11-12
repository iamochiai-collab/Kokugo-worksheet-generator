"""小学校で 習う 漢字(1026字)の 書き順(1画ずつの 線)を KanjiVG から とって src/data/kanji_strokes.json を 作る。

  python3 tools/make_kanji_strokes.py

KanjiVG (https://kanjivg.tagaini.net)  © Ulrich Apel  CC BY-SA 3.0
「かきかた(じゆうに 書く)」の 書き順なぞりで つかう。形は kana_strokes.json と おなじ(0〜109 の 座標)。
ファイルを 小さく するため、数の 小数は 1けたに まるめる。
"""
import json, pathlib, re, urllib.request
from concurrent.futures import ThreadPoolExecutor

root = pathlib.Path(__file__).resolve().parent.parent
grades = json.loads((root / 'src' / 'data' / 'kanji_grades.json').read_text(encoding='utf-8'))
chars = [c for g in sorted(grades, key=int) for c in grades[g]]


def short(d):
    return re.sub(r'(\d+\.\d)\d+', r'\1', d)


def get(ch):
    url = f'https://raw.githubusercontent.com/KanjiVG/kanjivg/master/kanji/{ord(ch):05x}.svg'
    try:
        svg = urllib.request.urlopen(url, timeout=30).read().decode('utf-8')
    except Exception:
        return ch, None
    paths = re.findall(r'<path id="kvg:[0-9a-f]+-s(\d+)"[^>]*\sd="([^"]+)"', svg)
    return ch, [short(d) for _, d in sorted(paths, key=lambda x: int(x[0]))]


with ThreadPoolExecutor(16) as ex:
    res = list(ex.map(get, chars))
out = {ch: v for ch, v in res if v}
miss = [ch for ch, v in res if not v]
(root / 'src' / 'data' / 'kanji_strokes.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
print(f'kanji_strokes.json: {len(out)} 字', 'ない:', ''.join(miss))
