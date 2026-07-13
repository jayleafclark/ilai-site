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


def _draw_tracked(draw, xy, text, font, fill, tracking):
    """Draw text with manual letter-spacing (Pillow has no native tracking)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def _tracked_width(draw, text, font, tracking):
    return sum(draw.textlength(ch, font=font) + tracking for ch in text) - tracking


PAD = 76


def make_cover(slug, title, category, out_path):
    # Branded editorial cover: gradient + glow + leaf texture, with the post
    # TITLE baked on (an SEO-keyword eyebrow from tags[0], the wrapped Jost
    # title, the "Ilai Collective" wordmark lockup, and the domain footer).
    # These covers are the blog-card art and the social/OG share image, so the
    # title is the single visual title there; article pages keep the HTML <h1>
    # and do not repeat the image, so there is no double title. Theme is picked
    # deterministically from the slug for on-brand variety.
    h = int(hashlib.sha256(slug.encode()).hexdigest(), 16)
    (bg_top, bg_bot, title_c, eb_c, bar_c, muted_c,
     motif_c, logo_variant, glow_c) = THEMES[h % len(THEMES)]

    img = _vgrad(W, H, bg_top, bg_bot).convert("RGBA")
    img.alpha_composite(_radial_glow(W, H, int(W * 0.82), int(H * 0.14), 560, glow_c, 46))
    img.alpha_composite(_radial_glow(W, H, int(W * 0.12), int(H * 0.92), 440, glow_c, 26))

    # Soft leaf motif for texture — pushed to the far corners so it sits behind
    # the type, never across it.
    motif = motif_c + (24,)
    l1, p1 = _leaf(360, 520, motif, -30, W * 0.94, H * 0.90)
    img.alpha_composite(l1, p1)
    l2, p2 = _leaf(260, 380, motif, 34, W * 0.02, H * 0.06)
    img.alpha_composite(l2, p2)

    draw = ImageDraw.Draw(img)

    # --- Top-left brand lockup: 3-petal mark + "Ilai Collective" wordmark ---
    lock_y = 62
    mark_h = 44
    wordmark_x = PAD
    logo_path = os.path.join(
        PUB, "logo-mark-light.png" if logo_variant == "light" else "logo-mark.png")
    try:
        mark = Image.open(logo_path).convert("RGBA")
        mark = mark.resize((int(mark.width * mark_h / mark.height), mark_h), Image.LANCZOS)
        img.alpha_composite(mark, (PAD, lock_y))
        wordmark_x = PAD + mark.width + 18
    except Exception:
        pass
    wm_font = _font(30, "SemiBold")
    draw.text((wordmark_x, lock_y + (mark_h - 30) // 2 - 2),
              "Ilai Collective", font=wm_font, fill=title_c)

    # --- Title block: eyebrow (SEO keyword) + accent bar + wrapped title ---
    max_w = W - PAD * 2
    eb_text = (category or "Journal").upper()
    eb_font = _font(24, "SemiBold")
    eb_track = 4

    # Fit the title: largest size that wraps into <= 4 lines.
    title_font = None
    lines = []
    for size in (86, 78, 70, 62, 54, 48):
        title_font = _font(size, "SemiBold")
        lines = _wrap(draw, title, title_font, max_w)
        if len(lines) <= 4:
            break
    ascent, descent = title_font.getmetrics()
    lh = int((ascent + descent) * 1.06)

    BAR_H = 5
    BAR_GAP = 20          # bar -> eyebrow
    EB_H = 26
    EB_GAP = 24           # eyebrow -> title
    pre_title = BAR_H + BAR_GAP + EB_H + EB_GAP
    group_h = pre_title + len(lines) * lh

    top_limit = lock_y + mark_h + 44
    bot_limit = H - 116
    gy = top_limit + max(0, (bot_limit - top_limit - group_h) // 2)

    # accent bar
    draw.rounded_rectangle([PAD, gy, PAD + 62, gy + BAR_H], radius=3, fill=bar_c)
    # eyebrow (tracked, uppercase)
    _draw_tracked(draw, (PAD, gy + BAR_H + BAR_GAP), eb_text, eb_font, eb_c, eb_track)
    # title
    ty = gy + pre_title
    for ln in lines:
        draw.text((PAD, ty), ln, font=title_font, fill=title_c)
        ty += lh

    # --- Footer: domain, muted ---
    dom = "ilaicollective.com"
    dom_font = _font(24, "Medium")
    draw.text((PAD, H - 74), dom, font=dom_font, fill=muted_c)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.convert("RGB").save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    import sys
    print(make_cover(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
