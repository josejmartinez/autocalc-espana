#!/usr/bin/env python3
"""Regression tests for affiliate disclosures and outbound-link handling."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from build import (  # noqa: E402
    AMAZON_DISCLOSURE, AFFILIATE_PARTNER_DOMAINS, apply_affiliate_links,
    build_affiliate_url, render_ad_slot, render_affiliate_sidebar,
)

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

    # Priority merchants must be supported by the tracking configuration, even when their
    # templates stay empty until the user has a real approved campaign link.
    for partner in ("autodoc", "norauto", "ebay", "oscaro", "aurgi", "feuvert", "costco"):
        if partner not in AFFILIATE_PARTNER_DOMAINS:
            raise AssertionError(f"Falta el comercio prioritario {partner} en el sistema de afiliación.")

    oscaro_html = '<a href="https://www.oscaro.es/" target="_blank" rel="nofollow">Oscaro</a>'
    oscaro_tracked = apply_affiliate_links(oscaro_html, {
        "oscaro": "https://tracking.example/click?destination={destination}"
    })
    oscaro_rel = re.search(r'rel="([^"]+)"', oscaro_tracked)
    if "Enlace de afiliado" not in oscaro_tracked or not oscaro_rel or "sponsored" not in oscaro_rel.group(1):
        raise AssertionError("Oscaro no acepta plantilla de seguimiento configurable como afiliado.")

    ebay_html = '<a href="https://www.ebay.es/sch/i.html?_nkw=alternador" target="_blank" rel="nofollow">Buscar en eBay</a>'
    ebay_tracked = apply_affiliate_links(ebay_html, {
        "ebay": "https://tracking.example/click?destination={destination}"
    })
    if "Enlace de afiliado" not in ebay_tracked:
        raise AssertionError("eBay no acepta plantilla de seguimiento configurable como afiliado.")

    # A paid direct-sponsor placement remains sponsored even when it is not an affiliate link.
    paid_ad = '<a data-autocalc-paid-ad="true" href="https://sponsor.example/oferta" target="_blank" rel="sponsored nofollow">Publicidad</a>'
    paid_ad_html = apply_affiliate_links(paid_ad, {})
    paid_ad_rel = re.search(r'rel="([^"]+)"', paid_ad_html)
    if not paid_ad_rel or "sponsored" not in paid_ad_rel.group(1):
        raise AssertionError("Un patrocinio directo ha perdido rel=sponsored.")
    if "Enlace de afiliado" in paid_ad_html:
        raise AssertionError("Un patrocinio directo no debe etiquetarse falsamente como afiliación.")

    if render_ad_slot("sidebar_left") or render_ad_slot("sidebar_right") or render_ad_slot("inline"):
        raise AssertionError("Las posiciones de anuncios no configuradas deben permanecer invisibles.")
    safe_slot = render_ad_slot("inline", direct_slots={
        "inline": {
            "enabled": True,
            "advertiser": "Taller Ejemplo",
            "headline": "<Oferta> especial",
            "body": "Texto comercial",
            "image_url": "",
            "target_url": "https://sponsor.example/oferta",
        }
    }, adsense_slots={})
    if 'aria-label="Publicidad de Taller Ejemplo"' not in safe_slot or 'rel="sponsored nofollow noopener noreferrer"' not in safe_slot:
        raise AssertionError("El bloque de publicidad directa no tiene disclosure/rel correctos.")
    if "&lt;Oferta&gt; especial" not in safe_slot or "<Oferta>" in safe_slot:
        raise AssertionError("Los textos del patrocinador deben escaparse como texto plano.")

    # Side promos are invisible until an approved tracking template exists.
    sidebar_direct = render_affiliate_sidebar(
        "sidebar_left", "autodoc", "AUTODOC", "Buscar recambios",
        "https://www.autodoc.es/search?keyword=alternador", templates={}
    )
    if sidebar_direct:
        raise AssertionError("No debe aparecer un anuncio afiliado lateral sin tracking aprobado.")

    sidebar_tracked = render_affiliate_sidebar(
        "sidebar_left", "autodoc", "AUTODOC", "Buscar recambios",
        "https://www.autodoc.es/search?keyword=alternador",
        templates={"autodoc": "https://tracking.example/click?destination={destination}"}
    )
    sidebar_rel = re.search(r'rel="([^"]+)"', sidebar_tracked)
    if not sidebar_tracked or not sidebar_rel or "sponsored" not in sidebar_rel.group(1):
        raise AssertionError("La promoción lateral afiliada no tiene rel=sponsored.")
    if "Enlace de afiliado" not in sidebar_tracked or "AUTODOC" not in sidebar_tracked:
        raise AssertionError("La promoción lateral debe identificarse como afiliada y mostrar el comercio.")
    if quote("https://www.autodoc.es/search?keyword=alternador", safe="") not in sidebar_tracked:
        raise AssertionError("La promoción lateral no conserva su destino mediante el deeplink.")

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
