import type { APIRoute } from "astro";

const SITE = "https://ilaicollective.com";

// Static routes. The blog build appends its post URLs here.
const routes = [
  "/",
  "/what-we-do",
  "/method",
  "/work/dr-caroline-leaf",
  "/about",
  "/blog",
  "/contact",
];

export const GET: APIRoute = () => {
  const urls = routes
    .map(
      (r) =>
        `  <url><loc>${SITE}${r}</loc><changefreq>weekly</changefreq></url>`,
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
