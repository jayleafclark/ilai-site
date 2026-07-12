/**
 * Ilai Collective — lead-capture Worker.
 *
 * Receives the /contact "free teardown" form (JSON POST), validates it, drops
 * bots via a honeypot, and delivers the lead to Slack (and optionally email via
 * Resend). Returns JSON so the site can show an on-page success state.
 *
 * Secrets (set with `wrangler secret put <NAME>`):
 *   SLACK_WEBHOOK   (required)  Incoming webhook URL for the Ilai Collective channel.
 *   RESEND_API_KEY  (optional)  If set, also emails the lead.
 *   LEAD_TO         (optional)  Where lead emails go (e.g. hello@ilaicollective.com).
 *   LEAD_FROM       (optional)  Verified Resend sender (e.g. leads@ilaicollective.com).
 *
 * Vars (in wrangler.toml [vars]):
 *   ALLOW_ORIGINS   Comma-separated allowed origins for CORS.
 */

const DEFAULT_ORIGINS = [
  "https://ilaicollective.com",
  "https://www.ilaicollective.com",
];

function corsHeaders(origin, env) {
  const allowed = (env.ALLOW_ORIGINS
    ? env.ALLOW_ORIGINS.split(",").map((s) => s.trim())
    : DEFAULT_ORIGINS);
  const allow = allowed.includes(origin) ? origin : allowed[0];
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}

const json = (obj, status, headers) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", ...headers },
  });

const isEmail = (s) => typeof s === "string" && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(s);
const clean = (s) => (typeof s === "string" ? s.trim().slice(0, 4000) : "");

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(origin, env);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method === "GET") {
      return json({ ok: true, service: "ilai-lead" }, 200, cors);
    }
    if (request.method !== "POST") {
      return json({ ok: false, error: "method-not-allowed" }, 405, cors);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ ok: false, error: "bad-json" }, 400, cors);
    }

    // Honeypot: real people never fill "company".
    if (clean(body.company)) return json({ ok: true }, 200, cors);

    const name = clean(body.name);
    const email = clean(body.email);
    const about = clean(body.about);
    const budget = clean(body.budget);

    if (!name || !isEmail(email) || !about) {
      return json({ ok: false, error: "invalid" }, 422, cors);
    }

    const text =
      `*New free-teardown request*\n` +
      `*Name:* ${name}\n` +
      `*Email:* ${email}\n` +
      `*Budget:* ${budget || "Not specified"}\n` +
      `*About:* ${about}`;

    // Deliver to Slack (primary).
    if (env.SLACK_WEBHOOK) {
      try {
        await fetch(env.SLACK_WEBHOOK, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
      } catch (e) {
        // fall through; still try email / still report failure below
      }
    }

    // Optional email via Resend.
    if (env.RESEND_API_KEY && env.LEAD_TO && env.LEAD_FROM) {
      try {
        await fetch("https://api.resend.com/emails", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${env.RESEND_API_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            from: env.LEAD_FROM,
            to: [env.LEAD_TO],
            reply_to: email,
            subject: `Free teardown request — ${name}`,
            text: `Name: ${name}\nEmail: ${email}\nBudget: ${budget || "Not specified"}\n\nAbout:\n${about}\n`,
          }),
        });
      } catch (e) {
        // non-fatal
      }
    }

    if (!env.SLACK_WEBHOOK && !env.RESEND_API_KEY) {
      return json({ ok: false, error: "no-delivery-configured" }, 500, cors);
    }

    return json({ ok: true }, 200, cors);
  },
};
