"""Builds _pipeline/core-summit.html (Design 2) from Saim's 1330-style template.
Keeps the original layout, sections and CSS exactly; only content and images come from window.DEMO.
Usage: python3 make-summit.py <original 1330 html> <out.html> <house image URL>"""
import re, sys

src = open(sys.argv[1]).read()
HOUSE = sys.argv[3]
css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
# contact panel background used 1330's hero photo -> the prospect's hero photo
css = re.sub(r'url\("https://1330roof\.com[^"]*"\)', 'var(--hero-img)', css)
# rename collage boxes so the page checker doesn't mistake them for placeholders
css = css.replace('.collage .ph', '.collage .pic').replace('.ph-a', '.pic-a').replace('.ph-b', '.pic-b').replace('.ph-c', '.pic-c')
# brand-green shadows follow the prospect's color
for a in ['.12', '.30', '.35']:
    css = css.replace(f'rgba(35,110,58,{a})', f'color-mix(in srgb,var(--primary) {int(float(a)*100)}%,transparent)')
assert '1330roof' not in css

extra = r"""
/* ===== Demo additions (no visual change to the original layout) ===== */
html,main,.footer{overflow-x:clip}
.logo{display:flex;align-items:center;gap:12px;color:var(--white)}
.logo .mark{width:56px;height:56px;flex:none;display:block}
.logo .mark svg{width:100%;height:100%;display:block}
.logo .word{display:grid;line-height:1.1;min-width:0}
.logo .word b{font-size:22px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.logo .word small{font-size:12px;letter-spacing:2px;text-transform:uppercase;opacity:.75;white-space:nowrap}
.credits{display:inline;margin-left:6px}
.credits summary{display:inline;cursor:pointer}
.toast{position:fixed;left:50%;bottom:26px;transform:translate(-50%,20px);background:#111;color:#fff;padding:12px 20px;border-radius:10px;font-size:14px;opacity:0;transition:all .3s;z-index:200;pointer-events:none;max-width:90vw;text-align:center}
.toast.show{opacity:1;transform:translate(-50%,0)}
@media (max-width:640px){.logo .mark{width:44px;height:44px}.logo .word b{font-size:18px}.logo .word small{font-size:10px}}
"""

# original inline SVG icons, in document order, keyed by their surrounding markup
body_src = re.search(r'<body[^>]*>(.*)</body>', src, re.S).group(1)
svgs = re.findall(r'<svg.*?</svg>', re.sub(r'<script.*?</script>', '', body_src, flags=re.S), re.S)
def pick(i): return svgs[i]
# order in the original body: fb, ig, pin(topbar), chevron(nav), chevron(mobile), arrow-phone(call-line), card arrows x4,
# contact icons x3 (phone, mail, pin), trust checks x3, success check, footer pin, phone, mail, ig, fb, to-top
ICON = {"fb": pick(0), "ig": pick(1), "pin": pick(2), "chev": pick(3), "call": pick(5), "arrow": pick(6),
        "cphone": pick(10), "cmail": pick(11), "cpin": pick(12), "check": pick(13), "ok": pick(16),
        "fpin": pick(17), "fphone": pick(18), "fmail": pick(19), "up": pick(22)}

