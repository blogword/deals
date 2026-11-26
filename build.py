#!/usr/bin/env python3
"""Generate static, crawlable deal pages + category hubs + sitemap for blackfriday.onlinedecoded.com."""
import json, os, re, html, shutil
from collections import OrderedDict

BASE = "https://blackfriday.onlinedecoded.com"
TODAY = "2026-11-26"
OUT = "/home/claude/bf/out"
OG = f"{BASE}/og-image.png"
deals = [dict(zip(["slug","name","cat","catName","discount","price","base","aff","desc"], d))
         for d in json.load(open("/home/claude/bf/deals.json"))]

CATS = OrderedDict([
  ("hosting",      ("Web Hosting", "Black Friday Web Hosting Deals 2026",
     "Discounts on shared, managed WordPress, cloud and VPS hosting plus domain registrars. Hosting deals usually apply to the first billing term only, so compare the renewal price before you lock in a 3-year plan.")),
  ("plugins",      ("WordPress & Plugins", "Black Friday WordPress Theme & Plugin Deals 2026",
     "Deals on WordPress themes, page builders, form plugins, caching, SEO and affiliate plugins. Most are annual licences; check how many sites the licence covers and whether the discount applies on renewal.")),
  ("marketing",    ("Marketing & Courses", "Black Friday Email Marketing, Funnel & Course Platform Deals 2026",
     "Discounts on email marketing, funnel builders, course platforms, CRMs and chat tools. Pricing is usually tied to subscriber or contact counts, so pick the tier that matches your list size.")),
  ("ai-tools",     ("AI Writing", "Black Friday AI Writing Tool Deals 2026",
     "Deals on AI writers, paraphrasers and grammar checkers. Word or credit limits differ a lot between plans, so compare the monthly output you actually need, not just the headline discount.")),
  ("seo-tools",    ("SEO Tools", "Black Friday SEO Tool Deals 2026",
     "Discounts on keyword research, rank tracking, site audit and backlink tools. Many SEO suites only discount annual billing, and project or keyword-tracking limits vary by plan.")),
  ("design",       ("Design & Builders", "Black Friday Website Builder & Design Tool Deals 2026",
     "Deals on website builders, landing page tools, template marketplaces, and photo and video editors.")),
  ("vpn-security", ("VPN & Security", "Black Friday VPN Deals 2026",
     "Discounts on VPN services. The biggest VPN discounts are almost always on 2-year plans billed upfront, so check the total charged today and the renewal rate.")),
  ("utilities",    ("Utilities & Productivity", "Black Friday Software & Utility Deals 2026",
     "Deals on data recovery, cloud storage, PDF editors, video software, mind mapping and other productivity tools. Lifetime deals are paid once; subscriptions renew at full price unless stated otherwise.")),
])

def e(s): return html.escape(s, quote=True)
def url_cat(c): return f"/{c}/"
def url_deal(d): return f"/{d['cat']}/{d['slug']}/"

def money(s):
    m = re.match(r"^\$([\d,]+(?:\.\d+)?)/(mo|yr)$", s.strip())
    return (float(m.group(1).replace(",","")), m.group(2)) if m else None

def savings(d):
    a, b = money(d["price"]), money(d["base"])
    if a and b and a[1] == b[1] and b[0] > a[0]:
        diff = b[0]-a[0]
        if a[1] == "mo":
            return f"At {d['price']} instead of {d['base']}, you save about ${diff:,.2f} a month (around ${diff*12:,.0f} over 12 months)."
        return f"At {d['price']} instead of {d['base']}, you save about ${diff:,.2f} on a one-year licence."
    return ""

