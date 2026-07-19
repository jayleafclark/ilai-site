"""Generate the Ilai Collective Slack app icon (512x512, brand-on-brand).

3-petal mark + "ilai" wordmark, centered, on the forest-green brand field.
Slack wants a square PNG >= 512x512; this renders full-bleed so it reads on
both light and dark Slack themes and stays legible at sidebar size.
Run:  python scripts/make_slack_icon.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "assets", "Jost.ttf")
PUB = os.path.join(HERE, "..", "public")
OUT_DIR = os.path.join(HERE, "..", "public")

S = 512
FOREST = (18, 53, 39)
FOREST_2 = (11, 34, 24)
PINK = (230, 169, 196)
CREAM = (244, 241, 234)
WHITE = (255, 255, 255)


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


def make(out_path, bg_top, bg_bot, mark_file, word_color, glow):
    img = _vgrad(S, S, bg_top, bg_bot).convert("RGBA")
    img.alpha_composite(_radial(S, S, int(S * 0.5), int(S * 0.30), 360, glow, 46))

    # Layout the mark + wordmark as one vertically-centered group.
    mark = Image.open(os.path.join(PUB, mark_file)).convert("RGBA")
    mark_h = 210
    mark = mark.resize((int(mark.width * mark_h / mark.height), mark_h), Image.LANCZOS)

    word = "ilai"
    wf = _font(150, "SemiBold")
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), word, font=wf)
    word_w = bbox[2] - bbox[0]
    word_h = bbox[3] - bbox[1]
    word_top_pad = bbox[1]  # font's internal top bearing

    gap = 34
    group_h = mark_h + gap + word_h
    top = (S - group_h) // 2

    img.alpha_composite(mark, (int((S - mark.width) / 2), top))
    wx = int((S - word_w) / 2) - bbox[0]
    wy = top + mark_h + gap - word_top_pad
    draw.text((wx, wy), word, font=wf, fill=word_color)

    img.convert("RGB").save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    make(os.path.join(OUT_DIR, "ilai-slack-icon.png"),
         FOREST, FOREST_2, "logo-mark-light.png", CREAM, PINK)
    make(os.path.join(OUT_DIR, "ilai-slack-icon-pink.png"),
         (236, 184, 207), (222, 160, 189), "logo-mark.png", FOREST, WHITE)
    print("wrote ilai-slack-icon.png + ilai-slack-icon-pink.png")
