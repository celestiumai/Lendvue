/**
 * Form handler — POST /api/submit-form (called from worker/index.js)
 *
 * Receives JSON from any form on the site and emails it via Resend
 * (https://resend.com). Replaces Gravity Forms / WordPress mail entirely.
 *
 * REQUIRED variables (Cloudflare dashboard -> Workers & Pages -> lendvue ->
 * Settings -> Variables and Secrets):
 *   RESEND_API_KEY   - secret, from resend.com
 *   TO_EMAIL          - inbox that should receive leads, e.g. info@lendvue.com
 *   FROM_EMAIL        - a verified sending address on your Resend domain,
 *                        e.g. forms@lendvue.com (must be on a domain you
 *                        verified in Resend)
 *
 * Optional:
 *   ALLOWED_ORIGIN     - comma-separated list of site origins allowed to post
 *                        (set in wrangler.jsonc)
 */

const MAX_FIELD_LENGTH = 2000;
const MAX_FIELDS = 60;

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function jsonResponse(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status: status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": origin,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Cache-Control": "no-store"
    }
  });
}

function allowedOrigins(env) {
  return (env.ALLOWED_ORIGIN || "https://www.lendvue.com")
    .split(",").map((o) => o.trim()).filter(Boolean);
}
function corsOrigin(request, env) {
  const list = allowedOrigins(env);
  const origin = request.headers.get("Origin") || "";
  return list.includes(origin) ? origin : list[0];
}

export async function onRequestOptions(context) {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": corsOrigin(context.request, context.env),
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    }
  });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const allowedOrigin = corsOrigin(request, env);

  // Basic origin check (defense in depth — not the only safeguard)
  const origin = request.headers.get("Origin") || "";
  const isLocal = /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin);
  if (origin && !allowedOrigins(env).includes(origin) && !isLocal) {
    return jsonResponse({ error: "Forbidden" }, 403, allowedOrigin);
  }

  let data;
  try {
    data = await request.json();
  } catch (err) {
    return jsonResponse({ error: "Invalid submission" }, 400, allowedOrigin);
  }

  // Honeypot — silently accept but never send (bots fill hidden fields)
  if (data.website) {
    return jsonResponse({ ok: true }, 200, allowedOrigin);
  }

  const keys = Object.keys(data);
  if (keys.length === 0 || keys.length > MAX_FIELDS) {
    return jsonResponse({ error: "Invalid submission" }, 400, allowedOrigin);
  }
  for (const key of keys) {
    if (String(data[key]).length > MAX_FIELD_LENGTH) {
      return jsonResponse({ error: "Field too long" }, 400, allowedOrigin);
    }
  }

  const formName = escapeHtml(data.formName || "Website Form");
  const pageUrl = escapeHtml(data.pageUrl || "");

  // Very light required-field check — real validation happens client-side too
  const email = (data.email || data.Email || "").trim();
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return jsonResponse({ error: "Invalid email address" }, 400, allowedOrigin);
  }

  const rows = keys
    .filter((k) => !["formName", "pageUrl", "website"].includes(k))
    .map((k) => {
      const label = escapeHtml(k.replace(/^input_/, "Field ").replace(/[_-]/g, " "));
      const value = escapeHtml(data[k] === "" ? "-" : data[k]);
      return `<tr><td style="padding:8px 12px;font-weight:600;color:#1F3A56;border-bottom:1px solid #eee;">${label}</td><td style="padding:8px 12px;border-bottom:1px solid #eee;">${value}</td></tr>`;
    })
    .join("");

  const html = `
    <div style="font-family:Arial,sans-serif;max-width:620px;margin:0 auto;">
      <h2 style="color:#1F3A56;">New submission: ${formName}</h2>
      <p style="color:#666;font-size:13px;">From: ${pageUrl}</p>
      <table style="width:100%;border-collapse:collapse;margin-top:16px;">${rows}</table>
    </div>
  `;

  if (!env.RESEND_API_KEY) {
    console.error("RESEND_API_KEY is not set");
    return jsonResponse({ error: "Form email is not configured yet" }, 503, allowedOrigin);
  }
  const toEmail = env.TO_EMAIL || "info@lendvue.com";
  const fromEmail = env.FROM_EMAIL || "forms@lendvue.com";

  try {
    const resendResponse = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        from: `Lendvue Website <${fromEmail}>`,
        to: [toEmail],
        reply_to: email || undefined,
        subject: `New ${formName} submission — Lendvue website`,
        html: html
      })
    });

    if (!resendResponse.ok) {
      const errText = await resendResponse.text();
      console.error("Resend error:", errText);
      return jsonResponse({ error: "Could not send email" }, 502, allowedOrigin);
    }
  } catch (err) {
    console.error("Send failure:", err);
    return jsonResponse({ error: "Could not send email" }, 502, allowedOrigin);
  }

  return jsonResponse({ ok: true }, 200, allowedOrigin);
}

// Reject any other method
export async function onRequestGet(context) {
  return jsonResponse({ error: "Method not allowed" }, 405, corsOrigin(context.request, context.env));
}