CSS = """
:root{--bg:#090a0f;--card:#11131a;--border:#1e2230;--primary:#6366f1;--primary-hover:#4f46e5;--text:#f8fafc;--muted:#94a3b8;--badge:#e11d48;--mono:'JetBrains Mono',monospace}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:'Plus Jakarta Sans',system-ui,sans-serif;line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:#a5b4fc}
.wrap{max-width:1040px;margin:0 auto;padding:0 22px}
.top-banner{background:linear-gradient(90deg,#4f46e5,#e11d48);color:#fff;font-size:13px;font-weight:600;text-align:center;padding:9px 16px}
.top-nav{background:rgba(17,19,26,.95);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:10}
.top-nav-inner{display:flex;align-items:center;gap:14px;padding:10px 0;overflow-x:auto}
.brand{font-weight:800;color:#fff;text-decoration:none;white-space:nowrap}.brand span{color:var(--primary)}
.nav a{color:var(--muted);font-size:12.5px;font-weight:600;text-decoration:none;padding:6px 9px;border-radius:6px;white-space:nowrap}
.nav a:hover,.nav a.active{color:#fff;background:var(--primary)}
.nav{display:flex;gap:4px;list-style:none}
.crumbs{font-size:13px;color:var(--muted);margin:24px 0 14px}.crumbs a{color:var(--muted)}
.card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:32px;margin-bottom:28px}
h1{font-size:clamp(26px,4vw,38px);font-weight:800;line-height:1.2;margin:10px 0 12px}
h2{font-size:19px;color:#a5b4fc;margin:26px 0 10px;border-left:4px solid var(--primary);padding-left:10px}
p{color:#cbd5e1;margin-bottom:12px}
.tag{font-family:var(--mono);font-size:12px;color:#818cf8;text-transform:uppercase;letter-spacing:.05em}
.badge{background:var(--badge);color:#fff;font-family:var(--mono);font-size:12px;font-weight:700;padding:4px 10px;border-radius:6px;margin-left:10px}
.btn{display:inline-block;background:var(--primary);color:#fff;font-weight:700;padding:13px 26px;border-radius:10px;text-decoration:none;margin:8px 0}
.btn:hover{background:var(--primary-hover)}
table{width:100%;border-collapse:collapse;margin:10px 0}
th,td{border:1px solid var(--border);padding:11px 14px;text-align:left;font-size:14.5px}
th{background:#0c0e14;color:#a5b4fc;width:38%}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:18px}
.deal{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px;display:flex;flex-direction:column}
.deal h3{font-size:18px;margin:8px 0 6px}.deal h3 a{color:#fff;text-decoration:none}
.deal p{font-size:14px;color:var(--muted);flex-grow:1}
.deal .row{display:flex;gap:8px;margin-top:10px}.deal .row a{font-size:13px;font-weight:600;padding:9px 12px;border-radius:8px;text-decoration:none}
.deal .claim{background:var(--primary);color:#fff;flex:1;text-align:center}.deal .more{border:1px solid var(--border);color:var(--text)}
.links{display:flex;flex-wrap:wrap;gap:8px}.links a{background:#1e2230;color:#cbd5e1;padding:6px 12px;border-radius:6px;font-size:13px;text-decoration:none}
.links a:hover{background:var(--primary);color:#fff}
.note{font-size:13px;color:var(--muted);border-top:1px solid var(--border);padding-top:14px;margin-top:18px}
footer{border-top:1px solid var(--border);padding:30px 0;color:var(--muted);font-size:13px;text-align:center}
"""

def nav(active=None):
    items = [f'<li><a href="/"{" class=active" if active is None else ""}>All Deals</a></li>']
    for c,(short,_,_) in CATS.items():
        items.append(f'<li><a href="{url_cat(c)}"{" class=active" if c==active else ""}>{e(short)}</a></li>')
    return f'''<div class="top-banner">⚡ Black Friday &amp; Cyber Monday 2026 software, hosting, AI &amp; VPN deals</div>
<nav class="top-nav" aria-label="Deal categories"><div class="wrap top-nav-inner">
<a class="brand" href="/">BFCM<span>BloggerDeals</span></a><ul class="nav">{"".join(items)}</ul></div></nav>'''

