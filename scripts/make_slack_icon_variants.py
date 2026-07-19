"""Render the Ilai Collective Slack icon in every brand colorway + a montage.

Outputs each 512x512 variant and a labeled comparison sheet to OUT_DIR.
Run:  python scripts/make_slack_icon_variants.py <out_dir>
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "assets", "Jost.ttf")
PUB = os.path.join(HERE, "..", "public")
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else PUB

S = 512

# name -> (bg_top, bg_bot, wordmark_rgb, mark_file, glow_rgb)
FOREST = (18, 53, 39)
FOREST_2 = (11, 34, 24)
CREAM = (244, 241, 234)
FORESTINK = (18, 53, 39)
PINK = (230, 169, 196)
WHITE = (255, 255, 255)

THEMES = {
    "forest":   (FOREST, FOREST_2, CREAM, "logo-mark-light.png", PINK),
    "charcoal": ((42, 45, 46), (26, 29, 30), WHITE, "logo-mark-light.png", PINK),
    "black":    ((14, 17, 15), (0, 0, 0), CREAM, "logo-mark-light.png", (28, 107, 74)),
    "cream":    ((244, 241, 234), (231, 236, 227), FORESTINK, "logo-mark.png", PINK),
    "pink":     ((236, 184, 207), (222, 160, 189), FORESTINK, "logo-mark.png", WHITE),
    "white":    ((255, 255, 255), (244, 241, 234), FORESTINK, "logo-mark.png", PINK),
}


def _font(size, weight="SemiBold"):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def _vgrad(w, h, top, bot):
    img = Image.new("RGB", (w, h), top)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        row = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = row
    return img


def _radial(w, h, cx, cy, r, color, a_max):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 48
    for i in range(steps, 0, -1):
        rr = r * i / steps
        a = int(a_max * (1 - i / steps))
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    return layer


def make(bg_top, bg_bot, word_color, mark_file, glow):
    img = _vgrad(S, S, bg_top, bg_bot).convert("RGBA")
    img.alpha_composite(_radial(S, S, int(S * 0.5), int(S * 0.30), 360, glow, 40))
    mark = Image.open(os.path.join(PUB, mark_file)).convert("RGBA")
    mh = 210
    mark = mark.resize((int(mark.width * mh / mark.height), mh), Image.LANCZOS)
    word = "ilai"
    wf = _font(150, "SemiBold")
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0, 0), word, font=wf)
    ww, wh = bb[2] - bb[0], bb[3] - bb[1]
    gap = 34
    group_h = mh + gap + wh
    top = (S - group_h) // 2
    img.alpha_composite(mark, (int((S - mark.width) / 2), top))
    d.text((int((S - ww) / 2) - bb[0], top + mh + gap - bb[1]), word, font=wf, fill=word_color)
    return img.convert("RGB")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    icons = {}
    for name, (bt, bb, wc, mf, gl) in THEMES.items():
        im = make(bt, bb, wc, mf, gl)
        p = os.path.join(OUT_DIR, f"ilai-slack-{name}.png")
        im.save(p, "PNG")
        icons[name] = im
        print("wrote", p)

    # Montage: 3 cols, tiles with labels, on light gray.
    names = list(THEMES.keys())
    cols, tile, pad, label_h = 3, 300, 40, 56
    rows = (len(names) + cols - 1) // cols
    W = cols * tile + (cols + 1) * pad
    H = rows * (tile + label_h) + (rows + 1) * pad
    sheet = Image.new("RGB", (W, H), (238, 238, 236))
    d = ImageDraw.Draw(sheet)
    lf = _font(30, "Medium")
    for i, name in enumerate(names):
        r, c = divmod(i, cols)
        x = pad + c * (tile + pad)
        y = pad + r * (tile + label_h + pad)
        thumb = icons[name].resize((tile, tile), Image.LANCZOS)
        sheet.paste(thumb, (x, y))
        d.rectangle([x, y, x + tile - 1, y + tile - 1], outline=(210, 210, 208), width=1)
        bb = d.textbbox((0, 0), name, font=lf)
        d.text((x + (tile - (bb[2] - bb[0])) / 2, y + tile + 12), name, font=lf, fill=(60, 60, 58))
    sheet.save(os.path.join(OUT_DIR, "ilai-slack-variants.png"), "PNG")
    print("wrote montage")


if __name__ == "__main__":
    main()
