# Ilai Collective — Design Rules (Do / Don't)

The enforcement layer. Read with `BrandGuidelines.md` before touching any UI. When output
drifts from the intended look, add a NEW rule here — never one-off hand-fix a single page.
Build section-by-section (hero → nav → cards), never regenerate a whole page at once.

## Layout
- DO use a floating "fluid island" nav pill (centered, `margin-top`, rounded-full, hairline,
  subtle backdrop blur only because it's fixed). DON'T glue an edge-to-edge navbar to the top.
- DO breathe unevenly: tight groups, then real air between groups. Section padding `--section-y`.
- DON'T build symmetrical 3-column Bootstrap grids with no whitespace. Asymmetry + generous gaps.
- DO cap content at `--maxw` (1200px); full-bleed only for backgrounds/media bands.
- DO lead every conversion path to "Book a call."

## Type
- DO pair Figtree (headline/body) + Space Grotesk (eyebrow/metrics) only.
- DO put an eyebrow pill/label before major H1/H2 (Space Grotesk, uppercase, tracking 0.18em).
- DO use negative tracking on display sizes. DON'T ship default letter-spacing on 48px+ text.
- DO get hierarchy from weight + color + size together. DON'T rely on size alone.

## Color
- DO use `--signal` for primary CTAs, links, and active states ONLY. Repeat it so it reads as a system.
- DON'T sprinkle the accent everywhere. Everything non-CTA stays near-monochrome.
- DO use `--drleaf` raspberry only inside the Dr. Leaf case-study section (contextual co-brand).

## Depth / cards
- DO use the double-bezel card for premium surfaces: outer shell (subtle bg + hairline + small pad
  + large radius), inner core (own bg + inset highlight + mathematically smaller radius).
- DON'T place premium cards flat on the background. DON'T use `shadow-md` or `rgba(0,0,0,0.3)` drops.
- DO get depth from whitespace, hairlines (`ring`/1px `--line`), and the one soft `--shadow-card` tier.
- DO nest CTA arrows in their own circle button-in-button. DON'T leave a naked arrow.

## Motion
- DO use `--ease` and IntersectionObserver fade-ups. Animate only transform/opacity.
- DO respect `prefers-reduced-motion` everywhere.
- DON'T animate 100×/day or keyboard-triggered interactions. DON'T use linear/ease-in-out.
- Golden rule: the best animation goes unnoticed. If every hover shouts "nice animation", dial it back.
- DO add ONE signature moment (hero mesh/counter), keep the rest subtle.

## Imagery
- DO show real product/dashboard screenshots inside a browser-chrome frame.
- DON'T use generic stock or generic-AI illustration. Deliberate type + palette does the work.

## Copy
- DO run the voice gate (BrandGuidelines "Voice"). Every claim: number, named thing, or outcome.
- DON'T say "we use AI" or "we scrape." Frame as research, signal, and software that aids humans.
- DON'T promise sales outcomes. Report "interest / intent surfaced," hand off at the funnel.

## The failure test
If another AI given "premium creative-agency site" would produce substantially the same output,
it failed. Read each screen with the brand name removed — can you tell it's Ilai, a content studio?
If not, go deeper.
