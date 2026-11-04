"""ChatGPT で 描いた 白黒の 線画(PNG)を アプリ用に ととのえて assets/pics-line/ に 入れる。

  python3 tools/prep_line_pics.py <PNG の フォルダ>

- はしに ある 小さな ゴミ(切れはしの 線)を けす
- 絵の まわりを 切りつめて、まん中に おき、正方形(512×512・余白 6%)に そろえる
- 白黒 2色の PNG で 保存(かるい)
ファイル名は assets/pics/ の 絵と 同じ 名前(airplane.png など)。同じ 名前の 絵が あれば こちらが つかわれる。
"""
import sys, pathlib
from PIL import Image
from collections import deque

root = pathlib.Path(__file__).resolve().parent.parent
src = pathlib.Path(sys.argv[1])
dst = root / 'assets' / 'pics-line'
dst.mkdir(exist_ok=True)


def components(px, w, h):
    seen = bytearray(w * h)
    comps = []
    for i in range(w * h):
        if px[i] and not seen[i]:
            q = deque([i]); seen[i] = 1; pts = []
            while q:
                j = q.popleft(); pts.append(j)
                x, y = j % w, j // w
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        k = ny * w + nx
                        if px[k] and not seen[k]:
                            seen[k] = 1; q.append(k)
            comps.append(pts)
    return comps


report = []
for f in sorted(src.glob('*.png')):
    im = Image.open(f).convert('L')
    w, h = im.size
    px = [1 if v < 128 else 0 for v in im.tobytes()]
    comps = components(px, w, h)
    big = max(len(c) for c in comps)
    box = lambda c: (min(j % w for j in c), min(j // w for j in c), max(j % w for j in c), max(j // w for j in c))
    # 絵の 本体 = 大きな まとまり(いちばん 大きい ものの 15% いじょう)を あわせた わく
    mains = [box(c) for c in comps if len(c) >= big * 0.15]
    M = (min(b[0] for b in mains) - 4, min(b[1] for b in mains) - 4, max(b[2] for b in mains) + 4, max(b[3] for b in mains) + 4)
    keep = bytearray(w * h)
    removed = 0
    for c in comps:
        b = box(c)
        outside = b[2] < M[0] or b[0] > M[2] or b[3] < M[1] or b[1] > M[3]
        # 本体の 外に ぽつんと ある 小さな 線(切れはし)と、ごく 小さな 点は けす
        # 本体の わくの はしに くっついた ほそい 切れはし(絵の 線の 一部では ない もの)
        thin = min(b[2] - b[0], b[3] - b[1]) <= 12 and max(b[2] - b[0], b[3] - b[1]) >= 30
        at_side = b[2] <= M[0] + 16 or b[0] >= M[2] - 16
        if (outside and len(c) < big * 0.15) or (thin and at_side and len(c) < big * 0.05) or len(c) < 12:
            removed += len(c); continue
        for j in c: keep[j] = 1
    xs = [i % w for i in range(w * h) if keep[i]]; ys = [i // w for i in range(w * h) if keep[i]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    body = Image.new('L', (w, h), 255)
    body.putdata([0 if k else 255 for k in keep])
    body = body.crop((x0, y0, x1 + 1, y1 + 1))
    S = 512; inner = int(S * 0.88)
    sc = inner / max(body.size)
    body = body.resize((max(1, round(body.size[0] * sc)), max(1, round(body.size[1] * sc))), Image.LANCZOS)
    out = Image.new('L', (S, S), 255)
    out.paste(body, ((S - body.size[0]) // 2, (S - body.size[1]) // 2))
    out.point(lambda v: 0 if v < 140 else 255).convert('1').save(dst / f.name, optimize=True)
    if removed: report.append(f'{f.stem}: ごみ {removed}px')
print(f'{len(list(src.glob("*.png")))} まい → assets/pics-line/')
print('\n'.join(report))
