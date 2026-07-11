"""Generate covers for every blog post and ensure each has a `cover:` field.

Run from the repo root:  python scripts/gen_covers.py
Idempotent: regenerates the PNG each run; adds the cover frontmatter line
only if missing.
"""
import glob
import os
import re

from make_cover import make_cover

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.join(ROOT, "src", "content", "blog")
COVERS = os.path.join(ROOT, "public", "blog", "covers")


def parse_front(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None, None, None, None
    fm = m.group(1)
    end = m.end()
    title = re.search(r'^title:\s*"?(.+?)"?\s*$', fm, re.M)
    tags = re.search(r"^tags:\s*\[(.*?)\]", fm, re.M)
    cover = re.search(r"^cover:\s*", fm, re.M)
    title = title.group(1) if title else ""
    cat = ""
    if tags:
        first = tags.group(1).split(",")[0].strip().strip('"').strip("'")
        cat = first
    return title, cat, (cover is not None), end


def main():
    os.makedirs(COVERS, exist_ok=True)
    files = sorted(glob.glob(os.path.join(BLOG, "*.md")))
    for path in files:
        slug = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        title, cat, has_cover, fm_end = parse_front(text)
        if title is None:
            print("skip (no frontmatter):", slug)
            continue
        out = os.path.join(COVERS, slug + ".png")
        make_cover(slug, title, cat or "Journal", out)
        rel = f"/blog/covers/{slug}.png"
        if not has_cover:
            # insert cover line just before the closing --- of frontmatter
            text = re.sub(
                r"(^---\s*\n.*?\n)(---\s*\n)",
                lambda m: m.group(1) + f'cover: "{rel}"\n' + m.group(2),
                text, count=1, flags=re.S,
            )
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        print("cover:", slug, "->", rel, "(added)" if not has_cover else "(exists)")


if __name__ == "__main__":
    main()
