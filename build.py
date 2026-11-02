#!/usr/bin/env python3
"""Melóradar statikus oldalgenerátor (a HR monitor motorjára építve).

Bemenet:  data/articles.json (hírek és trendek), src/config.json, src/style.css, src/app.js
Kimenet:  docs/  (ezt szolgálja ki a GitHub Pages: main ág, /docs mappa)

Futtatás: python3 build.py
"""
import datetime as dt
import html
import json
import re
import shutil
import sys
from email.utils import format_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
CFG = json.loads((ROOT / "src/config.json").read_text(encoding="utf-8"))
SITE = CFG["site"]
TOPICS = CFG["topics"]
TMAP = {t["k"]: t for t in TOPICS}
ICONS = CFG["icons"]
BUDAPEST = ZoneInfo("Europe/Budapest")
MONTHS = ["január", "február", "március", "április", "május", "június", "július",
          "augusztus", "szeptember", "október", "november", "december"]
DAYS = ["hétfő", "kedd", "szerda", "csütörtök", "péntek", "szombat", "vasárnap"]
BADGE = {3: ("b3", "Itthon is érint"), 2: ("b2", "Ide is jöhet"), 1: ("b1", "Érdekesség")}
REQUIRED_NEWS = ["id", "day", "published", "source", "url", "region", "topic", "hu_score", "icon", "title", "lead", "hu"]
REQUIRED_TREND = ["id", "day", "published", "source", "url", "region", "topic", "icon", "term", "title", "what", "data", "hu"]

e = lambda s: html.escape(str(s if s is not None else ""), quote=True)
base_url = SITE["url"].rstrip("/")
DEV = bool(SITE.get("dev"))
BASE_PATH = "/" + base_url.split("://", 1)[-1].partition("/")[2].strip("/")
BASE_PATH = BASE_PATH.rstrip("/") + "/"


def slug(s):
    s = re.sub(r"[^a-z0-9-]+", "-", str(s).lower()).strip("-")
    return re.sub(r"-{2,}", "-", s) or "hir"


def long_date(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.year}. {MONTHS[d.month - 1]} {d.day}., {DAYS[d.weekday()]}"


def short_date(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.year}.{d.month:02d}.{d.day:02d}."


