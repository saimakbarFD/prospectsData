"""Builds _pipeline/core-roof.html (Design 2) from the 1330-style template CSS.
Usage: python3 make.py <orig.css> <out.html>"""
import re, sys

css = open(sys.argv[1]).read()
css = re.sub(r'url\("https://1330roof\.com[^"]*"\)', 'var(--hero-img)', css)
css = css.replace('.collage .ph', '.collage .pic').replace('.ph-a', '.pic-a').replace('.ph-b', '.pic-b').replace('.ph-c', '.pic-c')
for a in ['.12', '.30', '.35']:
    css = css.replace(f'rgba(35,110,58,{a})', f'color-mix(in srgb,var(--primary) {int(float(a)*100)}%,transparent)')
assert '1330roof' not in css and '.ph' not in css.replace('.phone', '')

extra = r"""
/* ===== Demo additions (Design 2) ===== */
html,main,.footer{overflow-x:clip}
.logo{display:flex;align-items:center;gap:12px;color:var(--white)}
.logo .mark{width:52px;height:52px;flex:none;display:block}
.logo .mark svg{width:100%;height:100%;display:block}
.logo .word{display:grid;line-height:1.1;min-width:0}
.logo .word b{font-size:21px;font-weight:700;letter-spacing:.3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.logo .word small{font-size:12px;letter-spacing:2px;text-transform:uppercase;opacity:.75;white-space:nowrap}
.hero h1 .hot{color:var(--primary-bright)}
.topbar .tb-note{opacity:.95}
.about-body{background:linear-gradient(180deg,#fff 0,color-mix(in srgb,var(--primary) 5%,#fff) 100%)}
.card-cta .card-img{display:flex;flex-direction:column;justify-content:center;align-items:flex-start;gap:12px;padding:30px;background:var(--primary);color:var(--white)}
.card-cta .card-img strong{font-size:26px;font-weight:600;line-height:1.2}
.card-cta .card-img span{font-size:22px;font-weight:600}
.card-cta .card-img svg{width:44px;height:44px}
.ba-sec{padding:100px 0;background:#fff}
.ba-head{text-align:center;max-width:760px;margin:0 auto 34px}
.ba-head h2{font-size:clamp(28px,2.8vw,40px);line-height:1.2;font-weight:600;color:#222;margin-bottom:14px}
.ba-head p{color:var(--muted);font-size:17px;line-height:1.6}
.ba-tabs{display:flex;justify-content:center;flex-wrap:wrap;gap:10px;margin-bottom:26px}
.ba-tabs button{font:inherit;font-size:15px;font-weight:600;padding:10px 22px;border-radius:999px;border:1px solid var(--line);background:#fff;color:#222;cursor:pointer}
.ba-tabs button[aria-selected=true]{background:var(--primary);border-color:var(--primary);color:var(--white)}
.ba{position:relative;margin:0 auto;max-width:900px;aspect-ratio:16/10;border-radius:20px;overflow:hidden;box-shadow:0 18px 40px rgba(0,0,0,.12);user-select:none;touch-action:pan-y;background:#ddd}
.ba img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;pointer-events:none}
.ba .after{clip-path:inset(0 0 0 var(--pos,50%))}
.ba .lab{position:absolute;top:16px;padding:6px 14px;border-radius:999px;font-size:13px;font-weight:600;letter-spacing:1px;text-transform:uppercase;background:rgba(0,0,0,.65);color:#fff;z-index:2}
.ba .lab.b{left:16px}.ba .lab.a{right:16px;background:var(--primary)}
.ba .bar{position:absolute;top:0;bottom:0;left:var(--pos,50%);width:3px;margin-left:-1.5px;background:#fff;z-index:3}
.ba .knob{position:absolute;top:50%;left:var(--pos,50%);width:52px;height:52px;margin:-26px 0 0 -26px;border-radius:50%;background:#fff;color:#222;display:grid;place-items:center;z-index:4;box-shadow:0 6px 18px rgba(0,0,0,.25)}
.ba input{position:absolute;inset:0;width:100%;height:100%;opacity:0;cursor:ew-resize;z-index:5;margin:0}
.ba-cap{text-align:center;color:var(--muted);font-size:14px;margin-top:14px}
.cta-house svg{width:170px;height:auto;color:var(--primary-bright);filter:drop-shadow(0 18px 20px rgba(0,0,0,.35));animation:float 5s ease-in-out infinite}
.credits{max-width:900px;margin:8px auto 0;font-size:12px;color:#bdbdbd;text-align:center}
.credits summary{cursor:pointer}
.credits a{color:#e6e6e6}
.toast{position:fixed;left:50%;bottom:26px;transform:translate(-50%,20px);background:#111;color:#fff;padding:12px 20px;border-radius:10px;font-size:14px;opacity:0;transition:all .3s;z-index:200;pointer-events:none;max-width:90vw;text-align:center}
.toast.show{opacity:1;transform:translate(-50%,0)}
@media (max-width:640px){.logo .mark{width:42px;height:42px}.logo .word b{font-size:17px}.logo .word small{font-size:10px}.ba-sec{padding:70px 0}.ba{aspect-ratio:4/5}}
@media (prefers-reduced-motion:reduce){.cta-house svg{animation:none}}
"""

