#!/usr/bin/env python3
"""Drop CSS rules whose selectors match nothing in a rendered page (Design 4 build step).

usage: python3 prune-css.py <raw template.html> <rendered fixture index.html> <out template.html>
The raw template's single big <style> block is parsed with a brace matcher, every selector
is tested in Chromium against the fixture page (state pseudo-classes stripped), and rules
that match nothing are removed as text, so all other CSS stays byte-for-byte.
"""
import json, re, subprocess, sys, os, tempfile

raw, fixture, out = sys.argv[1:4]
html = open(raw, encoding="utf-8").read()
start = html.index("<style>") + len("<style>")
end = html.index("</style>", start)
css = html[start:end]

def parse(s, i=0, depth=0):
    """returns list of nodes: ('rule', prelude, body) | ('at', prelude, children|body) ; stops at '}'"""
    nodes = []
    n = len(s)
    while i < n:
        # skip whitespace/comments
        while i < n and s[i] in " \t\r\n":
            i += 1
        if i >= n:
            break
        if s.startswith("/*", i):
            j = s.find("*/", i + 2); i = n if j < 0 else j + 2; continue
        if s[i] == "}":
            return nodes, i + 1
        # read prelude up to { or ;
        j = i; q = None
        while j < n:
            c = s[j]
            if q:
                if c == "\\": j += 2; continue
                if c == q: q = None
            elif c in "\"'": q = c
            elif c in "{;": break
            j += 1
        prelude = s[i:j].strip()
        if j >= n:
            break
        if s[j] == ";":  # @import / @charset etc.
            nodes.append(("stmt", prelude, None)); i = j + 1; continue
        if prelude.startswith("@") and re.match(r"@(media|supports|container|layer|document|-moz-document)\b", prelude):
            children, i = parse(s, j + 1, depth + 1)
            nodes.append(("at", prelude, children))
            continue
        # plain block: find matching close brace (body may contain nested braces for @keyframes/@font-face)
        k = j + 1; d = 1; q = None
        while k < n and d:
            c = s[k]
            if q:
                if c == "\\": k += 2; continue
                if c == q: q = None
            elif c in "\"'": q = c
            elif c == "{": d += 1
            elif c == "}": d -= 1
            k += 1
        nodes.append(("rule", prelude, s[j + 1:k - 1]))
        i = k
    return nodes, i

tree, _ = parse(css)

STATE = r"(?<!\\):(?:hover|focus-visible|focus-within|focus|active|visited|checked|disabled|enabled|placeholder-shown|invalid|valid|target|required|optional|read-only|read-write|indeterminate|autofill|-webkit-autofill|empty|link|any-link|default)\b"
PSEUDO_EL = r"::?(?:before|after|placeholder|selection|marker|first-letter|first-line|backdrop|file-selector-button|-webkit-[a-z-]+|-moz-[a-z-]+|-ms-[a-z-]+)(?:\([^)]*\))?"
KEEP_TOKENS = ("elementor-active", "ti-col-", "[open]", "elementor-message", "elementor-error", "ti-show", "ti-active", "highlighted", "e--ua-", "form-state", "is-open", "hv-")

def split_selectors(prelude):
    out, depth, cur, q = [], 0, "", None
    for c in prelude:
        if q:
            cur += c
            if c == q: q = None
            continue
        if c in "\"'": q = c
        elif c in "([": depth += 1
        elif c in ")]": depth -= 1
        if c == "," and depth == 0:
            out.append(cur.strip()); cur = ""
        else:
            cur += c
    if cur.strip(): out.append(cur.strip())
    return out

def test_form(sel):
    t = re.sub(PSEUDO_EL, "", sel)
    t = re.sub(STATE, "", t)
    t = re.sub(r":not\(\s*\)", "", t)
    t = t.strip() or "*"
    if t.endswith((">", "+", "~")): t = t[:-1].strip()
    return t

selectors = set()
def collect(nodes):
    for kind, pre, body in nodes:
        if kind == "rule" and not pre.startswith("@"):
            for s in split_selectors(pre): selectors.add(test_form(s))
        elif kind == "at":
            collect(body)
collect(tree)

with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
    json.dump(sorted(selectors), fh)
    sel_file = fh.name
js = r"""
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const sels = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome' }).catch(() => chromium.launch());
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto('file://' + process.argv[3], { waitUntil: 'load' }); await p.waitForTimeout(800);
  const res = await p.evaluate(sels => { const o = {}; for (const s of sels) { try { o[s] = !!document.querySelector(s); } catch (e) { o[s] = 'err'; } } return o; }, sels);
  fs.writeFileSync(process.argv[2] + '.out', JSON.stringify(res)); await b.close();
})();
"""
jsf = sel_file + ".js"; open(jsf, "w").write(js)
env = dict(os.environ); env["NODE_PATH"] = subprocess.check_output(["npm", "root", "-g"], text=True).strip()
subprocess.check_call(["node", jsf, sel_file, os.path.abspath(fixture)], env=env)
match = json.load(open(sel_file + ".out"))

def keep_sel(s):
    if any(k in s for k in KEEP_TOKENS): return True
    r = match.get(test_form(s))
    return r is True or r == "err"

stats = {"kept": 0, "dropped": 0}
def emit(nodes):
    out = []
    for kind, pre, body in nodes:
        if kind == "stmt":
            out.append(pre + ";")
        elif kind == "at":
            inner = emit(body)
            if inner: out.append(pre + "{" + inner + "}")
        elif pre.startswith("@"):
            if pre.startswith("@font-face") and "trustindex" in body.lower():
                continue
            out.append(pre + "{" + body + "}")
        else:
            sels = [s for s in split_selectors(pre) if keep_sel(s)]
            if sels:
                stats["kept"] += 1; out.append(",".join(sels) + "{" + body + "}")
            else:
                stats["dropped"] += 1
    return "".join(out)

pruned = emit(tree)
# drop @keyframes that nothing references
used_anims = set(re.findall(r"animation(?:-name)?\s*:\s*([A-Za-z0-9_-]+)", pruned)) | set(re.findall(r"animation\s*:[^;}]*?\b([A-Za-z][A-Za-z0-9_-]+)\b", pruned))
def drop_kf(m):
    return m.group(0) if m.group(2) in used_anims or m.group(2) in pruned.replace(m.group(0), "") else ""
pruned = re.sub(r"@(-webkit-)?keyframes\s+([A-Za-z0-9_-]+)\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", drop_kf, pruned)
html = html[:start] + "\n" + pruned + "\n" + html[end:]
open(out, "w", encoding="utf-8").write(html)
print(json.dumps(stats), "css bytes", len(css), "->", len(pruned), "file", len(html))