def svg_icon(name, size, sw, op=1):
    return (f'<svg class="ic" aria-hidden="true" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="#fff" stroke-opacity="{op}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            f'{ICONS.get(name, ICONS["globe"])}</svg>')


def topic_of(a):
    return TMAP.get(a.get("topic"), TOPICS[0])


def banner(a, cls="banner", h=120, size=56):
    t = topic_of(a)
    c1, o1, c2, o2 = t.get("dots", ["#ffffff", 0.09, "#ffffff", 0.06])
    return (f'<div class="{cls}" aria-hidden="true" style="background:{t["bg"]}">'
            f'<svg class="bg" viewBox="0 0 400 {h}" preserveAspectRatio="xMidYMid slice">'
            f'<circle cx="360" cy="10" r="{h*0.6:.0f}" fill="{c1}" fill-opacity="{o1}"/>'
            f'<circle cx="30" cy="{h-5}" r="{h*0.4:.0f}" fill="{c2}" fill-opacity="{o2}"/></svg>'
            f'{svg_icon(a.get("icon"), size, 1.6)}</div>')


# ---------------------------------------------------------------- adatok
def load_articles():
    data = json.loads((ROOT / "data/articles.json").read_text(encoding="utf-8"))
    items, seen, problems = [], set(), []
    for a in data.get("articles", []):
        is_trend = a.get("kind") == "trend"
        missing = [k for k in (REQUIRED_TREND if is_trend else REQUIRED_NEWS) if not a.get(k)]
        if missing:
            problems.append(f"{a.get('id', '?')}: hiányzó mező: {', '.join(missing)}")
            continue
        if a["topic"] not in TMAP:
            problems.append(f"{a['id']}: ismeretlen téma: {a['topic']}")
        if a["icon"] not in ICONS:
            problems.append(f"{a['id']}: ismeretlen ikon: {a['icon']} (globe lesz helyette)")
        s = slug(a["id"])
        while s in seen:
            s += "-2"
        seen.add(s)
        a["slug"] = s
        a["path"] = f'{"trend" if is_trend else "hir"}/{s}/'
        items.append(a)
    items.sort(key=lambda a: (a["day"], a["published"]), reverse=True)
    return data.get("updated", ""), items, problems


# ---------------------------------------------------------------- közös keret
def head(title, desc, path, prefix, og_type="website", extra=""):
    canon = f"{base_url}/{path}"
    full_title = title if title == SITE["name"] else f"{title} | {SITE['name']}"
    return f"""<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{e(canon)}">
<meta property="og:image" content="{e(base_url)}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="hu_HU">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
{'<meta name="robots" content="noindex,nofollow">' + chr(10) if DEV else ''}<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{e(SITE['name'])}" href="{prefix}feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="{prefix}assets/style.css">
{extra}</head>
<body>
<a class="skip" href="#main">Ugrás a tartalomra</a>"""


def header(prefix, nav_html=None):
    if nav_html is None:
        nav_html = (f'<a href="{prefix}">Összes hír</a>'
                    f'<a class="trendbtn" href="{prefix}#trendek">Trendfigyelő</a>')
    ribbon = ""
    if DEV:
        live = SITE.get("live_url", "")
        ribbon = (f'<div class="devbar"><div class="wrap">Fejlesztői változat, a keresők nem indexelik.'
                  f'{f" Az élő oldal: <a href={chr(34)}{e(live)}{chr(34)}>{e(live)}</a>" if live else ""}</div></div>')
    return ribbon + f"""<header class="top">
  <div class="wrap">
    <a class="brand" href="{prefix}" aria-label="{e(SITE['name'])}, kezdőlap">
      <span class="tile">{svg_icon("radar", 22, 2)}</span>
      <span><b>{e(SITE['name'])}</b><small>{e(SITE['tagline'])}</small></span>
    </a>
    <nav class="nav" id="nav" aria-label="Témák">{nav_html}</nav>
  </div>
</header>"""


def footer(prefix):
    return f"""<footer>
  <div class="wrap">
    <span class="disc">A hírek nemzetközi forrásokból, saját összefoglalásban és értelmezésben készülnek, mesterséges intelligencia segítségével. Minden hír mellett ott az eredeti forrás, ha a részletekre is kíváncsi vagy.</span>
    <nav aria-label="Lábléc"><a href="{prefix}impresszum/">Impresszum</a><a href="{prefix}feed.xml">RSS</a><span>{e(SITE['email'])}</span></nav>
  </div>
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------- főoldal
def build_index(items):
    news = [a for a in items if a.get("kind") != "trend"]
    static = "".join(
        f'<li><a href="{e(a["path"])}">{e(a.get("term") + ": " if a.get("term") else "")}{e(a["title"])}</a> '
        f'<small>({e(a["source"])}, {short_date(a["published"])})</small></li>'
        for a in items[:40])
    body = head(SITE["name"], SITE["description"], "", "")
    body += header("", nav_html="")
    body += f"""
<div class="wrap">
  <div class="bar">
    <span class="eyebrow" id="dateline">{e(long_date(news[0]["day"]) if news else "")}</span>
    <div class="tools">
      <input id="q" type="search" placeholder="Keresés: cég, ország, téma" aria-label="Keresés a hírekben">
      <select id="region" aria-label="Régió"><option value="">Minden régió</option></select>
      <select id="minrel" aria-label="Hazai hatás">
        <option value="1">Minden hír</option>
        <option value="2">Trendek és közvetlen hatás</option>
        <option value="3">Csak közvetlen hazai hatás</option>
      </select>
      <span class="upd" id="upd"></span>
    </div>
  </div>
  <main id="main">
    <section class="sec"><div class="sec-head"><h2>Legfrissebb hírek és trendek</h2></div><ul>{static}</ul></section>
  </main>
</div>
<script src="assets/config.js"></script>
<script src="assets/app.js"></script>
"""
    body += footer("")
    (OUT / "index.html").write_text(body, encoding="utf-8")


# ---------------------------------------------------------------- cikkoldalak
def aside_list(items, current, prefix):
    others = [a for a in items if a is not current][:6]
    cards = "".join(
        f'<a class="mini-card" href="{prefix}{e(a["path"])}"><span class="mini" style="background:{topic_of(a)["bg"]}">'
        f'{svg_icon(a["icon"], 16, 2)}</span><span><span class="t">{e(a.get("term") or a["title"])}</span>'
        f'<small>{e("Trend" if a.get("kind") == "trend" else topic_of(a)["nav"])} · {short_date(a["published"])}</small></span></a>'
        for a in others)
    return f'<aside aria-label="További friss tartalmak"><h2>Friss a Melóradaron</h2>{cards}</aside>'


def build_article(a, items):
    prefix = "../../"
    is_trend = a.get("kind") == "trend"
    t = topic_of(a)
    desc = a["lead"] if not is_trend else a["what"]
    title = f'{a["term"]}: {a["title"]}' if is_trend else a["title"]
    ld = {
        "@context": "https://schema.org", "@type": "NewsArticle", "headline": title[:110],
        "description": desc, "inLanguage": "hu", "datePublished": a["day"],
        "image": f"{base_url}/og.png", "mainEntityOfPage": f'{base_url}/{a["path"]}',
        "publisher": {"@type": "Organization", "name": "Sajtóművek"},
        "isBasedOn": a["url"],
    }
    extra = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n'
    out = head(title, desc, a["path"], prefix, "article", extra) + header(prefix)
    badge_cls, badge_txt = BADGE.get(a.get("hu_score", 1), BADGE[1])
    meta = (f'<div class="row"><span class="badge {"b2" if is_trend else badge_cls}">'
            f'{"Munkahelyi trend" if is_trend else badge_txt}</span><span class="tag">{e(t["nav"])}</span>'
            f'<span class="src" style="font-size:13px;color:var(--muted)">{e(a["region"])} · {e(a["source"])} · {short_date(a["published"])}</span></div>')
    if is_trend:
        content = f"""
      <span class="term">{e(a["term"])}{" · " + e(a["term_hu"]) if a.get("term_hu") else ""}</span>
      <h1>{e(a["title"])}</h1>
      <div class="box what-box"><span class="label">Mit jelent?</span><p>{e(a["what"])}</p></div>
      <div class="box num-box"><span class="label">A számok</span><p>{e(a["data"])}</p></div>
      <div class="box hu-box"><span class="label">Mit jelent ez neked?</span><p>{e(a["hu"])}</p></div>"""
    else:
        stat = ""
        if a.get("stat") and a["stat"].get("value"):
            stat = (f'<div class="box num-box"><span class="label">A szám</span><div class="statline">'
                    f'<b>{e(a["stat"]["value"])}</b><p>{e(a["stat"].get("label", ""))}</p></div></div>')
        content = f"""
      <h1>{e(a["title"])}</h1>
      <p class="lede">{e(a["lead"])}</p>
      {stat}
      <div class="box hu-box"><span class="label">Mit jelent ez neked?</span><p>{e(a["hu"])}</p></div>"""
    out += f"""
<div class="wrap">
  <nav class="crumbs" aria-label="Morzsamenü"><a href="{prefix}">{e(SITE["name"])}</a> › {"Trendfigyelő" if is_trend else e(t["k"])}</nav>
  <div class="article">
    <main id="main" class="main-col">
      {banner(a, "hero", 200, 88)}
      {meta}
      {content}
      <div class="source"><span>Forrás: <strong>{e(a["source"])}</strong>, {short_date(a["published"])}</span>
        <a class="btn" href="{e(a["url"])}" target="_blank" rel="noopener">Eredeti cikk megnyitása</a></div>
      <p class="note">Ez az összefoglaló a fenti forrás alapján, saját szavakkal és saját értelmezéssel, mesterséges intelligencia segítségével készült. A részletekért és a pontos megfogalmazásért nézd meg az eredeti cikket.</p>
    </main>
    {aside_list(items, a, prefix)}
  </div>
</div>
"""
    out += footer(prefix)
    path = OUT / a["path"]
    path.mkdir(parents=True, exist_ok=True)
    (path / "index.html").write_text(out, encoding="utf-8")


# ---------------------------------------------------------------- egyéb oldalak
def build_impressum():
    imp = SITE.get("impressum", {})
    def val(label, v):
        if not v:
            return '<em>[ellenőrzés alatt]</em>'
        if v.startswith("http"):
            return f'<a href="{e(v)}" target="_blank" rel="noopener">{e(v.split("//", 1)[1])}</a>'
        if "@" in v and " " not in v:
            return f'<a href="mailto:{e(v)}">{e(v)}</a>'
        if label.lower().startswith("telefon"):
            return f'<a href="tel:{e(v.replace(" ", ""))}">{e(v)}</a>'
        return e(v)
    rows = "".join(f"<dt>{e(k)}</dt><dd>{val(k, v)}</dd>" for k, v in imp.get("rows", []))
    out = head("Impresszum", f"A {SITE['name']} impresszuma és működési elvei.", "impresszum/", "../") + header("../")
    out += f"""
<div class="wrap"><main id="main" class="prose">
  <h1>Impresszum</h1>
  <p>{e(SITE['name'])} – {e(SITE['tagline'])}</p>
  <h2>A szolgáltató adatai</h2>
  <dl>{rows}</dl>
  <p>{e(imp.get('legal', ''))}</p>
  <h2>Hogyan készül?</h2>
  <p>A {e(SITE['name'])} nemzetközi statisztikai hivatalok, munkaerőpiaci kutatócégek, karrier- és HR-szaklapok és gazdasági hírportálok friss anyagait figyeli. A híreket mesterséges intelligencia válogatja és foglalja össze magyarul, saját szavakkal, és mindegyikhez rövid, gyakorlati értelmezést fűz a magyar munkavállalók és álláskeresők szemszögéből („Mit jelent ez neked?”). Csak olyan hír kerül fel, amelynek dátumát és számait az eredeti forrásban ellenőrizni lehetett.</p>
  <h2>Források és szerzői jog</h2>
  <p>A cikkek nem fordítások, hanem saját összefoglalások. Minden hír mellett szerepel az eredeti forrás neve és linkje; a teljes tartalom és a pontos megfogalmazás az eredeti kiadóé.</p>
  <h2>Hibát találtál?</h2>
  <p>Ha pontatlanságot látsz, írj nekünk a(z) {e(SITE['email'])} címre, és javítjuk.</p>
  <p class="note">Utolsó frissítés: {e(imp.get('updated', ''))}</p>
</main></div>
"""
    out += footer("../")
    (OUT / "impresszum").mkdir(exist_ok=True)
    (OUT / "impresszum/index.html").write_text(out, encoding="utf-8")


def build_404():
    out = head("Az oldal nem található", SITE["description"], "404.html", BASE_PATH) + header(BASE_PATH)
    out += f"""<div class="wrap"><main id="main" class="prose"><h1>Ez az oldal nem található</h1>
<p>Lehet, hogy a hír archívumba került, vagy elírás van a címben.</p><p><a href="{BASE_PATH}">Vissza a főoldalra</a></p></main></div>"""
    out += footer(BASE_PATH)
    (OUT / "404.html").write_text(out, encoding="utf-8")


def build_feed(items, updated):
    def rfc(day):
        return format_datetime(dt.datetime.fromisoformat(day + "T06:35").replace(tzinfo=BUDAPEST))
    entries = []
    for a in items[:60]:
        title = f'{a["term"]}: {a["title"]}' if a.get("kind") == "trend" else a["title"]
        desc = (a.get("what", "") + " " + a.get("data", "")) if a.get("kind") == "trend" else a["lead"]
        desc += " Neked: " + a["hu"]
        link = f'{base_url}/{a["path"]}'
        entries.append(f"""  <item>
    <title>{e(title)}</title>
    <link>{e(link)}</link>
    <guid isPermaLink="true">{e(link)}</guid>
    <pubDate>{rfc(a["day"])}</pubDate>
    <category>{e("Munkahelyi trend" if a.get("kind") == "trend" else a["topic"])}</category>
    <description>{e(desc)}</description>
  </item>""")
    last = rfc(items[0]["day"]) if items else format_datetime(dt.datetime.now(BUDAPEST))
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{e(SITE['name'])}</title>
  <link>{e(base_url)}/</link>
  <atom:link href="{e(base_url)}/feed.xml" rel="self" type="application/rss+xml"/>
  <description>{e(SITE['description'])}</description>
  <language>hu</language>
  <lastBuildDate>{last}</lastBuildDate>
{chr(10).join(entries)}
</channel>
</rss>
"""
    (OUT / "feed.xml").write_text(feed, encoding="utf-8")


def build_sitemap(items):
    urls = [f"{base_url}/", f"{base_url}/impresszum/"] + [f'{base_url}/{a["path"]}' for a in items]
    lastmods = [items[0]["day"] if items else ""] + [""] + [a["day"] for a in items]
    body = "".join(f"  <url><loc>{e(u)}</loc>{f'<lastmod>{m}</lastmod>' if m else ''}</url>\n" for u, m in zip(urls, lastmods))
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n',
        encoding="utf-8")
    robots = "User-agent: *\nDisallow: /\n" if DEV else f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n"
    (OUT / "robots.txt").write_text(robots, encoding="utf-8")


