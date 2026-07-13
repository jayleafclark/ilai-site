# Google Indexing API automation

Auto-notifies Google to (re)crawl every URL in the sitemap. Runs daily and on
demand via `.github/workflows/google-index.yml` → `scripts/google-index.mjs`.

It is **dormant until you add the service-account key** — the script no-ops
without `GOOGLE_INDEXING_SA_KEY`, so the workflow is safe to have committed.

## One-time setup (do these once)

1. **Google Cloud Console** (console.cloud.google.com) → create/select a project.
2. APIs & Services → Library → enable **"Web Search Indexing API"**.
3. APIs & Services → Credentials → **Create credentials → Service account**.
   Give it a name (e.g. `indexer`). No roles needed.
4. Open the service account → **Keys → Add key → Create new key → JSON** →
   download the JSON file.
5. **Google Search Console** → your property → Settings → **Users and
   permissions → Add user** → paste the service account's email
   (`indexer@<project>.iam.gserviceaccount.com`) as an **Owner**. (This is what
   authorizes the API to submit URLs for this property.)
6. Add the JSON file's **entire contents** as a repo secret named
   **`GOOGLE_INDEXING_SA_KEY`** (GitHub → repo → Settings → Secrets and
   variables → Actions → New repository secret).

Done. It now runs daily; trigger it any time from the Actions tab → this
workflow → **Run workflow**.

## Notes / caveats

- Quota is 200 URLs/day per project (this site has ~23, so plenty of headroom).
- Google's Indexing API is officially for JobPosting/BroadcastEvent pages; for
  marketing pages it is a **nudge**, not a guarantee — the sitemap remains the
  reliable path. Treat this as a speed-up, not magic.
- The sitemap URL is set via `SITEMAP_URL` env in the workflow.

## Replicate for another site (e.g. Karani)

Copy `scripts/google-index.mjs` + `.github/workflows/google-index.yml` into the
other repo, change `SITEMAP_URL`, and repeat steps 3–6 (a fresh service account
can reuse the same GCP project; just re-add it as an Owner in that site's Search
Console property). See the vault note `google-indexing-api-automation` for the
canonical write-up.
