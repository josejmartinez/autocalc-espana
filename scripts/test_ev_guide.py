#!/usr/bin/env python3
"""Regression checks for the EV charger guide and its search metadata."""
import json, subprocess, sys, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/"public"
subprocess.run([sys.executable,str(ROOT/"scripts"/"build_ev_guide.py")],cwd=ROOT,check=True)
page=(PUBLIC/"guia-cargadores-electricos.html").read_text(encoding="utf-8")
assert '<html lang="es">' in page
assert '<title>' in page and 'Cómo elegir un cargador' in page and 'guía práctica' in page
assert '<meta name="description"' in page
assert '<link rel="canonical" href="https://autocalc.es/guia-cargadores-electricos.html">' in page
assert 'application/ld+json' in page and '"@type":"Article"' in page
for marker in ("compatibilidad","instalación","seguridad","coste total","Publicidad y afiliación","calculadora de tiempo y coste de carga"):
    assert marker.lower() in page.lower(), f"Falta contenido esencial: {marker}"
for forbidden in ("EVDANCE recomienda", "mejor cargador del mercado", "reseñas verificadas", "5 estrellas"):
    assert forbidden.lower() not in page.lower(), f"Afirmación comercial no sustentada: {forbidden}"

# The approved EVDANCE Awin template must be used only on the buying guide.
from urllib.parse import quote
destination = "https://eu.evdances.com/es/products/evdance-schuko-type-2-portable-ev-charger-16a-3-68kw"
expected_tracking = "https://www.awin1.com/cread.php?awinmid=67740&awinaffid=3126791&ued=" + quote(destination, safe="")
assert expected_tracking in page, "La ficha EVDANCE no usa el enlace Awin aprobado."
assert 'rel="sponsored nofollow noopener noreferrer"' in page
assert "no ha recibido ni probado este producto" in page
assert "no es una prueba independiente" in page\nassert "pagead2.googlesyndication.com" not in page, "AdSense no debe cargarse mientras está desactivado."
calculator = (PUBLIC/"carga-vehiculo-electrico.html").read_text(encoding="utf-8")
assert "EVDANCE" not in calculator, "La promoción EVDANCE no debe contaminar la calculadora independiente."
root=ET.parse(PUBLIC/"sitemap.xml").getroot()
locs=[e.text for e in root.iter() if e.tag.endswith("loc")]
assert "https://autocalc.es/guia-cargadores-electricos.html" in locs
print("Guía EV: contenido, canonical, Article JSON-LD y sitemap correctos.")
