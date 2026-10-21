"""長文読解の データ(src/data/read*.json)の 検査。

  python3 tools/check_reads.py

  - 形(ジャンル・本文・問い・選択肢3つ・正解の番号・語句)
  - 英字・ハングル・キリル文字・へんな 部首文字が まざっていないか
  - 小1〜小3 は、その 学年までに 習う 漢字だけで 書かれているか(学年別漢字配当表)
"""
import json, pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent

# 学年別漢字配当表(平成29年告示・2020年度から)。src/data/kanji_grades.json
GRADES = json.loads((root / 'src' / 'data' / 'kanji_grades.json').read_text(encoding='utf-8'))
assert [len(GRADES[str(g)]) for g in range(1, 7)] == [80, 160, 200, 202, 193, 191]
ALLOWED = {}
acc = ''
for g in range(1, 7):
    acc += GRADES[str(g)]
    ALLOWED[g] = set(acc)

KANJI = re.compile(r'[㐀-䶿一-鿿]')
BAD = re.compile(r'[A-Za-zЀ-ӿ가-힣⺀-⿿‧]')
QN = {1: (3, 3), 2: (4, 4), 3: (5, 5)}          # 学年ごとの 問いの 数(下限, 上限)
# わざと 英字を 使っている ところ(地図記号の「H」、成績の「A」、磁石の「N極・S極」)
LATIN_OK = {'g418': set('H'), 'g5610': set('A'), 'g5664': set('NS'), 'g56120': set('NS')}

errors = []
for path in sorted(root.glob('src/data/read*.json')):
    grade = int(re.search(r'read(\d+)', path.name).group(1))
    data = json.loads(path.read_text(encoding='utf-8'))
    ids = set()
    lens = []
    for d in data:
        where = f'{path.name} {d.get("id")}'
        if d.get('genre') not in ('story', 'expo', 'essay'):
            errors.append(f'{where}: genre が story / expo / essay の どれでも ない -> {d.get("genre")!r}')
        if d['id'] in ids:
            errors.append(f'{where}: id が 重なっている')
        ids.add(d['id'])
        text = d['passage'] + ''.join(q['q'] + ''.join(q['c']) for q in d['questions']) + ''.join(d['vocab'])
        odd = set(BAD.findall(text)) - LATIN_OK.get(d['id'], set())
        if odd:
            errors.append(f'{where}: へんな 文字 {sorted(odd)}')
        lo, hi = QN.get(grade, (5, 5))
        if not lo <= len(d['questions']) <= hi:
            errors.append(f'{where}: 問いが {len(d["questions"])} 問')
        for i, q in enumerate(d['questions'], 1):
            if len(q['c']) != 3 or len(set(q['c'])) != 3:
                errors.append(f'{where} ({i}): 選択肢が 3つ そろっていない')
            if not (isinstance(q['a'], int) and 0 <= q['a'] < len(q['c'])):
                errors.append(f'{where} ({i}): 正解の 番号が おかしい -> {q["a"]}')
        if grade <= 3 and re.search(r'[0-9０-９]', text):
            errors.append(f'{where}: 数字が まざっている(低学年は 漢数字か ひらがなで)')
        if grade <= 3:
            over = sorted(set(KANJI.findall(text)) - ALLOWED[grade])
            if over:
                errors.append(f'{where}: {grade}年で まだ 習わない 漢字 {"".join(over)}')
        lens.append(len(d['passage']))
    print(f'{path.name}: {len(data)} 話  本文 {min(lens)}〜{max(lens)} 字')

if errors:
    print(f'NG {len(errors)} 件')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print('OK 長文の データは そろっています')
