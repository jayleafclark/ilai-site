import type { APIRoute } from "astro";
import { getCollection } from "astro:content";

const SITE = "https://ilaicollective.com";

// Static routes. Blog post URLs are appended dynamically below so every
// published article is discoverable — no manual edit per post.
const staticRoutes = [
  "/",
  "/what-we-do",
  "/method",
  "/work/dr-caroline-leaf",
  "/about",
  "/blog",
  "/contact",
];

export const GET: APIRoute = async () => {
  const posts = await getCollection("blog", ({ data }) => !data.draft);

  const entries: { loc: string; lastmod?: string }[] = [
    ...staticRoutes.map((r) => ({ loc: r === "/" ? `${SITE}/` : `${SITE}${r}/` })),
    ...posts.map((p) => ({
      loc: `${SITE}/blog/${p.slug}/`,
      lastmod: (p.data.updatedDate ?? p.data.pubDate)
        .toISOString()
        .slice(0, 10),
    })),
  ];

  const urls = entries
    .map(
      (e) =>
        `  <url><loc>${e.loc}</loc>${
          e.lastmod ? `<lastmod>${e.lastmod}</lastmod>` : ""
        }<changefreq>weekly</changefreq></url>`,
    )
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;
  return new Response(xml, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  });
};
