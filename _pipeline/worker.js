const SLUG = "__SLUG__";
let P = null, V = null, T = 0, C = {};
async function load(env) {
  if (P && Date.now() - T < 300000) return;
  const vs = await env.TPL.get("demo-" + SLUG, { cacheTtl: 60 });
  const ptr = JSON.parse(vs);
  let vals = ptr;
  if (ptr.src) { const r = await fetch(ptr.src, { cf: { cacheTtl: 300 } }); if (!r.ok) throw new Error("src " + r.status); vals = await r.json(); }
  P = ptr; V = vals; T = Date.now(); C = {};
}
async function render(env, design) {
  if (C[design]) return C[design];
  let core;
  if (design && design !== "lift") {
    const u = await env.TPL.get("core-url-" + design, { cacheTtl: 60 });
    const r = await fetch(u, { cf: { cacheTtl: 300 } }); if (!r.ok) throw new Error("core " + r.status); core = await r.text();
  } else {
    const key = await env.TPL.get("core-current", { cacheTtl: 60 });
    core = await env.TPL.get(key, { cacheTtl: 60 });
  }
  if (!core || !V) throw new Error("empty");
  let out = core; for (const [k, v] of Object.entries(V)) out = out.split(k).join(v);
  C[design] = out; return out;
}
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/robots.txt") return new Response("User-agent: *\nDisallow: /\n", { headers: { "content-type": "text/plain" } });
    const key = url.pathname.replace(/^\/+|\/+$/g, "");
    let page = null;
    try {
      await load(env);
      let design;
      if (key === "" || key === "index.html") design = P.design || "lift";
      else if (P.alts && Object.prototype.hasOwnProperty.call(P.alts, key)) design = P.alts[key];
      else return Response.redirect(url.origin + "/", 302);
      page = await render(env, design);
    } catch (e) {}
    if (!page) return new Response("This preview isn't available right now.", { status: 503 });
    return new Response(page, { headers: { "content-type": "text/html; charset=utf-8", "x-robots-tag": "noindex, nofollow", "cache-control": "public, max-age=120" } });
  }
};
