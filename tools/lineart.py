"""ようじ「え と ことば」の 絵を、白黒でも わかる 絵に する(tools/build.py が 使う)。

assets/pics/ には Microsoft の Fluent Emoji(フラット。MIT)の 色つき SVG が そのまま 入って いる。
プリントは 白黒なので、ビルドの ときに
  - 色を 明るさに おうじた うすい 灰色に(こい 色は 黒に。目や はななど)
  - 形の まわりに 黒い りんかく
を つけた 絵に かえる。ぬりえ の ように 色を ぬる ことも できる うすさに して ある。
"""
import re

STROKE = 0.55      # りんかくの 太さ(32×32 の 絵の なかでの 大きさ)
DARK = 0.28        # これより くらい 色は 黒に する
LIGHTEST, DARKEST = 255, 175   # 灰色の はんい


def _lum(hexs):
    h = hexs.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.299 * r + 0.587 * g + 0.114 * b


def _gray(y):
    if y < DARK:
        return '#222222'
    v = round(LIGHTEST - (1 - y) * (LIGHTEST - DARKEST) / (1 - DARK))
    v = max(DARKEST, min(LIGHTEST, v))
    return '#%02x%02x%02x' % (v, v, v)


def to_mono(svg):
    def fill(m):
        val = m.group(2)
        if re.fullmatch(r'#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?', val):
            return f'{m.group(1)}="{_gray(_lum(val))}"'
        if val.startswith('url'):
            return f'{m.group(1)}="#eeeeee"'
        return m.group(0)
    svg = re.sub(r'(fill|stroke|stop-color)="([^"]+)"', fill, svg)
    return svg.replace('<svg ', f'<svg stroke="#1a1a1a" stroke-width="{STROKE}" stroke-linejoin="round" '
                       'stroke-linecap="round" paint-order="stroke" ', 1)
