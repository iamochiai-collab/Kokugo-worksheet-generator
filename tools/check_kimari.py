"""ことばの きまり(src/data/kimari.txt)の 検査。

  python3 tools/check_kimari.py

調べること
  - ファイルが 読めるか(tools/kimari.py)
  - 小1 の 問題に 漢字が ないか / 小2 いじょうは その 学年までの 漢字だけか
    (いちばん 低い 学年で しらべる。ふりがな ｜漢字《よみ》 の 漢字は のぞく)
  - 英字・外国の 文字が まざって いないか
  - 同じ 問題が 2回 出て いないか
"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kimari import load_kimari

root = pathlib.Path(__file__).resolve().parent.parent
GRADES = json.loads((root / 'src' / 'data' / 'kanji_grades.json').read_text(encoding='utf-8'))
GRADE_OF = {c: int(g) for g, s in GRADES.items() for c in s}
KANJI = re.compile(r'[㐀-䶿一-鿿豈-﫿]')
FOREIGN = re.compile(r'[A-Za-zЀ-ӿ가-힣]')
RUBY = re.compile(r'｜[^《]+《[^》]+》')


def texts(item):
    if isinstance(item, dict):
        return item['order']
    out = []
    for p in item:
        if p[0] in 'tu': out.append(p[1])
        elif p[0] == 'c': out += p[1]
        elif p[0] == 'w': out += [p[1], p[2]]
        elif p[0] == 'b': out.append(p[1])
    return out


errors, total = [], 0
topics = load_kimari(root / 'src' / 'data' / 'kimari.txt')
for t in topics:
    g = min(t['grades'])
    for sec in t['sections']:
        seen = set()
        for it in sec['items']:
            total += 1
            body = texts(it) + [sec['title'], sec['inst']] + sec.get('legend', []) + sec.get('box', [])
            key = json.dumps(it, ensure_ascii=False)
            if key in seen: errors.append(f'[{t["id"]}] 同じ 問題: {key[:40]}')
            seen.add(key)
            for s in body:
                s2 = RUBY.sub('', s)
                if FOREIGN.search(s2) and t['id'] != 'romaji': errors.append(f'[{t["id"]}] 英字など: {s}')
                for c in KANJI.findall(s2):
                    k = GRADE_OF.get(c)
                    if t['id'] != 'kana' and (g == 1 or k is None or k > g):
                        errors.append(f'[{t["id"]}] 小{g} で つかえない 漢字「{c}」(配当 {k}): {s}')
print(f'ことばの きまり {len(topics)} こ / 問題 {total}')
if errors:
    for e in sorted(set(errors)): print(' -', e)
    sys.exit(1)
print('OK ことばの きまりの データは そろっています')
