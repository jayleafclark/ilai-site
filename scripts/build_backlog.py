"""Build content-engine/backlog.json for the Ilai SEO content engine.

Topics come from the DataForSEO keyword research (US search volume, 2026-07).
Any topic whose slug already exists as a published article in
src/content/blog/ is marked "published" so the engine never regenerates it.
Run:  python scripts/build_backlog.py
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content-engine", "backlog.json")
BLOG = os.path.join(ROOT, "src", "content", "blog")

# (slug, title, keyword, sv, intent, category, angle)
TOPICS = [
    # --- Content strategy ---
    ("how-to-build-a-content-strategy-expert", "How to Build a Content Marketing Strategy as a Subject-Matter Expert", "content marketing strategy", 4400, "informational", "Content Strategy", "The research-first framework: audience, niche study, pillars from real expertise, formats, measurement."),
    ("content-pillars-examples", "Content Pillars: Real Examples for Coaches, Authors and Founders", "content pillars examples", 320, "informational", "Content Strategy", "Show 3-4 pillar sets built from a real expert's expertise, not generic templates."),
    ("how-to-run-a-content-audit", "What a Content Audit Is and How to Run One", "content audit", 390, "informational", "Content Strategy", "Human-led audit checklist; teaser for a done-for-you audit."),
    ("evergreen-content-for-experts", "Evergreen Content: How Experts Compound Reach Over Time", "evergreen content", 1600, "informational", "Content Strategy", "Argue for durable, researched content over disposable filler."),
    ("content-marketing-examples-2026", "Content Marketing Examples Worth Copying in 2026", "content marketing examples", 720, "informational", "Content Strategy", "Curated teardown; establishes taste and expertise."),
    # --- Short-form video & repurposing ---
    ("how-to-make-a-reel-that-gets-watched", "How to Make a Reel That Actually Gets Watched", "how to make a reel", 2400, "informational", "Short-form Video", "Retention-first editing; hook, structure, pacing, captions."),
    ("turn-one-podcast-into-30-pieces", "How to Turn One Podcast Into 30 Pieces of Content", "repurpose a podcast", 210, "informational", "Repurposing", "The repurposing engine, flagship differentiator."),
    ("short-form-video-ideas-for-experts", "Short-Form Video Ideas for Experts Who Hate Being on Camera", "short form video ideas", 210, "informational", "Short-form Video", "Talking-head plus motion-graphics alternatives."),
    ("how-to-add-captions-to-video", "How to Add Captions to Video (and Why They Double Watch Time)", "how to add captions to video", 1300, "informational", "Short-form Video", "Practical plus a subtle craft flex."),
    ("how-to-write-a-hook-that-stops-the-scroll", "How to Write a Hook That Stops the Scroll", "how to write a hook", 5400, "informational", "Copywriting", "High-volume anchor; scripting expertise."),
    ("video-editing-for-beginners", "Video Editing for Beginners: A Creator's First 10 Edits", "video editing for beginners", 1600, "informational", "Short-form Video", "Top-funnel magnet; soft CTA to done-for-you editing."),
    # --- Podcast ---
    ("how-to-start-a-podcast-expert-guide", "How to Start a Podcast: A 2026 Guide for Experts", "how to start a podcast", 22200, "informational", "Podcasting", "Comprehensive guide; concept, gear, editing, publishing, repurposing."),
    ("how-to-edit-a-podcast", "How to Edit a Podcast So It Sounds Professional", "how to edit a podcast", 320, "informational", "Podcasting", "Craft piece; ladders to the service."),
    ("podcast-editing-service-guide", "Podcast Editing Service: What to Look For (and What It Costs)", "podcast editing service", 390, "commercial", "Podcasting", "Bottom-funnel; transparent pricing angle."),
    # --- Platform growth ---
    ("best-time-to-post-on-instagram", "The Best Time to Post on Instagram (What the Data Actually Says)", "best time to post on instagram", 90500, "informational", "Instagram", "Data-grounded; find your own best time from your audience."),
    ("how-the-instagram-algorithm-works", "How the Instagram Algorithm Works in 2026", "instagram algorithm", 3600, "informational", "Instagram", "Evergreen explainer; internal-link hub."),
    ("how-to-grow-on-linkedin-as-a-founder", "How to Grow on LinkedIn as a Founder or Expert", "how to grow on linkedin", 70, "informational", "LinkedIn", "ICP-aligned; feeds the LinkedIn service."),
    ("linkedin-post-ideas-for-thought-leaders", "LinkedIn Post Ideas for Thought Leaders", "linkedin post ideas", 590, "informational", "LinkedIn", "Idea bank; strategic depth."),
    ("how-to-grow-a-youtube-channel-with-seo", "How to Grow a YouTube Channel with SEO", "youtube seo", 2900, "informational", "YouTube", "Ranks for search-intent creators."),
    ("tiktok-for-business-playbook", "TikTok for Business: A Practical Playbook for Experts", "tiktok for business", 8100, "informational", "TikTok", "High-volume; brandable framework."),
    ("how-to-get-more-engagement-on-instagram", "How to Get More Engagement on Instagram (Without Gimmicks)", "how to get more engagement on instagram", 390, "informational", "Instagram", "Anti-hack, quality-first."),
    ("instagram-post-ideas-for-personal-brands", "Instagram Post Ideas for Personal Brands", "instagram post ideas", 1300, "informational", "Instagram", "Idea bank magnet."),
    ("how-often-should-you-post-on-social-media", "How Often Should You Post on Social Media?", "how often should i post on social media", 110, "informational", "Content Systems", "Bridges to scheduling and consistency."),
    # --- Thought leadership ---
    ("what-is-thought-leadership", "What Is Thought Leadership (and How to Build It)", "what is thought leadership", 1900, "informational", "Thought Leadership", "Definition first, then a real build."),
    ("how-to-build-a-personal-brand", "How to Build a Personal Brand as an Expert", "how to build a personal brand", 590, "informational", "Personal Brand", "Foundational; links to services."),
    ("thought-leadership-content-formats", "Thought Leadership Content: Formats That Build Authority", "thought leadership content", 210, "informational", "Thought Leadership", "Ties formats to Ilai's craft menu."),
    ("personal-branding-tips-for-founders", "Personal Branding Tips for Founders and Consultants", "personal branding tips", 260, "informational", "Personal Brand", "Audience-specific."),
    # --- Newsletters & long-form ---
    ("newsletter-examples-that-work", "Newsletter Examples That Prove Long-Form Still Wins", "newsletter examples", 3600, "informational", "Newsletters", "Format types with what makes each work."),
    ("how-to-write-a-newsletter", "How to Write a Newsletter People Actually Open", "how to write a newsletter", 480, "informational", "Newsletters", "Craft plus soft CTA to the newsletter service."),
    ("how-to-grow-a-newsletter-from-zero", "How to Grow a Newsletter from Zero", "how to grow a newsletter", 90, "informational", "Newsletters", "Ladder and lead-magnet angle."),
    ("seo-content-writing-for-experts", "SEO Content Writing: How Experts Rank Without Sounding Robotic", "seo content writing", 1300, "informational", "SEO", "Human-led thesis front and center."),
    ("how-to-write-a-blog-post-that-ranks", "How to Write a Blog Post That Ranks and Reads Well", "how to write a blog post", 720, "informational", "SEO", "Meta craft piece; demonstrates ability."),
    ("long-form-vs-short-form-content", "Long-Form Content: When It Beats Short-Form", "long form content", 720, "informational", "Content Strategy", "Positions full-funnel capability."),
    # --- Hiring an agency (commercial) ---
    ("what-a-content-agency-does", "What a Content Creation Agency Does (and When to Hire One)", "content creation agency", 8100, "commercial", "Hiring an Agency", "Define the human-led model; when to hire."),
    ("content-agency-vs-freelancer", "Content Agency vs Freelancer vs In-House: How to Choose", "content agency vs freelancer", 90, "commercial", "Hiring an Agency", "Decision guide; ranks easily, converts."),
    ("how-much-does-a-content-agency-cost", "How Much Does a Content Agency Cost?", "content marketing pricing", 90, "commercial", "Hiring an Agency", "Transparent pricing equals trust."),
    ("done-for-you-content-explained", "Done-for-You Content: What It Includes and Who It's For", "done for you content", 90, "commercial", "Hiring an Agency", "Owns Ilai's exact positioning term."),
    ("social-media-management-services", "Social Media Management Services: What's Actually Included", "social media management services", 2400, "commercial", "Hiring an Agency", "High-volume commercial page."),
    ("content-strategy-agency-what-you-get", "Content Strategy Agency: What You Get Beyond Posting", "content strategy agency", 210, "commercial", "Hiring an Agency", "Strategy-first differentiation."),
    # --- Content systems ---
    ("how-to-build-a-social-media-content-calendar", "How to Build a Social Media Content Calendar", "social media content calendar", 2400, "informational", "Content Systems", "Pillars to slots; cadence by stage."),
    ("content-batching-for-experts", "Content Batching: How Experts Create a Month in a Day", "content batching", 90, "informational", "Content Systems", "Systems and consistency angle."),
    ("social-media-engagement-strategy", "A Social Media Engagement Strategy That Builds Community", "social media engagement strategy", 260, "informational", "Engagement", "First-30-min replies; a differentiator."),
    ("community-management-on-social-media", "Community Management on Social Media: The Human Layer", "community management social media", 390, "informational", "Engagement", "Engagement at any stage."),
    ("content-distribution-strategy", "Content Distribution Strategy: Getting Seen on Every Channel", "content distribution strategy", 140, "informational", "Content Systems", "Full-funnel systems thinking."),
    # --- By audience ---
    ("social-media-for-authors", "Social Media for Authors: Building a Platform Before Launch", "social media for authors", 140, "commercial", "By Audience", "Hyper-targeted; easy rank."),
    ("content-marketing-for-coaches", "Content Marketing for Coaches: A Client-Attracting System", "content marketing for coaches", 90, "commercial", "By Audience", "ICP page."),
    ("content-marketing-for-consultants", "Content Marketing for Consultants and B2B Experts", "content marketing for consultants", 70, "commercial", "By Audience", "Links to B2B pillar."),
    # --- Design / motion ---
    ("motion-graphics-for-social-media", "Motion Graphics for Social Media: When Movement Beats Static", "motion graphics for social media", 90, "informational", "Design", "A real Ilai edge; near-zero competition."),
    ("how-to-design-an-instagram-carousel", "How to Design an Instagram Carousel That Gets Saved", "instagram carousel", 1900, "informational", "Design", "High-volume design piece; craft showcase."),
    ("how-to-make-quote-cards-on-brand", "How to Make Quote Cards That Stay On-Brand", "how to make quote cards", 90, "informational", "Design", "On-brand-templates flex."),
]


def main():
    published = set()
    for p in glob.glob(os.path.join(BLOG, "*.md")):
        published.add(os.path.splitext(os.path.basename(p))[0])

    rows = []
    for slug, title, kw, sv, intent, cat, angle in TOPICS:
        rows.append({
            "slug": slug,
            "title": title,
            "keyword": kw,
            "sv": sv,
            "intent": intent,
            "category": cat,
            "angle": angle,
            "status": "published" if slug in published else "pending",
        })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
        f.write("\n")

    pend = sum(1 for r in rows if r["status"] == "pending")
    pub = len(rows) - pend
    print(f"backlog.json written: {len(rows)} topics ({pub} published, {pend} pending)")


if __name__ == "__main__":
    main()
