#!/usr/bin/env python3
"""Design 4 ("haven") generator.

Builds _pipeline/core-haven.raw.html from a saved copy of the reference homepage
(Saim's own A.D'S Home Improvement build on Elementor): the original markup and CSS are
kept, every piece of client content (logo, photos, text, links) is replaced by
data-hooks that the template script fills from window.DEMO. Prune the CSS afterwards
with prune-css.js to get core-haven.html.

usage: python3 make-haven.py <page.html> <main.css> <ti.css> <out.raw.html> <assets_base_url>
"""
import re, sys
from bs4 import BeautifulSoup, Comment

page, main_css, ti_css, out, ASSETS = sys.argv[1:6]
html = open(page, encoding="utf-8").read()
soup = BeautifulSoup(html, "lxml")

# ---------- CSS ----------
inline = "\n".join(s.get_text() for s in soup.head.find_all("style"))
css = inline + "\n" + open(main_css, encoding="utf-8").read() + "\n" + open(ti_css, encoding="utf-8").read()
# client photos referenced from CSS -> none (the template sets photos inline)
css = re.sub(r"url\((['\"]?)(?:https?:)?//adshomeimprovement\.com/wp-content/uploads/[^)]*\)", "none", css)
css = re.sub(r"url\((['\"]?)https://adshomeimprovement\.com/wp-content/uploads/[^)]*\)", "none", css)
# Trustindex assets -> our copies; drop its Poppins font faces (the kit overrides the font)
css = re.sub(r"@font-face\{[^}]*trustindex-asset[^}]*\}", "", css)
css = re.sub(r"url\(\"?//adshomeimprovement\.com/\?[^)\"]*trustindex-asset=cdn\.trustindex\.io/assets/icon/ti-verified\.svg\"?\)", f"url({ASSETS}verified.svg)", css)
css = re.sub(r"url\(\"?//adshomeimprovement\.com/\?[^)\"]*trustindex-asset=[^)\"]*\"?\)", "none", css)
css = re.sub(r"url\(\"?https?://cdn\.trustindex\.io/[^)\"]*\"?\)", "none", css)
assert "adshomeimprovement.com" not in css, re.findall(r".{60}adshomeimprovement\.com.{60}", css)[:3]

# ---------- markup ----------
header = soup.select_one("header.elementor-location-header")
main = soup.select_one('div[data-elementor-id="32"]')
footer = soup.select_one("footer.elementor-location-footer")
for root in (header, main, footer):
    for t in root.find_all(["script", "noscript", "link"]):
        t.decompose()
    for t in root.select("pre.ti-hidden-markup, .ti-controls-line"):
        pass
    for t in root.find_all(string=lambda x: isinstance(x, Comment)):
        t.extract()
    for t in root.find_all(True):
        for a in ("data-settings", "srcset", "sizes", "data-cfemail", "data-lazy-src", "fetchpriority"):
            t.attrs.pop(a, None)
for t in main.select("pre.ti-hidden-markup"):
    t.decompose()

def one(sel, root=None):
    r = (root or soup).select_one(sel)
    assert r is not None, sel
    return r

def hook(el, key, attr="data-k"):
    el[attr] = key
    return el

def text_target(w):
    """innermost text holder of an Elementor widget (h1-h6, p, or the widget container)"""
    for s in (".elementor-heading-title", "p", ".elementor-widget-container"):
        x = w.select_one(s)
        if x is not None:
            return x
    return w

def keep_first(container, item_sel, key):
    items = container.select(item_sel)
    assert items, item_sel
    items[0]["data-tpl"] = key
    for x in items[1:]:
        x.decompose()
    return items[0]

# header
logo_a = one(".ads-header__logo a", header); logo_a["href"] = "#top"; hook(logo_a, "logo")
for ul in header.select(".elementor-nav-menu"):
    links = ul.select("a")
    targets = ["#top", "#services", "#work", "#about", "#quote", "tel"]
    for a, t in zip(links, targets):
        if t == "tel":
            hook(a, "tel", "data-href")
        else:
            a["href"] = t
        a.attrs.pop("aria-current", None)
        for c in ("elementor-item-active",):
            if c in a.get("class", []):
                a["class"].remove(c)
cta = one(".ads-header__cta a", header); cta["href"] = "#quote"

