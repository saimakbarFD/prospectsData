"""Build a demo page locally.
Usage: python3 build.py <config.json> <core.html> <out_dir>
config.json = {slug, title, description, favicon (optional URL or data URI), demo: {presets, settings, about}}
Writes <out_dir>/index.html and <out_dir>/values.json (the exact JSON to PUT as KV demo-<slug>), prints hashes."""
import hashlib, html, json, pathlib, sys, urllib.parse
M = ["/*__DEMO__*/", "__TITLE__", "__DESC__", "__FAVICON__"]
def vals(cfg):
    st = cfg["demo"]["settings"]
    icon = cfg.get("favicon") or (("data:image/svg+xml," + urllib.parse.quote(st["logoMark"], safe="")) if st.get("logoMark") else st.get("logoUrl", ""))
    return {M[0]: "window.DEMO = " + json.dumps(cfg["demo"], ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";",
            M[1]: html.escape(cfg["title"]), M[2]: html.escape(cfg["description"]), M[3]: icon}
def apply(core, v):
    for k in M:
        assert core.count(k) == 1, k
        core = v[k].join(core.split(k))
    return core
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
if __name__ == "__main__":
    cfg = json.loads(pathlib.Path(sys.argv[1]).read_text())
    core = pathlib.Path(sys.argv[2]).read_text()
    v = vals(cfg); page = apply(core, v)
    out = pathlib.Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page)
    vj = json.dumps(v, ensure_ascii=False); (out / "values.json").write_text(vj)
    print(json.dumps({"core_sha": sha(core), "page_sha": sha(page), "values_sha": sha(vj), "page_bytes": len(page.encode()), "values_bytes": len(vj.encode())}, indent=1))