def page(title, desc, path, body, schema, active=None):
    canon = BASE + path
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{canon}">
<link rel="icon" href="https://www.onlinedecoded.com/wp-content/uploads/2026/08/cropped-favicon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="OnlineDecoded Black Friday Deals">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{OG}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{OG}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
{nav(active)}
<main class="wrap">
{body}
</main>
<footer><div class="wrap">
<p>Affiliate disclosure: some links on this page are affiliate links. If you buy through them, OnlineDecoded may earn a commission at no extra cost to you.</p>
<p><a href="/">All Black Friday deals</a> · <a href="https://www.onlinedecoded.com/">OnlineDecoded.com</a> · Updated {TODAY}</p>
</div></footer>
</body>
</html>
'''

def crumbs_schema(items):
    return {"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":BASE+u} for i,(n,u) in enumerate(items)]}

def deal_card(d, show_cat=False):
    tag = CATS[d["cat"]][0] if show_cat else d["discount"]
    return f'''<article class="deal"><span class="tag">{e(tag)}</span>
<h3><a href="{url_deal(d)}">{e(d["name"])} Black Friday Deal</a></h3>
<p><strong>{e(d["discount"])}</strong> · {e(d["price"])} (regular {e(d["base"])})<br>{e(d["desc"])}</p>
<div class="row"><a class="claim" href="{e(d["aff"])}" target="_blank" rel="nofollow sponsored noopener">Get deal →</a><a class="more" href="{url_deal(d)}">Details</a></div></article>'''

def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    urls = [("/", "daily", "1.0")]
    bycat = OrderedDict((c, [d for d in deals if d["cat"] == c]) for c in CATS)

    # Product pages
    for d in deals:
        short, ctitle, cintro = CATS[d["cat"]]
        siblings = [x for x in bycat[d["cat"]] if x["slug"] != d["slug"]]
        idx = bycat[d["cat"]].index(d)
        related = (bycat[d["cat"]][idx+1:] + bycat[d["cat"]][:idx])[:6]
        title = f"{d['name']} Black Friday Deal 2026: {d['discount']} ({d['price']})"
        if len(title) > 65: title = f"{d['name']} Black Friday 2026: {d['discount']}"
        desc = f"{d['name']} Black Friday 2026 deal: {d['discount']}, from {d['price']} (regular {d['base']}). {d['desc']}"[:158]
        sv = savings(d)
        body = f'''<div class="crumbs"><a href="/">All deals</a> › <a href="{url_cat(d['cat'])}">{e(short)}</a> › {e(d['name'])}</div>
<div class="card">
<span class="tag">{e(short)}</span><span class="badge">{e(d['discount'])}</span>
<h1>{e(d['name'])} Black Friday Deal 2026</h1>
<p>{e(d['desc'])}</p>
<a class="btn" href="{e(d['aff'])}" target="_blank" rel="nofollow sponsored noopener">Get {e(d['discount'])} on {e(d['name'])} →</a>

<h2>Deal at a glance</h2>
<table>
<tr><th>Discount</th><td>{e(d['discount'])}</td></tr>
<tr><th>Deal price</th><td>{e(d['price'])}</td></tr>
<tr><th>Regular price</th><td>{e(d['base'])}</td></tr>
<tr><th>Category</th><td><a href="{url_cat(d['cat'])}">{e(CATS[d['cat']][0])}</a></td></tr>
</table>
{f"<p>{e(sv)}</p>" if sv else ""}

<h2>Before you buy</h2>
<p>{e(cintro)}</p>
<p>Confirm the final price, billing term and renewal rate on the {e(d['name'])} checkout page before you pay. Black Friday promotions can change or end without notice.</p>