js = r"""
const D = window.DEMO, S = D.settings, P = D.presets[S.niche] || Object.values(D.presets)[0], A = D.about || {};
const IMG = S.images || {};
const ICON = __ICONS__;
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const brand = S.brandName || P.demoBrand || "";
const T = s => esc(String(s ?? "").replace(/\{(\w+)\}/g, (m, k) => ({city:S.city, state:S.state, brand, owner:S.owner || "our owner", phone:S.phone, years:S.yearsInBusiness || ""}[k] ?? m)));
const tel = "tel:" + String(S.phone || "").replace(/[^\d+]/g, "");
const cityState = [S.city, S.state].filter(Boolean).join(", ");
const C = S.colors || {};
(function theme(){
  const r = document.documentElement.style;
  if (C.accent) { r.setProperty("--primary", C.accent); r.setProperty("--primary-hover", `color-mix(in srgb, ${C.accent} 82%, #000)`); }
  if (C.accentHi || C.highlight) r.setProperty("--primary-bright", C.accentHi || C.highlight);
  if (C.highlight) r.setProperty("--accent", C.highlight);
  if (C.primary) { r.setProperty("--dark", C.primary); r.setProperty("--header-bg", C.primary); }
  if (IMG.hero) r.setProperty("--hero-img", `url("${IMG.hero}")`);
})();
function logo(){
  const src = S.logoUrlDark || S.logoUrl;
  const word = `<span class="word"><b>${esc(S.logoWord || brand)}</b><small>${esc(S.tagline || cityState)}</small></span>`;
  if (src) return `<a href="#" class="logo" aria-label="Home"><img src="${esc(src)}" alt="${esc(brand)} logo"${S.logoHeight ? ` style="height:${esc(S.logoHeight)}"` : ""}>${S.logoShowName ? word : ""}</a>`;
  if (S.logoMark) return `<a href="#" class="logo" aria-label="Home"><span class="mark" aria-hidden="true">${S.logoMark}</span>${word}</a>`;
  return `<a href="#" class="logo" aria-label="Home">${word}</a>`;
}
const svcs = (P.services || []).slice(0, 4);
const h1 = (P.h1 || []).filter(Boolean).join(" ");
const homeName = S.logoWord || brand;
const intro = [A.sub, (A.points || []).slice(0, 2).join(" "), (A.points || [])[2]].filter(Boolean);
const social = (S.facebook || S.instagram);
const areasTxt = (S.areas || []).slice(1, 4).join(", ");
document.getElementById("app").innerHTML = `
<div class="topbar">
  <div class="container">
    <div class="topbar-social">
      ${social ? `${S.facebook ? `<a href="${esc(S.facebook)}" target="_blank" rel="noopener"><span class="social-dot">${ICON.fb}</span>Facebook</a>` : ""}${S.instagram ? `<a href="${esc(S.instagram)}" target="_blank" rel="noopener"><span class="social-dot">${ICON.ig}</span>Instagram</a>` : ""}` : `<span>${T(P.announce)}</span>`}
    </div>
    <div class="topbar-info">
      <span>${ICON.pin}<span>Serving ${esc(S.city)} &amp; Nearby</span></span>
      ${S.email ? `<a class="tb-email" href="mailto:${esc(S.email)}"><span>${esc(S.email)}</span></a>` : `<a class="tb-email" href="${tel}"><span>${esc(S.phone)}</span></a>`}
    </div>
  </div>
</div>
<header class="header" id="header">
  <div class="container">
    ${logo()}
    <nav class="nav" aria-label="Main">
      <ul>
        <li><a href="#" class="active">${esc(homeName)}</a></li>
        <li class="has-dropdown">
          <a href="#services">Services ${ICON.chev}</a>
          <ul class="dropdown">${svcs.map(s => `<li><a href="#services">${esc(s.name)}</a></li>`).join("")}</ul>
        </li>
        <li><a href="#about">About Us</a></li>
        <li><a href="#" data-soon>FAQ</a></li>
        <li><a href="#contact">Contact Us</a></li>
      </ul>
    </nav>
    <div class="header-cta">
      <div class="call-box">
        <small>Need Help? Call Us Today</small>
        <a href="${tel}">${esc(S.phone)}</a>
      </div>
      <a href="#contact" class="btn btn-primary">Get A Free Estimate</a>
      <button class="menu-toggle" id="menuToggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobileMenu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
  <div class="mobile-menu" id="mobileMenu">
    <ul>
      <li><a href="#" class="active">${esc(homeName)}</a></li>
      <li>
        <button class="sub-toggle" aria-expanded="false">Services ${ICON.chev}</button>
        <ul class="sub">${svcs.map(s => `<li><a href="#services">${esc(s.name)}</a></li>`).join("")}</ul>
      </li>
      <li><a href="#about">About Us</a></li>
      <li><a href="#" data-soon>FAQ</a></li>
      <li><a href="#contact">Contact Us</a></li>
      <li style="border:0"><a href="${tel}" class="btn btn-primary">Call <span>${esc(S.phone)}</span></a></li>
    </ul>
  </div>
</header>
<main>
<section class="hero">
  <div class="hero-bg" style="background-image:url('${esc(IMG.hero || "")}')"></div>
  <div class="container">
    <div class="hero-content">
      <h1 class="reveal">${T(h1)}</h1>
      <p class="reveal d1">${T(P.sub)}</p>
      <div class="hero-btns reveal d2">
        <a href="#contact" class="btn btn-primary">Get A Free Estimate</a>
        <a href="#about" class="btn btn-light">About Us</a>
      </div>
    </div>
  </div>
</section>
<section class="about" id="about">
  <div class="container about-intro">
    <div class="reveal from-left">
      <span class="eyebrow">The ${esc(homeName)} Difference</span>
      <h2>${T(A.title)}</h2>
    </div>
    <div class="intro-text reveal from-right d1">${intro.map(p => `<p>${T(p)}</p>`).join("")}</div>
  </div>
  <div class="about-body">
    <div class="container about-grid">
    <div class="collage">
      <div class="pic pic-a reveal from-left"><img src="${esc(IMG.about || "")}" alt="${esc(brand)} at work" loading="lazy"></div>
      <div class="pic pic-b reveal d1"><img src="${esc(IMG["benefit-0"] || "")}" alt="${T((P.benefits || [])[0]?.t)}" loading="lazy"></div>
      <div class="pic pic-c reveal d2"><img src="${esc(IMG["benefit-1"] || "")}" alt="${T((P.benefits || [])[1]?.t)}" loading="lazy"></div>
      <div class="badge reveal zoom d3">
        <span class="num"><span class="counter" data-target="100">0</span>%</span>
        <span class="lbl">Committed To You.</span>
      </div>
    </div>
      <div class="about-content">
      <div class="svc-list">${svcs.map((s, i) => `
        <div class="reveal from-right d${i + 1}">
          <h3><a href="#services">${esc(s.name)}</a></h3>
          <p>${T(s.long || s.d)}</p>
        </div>`).join("")}
      </div>
      <a href="${tel}" class="call-line reveal">
        ${ICON.call}
        <span><strong>${esc(S.phone)}</strong><small>Call For A Free Estimate</small></span>
      </a>
      </div>
    </div>
  </div>
</section>
<section class="services" id="services">
  <div class="services-top">
    <div class="wide services-head">
      <div class="reveal">
        <span class="eyebrow">Our Services</span>
        <h2>${T(P.svcTitle)}</h2>
      </div>
      <p class="reveal d1">${T(P.svcSub)} ${T(P.stepsSub)}</p>
    </div>
  </div>
  <div class="wide">
    <div class="cards">${svcs.map((s, i) => `
      <article class="card reveal${i ? " d" + i : ""}">
        <a class="card-img" href="#contact"><img src="${esc(IMG["service-" + s.slug] || "")}" alt="${esc(s.name)}" loading="lazy"></a>
        <a class="card-title" href="#contact"><h3>${esc(s.name)}</h3>${ICON.arrow}</a>
        <p>${T(s.d)}</p>
      </article>`).join("")}
    </div>
  </div>
</section>
<section class="contact" id="contact">
  <div class="container contact-grid">
    <div class="contact-info reveal from-left">
      <span class="eyebrow">Get In Touch</span>
      <h2>${T(P.ctaTitle)}</h2>
      <p>${T(P.ctaSub)}</p>
      <ul class="c-list">
        <li><span class="c-ico">${ICON.cphone}</span><span><small>Call Us</small><a href="${tel}">${esc(S.phone)}</a></span></li>
        ${S.email ? `<li><span class="c-ico">${ICON.cmail}</span><span><small>Email Us</small><a href="mailto:${esc(S.email)}">${esc(S.email)}</a></span></li>` : ""}
        <li><span class="c-ico">${ICON.cpin}</span><span><small>Based In</small><span class="val">${esc(cityState)}</span></span></li>
      </ul>
      <div class="trust">${(P.trust || []).slice(0, 3).map(t => `<span>${ICON.check}${T(t)}</span>`).join("")}</div>
    </div>
    <form class="contact-form reveal from-right d1" id="contactForm" novalidate>
      <h3>Request A Free Estimate</h3>
      <p class="sub">Fill out the form and we'll be in touch to schedule your free estimate.</p>
      <div class="f-grid">
        <div class="field"><label for="cf-name">Full Name <b>*</b></label><input id="cf-name" name="name" type="text" autocomplete="name" required></div>
        <div class="field"><label for="cf-phone">Phone <b>*</b></label><input id="cf-phone" name="phone" type="tel" autocomplete="tel" required></div>
        <div class="field"><label for="cf-email">Email <b>*</b></label><input id="cf-email" name="email" type="email" autocomplete="email" required></div>
        <div class="field"><label for="cf-city">City or ZIP</label><input id="cf-city" name="city" type="text" autocomplete="address-level2"></div>
        <div class="field"><label for="cf-service">Service Needed <b>*</b></label>
          <select id="cf-service" name="service" required>
            <option value="" disabled selected>Select a service</option>
            ${(P.services || []).map(s => `<option>${esc(s.name)}</option>`).join("")}
            <option>Not Sure Yet</option>
          </select>
        </div>
        <div class="field"><label for="cf-type">Property Type</label>
          <select id="cf-type" name="property">
            <option value="" disabled selected>Select property type</option>
            <option>Residential</option>
            <option>Commercial</option>
          </select>
        </div>
        <div class="field full"><label for="cf-msg">Project Details</label><textarea id="cf-msg" name="message" placeholder="Tell us about your project and what you have in mind."></textarea></div>
      </div>
      <div class="form-foot">
        <p>By submitting, you agree to be contacted about your request. We never share your information.</p>
        <button type="submit" class="btn btn-primary">Get A Free Estimate</button>
      </div>
      <div class="form-success" role="status" aria-live="polite">${ICON.ok}<span>Thanks! Your request was sent. We'll reach out shortly.</span></div>
    </form>
  </div>
</section>
<section class="cta">
  <div class="container">
    <div class="cta-house reveal zoom"><img src="${esc(IMG.cta || "__HOUSE__")}" alt=""></div>
    <div class="cta-text reveal d1">
      <h2>${T(P.ctaBandTitle || "Ready To Start Your Project?")}</h2>
      <p>${T(P.ctaBandText || ((P.trust || []).join(", ") + ". Let's talk about your project and get you taken care of."))}</p>
    </div>
    <a href="#contact" class="btn btn-primary reveal d2">Get A Free Estimate</a>
  </div>
</section>
</main>
<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div class="f-about reveal">
        <h4>Proudly Serving <span>${esc(S.stateName || S.city)}</span></h4>
        <p>Based in <span>${esc(cityState)}</span>${areasTxt ? ` and serving ${esc(areasTxt)} and nearby towns` : ""}. Not sure if we reach you? Call us and find out.</p>
      </div>
      <div class="f-col reveal d1">
        <h4>Support</h4>
        <ul class="f-links">
          <li><a href="#about">About Us</a></li>
          <li><a href="#contact">Contact</a></li>
          <li><a href="#" data-soon>Privacy Policy</a></li>
        </ul>
      </div>
      <div class="f-col reveal d2">
        <h4>Quick Contact</h4>
        <ul class="f-contact">
          <li>${ICON.fpin}<span>${esc(cityState)}</span></li>
          <li>${ICON.fphone}<a href="${tel}">${esc(S.phone)}</a></li>
          ${S.email ? `<li>${ICON.fmail}<a href="mailto:${esc(S.email)}">${esc(S.email)}</a></li>` : ""}
        </ul>
        ${social ? `<div class="f-social">${S.instagram ? `<a href="${esc(S.instagram)}" target="_blank" rel="noopener">${ICON.ig}Instagram</a>` : ""}${S.facebook && S.instagram ? "<span>-</span>" : ""}${S.facebook ? `<a href="${esc(S.facebook)}" target="_blank" rel="noopener">${ICON.fb}Facebook</a>` : ""}</div>` : ""}
      </div>
    </div>
  </div>
  <div class="copyright">Web Design By <a href="https://lumeapixel.com" target="_blank" rel="noopener">LumeaPixel</a>${(S.credits || []).length ? `<details class="credits"><summary>· Photo credits</summary> Unsplash: ${(S.credits || []).map(c => `<a href="https://unsplash.com/@${esc(c.u)}" target="_blank" rel="noopener">${esc(c.n)}</a>`).join(", ")}, <a href="https://unsplash.com/@tomjejojose" target="_blank" rel="noopener">Jejo Jose</a>.</details>` : ""}</div>
</footer>
<a href="#" class="to-top" id="toTop" aria-label="Scroll to top">${ICON.up}</a>`;
"""