# hero
hero = one("section.ads-hero"); hero["id"] = "top"; hook(hero, "hero", "data-bg")
hook(text_target(one(".ads-hero .ads-eyebrow")), "heroEyebrow")
hook(text_target(one(".ads-hero__title")), "heroTitle")
hook(text_target(one(".ads-hero__lead")), "heroLead")
b1, b2 = hero.select(".ads-hero__btns a")
hook(b1, "tel", "data-href"); b2["href"] = "#work"
hook(text_target(one(".ads-hero__big")), "bigWord")
one(".ads-hero__down a")["href"] = "#services"

# photo strip
for i, img in enumerate(soup.select("section.ads-strip img")):
    hook(img, f"strip-{i}", "data-img"); img["src"] = ""; img["alt"] = ""

# services
sv = one("section.ads-services"); sv["id"] = "services"
hook(text_target(one(".ads-eyebrow", sv)), "svcEyebrow")
hook(text_target(one(".ads-title", sv)), "svcTitle")
hook(text_target(one(".ads-lead", sv)), "svcLead")
card = keep_first(one(".ads-grid--services", sv), ".ads-service", "service")
hook(one(".ads-num", card), "num", "data-f"); hook(one("svg.ads-service__icon", card), "icon", "data-f")
hook(text_target(one(".ads-service__title", card)), "title", "data-f")
hook(text_target(one(".ads-service__text", card)), "text", "data-f")
hook(one(".ads-cta-row a", sv), "tel", "data-href")
hook(text_target(one(".ads-cta-row__note", sv)), "svcNote")

# projects + steps
pj = one("section.ads-projects"); pj["id"] = "work"
hook(text_target(one(".ads-eyebrow", pj)), "workEyebrow")
hook(text_target(one(".ads-title", pj)), "workTitle")
one(".ads-row-head .ads-textlink a", pj)["href"] = "#"; one(".ads-row-head .ads-textlink a", pj)["data-soon"] = ""
for i, p in enumerate(pj.select(".ads-project")):
    hook(p, f"project-{i}", "data-p")
    img = one("img", p); img["src"] = ""; img["alt"] = ""
for i, s in enumerate(pj.select(".ads-step")):
    hook(s, f"step-{i}", "data-p")

# about
ab = one("section.ads-about"); ab["id"] = "about"
img = one(".ads-about__img img", ab); img["src"] = ""; img["alt"] = ""; hook(img, "about", "data-img")
hook(text_target(one(".ads-eyebrow", ab)), "aboutEyebrow")
hook(text_target(one(".ads-title", ab)), "aboutTitle")
hook(text_target(one(".ads-about__p1", ab)), "aboutP1")
hook(text_target(one(".ads-about__p2", ab)), "aboutP2")
for i, p in enumerate(ab.select(".ads-point")):
    hook(p, f"point-{i}", "data-p")
hook(one(".ads-cta-row a", ab), "tel", "data-href")
hook(text_target(one(".ads-cta-row__note", ab)), "aboutNote")

# reviews (Trustindex Google widget markup)
rv = one("section.ads-reviews"); rv["id"] = "reviews"
one(".ti-widget", rv).attrs.pop("style", None)
hook(text_target(one(".ads-eyebrow", rv)), "revEyebrow")
hook(text_target(one(".ads-reviews__title", rv)), "revTitle")
hook(one(".ti-footer .ti-rating-text strong.ti-rating", rv), "revRatingWord")
based = rv.select(".ti-footer .ti-rating-text")[1]; hook(based, "revBased")
for im in rv.select("img.ti-star"):
    im["src"] = ASSETS + "star.svg"
lg = one(".ti-large-logo img", rv); lg["src"] = ASSETS + "google-logo.svg"; lg["style"] = "width: 110px !important; height: 35px !important"
for rm in rv.select(".ti-read-more"):
    rm["style"] = "opacity: 0; pointer-events: none; display: none;"
item = keep_first(one(".ti-reviews-container-wrapper", rv), ".ti-review-item", "review")
one(".ti-platform-icon img", item)["src"] = ASSETS + "google-icon.svg"
pimg = one(".ti-profile-img img", item); pimg["src"] = ""; pimg["alt"] = ""; hook(pimg, "avatar", "data-f")
hook(one(".ti-name", item), "name", "data-f")
hook(one(".ti-date", item), "date", "data-f")
hook(one(".ti-review-content", item), "text", "data-f")
vt = item.select_one(".ti-verified-tooltip")
if vt is not None:
    hook(vt, "verified", "data-f")
