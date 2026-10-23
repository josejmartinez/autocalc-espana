#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el hub estático de reseñas de AutoCalc España sin inventar opiniones.

El sitio actual se despliega como HTML estático. Este primer módulo aporta una
landing pública y un contrato JSON versionado; no finge disponer de cuentas,
reseñas ni backend. Las aportaciones de usuarios se habilitarán al conectar un
servicio persistente con moderación, privacidad y controles antispam.
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
BASE = (f"https://{CONFIG.get('custom_domain', 'autocalc.es').strip()}"
        if CONFIG.get("use_custom_domain") is True
        else CONFIG.get("domain", "").rstrip("/"))
CANONICAL = f"{BASE}/resenas/"
SITEMAP = PUBLIC / "sitemap.xml"
REVIEWS_DIR = PUBLIC / "resenas"


def render_page() -> str:
    title = "Reseñas y experiencias reales de productos para el coche | AutoCalc España"
    description = (
        "Guías para evaluar accesorios, cargadores eléctricos, neumáticos y herramientas "
        "de automóvil con criterios transparentes, pruebas reales y opiniones independientes."
    )
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{escape(CANONICAL, quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#0f172a">
<style>
:root{{color-scheme:light;--ink:#0f172a;--muted:#475569;--line:#dbe3ee;--blue:#155eef;--bg:#f8fafc}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
a{{color:var(--blue)}}.wrap{{width:min(1100px,calc(100% - 32px));margin:auto}}header{{background:#0f172a;color:white;padding:16px 0}}header a{{color:white;text-decoration:none;font-weight:700}}
.hero{{padding:58px 0 42px;background:linear-gradient(135deg,#eef4ff,#fff 70%);border-bottom:1px solid var(--line)}}.eyebrow{{font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;font-weight:800;color:#1d4ed8}}
h1{{font-size:clamp(2rem,5vw,3.5rem);line-height:1.08;letter-spacing:-.04em;max-width:850px;margin:.6rem 0 1rem}}h2{{line-height:1.2;letter-spacing:-.02em}}.lead{{font-size:1.12rem;color:#334155;max-width:760px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:16px;margin:24px 0 40px}}.card{{background:white;border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:0 4px 18px #0f172a08}}.card h3{{margin:.4rem 0;font-size:1.1rem}}.icon{{font-size:1.7rem}}.pill{{display:inline-block;border-radius:999px;background:#e2e8f0;padding:4px 10px;font-size:.75rem;font-weight:800;color:#334155}}
.notice{{background:white;border:1px solid #cbd5e1;border-left:4px solid #2563eb;border-radius:12px;padding:18px 20px;margin:26px 0}}.steps{{padding-left:1.3rem}}.steps li{{margin:.6rem 0}}footer{{margin-top:48px;background:#0f172a;color:#cbd5e1;padding:26px 0;font-size:.9rem}}footer a{{color:white}}.toplink{{display:inline-block;margin:14px 0}}@media(prefers-reduced-motion:no-preference){{a{{transition:color .15s}}}} 
</style>
</head>
<body>
<header><div class="wrap"><a href="{BASE}/">AutoCalc España</a><span style="float:right"><a href="{BASE}/">Volver a las herramientas</a></span></div></header>
<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">Decisiones con datos, no con publicidad</p>
<h1>Reseñas que ayudan a elegir mejor para tu coche</h1>
<p class="lead">Queremos reunir análisis transparentes de accesorios, cargadores, neumáticos y herramientas de automoción, distinguiendo siempre las pruebas realizadas por AutoCalc de las experiencias aportadas por conductores.</p>
<div class="notice" role="status"><strong>Estamos preparando la comunidad.</strong><br>Esta sección todavía no contiene reseñas publicadas ni valoraciones de usuarios. No mostramos puntuaciones ficticias. Publicaremos opiniones cuando existan datos y experiencias reales que podamos revisar.</div>
</div></section>
<section class="wrap" aria-labelledby="areas">
<h2 id="areas">Categorías que queremos cubrir</h2>
<div class="grid">
<article class="card"><div class="icon" aria-hidden="true">⚡</div><span class="pill">Movilidad eléctrica</span><h3>Cargadores y accesorios EV</h3><p>Potencia, conectores, protecciones, facilidad de uso, compatibilidad y coste de carga en España.</p></article>
<article class="card"><div class="icon" aria-hidden="true">🛞</div><span class="pill">Seguridad</span><h3>Neumáticos y baterías</h3><p>Uso previsto, medidas, duración observada, comportamiento y relación calidad-precio.</p></article>
<article class="card"><div class="icon" aria-hidden="true">🔧</div><span class="pill">Taller y diagnóstico</span><h3>Herramientas y OBD2</h3><p>Compatibilidad, funciones reales, límites, facilidad de uso y utilidad para cada conductor.</p></article>
<article class="card"><div class="icon" aria-hidden="true">🚗</div><span class="pill">Uso diario</span><h3>Accesorios para el coche</h3><p>Calidad de construcción, instalación, durabilidad y costes de mantenimiento.</p></article>
</div>
</section>
<section class="wrap" aria-labelledby="metodo">
<h2 id="metodo">Cómo evaluaremos los productos</h2>
<div class="card"><ol class="steps">
<li><strong>Transparencia:</strong> indicaremos si se trata de una prueba propia, una muestra gratuita o una opinión de usuario.</li>
<li><strong>Experiencia demostrable:</strong> no llamaremos «probado» a un producto que no se haya utilizado realmente.</li>
<li><strong>Pros, contras y contexto:</strong> explicaremos para quién puede ser útil y en qué situaciones no lo recomendaríamos.</li>
<li><strong>Independencia editorial:</strong> una colaboración comercial o un enlace de afiliación nunca garantizarán una valoración positiva.</li>
<li><strong>Moderación:</strong> cuando se habiliten aportaciones de usuarios, aplicaremos controles contra spam, conflictos de interés y datos personales expuestos.</li>
<li><strong>Actualización:</strong> identificaremos la fecha de revisión y corregiremos errores cuando haya información nueva verificable.</li>
</ol></div>
<p>Las puntuaciones agregadas solo se mostrarán cuando existan suficientes valoraciones válidas. No se marcarán opiniones como verificadas sin una comprobación real.</p>
<a class="toplink" href="{BASE}/">Explorar las calculadoras y guías de AutoCalc España →</a>
</section>
</main>
<footer><div class="wrap"><strong>AutoCalc España</strong><p>Contenido informativo e independiente. Comprueba siempre las especificaciones del fabricante y las condiciones aplicables a cada producto.</p><a href="{BASE}/privacidad-cookies.html">Privacidad y cookies</a> · <a href="{BASE}/aviso-legal.html">Aviso legal</a> · <a href="{BASE}/">Inicio</a></div></footer>
</body></html>'''


def update_sitemap() -> None:
    if not SITEMAP.is_file():
        raise FileNotFoundError(f"No se encuentra el sitemap generado: {SITEMAP}")
    tree = ET.parse(SITEMAP)
    root = tree.getroot()
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    locs = {node.text for node in root.findall(f".//{namespace}loc")}
    if CANONICAL not in locs:
        url = ET.SubElement(root, f"{namespace}url")
        ET.SubElement(url, f"{namespace}loc").text = CANONICAL
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    tree.write(SITEMAP, encoding="utf-8", xml_declaration=True)


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    (REVIEWS_DIR / "index.html").write_text(render_page(), encoding="utf-8")
    schema = {
        "schema_version": 1,
        "status": "editorial-hub-only",
        "notice": "No hay reseñas publicadas. No crear valoraciones ficticias.",
        "review_fields": [
            "id", "slug", "title", "product_name", "category", "author_display",
            "submitted_at", "published_at", "updated_at", "rating_overall",
            "rating_value", "pros", "cons", "usage_context", "vehicle_context",
            "tested_by_autocalc", "sample_provided", "affiliate_relationship",
            "evidence_urls", "moderation_status", "moderation_notes"
        ],
        "moderation_statuses": ["pending", "approved", "rejected", "needs_changes"],
        "rules": {
            "ratings_range": [1, 5],
            "only_approved_reviews_public": True,
            "never_infer_verified_purchase": True,
            "never_publish_private_contact_details": True,
            "disclose_free_samples_and_affiliate_links": True,
            "structured_data_only_for_visible_approved_reviews": True
        },
        "reviews": []
    }
    (REVIEWS_DIR / "reviews.json").write_text(
        json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    update_sitemap()
    print(f"[OK] Hub de reseñas generado: {REVIEWS_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