body = r"""<div id="app"></div>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>/*__DEMO__*/</script>
<script>
const D = window.DEMO, S = D.settings, P = D.presets[S.niche] || Object.values(D.presets)[0], A = D.about || {};
const IMG = S.images || {};
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const brand = S.brandName || P.demoBrand || "";
const T = s => esc(String(s ?? "").replace(/\{(\w+)\}/g, (m, k) => ({city:S.city, state:S.state, brand, owner:S.owner || "our owner", phone:S.phone, years:S.yearsInBusiness || ""}[k] ?? m)));
const tel = "tel:" + String(S.phone || "").replace(/[^\d+]/g, "");
const cityState = [S.city, S.state].filter(Boolean).join(", ");
const ico = {
  phone:'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>',
  mail:'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
  pin:'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>',
  check:'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5 9-10"/></svg>',
  arrow:'<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>',
  chev:'<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
  up:'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 15 6-6 6 6"/></svg>',
  lr:'<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 6-6 6 6 6M15 6l6 6-6 6"/></svg>',
  house:'<svg viewBox="0 0 120 100" aria-hidden="true"><path d="M10 50 60 10l50 40" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/><path d="M24 44v46h72V44" fill="none" stroke="#fff" stroke-width="7" stroke-linejoin="round"/><rect x="50" y="62" width="20" height="28" rx="2" fill="currentColor"/><rect x="34" y="54" width="12" height="12" rx="1.5" fill="#fff"/><rect x="74" y="54" width="12" height="12" rx="1.5" fill="#fff"/></svg>'
};
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
  if (src) return `<a href="#top" class="logo" aria-label="${esc(brand)} home"><img src="${esc(src)}" alt="${esc(brand)}"${S.logoHeight ? ` style="height:${esc(S.logoHeight)}"` : ""}>${S.logoShowName ? word : ""}</a>`;
  if (S.logoMark) return `<a href="#top" class="logo" aria-label="${esc(brand)} home"><span class="mark" aria-hidden="true">${S.logoMark}</span>${word}</a>`;
  return `<a href="#top" class="logo" aria-label="${esc(brand)} home">${word}</a>`;
}
const svcs = (P.services || []).slice(0, 7);
const pairs = (P.baTabs || []).map((t, i) => ({t, b: IMG["before-" + i], a: IMG["after-" + i]})).filter(x => x.b && x.a);
let baTab = 0;
function baHTML(){
  if (!pairs.length) return "";
  const p = pairs[baTab];
  return `<div class="ba-tabs" role="tablist">${pairs.map((x, i) => `<button role="tab" data-ba="${i}" aria-selected="${i === baTab}">${esc(x.t)}</button>`).join("")}</div>
    <div class="ba" id="ba" style="--pos:50%${S.baAspect ? `;aspect-ratio:${esc(S.baAspect)};max-width:${esc(S.baMaxWidth || "440px")}` : ""}">
      <img src="${esc(p.b)}" alt="${esc(p.t)} before" loading="lazy"><img class="after" src="${esc(p.a)}" alt="${esc(p.t)} after" loading="lazy">
      <span class="lab b">Before</span><span class="lab a">After</span><span class="bar"></span><span class="knob">${ico.lr}</span>
      <input type="range" min="0" max="100" value="50" aria-label="Drag to compare before and after">
    </div><p class="ba-cap">${esc(p.t)}: before and after.</p>`;
}
const areasTxt = (S.areas || []).slice(1, 4).join(", ");
const year = new Date().getFullYear();
document.getElementById("app").innerHTML = `
<div class="topbar" id="top"><div class="container">
  <div class="topbar-social"><span class="tb-note">${T(P.announce)}</span></div>
  <div class="topbar-info"><span>${ico.pin}<span>Serving ${esc(S.city)} &amp; nearby</span></span>${S.email ? `<a class="tb-email" href="mailto:${esc(S.email)}">${esc(S.email)}</a>` : `<a href="${tel}">${esc(S.phone)}</a>`}</div>
</div></div>
<header class="header" id="header"><div class="container">
  ${logo()}
  <nav class="nav" aria-label="Main"><ul>
    <li><a href="#top" class="active">Home</a></li>
    <li class="has-dropdown"><a href="#services">Services ${ico.chev}</a><ul class="dropdown">${svcs.map(s => `<li><a href="#services">${esc(s.name)}</a></li>`).join("")}</ul></li>
    <li><a href="#about">About Us</a></li>
    ${pairs.length ? `<li><a href="#work">Our Work</a></li>` : ""}
    <li><a href="#contact">Contact Us</a></li>
  </ul></nav>
  <div class="header-cta">
    <div class="call-box"><small>Need Help? Call Us Today</small><a href="${tel}">${esc(S.phone)}</a></div>
    <a href="#contact" class="btn btn-primary">Free Estimate</a>
    <button class="menu-toggle" id="menuToggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobileMenu"><span></span><span></span><span></span></button>
  </div>
</div>
<div class="mobile-menu" id="mobileMenu"><ul>
  <li><a href="#top" class="active">Home</a></li>
  <li><button class="sub-toggle" aria-expanded="false">Services ${ico.chev}</button><ul class="sub">${svcs.map(s => `<li><a href="#services">${esc(s.name)}</a></li>`).join("")}</ul></li>
  <li><a href="#about">About Us</a></li>
  ${pairs.length ? `<li><a href="#work">Our Work</a></li>` : ""}
  <li><a href="#contact">Contact Us</a></li>
  <li style="border:0"><a href="${tel}" class="btn btn-primary">Call ${esc(S.phone)}</a></li>
</ul></div>
</header>
<main>
<section class="hero">
  <div class="hero-bg" style="background-image:url('${esc(IMG.hero || "")}')"></div>
  <div class="container"><div class="hero-content">
    <h1 class="reveal">${T((P.h1 || [])[0])} ${T((P.h1 || [])[1])} <span class="hot">${T((P.h1 || [])[2])}</span></h1>
    <p class="reveal d1">${T(P.sub)}</p>
    <div class="hero-btns reveal d2"><a href="#contact" class="btn btn-primary">Get A Free Estimate</a><a href="${tel}" class="btn btn-light">Call ${esc(S.phone)}</a></div>
  </div></div>
</section>
<section class="about" id="about">
  <div class="container about-intro">
    <div class="reveal from-left"><span class="eyebrow">The ${esc(S.logoWord || brand)} Difference</span><h2>${T(A.title)}</h2></div>
    <div class="intro-text reveal from-right d1"><p>${T(A.sub)}</p>${(A.points || []).map(x => `<p>${T(x)}</p>`).join("")}</div>
  </div>
  <div class="about-body"><div class="container about-grid">
    <div class="collage">
      <div class="pic pic-a reveal from-left"><img src="${esc(IMG.about || "")}" alt="${esc(brand)} at work" loading="lazy"></div>
      <div class="pic pic-b reveal d1"><img src="${esc(IMG["benefit-0"] || "")}" alt="${T((P.benefits || [])[0]?.t)}" loading="lazy"></div>
      <div class="pic pic-c reveal d2"><img src="${esc(IMG["benefit-1"] || "")}" alt="${T((P.benefits || [])[1]?.t)}" loading="lazy"></div>
      <div class="badge reveal zoom d3"><span class="num"><span class="counter" data-target="100">0</span>%</span><span class="lbl">Committed To You.</span></div>
    </div>
    <div class="about-content">
      <div class="svc-list">${(P.benefits || []).map((b, i) => `<div class="reveal from-right d${i + 1}"><h3>${T(b.t)}</h3><p>${T(b.d)}</p></div>`).join("")}</div>
      <a href="${tel}" class="call-line reveal">${ico.phone}<span><strong>${esc(S.phone)}</strong><small>Call For A Free Estimate</small></span></a>
    </div>
  </div></div>
</section>
<section class="services" id="services">
  <div class="services-top"><div class="wide services-head">
    <div class="reveal"><span class="eyebrow">Our Services</span><h2>${T(P.svcTitle)}</h2></div>
    <p class="reveal d1">${T(P.svcSub)} ${T(P.stepsSub)}</p>
  </div></div>
  <div class="wide"><div class="cards">
    ${svcs.map((s, i) => `<article class="card reveal d${i % 4}"><a class="card-img" href="#contact"><img src="${esc(IMG["service-" + s.slug] || "")}" alt="${esc(s.name)}" loading="lazy"></a><a class="card-title" href="#contact"><h3>${esc(s.name)}</h3>${ico.arrow}</a><p>${T(s.d)}</p></article>`).join("")}
    <article class="card card-cta reveal d3"><a class="card-img" href="${tel}">${ico.phone}<strong>Not sure what you need?</strong><span>${esc(S.phone)}</span></a><a class="card-title" href="#contact"><h3>Free Estimate</h3>${ico.arrow}</a><p>${T(P.ctaSub)}</p></article>
  </div></div>
</section>
${pairs.length ? `<section class="ba-sec" id="work"><div class="container">
  <div class="ba-head reveal"><span class="eyebrow">Before &amp; After</span><h2>${T(P.baTitle)}</h2><p>${T(P.baSub)}</p></div>
  <div id="baWrap">${baHTML()}</div>
</div></section>` : ""}
<section class="contact" id="contact"><div class="container contact-grid">
  <div class="contact-info reveal from-left">
    <span class="eyebrow">Get In Touch</span><h2>${T(P.ctaTitle)}</h2><p>${T(P.ctaSub)}</p>
    <ul class="c-list">
      <li><span class="c-ico">${ico.phone}</span><span><small>Call Us</small><a href="${tel}">${esc(S.phone)}</a></span></li>
      ${S.email ? `<li><span class="c-ico">${ico.mail}</span><span><small>Email Us</small><a href="mailto:${esc(S.email)}">${esc(S.email)}</a></span></li>` : ""}
      <li><span class="c-ico">${ico.pin}</span><span><small>Based In</small><span class="val">${esc(cityState)}</span></span></li>
    </ul>
    <div class="trust">${(P.trust || []).map(t => `<span>${ico.check}${T(t)}</span>`).join("")}</div>
  </div>
  <form class="contact-form reveal from-right d1" id="contactForm" novalidate>
    <h3>Request A Free Estimate</h3>
    <p class="sub">Fill out the form and we'll be in touch to set up a visit.</p>
    <div class="f-grid">
      <div class="field"><label for="cf-name">Full Name <b>*</b></label><input id="cf-name" name="name" type="text" autocomplete="name" required></div>
      <div class="field"><label for="cf-phone">Phone <b>*</b></label><input id="cf-phone" name="phone" type="tel" autocomplete="tel" required></div>
      <div class="field"><label for="cf-email">Email <b>*</b></label><input id="cf-email" name="email" type="email" autocomplete="email" required></div>
      <div class="field"><label for="cf-city">City or ZIP</label><input id="cf-city" name="city" type="text" autocomplete="address-level2"></div>
      <div class="field"><label for="cf-service">${T(P.formAsk || "Service Needed")} <b>*</b></label><select id="cf-service" name="service" required><option value="" disabled selected>Select a service</option>${svcs.map(s => `<option>${esc(s.name)}</option>`).join("")}<option>Not Sure Yet</option></select></div>
      <div class="field"><label for="cf-type">Property Type</label><select id="cf-type" name="property"><option value="" disabled selected>Select property type</option><option>Residential</option><option>Commercial</option></select></div>
      <div class="field full"><label for="cf-msg">Project Details</label><textarea id="cf-msg" name="message" placeholder="Tell us about your project."></textarea></div>
    </div>
    <div class="form-foot"><p>By submitting, you agree to be contacted about your request. We never share your information.</p><button type="submit" class="btn btn-primary">Request My Estimate</button></div>
    <div class="form-success" role="status" aria-live="polite">${ico.check}<span>Thanks! Your request was sent. We'll reach out shortly.</span></div>
  </form>
</div></section>
<section class="cta"><div class="container">
  <div class="cta-house reveal zoom">${ico.house}</div>
  <div class="cta-text reveal d1"><h2>Ready To Start Your Project?</h2><p>${(P.trust || []).map(t => T(t)).join(" · ")}. Call ${esc(S.phone)} or send a request and we'll take it from there.</p></div>
  <a href="#contact" class="btn btn-primary reveal d2">Free Estimate</a>
</div></section>
</main>
<footer class="footer"><div class="container">
  <div class="footer-grid">
    <div class="f-about reveal"><h4>Proudly Serving ${esc(S.city)}</h4><p>Based in ${esc(cityState)}${areasTxt ? ` and serving ${esc(areasTxt)} and nearby towns` : ""}. Not sure if we reach you? Call us and find out.</p></div>
    <div class="f-col reveal d1"><h4>Support</h4><ul class="f-links"><li><a href="#about">About Us</a></li><li><a href="#contact">Contact</a></li><li><a href="#" data-soon>Privacy Policy</a></li></ul></div>
    <div class="f-col reveal d2"><h4>Quick Contact</h4><ul class="f-contact">
      <li>${ico.pin}<span>${esc(cityState)}</span></li>
      <li>${ico.phone}<a href="${tel}">${esc(S.phone)}</a></li>
      ${S.email ? `<li>${ico.mail}<a href="mailto:${esc(S.email)}">${esc(S.email)}</a></li>` : ""}
    </ul></div>
  </div>
</div>
<div class="copyright">© ${year} ${esc(brand)}. All rights reserved.
  ${(S.credits || []).length ? `<details class="credits"><summary>Photo credits</summary>Photos from Unsplash by ${(S.credits || []).map(c => `<a href="https://unsplash.com/@${esc(c.u)}" target="_blank" rel="noopener">${esc(c.n)}</a>`).join(", ")}.</details>` : ""}
</div>
</footer>
<a href="#top" class="to-top" id="toTop" aria-label="Scroll to top">${ico.up}</a>`;

/* toast */
const toastEl = document.getElementById("toast");
function toast(msg){ toastEl.textContent = msg; toastEl.classList.add("show"); clearTimeout(toast.t); toast.t = setTimeout(() => toastEl.classList.remove("show"), 2600); }
document.addEventListener("click", e => { if (e.target.closest("[data-soon]")) { e.preventDefault(); toast("This page is part of the full site build."); } });

/* before/after */
function bindBA(){
  const ba = document.getElementById("ba"); if (!ba) return;
  const r = ba.querySelector("input");
  r.addEventListener("input", () => ba.style.setProperty("--pos", r.value + "%"));
}
document.addEventListener("click", e => {
  const b = e.target.closest("[data-ba]"); if (!b) return;
  baTab = +b.dataset.ba; document.getElementById("baWrap").innerHTML = baHTML(); bindBA();
  document.querySelector(`[data-ba="${baTab}"]`)?.focus();
});
bindBA();

/* Sticky header + scroll to top */
const header = document.getElementById("header");
const toTop = document.getElementById("toTop");
const onScroll = () => { const y = window.scrollY; header.classList.toggle("scrolled", y > 60); toTop.classList.toggle("show", y > 600); };
window.addEventListener("scroll", onScroll, { passive:true }); onScroll();
toTop.addEventListener("click", e => { e.preventDefault(); window.scrollTo({ top:0, behavior:"smooth" }); });

/* Mobile menu */
const toggle = document.getElementById("menuToggle");
const mobileMenu = document.getElementById("mobileMenu");
toggle.addEventListener("click", () => { const open = mobileMenu.classList.toggle("open"); toggle.classList.toggle("open", open); toggle.setAttribute("aria-expanded", open); });
mobileMenu.querySelectorAll(".sub-toggle").forEach(btn => btn.addEventListener("click", () => { const open = btn.nextElementSibling.classList.toggle("open"); btn.setAttribute("aria-expanded", open); }));
mobileMenu.querySelectorAll("a").forEach(a => a.addEventListener("click", () => { mobileMenu.classList.remove("open"); toggle.classList.remove("open"); toggle.setAttribute("aria-expanded", false); }));
window.addEventListener("resize", () => { if (window.innerWidth > 1024) { mobileMenu.classList.remove("open"); toggle.classList.remove("open"); } });

/* Contact form (front end only) */
const form = document.getElementById("contactForm");
form.addEventListener("submit", e => { e.preventDefault(); if (!form.checkValidity()) { form.reportValidity(); return; } form.querySelector(".form-success").classList.add("show"); form.reset(); });

/* Counter */
function runCounter(el){ const target = +el.dataset.target, dur = 1600, start = performance.now();
  const tick = now => { const p = Math.min((now - start) / dur, 1); el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(tick); };
  requestAnimationFrame(tick); }

/* Scroll reveal */
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const revealEls = document.querySelectorAll(".reveal");
if (reduced || !("IntersectionObserver" in window)) { revealEls.forEach(el => el.classList.add("in")); document.querySelectorAll(".counter").forEach(c => c.textContent = c.dataset.target); }
else {
  const io = new IntersectionObserver(entries => { entries.forEach(entry => { if (!entry.isIntersecting) return; entry.target.classList.add("in"); entry.target.querySelectorAll(".counter").forEach(runCounter); io.unobserve(entry.target); }); }, { threshold:0.15, rootMargin:"0px 0px -40px 0px" });
  revealEls.forEach(el => io.observe(el));
}
</script>"""

head = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<link rel="icon" href="__FAVICON__">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>"""
out = head + css + extra + "</style>\n</head>\n<body>\n" + body + "\n</body>\n</html>\n"
for m in ["/*__DEMO__*/", "__TITLE__", "__DESC__", "__FAVICON__"]:
    assert out.count(m) == 1, m
open(sys.argv[2], "w").write(out)
print(len(out))