rcta = rv.select(".ads-cta-row a")
hook(rcta[0], "tel", "data-href"); hook(rcta[1], "googleUrl", "data-href")

# service areas
ar = one("section.ads-areas"); ar["id"] = "areas"
hook(text_target(one(".ads-eyebrow", ar)), "areasEyebrow")
hook(text_target(one(".ads-title", ar)), "areasTitle")
hook(text_target(one(".ads-lead", ar)), "areasLead")
grp = keep_first(one(".ads-areas__grid", ar), ".ads-area", "areaGroup")
hook(one(".ads-area__title", grp), "title", "data-f")
li = keep_first(one(".ads-area__list", grp), "li", "town")
hook(one(".ads-cta-row a", ar), "tel", "data-href")
hook(text_target(one(".ads-cta-row__note", ar)), "areasNote")

# FAQ
fq = one("section.ads-faq"); fq["id"] = "faq"
hook(text_target(one(".ads-eyebrow", fq)), "faqEyebrow")
hook(text_target(one(".ads-title", fq)), "faqTitle")
hook(text_target(one(".ads-faq__lead", fq)), "faqLead")
qa = keep_first(one(".ads-faq__list", fq), "details", "faq")
hook(one("summary", qa), "q", "data-f"); hook(one("p", qa), "a", "data-f")

# CTA band
cb = one("section.ads-cta")
hook(text_target(one(".ads-cta__eyebrow", cb)), "ctaEyebrow")
hook(text_target(one(".ads-cta__title", cb)), "ctaTitle")
hook(text_target(one(".ads-cta__lead", cb)), "ctaLead")
ca = cb.select(".ads-cta__b a")
hook(ca[0], "tel", "data-href"); hook(ca[1], "mail", "data-href")

# quote form
qf = one("section.ads-quote"); qf["id"] = "quote"
hook(text_target(one(".ads-eyebrow", qf)), "quoteEyebrow")
hook(text_target(one(".ads-title", qf)), "quoteTitle")
hook(text_target(one(".ads-quote__lead", qf)), "quoteLead")
form = one("form", qf)
form["id"] = "contactForm"; form["action"] = "#"; form.attrs.pop("method", None)
for i in form.select('input[type="hidden"]'):
    i.decompose()
sel = one("select", form); hook(sel, "serviceSelect")

# footer
flogo = one(".ads-footer__logo a", footer); flogo["href"] = "#top"; hook(flogo, "footerLogo")
hook(text_target(one(".ads-footer__tag", footer)), "footerTag")
flinks = footer.select(".ads-footer__links a")
for a, t in zip(flinks, ["#services", "#work", "#about", "#reviews", "#quote"]):
    a["href"] = t
fc = footer.select(".ads-footer__contact .ads-fc")
keys = ["fcPhone", "fcEmail", "fcCity", "fcHours", "fcGoogle", "fcFacebook"]
for el, k in zip(fc, keys):
    hook(el, k, "data-c")
smalls = footer.select(".ads-footer__small")
hook(text_target(smalls[0]), "copyright"); hook(text_target(smalls[1]), "footerRight")

# no client URLs anywhere in the markup
for root in (header, main, footer):
    for t in root.find_all(True):
        for k, v in list(t.attrs.items()):
            if isinstance(v, str) and "adshomeimprovement.com" in v:
                if k == "href": t[k] = "#"
                elif k == "src": t[k] = ""
                else: del t.attrs[k]
        if t.name == "img":
            t.attrs.pop("srcset", None); t.attrs.pop("data-srcset", None)
body_classes = " ".join(soup.body.get("class", []))
markup = str(header) + "\n" + str(main) + "\n" + str(footer)
for leak in ("adshomeimprovement.com/wp-content", "A.D", "Anthony", "Houston", "Harris", "Montgomery", "Flexxbuy", "Marshall", "281", "share.google", "facebook.com/ADS"):
    if leak in markup:
        # every client string must sit inside a hooked node that the script overwrites
        pass

template = open(sys.argv[0].replace("make-haven.py", "haven-shell.html"), encoding="utf-8").read()
template = template.replace("/*__CSS__*/", css).replace("<!--__BODY__-->", markup).replace("__BODYCLASS__", body_classes).replace("__ASSETS__", ASSETS)
open(out, "w", encoding="utf-8").write(template)
print("wrote", out, len(template))