def build_assets(items, updated):
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    (OUT / "data").mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "src/style.css", OUT / "assets/style.css")
    shutil.copy(ROOT / "src/app.js", OUT / "assets/app.js")
    cfg = {"topics": TOPICS, "icons": ICONS}
    (OUT / "assets/config.js").write_text("window.HRM=" + json.dumps(cfg, ensure_ascii=False) + ";\n", encoding="utf-8")
    pub = [{k: v for k, v in a.items() if k != "slug"} for a in items]
    (OUT / "data/articles.json").write_text(json.dumps({"updated": updated, "articles": pub}, ensure_ascii=False), encoding="utf-8")
    (OUT / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" x2="1">'
        '<stop offset="0" stop-color="#50d7be"/><stop offset="1" stop-color="#37aff0"/></linearGradient></defs>'
        '<rect width="64" height="64" rx="16" fill="url(#g)"/><g transform="translate(12 12) scale(1.667)" fill="none" '
        'stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M16 8V5L19 2L20 4L22 5L19 8H16ZM16 8L12 11.9999M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2M17 12C17 14.7614 14.7614 17 12 17C9.23858 17 7 14.7614 7 12C7 9.23858 9.23858 7 12 7"/></g></svg>', encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    src_og = ROOT / "src/og.png"
    if src_og.exists():
        shutil.copy(src_og, OUT / "og.png")
    if SITE.get("domain"):
        (OUT / "CNAME").write_text(SITE["domain"].strip() + "\n", encoding="utf-8")


def main():
    updated, items, problems = load_articles()
    for p in problems:
        print("FIGYELEM:", p, file=sys.stderr)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    build_assets(items, updated)
    build_index(items)
    for a in items:
        build_article(a, items)
    build_impressum()
    build_404()
    build_feed(items, updated)
    build_sitemap(items)
    print(f"Kész: {len(items)} elem ({sum(1 for a in items if a.get('kind') == 'trend')} trend) -> {OUT}")


if __name__ == "__main__":
    main()
