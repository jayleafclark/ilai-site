// Google Indexing API submitter.
//
// Reads a Google service-account JSON from the GOOGLE_INDEXING_SA_KEY env var
// (the full JSON string), fetches the site sitemap, and notifies Google's
// Indexing API (urlNotifications:publish, type URL_UPDATED) for every URL so
// Google is nudged to (re)crawl. Self-contained: signs the JWT with Node's
// crypto, no extra dependencies.
//
// Skips gracefully (exit 0) when the key is not set, so the workflow is a
// no-op until the secret is added.
//
// Env:
//   GOOGLE_INDEXING_SA_KEY  (required) full service-account JSON string
//   SITEMAP_URL             (optional) defaults to the Ilai sitemap
//
// Setup + how to replicate for other sites: see scripts/GOOGLE-INDEXING.md
// and the vault note "google-indexing-api-automation".

import crypto from "node:crypto";

const SA_RAW = process.env.GOOGLE_INDEXING_SA_KEY;
const SITEMAP = process.env.SITEMAP_URL || "https://ilaicollective.com/sitemap.xml";

if (!SA_RAW || !SA_RAW.trim()) {
  console.log("GOOGLE_INDEXING_SA_KEY not set — skipping (no-op).");
  process.exit(0);
}

const sa = JSON.parse(SA_RAW);

const b64url = (buf) =>
  Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

async function getAccessToken() {
  const now = Math.floor(Date.now() / 1000);
  const header = b64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claim = b64url(
    JSON.stringify({
      iss: sa.client_email,
      scope: "https://www.googleapis.com/auth/indexing",
      aud: "https://oauth2.googleapis.com/token",
      iat: now,
      exp: now + 3600,
    }),
  );
  const signer = crypto.createSign("RSA-SHA256");
  signer.update(`${header}.${claim}`);
  const signature = b64url(signer.sign(sa.private_key));
  const jwt = `${header}.${claim}.${signature}`;

  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
      assertion: jwt,
    }),
  });
  const json = await res.json();
  if (!json.access_token) throw new Error("Token exchange failed: " + JSON.stringify(json));
  return json.access_token;
}

async function getSitemapUrls() {
  const res = await fetch(SITEMAP);
  if (!res.ok) throw new Error(`Sitemap fetch failed: ${res.status}`);
  const xml = await res.text();
  return [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].trim());
}

const token = await getAccessToken();
const urls = await getSitemapUrls();
console.log(`Notifying Google Indexing API of ${urls.length} URLs from ${SITEMAP}`);

let ok = 0;
let failed = 0;
for (const url of urls) {
  try {
    const res = await fetch("https://indexing.googleapis.com/v3/urlNotifications:publish", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ url, type: "URL_UPDATED" }),
    });
    if (res.ok) {
      ok++;
    } else {
      failed++;
      console.log(`  FAIL ${url} -> ${res.status} ${(await res.text()).slice(0, 140)}`);
    }
  } catch (e) {
    failed++;
    console.log(`  ERROR ${url} -> ${String(e)}`);
  }
  await new Promise((r) => setTimeout(r, 300)); // gentle pacing (200/day quota)
}
console.log(`Done: ${ok} submitted, ${failed} failed.`);
if (failed && !ok) process.exit(1);