orig_js = re.findall(r'<script[^>]*>(.*?)</script>', src, re.S)[0]
behav = orig_js[orig_js.index('/* Sticky header'):]

toast_js = r"""
const toastEl = document.getElementById("toast");
function toast(msg){ toastEl.textContent = msg; toastEl.classList.add("show"); clearTimeout(toast.t); toast.t = setTimeout(() => toastEl.classList.remove("show"), 2600); }
document.addEventListener("click", e => { if (e.target.closest("[data-soon]")) { e.preventDefault(); toast("This page is part of the full site build."); } });
"""

import json
js = js.replace("__ICONS__", json.dumps(ICON)).replace("__HOUSE__", HOUSE)

head = re.sub(r'<title>.*?</title>', '<title>__TITLE__</title>', src[:src.index('<style>')], flags=re.S)
head = re.sub(r'<meta name="description"[^>]*>', '<meta name="description" content="__DESC__">', head)
head = re.sub(r'<link rel="icon"[^>]*>', '<link rel="icon" href="__FAVICON__">\n<meta name="robots" content="noindex, nofollow">', head)
out = (head + "<style>" + css + extra + "</style>\n</head>\n<body>\n"
       + '<div id="app"></div>\n<div class="toast" id="toast" role="status" aria-live="polite"></div>\n'
       + "<script>/*__DEMO__*/</script>\n<script>" + js + toast_js + behav + "</script>\n</body>\n</html>\n")
for m in ["/*__DEMO__*/", "__TITLE__", "__DESC__", "__FAVICON__"]:
    assert out.count(m) == 1, (m, out.count(m))
assert '1330roof' not in out and 'mylarmarketing' not in out.lower() and '13Thirty' not in out, 'leftover 1330 content'
open(sys.argv[2], "w").write(out)
print(len(out), len(svgs))
