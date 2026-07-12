# Ilai lead-capture Worker

Receives the `/contact` free-teardown form and delivers leads to Slack (and
optionally email). The site posts JSON to this Worker; on success it shows an
on-page confirmation. If the Worker is unreachable, the form falls back to a
pre-filled email so no lead is ever lost.

## Deploy

```bash
cd worker
npx wrangler login          # or set CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID
npx wrangler deploy
```

Deploy prints the public URL, e.g. `https://ilai-lead.<your-subdomain>.workers.dev`.

## Set secrets (after first deploy)

```bash
npx wrangler secret put SLACK_WEBHOOK     # required: Ilai Collective incoming webhook
# optional email delivery:
npx wrangler secret put RESEND_API_KEY
npx wrangler secret put LEAD_TO           # e.g. hello@ilaicollective.com
npx wrangler secret put LEAD_FROM         # verified Resend sender
```

## Wire the site

Put the deployed URL into the form's `data-endpoint` in
`src/pages/contact.astro` (currently a `REPLACE` placeholder), then rebuild and
deploy the site. Until then the form works via the email fallback.

Optional: bind a custom route like `forms.ilaicollective.com` in the Cloudflare
dashboard and use that as the endpoint instead of the `workers.dev` URL.
