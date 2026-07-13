// Search-engine indexing pings.
//
// 1. IndexNow (Bing, Yandex, etc.) — always runs; no auth, the key is public
//    and hosted at /<key>.txt on the domain.
// 2. Google Indexing API — runs when GOOGLE_INDEXING_SA_KEY (service-account
//    JSON) is set; signs a JWT with Node crypto, no extra deps.
//
// Both read the live sitemap and notify each URL. Setup + replication:
// scripts/GOOGLE-INDEXING.md and the vault note "google-indexing-api-automation".
//
// Env:
//   GOOGLE_INDEXING_SA_KEY  (optional) service-account JSON string
//   SITEMAP_URL             (optional) defaults to the Ilai sitemap

import crypto from "node:crypto";

const SA_RAW = process.env.GOOGLE_INDEXING_SA_KEY;
const SITEMAP = process.env.SITEMAP_URL || "https://ilaicollective.com/sitemap.xml";
const INDEXNOW_KEY = "edae0875e8ccec77d0a7a85e4445cb70";

const b64url = (buf) =>
  Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

async function getSitemapUrls() {
  const res = await fetch(SITEMAP);
  if (!res.ok) throw new Error(`Sitemap fetch failed: ${res.status}`);
  const xml = await res.text();
  return [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].trim());
}

async function pingIndexNow(urls) {
  const host = new URL(SITEMAP).host;
  try {
    const res = await fetch("https://api.indexnow.org/indexnow", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        host,
        key: INDEXNOW_KEY,
        keyLocation: `https://${host}/${INDEXNOW_KEY}.txt`,
        urlList: urls,
      }),
    });
    const okStatus = res.status === 200 || res.status === 202;
    console.log(
      `IndexNow (Bing/Yandex): HTTP ${res.status} ${okStatus ? "accepted" : (await res.text()).slice(0, 140)}`,
    );
  } catch (e) {
    console.log("IndexNow error:", String(e));
  }
}

async function getGoogleToken(sa) {
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

async function googleSubmit(urls) {
  const sa = JSON.parse(SA_RAW);
  const token = await getGoogleToken(sa);
  let ok = 0;
  let failed = 0;
  for (const url of urls) {
    try {
      const res = await fetch("https://indexing.googleapis.com/v3/urlNotifications:publish", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ url, type: "URL_UPDATED" }),
      });
      if (res.ok) ok++;
      else {
        failed++;
        console.log(`  FAIL ${url} -> ${res.status} ${(await res.text()).slice(0, 140)}`);
      }
    } catch (e) {
      failed++;
      console.log(`  ERROR ${url} -> ${String(e)}`);
    }
    await new Promise((r) => setTimeout(r, 300));
  }
  console.log(`Google Indexing API: ${ok} submitted, ${failed} failed.`);
  return failed && !ok ? 1 : 0;
}

const urls = await getSitemapUrls();
console.log(`Found ${urls.length} URLs in ${SITEMAP}`);

await pingIndexNow(urls);

let exitCode = 0;
if (SA_RAW && SA_RAW.trim()) {
  exitCode = await googleSubmit(urls);
} else {
  console.log("GOOGLE_INDEXING_SA_KEY not set — skipping Google (IndexNow done).");
}
process.exit(exitCode);
