#!/usr/bin/env python3
"""Regression tests for affiliate disclosures and outbound-link handling."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from build import AMAZON_DISCLOSURE, apply_affiliate_links, build_affiliate_url  # noqa: E402

PUBLIC = ROOT / "public"


def main() -> int:
    pages = sorted(PUBLIC.glob("*.html"))
    if not pages:
        raise AssertionError("No hay páginas generadas en public/.")

    for page in pages:
        html = page.read_text(encoding="utf-8")
        if AMAZON_DISCLOSURE not in html:
            raise AssertionError(f"Falta la declaración de Amazon en {page.name}.")
        if "Publicidad y enlaces de afiliación." not in html:
            raise AssertionError(f"Falta el aviso comercial en {page.name}.")
        if "__AFFILIATE_LINK_TEMPLATES_JSON__" in html or "__AMAZON_DISCLOSURE__" in html:
            raise AssertionError(f"Quedó un marcador de plantilla en {page.name}.")

    sample = '<a href="https://www.autodoc.es/search?keyword=alternador" target="_blank" rel="nofollow sponsored">Buscar AUTODOC</a>'
    direct = apply_affiliate_links(sample, {})
    direct_rel = re.search(r'rel="([^"]+)"', direct)
    if not direct_rel or "sponsored" in direct_rel.group(1) or "Enlace de afiliado" in direct:
        raise AssertionError("El enlace directo de AUTODOC se marca incorrectamente como afiliado.")

    templates = {"autodoc": "https://tracking.example/click?destination={destination}"}
    tracked = apply_affiliate_links(sample, templates)
    tracked_rel = re.search(r'rel="([^"]+)"', tracked)
    encoded = quote("https://www.autodoc.es/search?keyword=alternador", safe="")
    if encoded not in tracked or not tracked_rel or "sponsored" not in tracked_rel.group(1):
        raise AssertionError("No se genera un enlace de seguimiento correctamente etiquetado.")
    if "Enlace de afiliado" not in tracked:
        raise AssertionError("Falta el aviso visible en un enlace rastreado.")
    if encoded not in build_affiliate_url("autodoc", "https://www.autodoc.es/search?keyword=alternador", templates):
        raise AssertionError("build_affiliate_url no codifica el destino.")
    if build_affiliate_url("autodoc", "https://www.autodoc.es/search?keyword=alternador", {}) != "https://www.autodoc.es/search?keyword=alternador":
        raise AssertionError("Sin plantilla, el destino debe permanecer directo.")

    local_link = apply_affiliate_links('<a href="/privacidad-cookies.html">Privacidad</a>', {})
    if 'rel="nofollow"' in local_link:
        raise AssertionError("Se alteró indebidamente un enlace interno.")

    index_html = (PUBLIC / "index.html").read_text(encoding="utf-8")
    amazon = re.findall(
        r'<a\b[^>]*href="https://(?:www\.)?amazon\.es/[^"]*tag=[^"]*"[^>]*>(.*?)</a\s*>',
        index_html,
        re.IGNORECASE | re.DOTALL,
    )
    if not amazon:
        raise AssertionError("No se encontraron enlaces Amazon etiquetados en la portada.")
    if any("Enlace de afiliado" not in body for body in amazon):
        raise AssertionError("Hay enlaces Amazon etiquetados sin aviso visible.")

    print(f"[OK] Avisos de afiliación y seguimiento validados en {len(pages)} páginas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
