#!/usr/bin/env python3
"""Regression tests for the canonical sitemap emitted by the static-site builder."""
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit
import json

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
base = ("https://" + cfg["custom_domain"].strip().lower()) if cfg.get("use_custom_domain") else str(cfg.get("github_pages_url") or cfg.get("domain", "")).rstrip("/")
root = ET.parse(PUBLIC / "sitemap.xml").getroot()
assert root.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset", "Sitemap must use the standard urlset format"
entries = root.findall("sm:url", NS)
urls = [e.findtext("sm:loc", default="", namespaces=NS).strip() for e in entries]
assert urls and all(urls), "Sitemap must contain non-empty loc URLs"
assert len(urls) == len(set(urls)), "Sitemap must not contain duplicate URLs"
for url in urls:
    parsed = urlsplit(url)
    assert parsed.scheme == "https" and parsed.netloc == urlsplit(base).netloc, f"Non-canonical URL in sitemap: {url}"
    assert not parsed.query and not parsed.fragment, f"URL with query/fragment in sitemap: {url}"
    # lastmod must be omitted until the generator has reliable per-page edit timestamps.
    entry = entries[urls.index(url)]
    assert entry.find("sm:lastmod", NS) is None, f"Unreliable lastmod emitted for {url}"

expected = [
    "equivalencia-neumaticos-205-60-r16.html",
    "equivalencia-neumaticos-215-55-r17.html",
    "equivalencia-neumaticos-195-50-r15.html",
    "equivalencia-neumaticos-215-60-r17.html",
    "desguaces-itv-torrejon-de-la-calzada-la-torre.html",
    "desguaces-itv-ocana-sesena-illescas-toledo.html",
    "mapa-web.html",
]
for filename in expected:
    canonical = base + ("/" if filename == "index.html" else "/" + filename)
    assert canonical in urls, f"Priority URL missing from sitemap: {canonical}"
    assert (PUBLIC / filename).is_file(), f"Sitemap priority page not generated: {filename}"

print(f"[OK] Sitemap SEO: {len(urls)} URLs únicas en dominio canónico; sin lastmod ficticio; páginas prioritarias presentes.")
