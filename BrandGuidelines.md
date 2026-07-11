# Ilai Collective — Brand Guidelines (tokens)

The single source of truth for design tokens. Every page and component reads from
`src/styles/tokens.css`. Do not hardcode colors, fonts, radii, or spacing anywhere else.
When a value is missing, add it here first, then to `tokens.css`, then use it.

Companion file: `Design.md` (the Do/Don't rules). Read both before building any UI.

---

## Brand in one line
The human-led content studio for experts and personal brands. **Tagline: "Proven to spread."**

Aesthetic target: **Airbnb** — techy, clean, mature ("went-public" polish), one accent,
soft rounded corners, depth from whitespace not heavy shadows. Warm and human, never cold.
NOT Headspace (avoid their warm orange/coral world), NOT an Airbnb clone (cool accent, our own type).

---

## Color

Airbnb-style discipline: white base, one vivid accent reserved for primary CTAs only,
everything else near-monochrome. Depth comes from whitespace and hairlines, not shadows.

| Token | Hex | Role |
|---|---|---|
| `--ink` | `#16161A` | Primary text, headlines |
| `--ink-2` | `#3D3D46` | Strong secondary text |
| `--muted` | `#6B6B75` | Secondary / caption text |
| `--canvas` | `#FFFFFF` | Page background (base) |
| `--mist` | `#F6F5F2` | Alt section background (warm off-white) |
| `--sand` | `#EFEDE7` | Deeper panel background |
| `--line` | `#E7E5DF` | Hairline borders |
| `--line-2` | `#D9D7CF` | Stronger hairline |
| `--signal` | `#4B3FE4` | PRIMARY ACCENT — CTAs, links, active only |
| `--signal-hover` | `#3A2FC4` | Accent hover/pressed |
| `--signal-tint` | `#ECEAFF` | Accent wash / badge backgrounds |
| `--signal-ink` | `#2A2199` | Accent text on tint |
| `--drleaf` | `#E03064` | Dr. Leaf co-brand raspberry — case-study section ONLY |

Accent is swappable: change `--signal*` only. Documented alternates: teal `#0E9F8E`, coral `#F0492E`.

## Typography

Two families only. Both free on Google Fonts. Neither is in the AI-default banned set.

- **Figtree** — display, headlines, body, UI. Warm geometric-humanist (free Airbnb-Cereal analog).
  Weights used: 400, 500, 600, 700, 800.
- **Space Grotesk** — eyebrow labels, metric numerals, small techy accents. Weights: 500, 700.

Type scale (ratio ~1.25, stepped — never pick sizes by feel):

| Token | clamp() | Use |
|---|---|---|
| `--fs-display` | `clamp(2.75rem, 6vw + 1rem, 5.5rem)` | Hero H1 |
| `--fs-h1` | `clamp(2.25rem, 3.5vw + 1rem, 3.75rem)` | Page titles |
| `--fs-h2` | `clamp(1.75rem, 2vw + 1rem, 2.75rem)` | Section titles |
| `--fs-h3` | `clamp(1.25rem, 1vw + 1rem, 1.6rem)` | Card titles |
| `--fs-lead` | `clamp(1.125rem, 0.6vw + 1rem, 1.375rem)` | Lead paragraphs |
| `--fs-body` | `1.0625rem` | Body |
| `--fs-sm` | `0.9375rem` | Small |
| `--fs-eyebrow` | `0.75rem` | Uppercase eyebrow (Space Grotesk, tracking 0.18em) |

Rules: negative tracking at display sizes (`--tracking-display: -0.03em`). Hierarchy from
weight + color + size together, never size alone. Line-height tight on headlines (1.05–1.12),
open on body (1.6).

## Spacing (4px base)

`--sp-1: 4px` … `2:8 3:12 4:16 5:24 6:32 8:48 10:64 12:96 16:128`.
Section vertical padding: `--section-y: clamp(5rem, 10vw, 10rem)` (generous, Airbnb-like).
Content max width: `--maxw: 1200px`; prose `--maxw-prose: 68ch`.

## Radius

Fixed per element type (mixing radii is an AI tell):
- Buttons/pills: `--r-pill: 999px`
- Cards: `--r-card: 20px` (Airbnb signature), inner core `calc(20px - 5px)`
- Inputs: `--r-input: 12px`
- Media: `--r-media: 16px`

## Elevation

No harsh shadows. One soft card shadow tier only (Airbnb 3-layer):
`--shadow-card: rgba(22,22,26,0.03) 0 0 0 1px, rgba(22,22,26,0.04) 0 2px 8px, rgba(22,22,26,0.08) 0 12px 28px -12px`.
Prefer hairlines (`1px solid var(--line)`) and whitespace for structure.

## Motion

- Easing: `--ease: cubic-bezier(0.32, 0.72, 0, 1)` (never linear/ease-in-out).
- Durations: micro 160–220ms; entrances 500–700ms; hero 700ms+.
- Scroll entrances: heavy fade-up (`translateY(24px)` + slight blur → resolved) via IntersectionObserver.
- Buttons: `active:scale(0.98)`, nested arrow translates on hover.
- `prefers-reduced-motion: reduce` disables all transitions/animation. Mandatory.
- Animate only `transform` and `opacity`.

## Iconography
Ultra-light line icons only (inline SVG, 1.5px stroke). No thick Lucide/FontAwesome/Material.

## Voice (enforced on every line of copy)
Plain, specific, confident. Every claim carries a number, a named thing, or a concrete outcome.
Sentence case. No hype. Human-led framing — sophisticated software/engines *aid* the work;
humans direct, judge, sign off. NEVER "we use AI" or "we scrape."
Banned: em dashes; "not X, it's Y" cadence; "not only…but also"; delve/tapestry/seamless/
showcase/testament/underscore; unlock/transformative/game-changing/supercharge; quietly/
secretly/subtly/profound/incredible/remarkable; "at the end of the day"/"here's the thing"/"the truth is".