<h2>Similar {e(short)} deals</h2>
<div class="links">{"".join(f'<a href="{url_deal(r)}">{e(r["name"])} ({e(r["discount"])})</a>' for r in related)}</div>
<p class="note">See all <a href="{url_cat(d['cat'])}">{len(bycat[d['cat']])} {e(short)} Black Friday deals</a> or browse the <a href="/">full deals directory</a>.</p>
</div>'''
        schema = {"@context":"https://schema.org","@graph":[
            crumbs_schema([("Home","/"),(short,url_cat(d["cat"])),(d["name"],url_deal(d))]),
            {"@type":"WebPage","@id":BASE+url_deal(d),"url":BASE+url_deal(d),"name":title,"description":desc,
             "dateModified":TODAY,"isPartOf":{"@id":BASE+"/#website"}}]}
        p = os.path.join(OUT, d["cat"], d["slug"]); os.makedirs(p, exist_ok=True)
        open(os.path.join(p,"index.html"),"w").write(page(title, desc, url_deal(d), body, schema, d["cat"]))
        urls.append((url_deal(d), "weekly", "0.6"))

    # Category pages
    for c,(short,ctitle,cintro) in CATS.items():
        items = bycat[c]
        top = ", ".join(x["name"] for x in items[:4])
        desc = f"{len(items)} Black Friday 2026 {short.lower()} deals, including {top}. Compare discounts, deal prices and regular prices."[:158]
        body = f'''<div class="crumbs"><a href="/">All deals</a> › {e(short)}</div>
<div class="card"><span class="tag">{len(items)} deals</span>
<h1>{e(ctitle)}</h1><p>{e(cintro)}</p>
<table><tr><th style="width:auto">Provider</th><th style="width:auto">Discount</th><th style="width:auto">Deal price</th><th style="width:auto">Regular</th></tr>
{"".join(f'<tr><td><a href="{url_deal(x)}">{e(x["name"])}</a></td><td>{e(x["discount"])}</td><td>{e(x["price"])}</td><td>{e(x["base"])}</td></tr>' for x in items)}
</table></div>
<div class="grid">{"".join(deal_card(x) for x in items)}</div>
<div class="card" style="margin-top:28px"><h2>Other deal categories</h2><div class="links">{"".join(f'<a href="{url_cat(o)}">{e(v[0])}</a>' for o,v in CATS.items() if o!=c)}</div></div>'''
        schema = {"@context":"https://schema.org","@graph":[
            crumbs_schema([("Home","/"),(short,url_cat(c))]),
            {"@type":"CollectionPage","url":BASE+url_cat(c),"name":ctitle,"description":desc,"dateModified":TODAY,
             "mainEntity":{"@type":"ItemList","numberOfItems":len(items),"itemListElement":[
                 {"@type":"ListItem","position":i+1,"name":f'{x["name"]} Black Friday Deal',"url":BASE+url_deal(x)} for i,x in enumerate(items)]}}]}
        p = os.path.join(OUT, c); os.makedirs(p, exist_ok=True)
        open(os.path.join(p,"index.html"),"w").write(page(ctitle, desc, url_cat(c), body, schema, c))
        urls.insert(1+list(CATS).index(c), (url_cat(c), "daily", "0.8"))

    # Sitemap
    sm = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u,cf,pr in urls:
        sm.append(f"  <url>\n    <loc>{BASE}{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{cf}</changefreq>\n    <priority>{pr}</priority>\n  </url>")
    sm.append("</urlset>\n")
    open(os.path.join(OUT,"sitemap.xml"),"w").write("\n".join(sm))

    # Homepage snippets
    block = ['<!-- PASTE THIS JUST ABOVE <footer> IN index.html: crawlable links to every category and deal page -->',
             '<section class="wrap" id="all-deal-pages" style="padding:40px 24px">',
             '  <h2 style="font-size:24px;margin-bottom:6px">Browse All Black Friday 2026 Deals by Category</h2>']
    for c,(short,ctitle,_) in CATS.items():
        block.append(f'  <h3 style="margin:22px 0 8px"><a href="{url_cat(c)}" style="color:#a5b4fc">{e(ctitle)}</a></h3>')
        block.append('  <p style="color:#94a3b8;font-size:14px;line-height:2">' + " · ".join(
            f'<a href="{url_deal(x)}" style="color:#cbd5e1">{e(x["name"])} ({e(x["discount"])})</a>' for x in bycat[c]) + '</p>')
    block.append('</section>')
    open(os.path.join(OUT,"homepage-deal-links-snippet.html"),"w").write("\n".join(block)+"\n")
    return urls

if __name__ == "__main__":
    u = build()
    print(len(u), "URLs;", len(deals), "deals;", len(CATS), "categories")
