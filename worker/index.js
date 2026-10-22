/**
 * Lendvue site Worker.
 * Static pages/assets in ./public are served by Cloudflare directly (see wrangler.jsonc
 * "assets"); only /api/* requests reach this code.
 */
import { onRequestPost, onRequestOptions, onRequestGet } from "./submit-form.js";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/api/submit-form") {
      const context = { request, env, ctx };
      if (request.method === "POST") return onRequestPost(context);
      if (request.method === "OPTIONS") return onRequestOptions(context);
      return onRequestGet(context);
    }
    if (url.pathname.startsWith("/api/")) {
      return new Response("Not found", { status: 404 });
    }
    return env.ASSETS.fetch(request);
  }
};
