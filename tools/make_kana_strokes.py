"""ひらがな・カタカナの 書き順(1画ずつの 線)を KanjiVG から とって src/data/kana_strokes.json を 作る。

  python3 tools/make_kana_strokes.py

KanjiVG (https://kanjivg.tagaini.net)  © Ulrich Apel  CC BY-SA 3.0
ようじの なぞり書きで「書き順(1画ずつ)」「線で なぞる」を えらんだ ときに つかう。
1字 = 画の ならび(SVG の path の d。0〜109 の 座標)。
"""
import json, pathlib, re, urllib.request

root = pathlib.Path(__file__).resolve().parent.parent
chars = [chr(c) for c in range(0x3041, 0x3097)] + [chr(c) for c in range(0x30A1, 0x30FB)] + ['ー']
out, miss = {}, []
for ch in chars:
    url = f'https://raw.githubusercontent.com/KanjiVG/kanjivg/master/kanji/{ord(ch):05x}.svg'
    try:
        svg = urllib.request.urlopen(url, timeout=30).read().decode('utf-8')
    except Exception:
        miss.append(ch)
        continue
    paths = re.findall(r'<path id="kvg:[0-9a-f]+-s(\d+)"[^>]*\sd="([^"]+)"', svg)
    out[ch] = [d for _, d in sorted(paths, key=lambda x: int(x[0]))]
(root / 'src' / 'data' / 'kana_strokes.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
print(f'kana_strokes.json: {len(out)} 字', 'ない:', ''.join(miss))
