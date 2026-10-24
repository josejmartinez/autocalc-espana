#!/usr/bin/env python3
"""Audit generated pages for SEO metadata, local links, JSON-LD and sitemap integrity."""
import json, re, sys, xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]; PUBLIC=ROOT/"public"
NS={"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}

class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.links=[]; self.canonicals=[]; self.titles=0; self.title=""; self.in_title=False
        self.descriptions=0; self.lang=""; self.robots=[]; self.json_blocks=[]; self.in_json=False; self.json_buf=""
    def handle_starttag(self,tag,attrs):
        a={k.lower():(v or "") for k,v in attrs}
        if tag=="html": self.lang=a.get("lang","")
        if a.get("id"): self.ids.append(a["id"])
        if tag=="a" and a.get("href"): self.links.append((a["href"],a))
        if tag=="link" and a.get("rel","").lower()=="canonical": self.canonicals.append(a.get("href",""))
        if tag=="title": self.titles+=1; self.in_title=True
        if tag=="meta" and a.get("name","").lower()=="description" and a.get("content","").strip(): self.descriptions+=1
        if tag=="meta" and a.get("name","").lower()=="robots": self.robots.append(a.get("content","").lower())
        if tag=="script" and a.get("type","").lower()=="application/ld+json": self.in_json=True; self.json_buf=""
    def handle_data(self,data):
        if self.in_title: self.title+=data
        if self.in_json: self.json_buf+=data
    def handle_endtag(self,tag):
        if tag=="title": self.in_title=False
        if tag=="script" and self.in_json: self.json_blocks.append(self.json_buf); self.in_json=False

def main():
    cfg=json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
    base=("https://"+cfg["custom_domain"].strip().lower()) if cfg.get("use_custom_domain") else str(cfg.get("github_pages_url") or cfg.get("domain","")).rstrip("/")
    if not base.startswith("https://"): raise SystemExit("Dominio activo HTTPS inválido en config.json")
    pages=sorted(PUBLIC.rglob("*.html")); files={p.relative_to(PUBLIC).as_posix() for p in PUBLIC.rglob("*") if p.is_file()}
    errors=[]; warnings=[]; canonicals=set(); sitemap_urls=[]; link_count=0; indexable_pages=set()
    if not pages: errors.append("No se generaron páginas HTML.")
    for page in pages:
        html=page.read_text(encoding="utf-8"); p=AuditParser(); p.feed(html)
        if not any("noindex" in value for value in p.robots): indexable_pages.add(page.name)
        link_count += len(p.links)
        for ident,n in Counter(p.ids).items():
            if n>1: errors.append(f"{page.name}: ID duplicado {ident!r}.")
        if p.lang!="es": errors.append(f"{page.name}: falta lang=es.")
        if p.titles!=1 or not p.title.strip(): errors.append(f"{page.name}: title ausente o duplicado.")
        if p.descriptions!=1: errors.append(f"{page.name}: meta description ausente o duplicada.")
        if len(p.canonicals)!=1 or not p.canonicals[0].startswith(base+"/"): errors.append(f"{page.name}: canonical incorrecta.")
        elif p.canonicals[0] in canonicals: errors.append(f"{page.name}: canonical duplicada {p.canonicals[0]}.")
        else: canonicals.add(p.canonicals[0])
        if "googletagmanager.com/gtag/js" in html.split("</head>",1)[0]: errors.append(f"{page.name}: Analytics carga en head antes del consentimiento.")
        if any(x in html for x in ("__CANONICAL__","__SCHEMA__","__ADSENSE_HEAD__","__AMAZON_DISCLOSURE__")): errors.append(f"{page.name}: marcador de plantilla sin sustituir.")
        for block in p.json_blocks:
            try: json.loads(block)
            except json.JSONDecodeError as exc: errors.append(f"{page.name}: JSON-LD inválido ({exc.msg}).")
        for href,attrs in p.links:
            if href.startswith("#"):
                frag=unquote(href[1:])
                if frag and frag not in p.ids: errors.append(f"{page.name}: fragmento interno inexistente #{frag}.")
                continue
            if href.startswith(("mailto:","tel:","javascript:","data:")): continue
            u=urlsplit(href)
            if attrs.get("target","").lower()=="_blank" and u.scheme in ("http","https"):
                rel=set(attrs.get("rel","").lower().split())
                if not {"noopener","noreferrer"}.issubset(rel): errors.append(f"{page.name}: target=_blank sin noopener/noreferrer: {href[:140]}")
            if u.scheme in ("http","https") and (u.hostname or "").lower()!=urlsplit(base).hostname: continue
            if u.scheme and u.scheme not in ("http","https"): continue
            path=unquote(u.path).lstrip("/") or "index.html"
            if path.endswith("/"): path+="index.html"
            if path.endswith((".html",".xml",".txt",".svg",".json")) and path not in files: errors.append(f"{page.name}: enlace a archivo inexistente: {href[:140]}")
            elif path.endswith("/") and (path + "index.html") not in files: errors.append(f"{page.name}: enlace a directorio sin index.html: {href[:140]}")
    sm=PUBLIC/"sitemap.xml"; robots=PUBLIC/"robots.txt"
    if not sm.is_file(): errors.append("Falta sitemap.xml.")
    else:
        try:
            root=ET.parse(sm).getroot()
            if root.tag!="{http://www.sitemaps.org/schemas/sitemap/0.9}urlset": errors.append("Raíz de sitemap.xml no estándar.")
            sitemap_urls=[x.text.strip() for x in root.findall("s:url/s:loc",NS) if x.text and x.text.strip()]
            if not sitemap_urls: errors.append("Sitemap vacío.")
            if len(sitemap_urls)!=len(set(sitemap_urls)): errors.append("URLs duplicadas en sitemap.")
            for url in sitemap_urls:
                u=urlsplit(url)
                if u.scheme!="https" or u.netloc.lower()!=urlsplit(base).netloc.lower(): errors.append(f"URL sitemap fuera de dominio: {url}"); continue
                path=unquote(u.path).lstrip("/") or "index.html"
                if path.endswith("/"): path+="index.html"
                if path.endswith((".html",".xml",".txt")) and path not in files: errors.append(f"Sitemap apunta a archivo inexistente: {url}")
            for page in pages:
                if page.name in indexable_pages and page.name!="404.html":\n                    rel=page.relative_to(PUBLIC).as_posix()\n                    expected=base+("/" if rel=="index.html" else "/"+rel)\n                    if expected not in sitemap_urls: errors.append(f"{rel}: página indexable que no aparece en sitemap.")
        except (ET.ParseError,OSError) as exc: errors.append(f"Sitemap XML inválido: {exc}")
    if not robots.is_file(): errors.append("Falta robots.txt.")
    elif f"Sitemap: {base}/sitemap.xml" not in robots.read_text(encoding="utf-8"): errors.append("robots.txt no declara el sitemap activo.")
    if not (PUBLIC/"privacidad-cookies.html").is_file(): errors.append("Falta privacidad-cookies.html.")
    if cfg.get("adsense_ads_enabled") is True and cfg.get("google_certified_cmp_configured") is not True: errors.append("AdSense activado sin CMP certificada.")
    if not str(cfg.get("contact_email","")).strip(): warnings.append("contact_email vacío: completar datos legales antes de explotación comercial.")
    print(f"Auditoría: {len(pages)} páginas HTML; {link_count} enlaces revisados; {len(sitemap_urls)} URLs en sitemap.")
    for w in warnings: print("[AVISO]",w)
    for e in errors[:120]: print("[ERROR]",e)
    if len(errors)>120: print(f"... y {len(errors)-120} errores más.")
    if errors: print(f"Auditoría fallida: {len(errors)} errores."); return 1
    print("[OK] SEO básico, canonicals, enlaces locales, JSON-LD, sitemap, robots y salvaguardas.")
    return 0
if __name__=="__main__": raise SystemExit(main())
