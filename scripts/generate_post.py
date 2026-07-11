"""Ilai Collective content engine — generate the next blog post.

Picks the next pending topic from content-engine/backlog.json, drafts it
with the Anthropic API (raw urllib, no SDK) using content-engine/voice.md as
the system brief, runs the language gate (rules_check) with a regenerate
loop, generates a branded cover, writes the Astro markdown into
src/content/blog/, and updates the backlog + log ledgers.

Exit codes: 0 = published, 3 = backlog empty (clean success), 1 = error.

Env:
  ANTHROPIC_API_KEY  (required)
  ILAI_MODEL         (default claude-sonnet-5)
  ILAI_DATE          (override pubDate, YYYY-MM-DD, for testing)
  ILAI_SLUG          (force a specific backlog slug, for testing)
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

from rules_check import scan
from make_cover import make_cover

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, "content-engine")
BACKLOG = os.path.join(ENGINE, "backlog.json")
LOG = os.path.join(ENGINE, "log.json")
VOICE = os.path.join(ENGINE, "voice.md")
BLOG = os.path.join(ROOT, "src", "content", "blog")
COVERS = os.path.join(ROOT, "public", "blog", "covers")

MODEL = os.environ.get("ILAI_MODEL", "claude-sonnet-5")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


def _load(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _save(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def call_anthropic(system, user, max_tokens=4000):
    body = json.dumps({
        "model": MODEL,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    delay = 4
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode("utf-8"))
                return "".join(b.get("text", "") for b in data.get("content", []))
        except urllib.error.HTTPError as e:
            code = e.code
            if code in (429, 500, 502, 503, 529) and attempt < 5:
                time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            raise
    raise RuntimeError("anthropic call failed after retries")


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.S)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model output")
    return json.loads(text[start:end + 1])


def build_user(topic, violations=None):
    base = (
        f"Write the article for this topic.\n"
        f"Primary keyword: {topic['keyword']}\n"
        f"Suggested title: {topic['title']}\n"
        f"Category (use as the first tag): {topic['category']}\n"
        f"Search intent: {topic['intent']}\n"
        f"Angle: {topic['angle']}\n\n"
        f"Return only the JSON object per the output contract."
    )
    if violations:
        vt = "\n".join(f"- {c}: {m}" for c, m in violations)
        base += (
            "\n\nYour previous draft violated the language rules. Rewrite the WHOLE "
            "article to remove every one of these, keeping the meaning and quality:\n" + vt
        )
    return base


def main():
    if not API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 1

    backlog = _load(BACKLOG, [])
    log = _load(LOG, [])
    logged = {e["slug"] for e in log}

    forced = os.environ.get("ILAI_SLUG", "").strip()
    topic = None
    for row in backlog:
        if forced:
            if row["slug"] == forced:
                topic = row
                break
        elif row.get("status") == "pending" and row["slug"] not in logged:
            topic = row
            break

    if topic is None:
        print("Backlog empty — nothing to publish.")
        return 3

    with open(VOICE, "r", encoding="utf-8") as f:
        system = f.read()

    obj, violations = None, None
    for attempt in range(4):
        out = call_anthropic(system, build_user(topic, violations))
        try:
            obj = extract_json(out)
        except Exception as e:
            print(f"attempt {attempt+1}: parse error: {e}", file=sys.stderr)
            violations = [("parse", "return one valid JSON object")]
            continue
        blob = "\n".join([obj.get("title", ""), obj.get("description", ""), obj.get("body_markdown", "")])
        violations = scan(blob)
        if not violations:
            break
        print(f"attempt {attempt+1}: {len(violations)} violations, regenerating", file=sys.stderr)

    if obj is None:
        print("ERROR: no usable draft", file=sys.stderr)
        return 1
    final = scan("\n".join([obj.get("title", ""), obj.get("description", ""), obj.get("body_markdown", "")]))
    if final:
        print("ERROR: draft still violates rules after 4 attempts:", file=sys.stderr)
        for c, m in final:
            print(f"  {c}: {m}", file=sys.stderr)
        return 1

    slug = topic["slug"]
    title = obj["title"].strip()
    desc = obj["description"].strip().replace('"', "'")
    tags = obj.get("tags") or [topic["category"]]
    tag_str = ", ".join(f'"{t}"' for t in tags)
    pub = os.environ.get("ILAI_DATE") or time.strftime("%Y-%m-%d")

    make_cover(slug, title, tags[0] if tags else topic["category"], os.path.join(COVERS, slug + ".png"))

    fm = (
        "---\n"
        f'title: "{title}"\n'
        f'description: "{desc}"\n'
        f"pubDate: {pub}\n"
        f'author: "Ilai Collective"\n'
        f"tags: [{tag_str}]\n"
        f'cover: "/blog/covers/{slug}.png"\n'
        "---\n\n"
    )
    with open(os.path.join(BLOG, slug + ".md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(fm + obj["body_markdown"].strip() + "\n")

    for row in backlog:
        if row["slug"] == slug:
            row["status"] = "published"
    log.append({"slug": slug, "keyword": topic["keyword"], "title": title,
                "category": topic["category"], "date": pub, "url": f"/blog/{slug}"})
    _save(BACKLOG, backlog)
    _save(LOG, log)
    print(f"Published: {slug} ({pub})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
