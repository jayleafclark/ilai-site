# Ilai Collective — website

Marketing site for [ilaicollective.com](https://ilaicollective.com). The human-led content
studio for experts and personal brands.

## Stack
- **Astro** (static output), hand-authored CSS with design tokens. No CSS framework.
- Fonts: **Figtree** (display/body) + **Space Grotesk** (labels/metrics), via Google Fonts.
- Deploys to **GitHub Pages** via `.github/workflows/deploy.yml` on push to `main`.

## Design system (read before editing UI)
- `BrandGuidelines.md` — tokens (color, type, spacing, radius, motion) + the voice gate.
- `Design.md` — the Do/Don't rules. When output drifts, add a new rule here.
- `src/styles/tokens.css` — the single source of truth for CSS variables.
- `src/styles/global.css` — resets + reusable classes (`.container`, `.section`, `.btn`, `.card`, etc.).

Every page reads tokens/classes from these. Page-specific CSS lives in each page's scoped
`<style>` block. Do not hardcode colors/fonts/spacing.

## Structure
```
src/
  layouts/Layout.astro        # <head>, SEO, fonts, reveal + counter scripts
  components/                 # Nav, Footer, Logo, SectionHeader, CTASection
  pages/
    index.astro               # Home
    what-we-do.astro          # Services
    method.astro              # The Signal Method
    work/dr-caroline-leaf.astro  # Case study
    about.astro
    contact.astro             # Book a call
    blog/                     # Blog (Astro content collections)
    sitemap.xml.ts
  content/blog/*.md           # Blog posts
public/                       # favicon, robots.txt, llms.txt, CNAME, images
```

## Develop
```bash
npm install
npm run dev      # local dev server
npm run build    # production build to dist/
npm run preview  # serve the build
```

## To finish before / after launch
- Replace the Formspree endpoint placeholder in `src/pages/contact.astro`.
- Add images: `public/work/dr-caroline-leaf.jpg` (headshot), optional
  `public/work/dashboard-year-review.png`, `public/about/jay.jpg`, `public/about/jj.jpg`,
  and `public/og.png` (1200×630 social card).
- Point the `ilaicollective.com` DNS at GitHub Pages and enable Pages (source: GitHub Actions).
