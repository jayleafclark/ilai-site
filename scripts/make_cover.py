"""Generate a branded 1200x630 blog cover for Ilai Collective.

Pure Pillow, no paid credits. Each cover uses one of several brand THEMES
(deep forest, powder pink, cream, charcoal), chosen deterministically from
the slug so the blog grid has real variety while staying on-brand. Every
theme sets its own background, text colour, accent, and logo variant.
Layout: category eyebrow + accent bar, wrapped Jost title, subtle leaf
motif, and the ilai wordmark + ilaicollective.com footer. Mirrors the
Karani cover engine, retuned to Ilai.
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "assets", "Jost.ttf")
PUB = os.path.join(HERE, "..", "public")

W, H = 1200, 630

# Brand colours
FOREST = (18, 53, 39)      # #123527
FOREST_2 = (13, 40, 29)    # #0d281d
GREEN = (28, 107, 74)      # #1c6b4a
PINK = (230, 169, 196)     # #e6a9c4
PINK_INK = (176, 99, 136)  # #b06388
GOLD = (201, 162, 92)      # #c9a25c
CREAM = (244, 241, 234)
MIST = (232, 237, 229)
WHITE = (255, 255, 255)

# theme = (bg_top, bg_bottom, title_rgb, eyebrow_rgb, bar_rgb, muted_rgb,
#          motif_rgb, logo_variant, glow_rgb)
THEMES = [
    # deep forest — white text, gold accent, light logo
    (FOREST, FOREST_2, WHITE, GOLD, GOLD, (176, 197, 186), PINK, "light", GOLD),
    # powder pink — dark forest text, forest accent, dark logo
    ((236, 184, 207), (222, 160, 189), FOREST, FOREST, GREEN, (138, 82, 110),
     GREEN, "dark", WHITE),
    # cream — dark forest text, pink accent, dark logo
    (CREAM, MIST, FOREST, GREEN, PINK_INK, (121, 132, 123), GREEN, "dark", PINK),
    # charcoal — white text, pink accent, light logo
    ((42, 45, 46), (29, 32, 33), WHITE, PINK, PINK, (170, 176, 172), PINK,
     "light", PINK),
]


def _font(size, weight="Regular"):
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def _vgrad(w, h, top, bottom):
    base = Image.new("RGB", (w, h), top)
    px = base.load()
    for y in range(h):
        t = y / max(1, h - 1)
        px_row = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = px_row
    return base


def _radial_glow(w, h, cx, cy, radius, color, max_alpha):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 60
    for i in range(steps, 0, -1):
        rr = radius * i / steps
        a = int(max_alpha * (1 - i / steps))
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    return layer


def _leaf(w, h, color, rot_deg, cx, cy):
    lyr = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lyr)
    d.ellipse([w * 0.32, 0, w * 0.68, h], fill=color)
    lyr = lyr.rotate(rot_deg, expand=True, resample=Image.BICUBIC)
    return lyr, (int(cx - lyr.width / 2), int(cy - lyr.height / 2))


def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def make_cover(slug, title, category, out_path):
    h = int(hashlib.sha256(slug.encode()).hexdigest(), 16)
    (bg_top, bg_bot, title_c, eb_c, bar_c, muted_c,
     motif_c, logo_variant, glow_c) = THEMES[h % len(THEMES)]

    img = _vgrad(W, H, bg_top, bg_bot).convert("RGBA")
    img.alpha_composite(_radial_glow(W, H, int(W * 0.86), int(H * 0.12), 520, glow_c, 46))

    motif = motif_c + (30,)
    l1, p1 = _leaf(320, 460, motif, -32, W * 0.86, H * 0.82)
    img.alpha_composite(l1, p1)
    l2, p2 = _leaf(300, 440, motif, 34, W * 0.965, H * 0.86)
    img.alpha_composite(l2, p2)

    draw = ImageDraw.Draw(img)
    pad = 76

    eb_font = _font(24, "SemiBold")
    draw.text((pad, 78), " ".join((category or "Journal").upper()), font=eb_font, fill=eb_c)
    draw.rounded_rectangle([pad, 124, pad + 64, 130], radius=3, fill=bar_c)

    title_font = _font(70, "SemiBold")
    lines = _wrap(draw, title, title_font, W - pad * 2 - 40)
    if len(lines) > 4:
        title_font = _font(58, "SemiBold")
        lines = _wrap(draw, title, title_font, W - pad * 2 - 40)
    line_h = int(title_font.size * 1.14)
    ty = int((H - line_h * len(lines)) / 2) + 18
    for ln in lines:
        draw.text((pad, ty), ln, font=title_font, fill=title_c)
        ty += line_h

    fy = H - 92
    logo_path = os.path.join(PUB, "logo-mark-light.png" if logo_variant == "light" else "logo-mark.png")
    word_x = pad
    try:
        mark = Image.open(logo_path).convert("RGBA")
        mh = 40
        mark = mark.resize((int(mark.width * mh / mark.height), mh), Image.LANCZOS)
        img.alpha_composite(mark, (pad, fy))
        word_x = pad + mark.width + 14
    except Exception:
        pass
    draw.text((word_x, fy - 2), "ilai", font=_font(38, "SemiBold"), fill=title_c)

    dom_font = _font(24, "Medium")
    dom = "ilaicollective.com"
    draw.text((W - pad - draw.textlength(dom, font=dom_font), fy + 8), dom, font=dom_font, fill=muted_c)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.convert("RGB").save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    import sys
    print(make_cover(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
