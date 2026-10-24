#!/usr/bin/env python3
"""Build an evidence-led EV charging buying guide for AutoCalc España."""
from __future__ import annotations
import json
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
BASE = (f"https://{CFG.get('custom_domain', 'autocalc.es').strip().lower()}"
        if CFG.get("use_custom_domain") is True
        else str(CFG.get("github_pages_url") or CFG.get("domain", "")).rstrip("/"))
URL = f"{BASE}/guia-cargadores-electricos.html"
TITLE = "Cómo elegir un cargador para coche eléctrico en España: guía práctica"
DESCRIPTION = ("Guía independiente para elegir cargador de coche eléctrico: potencia, conectores, "
               "instalación, seguridad, carga doméstica y costes. Sin rankings ni pruebas inventadas.")
PAGE = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(TITLE)}</title>
<meta name="description" content="{escape(DESCRIPTION, quote=True)}">
<link rel="canonical" href="{escape(URL, quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#0f172a">
<meta property="og:type" content="article">
<meta property="og:title" content="{escape(TITLE, quote=True)}">
<meta property="og:description" content="{escape(DESCRIPTION, quote=True)}">
<meta property="og:url" content="{escape(URL, quote=True)}">
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"Article","headline":TITLE,"description":DESCRIPTION,"mainEntityOfPage":{"@type":"WebPage","@id":URL},"publisher":{"@type":"Organization","name":"AutoCalc España","url":BASE+"/"}},ensure_ascii=False,separators=(",",":"))}</script>
<style>
:root{{color-scheme:light;--ink:#0f172a;--muted:#475569;--line:#dbe3ee;--blue:#155eef;--bg:#f8fafc}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.7 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
a{{color:#1749b8}}a:focus-visible,button:focus-visible{{outline:3px solid #f59e0b;outline-offset:3px}}
.wrap{{width:min(1000px,calc(100% - 32px));margin:auto}}header{{background:#0f172a;color:white;padding:16px 0}}header a{{color:white;text-decoration:none;font-weight:700}}
.hero{{padding:54px 0 36px;background:linear-gradient(135deg,#e8f1ff,#fff 72%);border-bottom:1px solid var(--line)}}.eyebrow{{font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;font-weight:800;color:#1d4ed8}}
h1{{font-size:clamp(2rem,5vw,3.2rem);line-height:1.1;letter-spacing:-.04em;max-width:850px;margin:.6rem 0 1rem}}h2{{line-height:1.25;letter-spacing:-.02em;margin-top:2rem}}h3{{line-height:1.3}}.lead{{font-size:1.12rem;color:#334155;max-width:800px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:16px;margin:22px 0}}.card{{background:white;border:1px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 4px 18px #0f172a08}}
.note{{background:#fff;border:1px solid #cbd5e1;border-left:4px solid #2563eb;border-radius:12px;padding:16px 18px;margin:22px 0}}.check{{padding-left:1.3rem}}.check li{{margin:.55rem 0}}table{{width:100%;border-collapse:collapse;background:#fff;margin:16px 0}}th,td{{text-align:left;padding:12px;border:1px solid var(--line);vertical-align:top}}th{{background:#edf2f8}}.table-wrap{{overflow-x:auto;border-radius:12px}}.cta{{display:inline-block;background:#0f172a;color:white;padding:12px 16px;border-radius:10px;text-decoration:none;font-weight:700;margin:8px 8px 0 0}}footer{{margin-top:46px;background:#0f172a;color:#cbd5e1;padding:26px 0;font-size:.9rem}}footer a{{color:white}}
@media(prefers-reduced-motion:no-preference){{a{{transition:color .15s}}}}
</style>
</head>
<body>
<header><div class="wrap"><a href="{BASE}/">AutoCalc España</a><span style="float:right"><a href="{BASE}/carga-vehiculo-electrico.html">Calculadora de carga</a></span></div></header>
<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">Guía de compra · movilidad eléctrica</p>
<h1>Cómo elegir un cargador para tu coche eléctrico</h1>
<p class="lead">La mejor elección depende del vehículo, la instalación disponible, la potencia que puedes aprovechar y cómo cargas a diario. Esta guía prioriza la seguridad y la compatibilidad antes que la marca o el precio.</p>
<div class="note"><strong>Transparencia editorial:</strong> esta guía explica criterios generales de selección. No es una prueba práctica de un modelo concreto ni una clasificación comercial. Actualizaremos las recomendaciones específicas cuando dispongamos de pruebas verificables.</div>
<a class="cta" href="{BASE}/carga-vehiculo-electrico.html">Calcular tiempo y coste de carga</a>
<a class="cta" href="{BASE}/resenas/">Criterios de reseñas</a>
</div></section>
<section class="wrap">
<h2>1. Qué tipo de solución necesitas</h2>
<div class="grid">
<article class="card"><h3>Cargador portátil compatible</h3><p>Puede resultar útil si necesitas flexibilidad o cargar en distintos lugares. Comprueba el conector del vehículo, el tipo de toma, la corriente admisible y las protecciones requeridas. No des por segura una toma doméstica antigua o deteriorada.</p></article>
<article class="card"><h3>Wallbox doméstico</h3><p>Es una solución fija habitual para cargar regularmente en una plaza privada. La potencia útil depende del cargador embarcado del coche, la instalación, la potencia contratada y la gestión de cargas.</p></article>
<article class="card"><h3>Carga pública</h3><p>Puede cubrir necesidades ocasionales o viajes. Verifica conector, potencia disponible, precio por kWh, posibles tarifas por tiempo y condiciones de acceso antes de iniciar la sesión.</p></article>
</div>
<h2>2. Lista de comprobación antes de comprar</h2>
<div class="card"><ol class="check">
<li><strong>Compatibilidad:</strong> confirma en el manual del vehículo el conector AC, la potencia máxima en corriente alterna y cualquier limitación de carga.</li>
<li><strong>Instalación:</strong> pide a un instalador electricista cualificado que compruebe circuito, protecciones, toma de tierra, sección del cable y requisitos aplicables. Una guía web no puede certificar una instalación.</li>
<li><strong>Potencia real:</strong> la potencia anunciada por el equipo no garantiza que el coche la acepte ni que la instalación pueda suministrarla.</li>
<li><strong>Uso exterior:</strong> si se instalará al aire libre, revisa las condiciones de uso, resistencia ambiental, almacenamiento y protección indicadas por el fabricante.</li>
<li><strong>Control térmico y protecciones:</strong> lee la documentación técnica y las instrucciones. No uses adaptadores, alargadores o enchufes múltiples salvo que el fabricante y un profesional confirmen expresamente que son adecuados.</li>
<li><strong>Garantía y servicio:</strong> revisa duración y cobertura, asistencia, política de devolución, disponibilidad de repuestos y quién responde en España.</li>
<li><strong>Coste total:</strong> suma equipo, instalación, posibles adecuaciones eléctricas, tarifa de energía y servicios adicionales; no compares solo el precio inicial.</li>
</ol></div>
<h2>3. Potencia: no siempre más es mejor</h2>
<p>La carga en AC está limitada por el menor de los límites relevantes: equipo de carga, capacidad AC del vehículo e instalación. En condiciones reales también pueden influir la temperatura, el estado de la batería y la gestión de potencia. Para una estimación inicial, usa nuestra <a href="{BASE}/carga-vehiculo-electrico.html">calculadora de tiempo y coste de carga</a>; el resultado no sustituye los datos del fabricante ni una evaluación eléctrica.</p>
<div class="table-wrap"><table><thead><tr><th>Potencia nominal orientativa</th><th>Qué comprobar</th><th>Antes de decidir</th></tr></thead><tbody>
<tr><td>2,3 kW</td><td>Admisibilidad de la toma y del circuito, corriente continua y estado de la instalación.</td><td>Puede ser lenta; no implica que cualquier enchufe doméstico sea adecuado para carga prolongada.</td></tr>
<tr><td>3,7–7,4 kW</td><td>Capacidad monofásica del vehículo, protecciones y potencia disponible en la vivienda.</td><td>Comprueba si necesitas balanceo dinámico o ajustar otros consumos.</td></tr>
<tr><td>11–22 kW</td><td>Capacidad trifásica del vehículo y suministro, además de requisitos del equipo.</td><td>El vehículo podría aceptar menos potencia y no aprovechar el máximo anunciado.</td></tr>
</tbody></table></div>
<h2>4. Cómo comparar modelos de forma justa</h2>
<div class="grid">
<article class="card"><h3>Datos técnicos verificables</h3><p>Modelo exacto, potencia, conectores, longitud del cable, protecciones, condiciones ambientales, certificaciones declaradas y manual disponible.</p></article>
<article class="card"><h3>Prueba práctica</h3><p>Una reseña propia debe describir qué se probó, durante cuánto tiempo, con qué vehículo e instalación y qué limitaciones tuvo. No presentaremos como probado un producto que solo hemos consultado en una ficha comercial.</p></article>
<article class="card"><h3>Precio y soporte</h3><p>Compara precio final, envío, instalación si procede, garantía, devoluciones y atención posventa. Una comisión de afiliación no determina la valoración editorial.</p></article>
</div>
<h2>5. Seguridad y normativa</h2>
<p>La instalación y el uso deben ajustarse a la normativa vigente y a las instrucciones del fabricante. En España, las instalaciones de recarga pueden estar sujetas a requisitos del Reglamento electrotécnico para baja tensión y de la ITC-BT-52, según el caso. Consulta a un profesional cualificado y las fuentes oficiales antes de ejecutar una instalación.</p>
<p>Fuentes oficiales de referencia: <a href="https://www.boe.es/buscar/act.php?id=BOE-A-2002-18099" target="_blank" rel="noopener noreferrer">Reglamento electrotécnico para baja tensión (BOE)</a> y <a href="https://industria.gob.es/Calidad-Industrial/seguridadindustrial/instalacionesindustriales/baja-tension/Paginas/reglamento-electrotecnico.aspx" target="_blank" rel="noopener noreferrer">información sobre baja tensión del Ministerio de Industria</a>. Comprueba siempre la versión y las disposiciones aplicables a tu instalación.</p>
<div class="note"><strong>Publicidad y afiliación:</strong> AutoCalc España puede incorporar enlaces comerciales cuando un programa esté aprobado y sus enlaces de seguimiento hayan sido verificados. Si un enlace genera comisión, lo identificaremos claramente. La disponibilidad de una colaboración no implica una recomendación positiva ni sustituye una prueba independiente.</div>
<h2>Preguntas frecuentes</h2>
<details class="card"><summary><strong>¿Puedo cargar siempre en un enchufe doméstico?</strong></summary><p>No debe asumirse. La toma, el circuito, las protecciones y el uso prolongado deben ser adecuados y verificados por un profesional; sigue las instrucciones del fabricante.</p></details>
<details class="card"><summary><strong>¿Un cargador de 22 kW cargará mi coche a 22 kW?</strong></summary><p>No necesariamente. La potencia real depende, entre otros factores, de la capacidad de carga AC del vehículo y de la instalación.</p></details>
<details class="card"><summary><strong>¿Qué es más importante: potencia o seguridad?</strong></summary><p>La compatibilidad y la seguridad de la instalación son requisitos previos. Después, compara potencia útil, facilidad de uso, garantía, soporte y coste total.</p></details>
<p><a class="cta" href="{BASE}/carga-vehiculo-electrico.html">Abrir calculadora de carga</a><a class="cta" href="{BASE}/">Volver a todas las herramientas</a></p>
</section>
</main>
<footer><div class="wrap"><strong>AutoCalc España</strong><p>Información general; no sustituye el manual del vehículo, la documentación del fabricante ni el asesoramiento de un instalador cualificado.</p><a href="{BASE}/privacidad-cookies.html">Privacidad y cookies</a> · <a href="{BASE}/aviso-legal.html">Aviso legal</a></div></footer>
</body></html>'''

def update_sitemap() -> None:
    path = PUBLIC / "sitemap.xml"
    tree = ET.parse(path)
    root = tree.getroot()
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    locs = {e.text for e in root.findall(f".//{ns}loc")}
    if URL not in locs:
        entry = ET.SubElement(root, f"{ns}url")
        ET.SubElement(entry, f"{ns}loc").text = URL
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    tree.write(path, encoding="utf-8", xml_declaration=True)

def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "guia-cargadores-electricos.html").write_text(PAGE, encoding="utf-8")
    update_sitemap()
    print(f"[OK] Guía de cargadores generada: {URL}")

if __name__ == "__main__":
    main()
