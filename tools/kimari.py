"""ことばの きまり の データ(src/data/kimari.txt)を 読んで、アプリに 入れる 形に する。

  from kimari import load_kimari
  topics = load_kimari(path)

1つの 問題は「部品」の ならび:
  ["t", 文字]            ふつうの 文字(｜漢字《よみ》 は アプリで ふりがなに する)
  ["c", [えらぶもの…], 答えの 番号]   ○で かこむ
  ["w", 答え, ラベル]      （　）に 書く
  ["b", 答え]             □に 書く(記号。答えが "" なら 何も 書かない □)
  ["u", 文字]             下線
  ["br"]                 行を かえる
じゅんばん(@order)の 問題は {"order": [正しい じゅんの 文…]}。
"""
import re

TOKEN = re.compile(r'\[\[(.*?)\]\]|\{([^}]*)\}|\[([^\]]*)\]|<([^>]*)>|//')


def parse_item(line, where):
    if line.startswith('@order '):
        steps = [x.strip() for x in line[7:].split('|')]
        if len(steps) < 3:
            raise SystemExit(f'{where}: じゅんばんの 文が 少ない')
        return {'order': steps}
    parts, pos = [], 0
    for m in TOKEN.finditer(line):
        if m.start() > pos:
            parts.append(['t', line[pos:m.start()]])
        box, choice, write, under = m.group(1), m.group(2), m.group(3), m.group(4)
        if box is not None:
            parts.append(['b', box])
        elif choice is not None:
            opts = choice.split('|')
            stars = [i for i, o in enumerate(opts) if o.startswith('*')]
            if len(opts) < 2 or len(stars) > 1:
                raise SystemExit(f'{where}: えらぶ ものが おかしい {{{choice}}}')
            parts.append(['c', [o.lstrip('*') for o in opts], stars[0] if stars else 0])
        elif write is not None:
            ans, _, label = write.partition('@')
            if not ans:
                raise SystemExit(f'{where}: [] の 答えが ない')
            parts.append(['w', ans, label])
        elif under is not None:
            parts.append(['u', under])
        else:
            parts.append(['br'])
        pos = m.end()
    if pos < len(line):
        parts.append(['t', line[pos:]])
    if not any(p[0] in 'cwb' for p in parts):
        raise SystemExit(f'{where}: 答える ところが ない -> {line}')
    return parts


def load_kimari(path):
    topics, topic, sec = [], None, None
    for n, raw in enumerate(path.read_text(encoding='utf-8').split('\n'), 1):
        line = raw.strip()
        where = f'{path.name}:{n}'
        if not line or line.startswith('#'):
            continue
        if line.startswith('@ '):
            f = [x.strip() for x in line[2:].split('|')]
            if len(f) != 4:
                raise SystemExit(f'{where}: @ の 列が {len(f)} つ')
            topic = {'id': f[0], 'grades': [int(g) for g in f[1].split(',')], 'name': f[2], 'desc': f[3], 'sections': []}
            topics.append(topic)
        elif line.startswith('== '):
            f = [x.strip() for x in line[3:].split('|')]
            if len(f) < 3:
                raise SystemExit(f'{where}: == の 列が 足りない')
            sec = {'title': f[0], 'inst': f[1], 'n': int(f[2]), 'items': []}
            for opt in f[3:]:
                k, _, v = opt.partition('=')
                if k == 'bank': sec['bank'] = True
                elif k == 'fixed': sec['fixed'] = True
                elif k == 'box': sec['box'] = v.split(',')
                elif k == 'cols': sec['cols'] = int(v)
                elif k == 'w': sec['w'] = float(v)
                elif k == 'legend': sec['legend'] = v.split('/')
                else: raise SystemExit(f'{where}: しらない オプション {opt}')
            topic['sections'].append(sec)
        else:
            if sec is None:
                raise SystemExit(f'{where}: == の 前に 問題が ある')
            sec['items'].append(parse_item(line, where))
    ids = [t['id'] for t in topics]
    if len(ids) != len(set(ids)):
        raise SystemExit('kimari.txt: id が 重なって いる')
    for t in topics:
        for s in t['sections']:
            if len(s['items']) < s['n']:
                raise SystemExit(f'kimari.txt [{t["id"]}] {s["title"]}: 問題が {len(s["items"])} しか ない(n={s["n"]})')
    return topics
