"""語いバンク(src/data/words*.tsv)の検査。

  python3 tools/check_words.py

1行 = 語 \t 読み \t 例文({}が語の場所) \t 難易度(1..3)

調べること
  - 列が 4つ そろっているか
  - 語に 漢字が あるか / 読みが かな だけか
  - 例文に {} が ちょうど 1つ あるか
  - 例文の、ねらいの語 いがいに 漢字が まざっていないか
  - 英字・ハングル・キリル文字などが まざっていないか
  - 同じ 語と 読みが 2回 出ていないか
おわりに 学年ごとに つかっている漢字を ならべて出す(学年をこえた漢字を 目で見つけるため)。
"""
import json, pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
KANJI = r'㐀-䶿一-鿿豈-﫿'
KANA = r'ぁ-ゟァ-ヿー'
PUNCT = set('。、「」『』・（）？！…ー〜 　')
FOREIGN = re.compile(r'[A-Za-zЀ-ӿ가-힣؀-ۿ]')

GRADES = json.loads((root / 'src' / 'data' / 'kanji_grades.json').read_text(encoding='utf-8'))
GRADE_OF = {c: int(g) for g, s in GRADES.items() for c in s}

errors, report = [], []
for path in sorted(root.glob('src/data/words*.tsv')):
    lines = [l for l in path.read_text(encoding='utf-8').split('\n')
             if l.strip() and not l.startswith('#')]
    seen, kanji_used = set(), set()
    for n, line in enumerate(lines, 2):
        where = f'{path.name}:{n}'
        f = line.split('\t')
        if len(f) != 4:
            errors.append(f'{where}: 列が {len(f)} つ -> {line!r}')
            continue
        w, r, s, lv = f
        if FOREIGN.search(line):
            errors.append(f'{where} [{w}]: 英字・外国語が まざっている')
        if not re.search(f'[{KANJI}]', w):
            errors.append(f'{where} [{w}]: 語に 漢字が ない')
        if re.search(f'[^{KANJI}{KANA}]', w):
            errors.append(f'{where} [{w}]: 語に 使えない 文字が ある')
        if not r or re.search(f'[^{KANA}]', r):
            errors.append(f'{where} [{w}]: 読みが かな だけでは ない -> {r!r}')
        if s.count('{}') != 1:
            errors.append(f'{where} [{w}]: 例文の {{}} が {s.count("{}")} 個')
        rest = s.replace('{}', '')
        mixed = sorted(set(re.findall(f'[{KANJI}]', rest)))
        if mixed:
            errors.append(f'{where} [{w}]: 例文に 漢字 {"".join(mixed)} が まざっている')
        odd = sorted(set(c for c in rest
                         if not re.match(f'[{KANA}]', c) and c not in PUNCT))
        if odd:
            errors.append(f'{where} [{w}]: 例文に 使えない 文字 {"".join(odd)}')
        if lv not in ('1', '2', '3'):
            errors.append(f'{where} [{w}]: 難易度が 1..3 では ない -> {lv!r}')
        if (w, r) in seen:
            errors.append(f'{where} [{w}]: 同じ 語と 読みが 2回 出ている')
        seen.add((w, r))
        kanji_used |= set(re.findall(f'[{KANJI}]', w))
        bank = int(re.search(r'words(\d+)', path.name).group(1))
        over = [k for k in re.findall(f'[{KANJI}]', w) if GRADE_OF.get(k, 7) > bank]
        if bank <= 6 and over:
            errors.append(f'{where} [{w}]: 小{bank}で まだ 習わない 漢字 {"".join(over)}(学年別漢字配当表)')
    report.append((path.name, len(lines), kanji_used))

prev = set()
for name, n, kanji in report:
    print(f'{name}: {n} 件  漢字 {len(kanji)} 字')
    print(f'  はじめて出る漢字: {"".join(sorted(kanji - prev))}')
    again = kanji & prev
    if again:
        print(f'  下の学年にも出た漢字: {"".join(sorted(again))}')
    prev |= kanji
print()
if errors:
    print(f'NG {len(errors)} 件')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print('OK すべての 語いバンクが そろっています')
