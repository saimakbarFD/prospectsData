const SLUG = "__SLUG__";
let C = null, T = 0;
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/robots.txt") return new Response("User-agent: *\nDisallow: /\n", { headers: { "content-type": "text/plain" } });
    if (url.pathname !== "/" && url.pathname !== "/index.html") return Response.redirect(url.origin + "/", 302);
    if (!C || Date.now() - T > 300000) {
      try {
        const key = await env.TPL.get("core-current", { cacheTtl: 60 });
        const [core, vs] = await Promise.all([env.TPL.get(key, { cacheTtl: 60 }), env.TPL.get("demo-" + SLUG, { cacheTtl: 60 })]);
        if (core && vs) {
          let vals = JSON.parse(vs);
          if (vals.src) { const r = await fetch(vals.src, { cf: { cacheTtl: 300 } }); if (!r.ok) throw new Error("src " + r.status); vals = await r.json(); }
          let out = core; for (const [k, v] of Object.entries(vals)) out = out.split(k).join(v); C = out; T = Date.now();
        }
      } catch (e) {}
      if (!C) return new Response("This preview isn't available right now.", { status: 503 });
    }
    return new Response(C, { headers: { "content-type": "text/html; charset=utf-8", "x-robots-tag": "noindex, nofollow", "cache-control": "public, max-age=120" } });
  }
};
