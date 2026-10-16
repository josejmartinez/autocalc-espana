#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor generador estático AutoCalc España v5.0 (Edición completa estilo dieselogasolina.com)
Incluye:
1. ITV Neumáticos (±3 %) + Calculadora de ET (offset) y separadores + Tablas de índices de carga/velocidad.
2. Coste de viaje con peajes/desgaste + Calculadora de consumo real L/100km + Buscador de gasolineras en vivo (API Ministerio).
3. Comparador TCO (Gasolina vs. Diésel vs. Híbrido vs. GLP) con impuestos y mantenimiento.
4. Datador de matrículas españolas (mes/año y edad) + Calculadora oficial BOE de caballos fiscales (CVF), IVTM, ITP y CO2.
5. Checklist pre-ITV de 12 puntos + Buscador interactivo de códigos de avería OBD2 + Plan de mantenimiento.
6. Calculadora ¿Desguace, Autodoc o taller? con 20 piezas reales preconfiguradas y directorio de desguaces.
"""

import os
import json
import re
from html import escape
from datetime import date
from catalogo import MEDIDAS_ESPANA, MODELOS_COCHES, RUTAS_ESPANA, ZONAS_DESGUACES_ITV, GARGANTA_POR_ANCHO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "public")

with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
    CFG = json.load(f)

GITHUB_PAGES_URL = CFG.get("github_pages_url", CFG.get("domain", "")).strip().rstrip("/")
CUSTOM_DOMAIN = CFG.get("custom_domain", "autocalc.es").strip().lower().rstrip(".")
USE_CUSTOM_DOMAIN = CFG.get("use_custom_domain", False) is True

if not GITHUB_PAGES_URL.startswith("https://"):
    raise ValueError("La URL de GitHub Pages debe ser HTTPS.")
if USE_CUSTOM_DOMAIN:
    if not re.fullmatch(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", CUSTOM_DOMAIN):
        raise ValueError("custom_domain debe ser un nombre DNS válido, sin protocolo ni rutas.")
    DOMINIO = f"https://{CUSTOM_DOMAIN}"
else:
    DOMINIO = GITHUB_PAGES_URL

AMAZON_TAG = CFG["amazon_tag"]
SITE_NAME = CFG["site_name"]
EMAIL_CONTACTO = CFG["contact_email"]
ADSENSE_CLIENT = CFG.get("adsense_client", "").strip()
GOOGLE_ANALYTICS_ID = CFG.get("google_analytics_id", "").strip()
GOOGLE_CERTIFIED_CMP_CONFIGURED = CFG.get("google_certified_cmp_configured", False) is True
GOOGLE_SITE_VERIFICATION = CFG.get("google_site_verification", "").strip()
GOOGLE_SITE_VERIFICATION_TAG = (
    f'<meta name="google-site-verification" content="{escape(GOOGLE_SITE_VERIFICATION, quote=True)}" />'
    if GOOGLE_SITE_VERIFICATION else ""
)

if ADSENSE_CLIENT:
    if not GOOGLE_CERTIFIED_CMP_CONFIGURED:
        raise RuntimeError(
            "AdSense no se puede activar hasta integrar y verificar una CMP certificada de Google "
            "compatible con el TCF para el tráfico del EEE/Reino Unido/Suiza."
        )
    if not (ADSENSE_CLIENT.startswith("ca-pub-") and ADSENSE_CLIENT[7:].isdigit()):
        raise ValueError("adsense_client debe tener el formato ca-pub- seguido del identificador numérico.")

ANCHOS_COMUNES = sorted(list(GARGANTA_POR_ANCHO.keys()))
PERFILES_COMUNES = [35, 40, 45, 50, 55, 60, 65, 70, 75]


def calcular_diametro(ancho, perfil, llanta):
    return (2.0 * ancho * (perfil / 100.0)) + (llanta * 25.4)


def generar_tabla_equivalencias_html(a_orig, p_orig, l_orig):
    d_orig = calcular_diametro(a_orig, p_orig, l_orig)
    filas = []

    for llanta in range(max(13, l_orig - 1), min(22, l_orig + 3)):
        for ancho in ANCHOS_COMUNES:
            if abs(ancho - a_orig) > 40:
                continue
            for perfil in PERFILES_COMUNES:
                if ancho == a_orig and perfil == p_orig and llanta == l_orig:
                    continue
                d_cand = calcular_diametro(ancho, perfil, llanta)
                diff_pct = ((d_cand - d_orig) / d_orig) * 100.0
                if abs(diff_pct) <= 3.0:
                    delta_alt = (d_cand - d_orig) / 2.0
                    garganta = GARGANTA_POR_ANCHO.get(ancho, '6.0" - 8.0"')
                    badge = "bg-emerald-100 text-emerald-800" if abs(diff_pct) <= 1.5 else "bg-amber-100 text-amber-800"
                    s_pct = "+" if diff_pct > 0 else ""
                    s_alt = "+" if delta_alt > 0 else ""

                    url_mucho = f"https://www.muchoneumatico.com/buscar?controller=search&s={ancho}+{perfil}+{llanta}"
                    url_norauto = f"https://www.norauto.es/c/47595-neumaticos.html?q={ancho}%2F{perfil}R{llanta}"
                    url_amz = f"https://www.amazon.es/s?k=neumaticos+{ancho}+{perfil}+R{llanta}&tag={AMAZON_TAG}"

                    fila_html = f"""
                    <tr class="border-b border-slate-100 hover:bg-slate-50 transition">
                        <td class="py-2.5 px-3 font-bold text-slate-900">
                            <button onclick="cargarMedidaCandidata({ancho},{perfil},{llanta})" class="text-left hover:text-amber-600 underline decoration-dotted" title="Simular esta medida arriba">
                                {ancho}/{perfil} R{llanta}
                            </button>
                        </td>
                        <td class="py-2.5 px-3 text-center text-xs text-slate-600">{garganta}</td>
                        <td class="py-2.5 px-3 text-center">{d_cand:.1f} mm</td>
                        <td class="py-2.5 px-3 text-center">
                            <span class="px-2 py-0.5 rounded-full text-xs font-semibold {badge}">{s_pct}{diff_pct:.2f} %</span>
                        </td>
                        <td class="py-2.5 px-3 text-center text-slate-600">{s_alt}{delta_alt:.1f} mm</td>
                        <td class="py-2.5 px-3 text-right">
                            <div class="flex flex-wrap justify-end gap-1">
                                <a href="{url_mucho}" target="_blank" rel="nofollow sponsored" class="text-[11px] bg-sky-600 hover:bg-sky-700 text-white font-semibold px-2 py-1 rounded transition">Muchoneumático</a>
                                <a href="{url_norauto}" target="_blank" rel="nofollow sponsored" class="text-[11px] bg-blue-900 hover:bg-blue-950 text-white font-semibold px-2 py-1 rounded transition">Norauto</a>
                                <a href="{url_amz}" target="_blank" rel="nofollow sponsored" class="text-[11px] bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold px-2 py-1 rounded transition">Amazon</a>
                            </div>
                        </td>
                    </tr>"""
                    filas.append((abs(diff_pct), fila_html))

    filas.sort(key=lambda x: x[0])
    filas_top = "".join([f[1] for f in filas[:20]])

    return f"""
    <div class="mt-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 overflow-x-auto">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
            <div>
                <h2 class="text-lg font-bold text-slate-900">Medidas candidatas por diámetro para {a_orig}/{p_orig} R{l_orig} (±3 % orientativo)</h2>
                <p class="text-xs text-slate-500">Diámetro de referencia: <strong>{d_orig:.1f} mm</strong> · Intervalo matemático ±3 %: <strong>{d_orig*0.97:.1f} mm a {d_orig*1.03:.1f} mm</strong>. Este cálculo compara solo el diámetro exterior: no acredita homologación ni validez para ITV. Verifica ficha técnica, índice de carga, código de velocidad y compatibilidad.</p>
            </div>
            <span class="text-xs bg-amber-50 text-amber-800 border border-amber-200 px-3 py-1 rounded-full font-semibold w-fit">Verificar ficha técnica</span>
        </div>
        <table class="w-full text-left text-sm">
            <thead>
                <tr class="border-b-2 border-slate-200 text-xs text-slate-500">
                    <th class="py-2 px-3 font-semibold">Medida equivalente</th>
                    <th class="py-2 px-3 text-center font-semibold">Ancho de llanta</th>
                    <th class="py-2 px-3 text-center font-semibold">Diámetro</th>
                    <th class="py-2 px-3 text-center font-semibold">Variación diámetro</th>
                    <th class="py-2 px-3 text-center font-semibold">Altura chasis</th>
                    <th class="py-2 px-3 text-right font-semibold">Comparar precios por tienda</th>
                </tr>
            </thead>
            <tbody>{filas_top}</tbody>
        </table>
    </div>
    """


PLANTILLA_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
    <!-- Google Analytics se carga únicamente después de aceptar analítica. -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__PAGE_TITLE__</title>
    <meta name="description" content="__META_DESC__">
    <meta property="og:title" content="__PAGE_TITLE__">
    <meta property="og:description" content="__META_DESC__">
    <meta property="og:url" content="__CANONICAL_URL__">
    <meta property="og:type" content="website">
    <link rel="canonical" href="__CANONICAL_URL__">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <meta name="robots" content="__ROBOTS_META__">
    __GOOGLE_SITE_VERIFICATION_TAG__
    <link rel="preconnect" href="https://www.amazon.es">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {
            .no-print { display: none !important; }
            body { background: #fff !important; }
        }
    </style>
    __ADSENSE_HEAD__
    <script type="application/ld+json">
    __SCHEMA_JSON__
    </script>
</head>
<body class="bg-slate-50 text-slate-800 font-sans min-h-screen flex flex-col">

    <header class="bg-slate-900 text-white py-4 shadow-md sticky top-0 z-30 no-print">
        <div class="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-3">
            <div class="flex items-center gap-3">
                <a href="index.html" class="hover:opacity-90 transition flex items-center gap-2">
                    <span class="text-2xl font-extrabold tracking-tight text-amber-400">__SITE_NAME__</span>
                    <span class="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">Portal técnico del motor</span>
                </a>
            </div>
            <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto justify-end">
                <a href="desguaces-itv-aranjuez-comarca-las-vegas.html" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-2 rounded-lg border border-slate-700 transition">Desguaces y talleres</a>
                <a href="mapa-web.html" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-2 rounded-lg border border-slate-700 transition">Buscador (116 guías)</a>
                <button onclick="copiarEnlaceCalculo()" id="btn-compartir" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-2 rounded-lg border border-slate-700 transition">Copiar enlace</button>
                <button onclick="window.print()" class="bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs px-3 py-2 rounded-lg transition">Guardar PDF</button>
            </div>
        </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 py-6 flex-grow w-full">

        <div class="mb-6">
            <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900">__H1_TITLE__</h1>
            <p class="text-sm text-slate-600 mt-1">__HERO_SUBTITLE__</p>
        </div>

        <!-- Selector de las 6 suites de herramientas -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 mb-6 bg-slate-200 p-1.5 rounded-xl no-print">
            <button onclick="cambiarTab('itv')" id="tab-itv" class="py-2.5 px-2 rounded-lg font-semibold text-xs bg-white text-slate-900 shadow-sm transition">
                1. Neumáticos y ET
            </button>
            <button onclick="cambiarTab('consumo')" id="tab-consumo" class="py-2.5 px-2 rounded-lg font-semibold text-xs text-slate-600 hover:text-slate-900 transition">
                2. Viajes y gasolineras
            </button>
            <button onclick="cambiarTab('amortizacion')" id="tab-amortizacion" class="py-2.5 px-2 rounded-lg font-semibold text-xs text-slate-600 hover:text-slate-900 transition">
                3. ¿Diésel, híbrido o GLP?
            </button>
            <button onclick="cambiarTab('dgt')" id="tab-dgt" class="py-2.5 px-2 rounded-lg font-semibold text-xs text-slate-600 hover:text-slate-900 transition">
                4. Matrículas, CVF y DGT
            </button>
            <button onclick="cambiarTab('preitv')" id="tab-preitv" class="py-2.5 px-2 rounded-lg font-semibold text-xs text-slate-600 hover:text-slate-900 transition">
                5. Pre-ITV y fallos OBD2
            </button>
            <button onclick="cambiarTab('desguace')" id="tab-desguace" class="py-2.5 px-2 rounded-lg font-semibold text-xs text-slate-600 hover:text-slate-900 transition">
                6. ¿Desguace o nuevo?
            </button>
        </div>

        <!-- ==================== SECCIÓN 1: NEUMÁTICOS, EQUIVALENCIAS ITV Y OFFSET ET ==================== -->
        <section id="sec-itv" class="space-y-6">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-5 pb-4 border-b border-slate-100 no-print">
                    <label for="preset-coche" class="text-xs font-semibold text-slate-600">Autocompletar medida de serie por vehículo:</label>
                    <select id="preset-coche" onchange="aplicarPresetCoche()" class="p-2 border rounded-lg text-xs bg-slate-50 font-medium text-slate-800 w-full sm:w-80">
                        <option value="">— Seleccionar modelo rápido —</option>
                        <option value="205,55,16,225,45,17">Seat León / VW Golf / Toyota Corolla (205/55 R16)</option>
                        <option value="225,45,17,225,40,18">Seat León FR / Golf GTI / Audi A3 (225/45 R17)</option>
                        <option value="195,65,15,205,55,16">Seat León I-II / Skoda Octavia / Golf IV (195/65 R15)</option>
                        <option value="185,65,15,195,60,15">Dacia Sandero / Renault Clio / Nissan Primera (185/65 R15)</option>
                        <option value="175,65,14,185,60,14">Opel Corsa C / Ford Fiesta / Peugeot 206 (175/65 R14)</option>
                        <option value="215,60,17,225,55,17">Nissan Qashqai / Dacia Duster (215/60 R17)</option>
                        <option value="235,55,18,245,50,18">VW Tiguan / Kia Sportage / Toyota RAV4 (235/55 R18)</option>
                        <option value="205,65,16,215,60,16">VW Transporter / Mercedes Vito / Trafic (205/65 R16)</option>
                    </select>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-slate-50 p-4 rounded-xl border border-slate-200">
                        <h2 class="font-bold text-xs text-slate-700 mb-3">1A. Neumático original (en ficha técnica ITV)</h2>
                        <div class="grid grid-cols-3 gap-3 mb-3">
                            <div>
                                <label class="block text-xs text-slate-500 mb-1">Ancho (mm)</label>
                                <input type="number" id="ancho1" value="__VAL_A1__" oninput="calcularITV()" class="w-full p-2 border rounded-lg text-center font-bold text-slate-900">
                            </div>
                            <div>
                                <label class="block text-xs text-slate-500 mb-1">Perfil (%)</label>
                                <input type="number" id="perfil1" value="__VAL_P1__" oninput="calcularITV()" class="w-full p-2 border rounded-lg text-center font-bold text-slate-900">
                            </div>
                            <div>
                                <label class="block text-xs text-slate-500 mb-1">Llanta (pulg.)</label>
                                <input type="number" id="llanta1" value="__VAL_L1__" oninput="calcularITV()" class="w-full p-2 border rounded-lg text-center font-bold text-slate-900">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-3 pt-2 border-t border-slate-200/80">
                            <div>
                                <label class="block text-xs text-slate-500 mb-1">Índice de carga</label>
                                <input type="number" id="carga1" value="91" min="60" max="125" oninput="calcularITV()" class="w-full p-1.5 border rounded-lg text-center text-xs font-semibold">
                            </div>
                            <div>
                                <label class="block text-xs text-slate-500 mb-1">Cód. velocidad</label>
                                <select id="vel1" onchange="calcularITV()" class="w-full p-1.5 border rounded-lg text-center text-xs font-semibold bg-white">
                                    <option value="160">Q (160 km/h)</option>
                                    <option value="170">R (170 km/h)</option>
                                    <option value="180">S (180 km/h)</option>
                                    <option value="190">T (190 km/h)</option>
                                    <option value="210">H (210 km/h)</option>
                                    <option value="240" selected>V (240 km/h)</option>
                                    <option value="270">W (270 km/h)</option>
                                    <option value="300">Y (300 km/h)</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="bg-slate-50 p-4 rounded-xl border border-slate-200">
                        <h2 class="font-bold text-xs text-slate-700 mb-3">Neumático nuevo a comprobar</h2>
                        <div class="grid grid-cols-3 gap-3 mb-3">
                            <div>
                                <label class="block text-xs text-slate-500 mb-1">Ancho (mm)</label>
                                <input type="number" id="ancho2" value="__VAL_A2__" oninput="calcularITV()" class="w-full p-2 border rounded-lg text-center font-bold text-slate-900">
                            </div>
                            <div>
                                <label class="block text-xs text-slate-500 mb-1">Perfil (%)</label>
                                <input type="number" id="perfil2" value="__VAL_P2__" oninput="calcularITV()" class="w-full p-2 border rounded-lg text-center font-bold text-slate-900">
                            </div>
                            <div>
                                <label class="block text-xs text-slate-500 mb-1">Llanta (pulg.)</label>
                                <input type="number" id="llanta2" value="__VAL_L2__" oninput="calcularITV()" class="w-full p-2 border rounded-lg text-center font-bold text-slate-900">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-3 pt-2 border-t border-slate-200/80">
                            <div>
                                <label class="block text-xs text-slate-500 mb-1">Índice de carga</label>
                                <input type="number" id="carga2" value="91" min="60" max="125" oninput="calcularITV()" class="w-full p-1.5 border rounded-lg text-center text-xs font-semibold">
                            </div>
                            <div>
                                <label class="block text-xs text-slate-500 mb-1">Cód. velocidad</label>
                                <select id="vel2" onchange="calcularITV()" class="w-full p-1.5 border rounded-lg text-center text-xs font-semibold bg-white">
                                    <option value="160">Q (160 km/h)</option>
                                    <option value="170">R (170 km/h)</option>
                                    <option value="180">S (180 km/h)</option>
                                    <option value="190">T (190 km/h)</option>
                                    <option value="210">H (210 km/h)</option>
                                    <option value="240">V (240 km/h)</option>
                                    <option value="270" selected>W (270 km/h)</option>
                                    <option value="300">Y (300 km/h)</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                <div id="res-itv" class="mt-6 p-5 rounded-xl border"></div>

                <div class="mt-6 bg-slate-50 p-4 rounded-xl border border-slate-200">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="text-xs font-bold text-slate-700">Comparación visual a escala (diámetro lateral y huella de pisada)</h3>
                        <div class="flex gap-4 text-xs">
                            <span class="flex items-center gap-1"><span class="w-3 h-3 inline-block rounded-full bg-slate-700"></span> Original</span>
                            <span class="flex items-center gap-1"><span class="w-3 h-3 inline-block rounded-full bg-amber-500"></span> Nueva medida</span>
                        </div>
                    </div>
                    <div id="svg-comparador" class="w-full flex justify-center py-2"></div>
                </div>
            </div>

            <!-- 1B. Calculadora de ET (Offset) de llanta, ancho de vías y separadores -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold text-slate-900 mb-1">1B. Calculadora de desplazamiento de llanta (ET / Offset) y ancho de vías ITV</h2>
                <p class="text-xs text-slate-500 mb-4">Comprueba si tus nuevas llantas o separadores rozarán con el amortiguador interior o si superan el límite legal de ancho de vías en la ITV (±30 mm totales en turismos).</p>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-xs text-slate-600 mb-1">Ancho llanta orig. (pulg.)</label>
                        <input type="number" step="0.5" id="et-j1" value="6.5" oninput="calcularET()" class="w-full p-2 border rounded-lg font-bold text-center">
                    </div>
                    <div>
                        <label class="block text-xs text-slate-600 mb-1">ET original (mm)</label>
                        <input type="number" id="et-off1" value="45" oninput="calcularET()" class="w-full p-2 border rounded-lg font-bold text-center">
                    </div>
                    <div>
                        <label class="block text-xs text-slate-600 mb-1">Ancho llanta nueva (pulg.)</label>
                        <input type="number" step="0.5" id="et-j2" value="7.5" oninput="calcularET()" class="w-full p-2 border rounded-lg font-bold text-center">
                    </div>
                    <div>
                        <label class="block text-xs text-slate-600 mb-1">ET nuevo (mm)</label>
                        <input type="number" id="et-off2" value="35" oninput="calcularET()" class="w-full p-2 border rounded-lg font-bold text-center">
                    </div>
                </div>
                <div id="res-et" class="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200"></div>
            </div>

            <!-- 1C. Tablas de referencia de índice de carga y velocidad -->
            <details class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 text-xs">
                <summary class="font-bold text-sm text-slate-900 cursor-pointer">Ver tablas oficiales de índices de carga (kg) y códigos de velocidad ITV</summary>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4 pt-4 border-t border-slate-100">
                    <div>
                        <h4 class="font-bold text-slate-800 mb-2">Equivalencia de índices de carga más comunes</h4>
                        <div class="grid grid-cols-3 gap-1.5 text-slate-600">
                            <div class="p-1.5 bg-slate-50 rounded"><strong>75:</strong> 387 kg</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>82:</strong> 475 kg</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>84:</strong> 500 kg</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>86:</strong> 530 kg</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>88:</strong> 560 kg</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>91:</strong> 615 kg</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>92:</strong> 630 kg</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>94:</strong> 670 kg</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>95:</strong> 690 kg</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>97:</strong> 730 kg</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>99:</strong> 775 kg</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>103:</strong> 875 kg</div>
                        </div>
                    </div>
                    <div>
                        <h4 class="font-bold text-slate-800 mb-2">Códigos de velocidad máxima</h4>
                        <div class="grid grid-cols-3 gap-1.5 text-slate-600">
                            <div class="p-1.5 bg-slate-50 rounded"><strong>Q:</strong> 160 km/h</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>R:</strong> 170 km/h</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>S:</strong> 180 km/h</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>T:</strong> 190 km/h</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>H:</strong> 210 km/h</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>V:</strong> 240 km/h</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>W:</strong> 270 km/h</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>Y:</strong> 300 km/h</div>
                            <div class="p-1.5 bg-slate-50 rounded"><strong>ZR:</strong> >240 km/h</div>
                        </div>
                    </div>
                </div>
            </details>
        </section>

        <!-- ==================== SECCIÓN 2: VIAJES, CONSUMO REAL L/100KM Y GASOLINERAS EN VIVO ==================== -->
        <section id="sec-consumo" class="space-y-6 hidden">
            <!-- 2A. Coste de viaje completo (con peajes, desgaste y tiempo) -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold mb-1 text-slate-900">2A. Calculadora de coste de viaje, peajes, desgaste y tiempo</h2>
                <p class="text-xs text-slate-500 mb-4">Calcula el gasto exacto de carburante, el coste real incluyendo desgaste mecánico (neumáticos, frenos y aceite: ~0,06 €/km) y cuánto paga cada pasajero.</p>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Distancia (km)</label>
                        <input type="number" id="km-viaje" value="__VAL_KM__" oninput="calcularConsumo()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Consumo (L/100)</label>
                        <input type="number" step="0.1" id="litros-100" value="__VAL_L100__" oninput="calcularConsumo()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Precio (€/L)</label>
                        <input type="number" step="0.01" id="precio-litro" value="1.56" oninput="calcularConsumo()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Peajes (€)</label>
                        <input type="number" step="0.5" id="peajes-viaje" value="0" oninput="calcularConsumo()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Vel. media (km/h)</label>
                        <input type="number" id="vel-viaje" value="105" oninput="calcularConsumo()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Ocupantes</label>
                        <input type="number" id="ocupantes" value="2" min="1" oninput="calcularConsumo()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                </div>
                <div id="res-consumo" class="mt-5 p-4 rounded-xl bg-slate-50 border border-slate-200"></div>
            </div>

            <!-- 2B. Calculadora inversa: averigua el consumo real de tu coche (L/100 km) -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold mb-1 text-slate-900">2B. Calculadora de consumo real de tu coche (depósito lleno)</h2>
                <p class="text-xs text-slate-500 mb-4">El ordenador de a bordo suele mentir entre un 5 % y un 10 %. Llena el depósito, pon el cuentakilómetros parcial a cero y, en el siguiente repostaje, introduce los litros que han entrado y los kilómetros recorridos:</p>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Litros repostados (L)</label>
                        <input type="number" step="0.1" id="real-litros" value="42.5" oninput="calcularConsumoReal()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Kilómetros recorridos (km)</label>
                        <input type="number" id="real-km" value="740" oninput="calcularConsumoReal()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Precio pagado (€/L)</label>
                        <input type="number" step="0.01" id="real-precio" value="1.56" oninput="calcularConsumoReal()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                </div>
                <div id="res-consumo-real" class="mt-4 p-4 rounded-xl bg-emerald-50 border border-emerald-200"></div>
            </div>

            <!-- 2C. Buscador en tiempo real de gasolineras baratas (API Oficial Ministerio) + Ahorro Low-Cost -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                    <div>
                        <h2 class="text-lg font-bold text-slate-900">2C. Precio de gasolineras hoy en tiempo real (datos oficiales del Ministerio)</h2>
                        <p class="text-xs text-slate-500">Consulta las estaciones más económicas de tu municipio hoy mismo y comprueba cuánto ahorras por depósito.</p>
                    </div>
                    <div class="flex gap-2">
                        <select id="municipio-gas" onchange="cargarGasolinerasMunicipio()" class="p-2 border rounded-xl text-xs font-bold bg-slate-50">
                            <option value="4281" selected>Aranjuez (Madrid)</option>
                            <option value="4313">Ciempozuelos (Madrid)</option>
                            <option value="4448">Valdemoro (Madrid)</option>
                            <option value="4392">Pinto (Madrid)</option>
                            <option value="4418">San Martín de la Vega (Madrid)</option>
                            <option value="4334">Getafe (Madrid)</option>
                            <option value="4386">Parla (Madrid)</option>
                            <option value="6862">Ocaña (Toledo)</option>
                            <option value="6902">Seseña (Toledo)</option>
                            <option value="6828">Illescas (Toledo)</option>
                            <option value="6912">Toledo capital</option>
                            <option value="4354">Madrid capital</option>
                            <option value="881">Barcelona</option>
                            <option value="7247">Valencia</option>
                            <option value="6152">Sevilla</option>
                            <option value="8116">Zaragoza</option>
                            <option value="4540">Málaga</option>
                        </select>
                        <button onclick="cargarGasolinerasMunicipio()" class="bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs px-3 py-2 rounded-xl transition">Actualizar</button>
                    </div>
                </div>
                <div id="contenedor-gasolineras" class="text-xs text-slate-600">
                    Pulsa en «Actualizar» o cambia de municipio para consultar los precios oficiales de hoy...
                </div>
            </div>
        </section>

        <!-- ==================== SECCIÓN 3: COMPARADOR TOTAL (GASOLINA VS DIÉSEL VS HÍBRIDO VS GLP) ==================== -->
        <section id="sec-amortizacion" class="space-y-6 hidden">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold mb-1 text-slate-900">3. Calculadora de rentabilidad total: ¿gasolina, diésel, híbrido o GLP?</h2>
                <p class="text-xs text-slate-500 mb-4">Incluye precio de compra, consumo real, diferencia de mantenimiento anual (aceite, filtros, AdBlue/GLP) e impuestos para hallar el kilómetro exacto de amortización.</p>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Kilómetros recorridos al año</label>
                        <input type="number" id="km-anual" value="15000" oninput="calcularAmortizacion()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Sobreprecio de compra Opción B (€)</label>
                        <input type="number" id="dif-precio" value="2500" oninput="calcularAmortizacion()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Años que mantendrás el coche</label>
                        <input type="number" id="anios-uso" value="8" min="1" max="25" oninput="calcularAmortizacion()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-slate-50 p-4 rounded-xl border">
                        <h3 class="font-bold text-sm mb-2 text-slate-800">Vehículo A (ej. gasolina)</h3>
                        <div class="grid grid-cols-3 gap-2">
                            <div>
                                <label class="block text-xs text-slate-600">L/100 km</label>
                                <input type="number" step="0.1" id="cons-a" value="6.8" oninput="calcularAmortizacion()" class="w-full p-2 border rounded-lg font-semibold">
                            </div>
                            <div>
                                <label class="block text-xs text-slate-600">Precio (€/L)</label>
                                <input type="number" step="0.01" id="prec-a" value="1.61" oninput="calcularAmortizacion()" class="w-full p-2 border rounded-lg font-semibold">
                            </div>
                            <div>
                                <label class="block text-xs text-slate-600">Mantenim./año (€)</label>
                                <input type="number" id="mant-a" value="220" oninput="calcularAmortizacion()" class="w-full p-2 border rounded-lg font-semibold">
                            </div>
                        </div>
                    </div>
                    <div class="bg-slate-50 p-4 rounded-xl border">
                        <h3 class="font-bold text-sm mb-2 text-slate-800">Vehículo B (ej. diésel / híbrido / GLP)</h3>
                        <div class="grid grid-cols-3 gap-2">
                            <div>
                                <label class="block text-xs text-slate-600">L/100 km</label>
                                <input type="number" step="0.1" id="cons-b" value="4.7" oninput="calcularAmortizacion()" class="w-full p-2 border rounded-lg font-semibold">
                            </div>
                            <div>
                                <label class="block text-xs text-slate-600">Precio (€/L)</label>
                                <input type="number" step="0.01" id="prec-b" value="1.51" oninput="calcularAmortizacion()" class="w-full p-2 border rounded-lg font-semibold">
                            </div>
                            <div>
                                <label class="block text-xs text-slate-600">Mantenim./año (€)</label>
                                <input type="number" id="mant-b" value="260" oninput="calcularAmortizacion()" class="w-full p-2 border rounded-lg font-semibold">
                            </div>
                        </div>
                    </div>
                </div>
                <div id="res-amortizacion" class="mt-6 p-5 rounded-xl bg-slate-50 border border-slate-200"></div>
            </div>
        </section>

        <!-- ==================== SECCIÓN 4: MATRÍCULAS ESPAÑOLAS, CABALLOS FISCALES (CVF) Y DGT ==================== -->
        <section id="sec-dgt" class="space-y-6 hidden">
            <!-- 4A. Datador de matrículas españolas (mes/año, antigüedad y periodicidad ITV) -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold mb-1 text-slate-900">4A. Calculadora de fecha de matriculación por matrícula, edad y próxima ITV</h2>
                <p class="text-xs text-slate-500 mb-4">Introduce las 3 letras de cualquier matrícula europea española (desde BBB en el año 2000 hasta la actualidad) para conocer el mes y año estimado de matriculación, su antigüedad y cada cuánto debe pasar la ITV.</p>
                <div class="flex flex-col sm:flex-row items-center gap-4">
                    <div class="flex items-center border-2 border-slate-900 rounded-xl overflow-hidden bg-white shadow-sm w-64 h-14">
                        <div class="bg-blue-700 text-white h-full px-2.5 flex flex-col justify-center items-center text-[10px] font-bold">
                            <span>★★★</span>
                            <span>E</span>
                        </div>
                        <input type="text" id="mat-num" value="4820" maxlength="4" class="w-24 text-center text-2xl font-mono font-extrabold tracking-wider outline-none" placeholder="0000">
                        <input type="text" id="mat-letras" value="JXK" maxlength="3" oninput="calcularMatricula()" class="w-24 text-center text-2xl font-mono font-extrabold tracking-widest uppercase outline-none text-amber-600" placeholder="BBB">
                    </div>
                    <button onclick="calcularMatricula()" class="bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs px-5 py-3.5 rounded-xl transition">Consultar matrícula</button>
                </div>
                <div id="res-matricula" class="mt-5 p-4 rounded-xl bg-slate-50 border border-slate-200"></div>
            </div>

            <!-- 4B. Calculadora oficial BOE de caballos fiscales (CVF), IVTM, etiqueta DGT y CO2 -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold mb-1 text-slate-900">4B. Calculadora de caballos fiscales (CVF), etiqueta DGT e impuestos (IVTM y CO₂)</h2>
                <p class="text-xs text-slate-500 mb-4">Calcula la potencia fiscal con la fórmula del Anexo V del Reglamento General de Vehículos y obtiene una orientación inicial sobre el distintivo ambiental y el impuesto de matriculación. El IVTM depende del ayuntamiento: mostramos el tramo de potencia fiscal, no una cuota municipal.</p>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Motorización</label>
                        <select id="dgt-motor" onchange="calcularDGT()" class="w-full p-2 border rounded-lg font-bold bg-white text-xs">
                            <option value="gasolina">Gasolina</option>
                            <option value="diesel" selected>Diésel</option>
                            <option value="hibrido">Híbrido no enchufable / GLP (posible ECO)</option>
                            <option value="electrico">Eléctrico puro</option>
                            <option value="phev">Híbrido enchufable (PHEV)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Año 1.ª matr.</label>
                        <input type="number" id="dgt-anio" value="2015" min="1980" max="2100" oninput="calcularDGT()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Cilindrada térmica (cm³)</label>
                        <input type="number" id="dgt-cc" value="1968" oninput="calcularDGT()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Cilindros térmicos</label>
                        <input type="number" id="dgt-cil" value="4" min="2" max="12" oninput="calcularDGT()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">CO₂ (g/km)</label>
                        <input type="number" id="dgt-co2" value="119" oninput="calcularDGT()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Base imponible estimada (€)</label>
                        <input type="number" id="dgt-base" value="22000" oninput="calcularDGT()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                </div>
                <div id="res-dgt" class="mt-5 p-4 rounded-xl bg-slate-50 border border-slate-200"></div>
                <p class="mt-3 text-xs leading-relaxed text-slate-500">Orientativo, no una liquidación oficial: la etiqueta DGT no se confirma solo con año y combustible; depende de la categoría, homologación y norma Euro. Consulta el distintivo por matrícula en <a href="https://www.dgt.es/nuestros-servicios/tu-vehiculo/tus-vehiculos/distintivo-ambiental/" target="_blank" rel="noopener noreferrer" class="underline font-semibold">la web oficial de la DGT</a>. El IVTM final depende de la ordenanza y bonificaciones municipales. El impuesto de matriculación puede variar según territorio, base imponible fiscal y exenciones o reducciones aplicables.</p>
            </div>
        </section>

        <!-- ==================== SECCIÓN 5: CHECKLIST PRE-ITV Y BUSCADOR DE CÓDIGOS OBD2 ==================== -->
        <section id="sec-preitv" class="space-y-6 hidden">
            <!-- 5A. Buscador de códigos de avería OBD2 frecuentes en rechazo ITV -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold mb-1 text-slate-900">5A. Consulta rápida de códigos de fallo OBD2 frecuentes</h2>
                <p class="text-xs text-slate-500 mb-4">La lectura OBD se aplica según la categoría del vehículo y el procedimiento de inspección vigente. Algunos defectos relacionados con emisiones, el testigo MIL o los resultados de la lectura pueden afectar la ITV; el resultado depende del vehículo, del defecto detectado y del manual aplicable. Selecciona un código frecuente para consultar una posible causa:</p>
                <select id="obd-select" onchange="mostrarFalloOBD()" class="w-full p-3 border rounded-xl font-bold text-sm bg-slate-50">
                    <option value="P0401">P0401 / P0402 — Flujo insuficiente o excesivo en válvula EGR (recirculación de gases)</option>
                    <option value="P2002">P2002 / P2463 — Eficiencia del filtro de partículas diésel (DPF / FAP) por debajo del umbral</option>
                    <option value="P0420">P0420 — Eficiencia del sistema catalizador por debajo del umbral (Banco 1)</option>
                    <option value="P0101">P0101 / P0102 — Problema de rango/rendimiento en caudalímetro (sensor MAF)</option>
                    <option value="P0380">P0380 / P0670 — Fallo en circuito de bujías de precalentamiento (calentadores diésel)</option>
                    <option value="P0135">P0135 / P0141 — Fallo en circuito calentador de sonda lambda (sensor de oxígeno)</option>
                    <option value="P0299">P0299 — Presión de sobrealimentación del turbocompresor baja (geometría o manguito)</option>
                </select>
                <div id="res-obd" class="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200"></div>
            </div>

            <!-- 5B. Checklist de 8 puntos pre-ITV -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold mb-1 text-slate-900">5B. Checklist interactivo de revisión pre-ITV en casa</h2>
                <p class="text-xs text-slate-500 mb-4">Repasa estos puntos antes de acudir a la estación ITV. Son comprobaciones preventivas y no garantizan el resultado de la inspección:</p>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <label class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border cursor-pointer hover:bg-slate-100 transition">
                        <input type="checkbox" class="chk-itv mt-1 w-4 h-4" onchange="evaluarChecklist()" checked>
                        <div>
                            <span class="font-bold block text-slate-900">1. Dibujo de neumáticos (más de 1,6 mm) y medida admitida</span>
                            <span class="text-xs text-slate-500">Comprueba la medida en la ficha técnica y la compatibilidad; el ±3 % por sí solo no confirma una equivalencia ITV. Revisa también cortes, bultos y daños en los flancos.</span>
                        </div>
                    </label>
                    <label class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border cursor-pointer hover:bg-slate-100 transition">
                        <input type="checkbox" class="chk-itv mt-1 w-4 h-4" onchange="evaluarChecklist()" checked>
                        <div>
                            <span class="font-bold block text-slate-900">2. Alumbrado completo, altura de faros y luz de matrícula</span>
                            <span class="text-xs text-slate-500">Las ópticas opacas o las bombillas de matrícula fundidas son motivo constante de falta.</span>
                        </div>
                    </label>
                    <label class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border cursor-pointer hover:bg-slate-100 transition">
                        <input type="checkbox" class="chk-itv mt-1 w-4 h-4" onchange="evaluarChecklist()">
                        <div>
                            <span class="font-bold block text-slate-900">3. Escobillas limpiaparabrisas y eyectores con líquido</span>
                            <span class="text-xs text-slate-500">Comprueba que barren sin dejar cortina de agua y que el depósito está lleno.</span>
                        </div>
                    </label>
                    <label class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border cursor-pointer hover:bg-slate-100 transition">
                        <input type="checkbox" class="chk-itv mt-1 w-4 h-4" onchange="evaluarChecklist()">
                        <div>
                            <span class="font-bold block text-slate-900">4. Centralita sin fallos OBD2 y descarbonización pre-ITV</span>
                            <span class="text-xs text-slate-500">En diésel, circular 20 min a ~3.000 rpm en autovía con motor caliente antes de la prueba de opacidad.</span>
                        </div>
                    </label>
                    <label class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border cursor-pointer hover:bg-slate-100 transition">
                        <input type="checkbox" class="chk-itv mt-1 w-4 h-4" onchange="evaluarChecklist()">
                        <div>
                            <span class="font-bold block text-slate-900">5. Baliza V16 conectada homologada DGT 3.0 y chaleco</span>
                            <span class="text-xs text-slate-500">Equipamiento obligatorio de señalización de averías en carretera.</span>
                        </div>
                    </label>
                    <label class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border cursor-pointer hover:bg-slate-100 transition">
                        <input type="checkbox" class="chk-itv mt-1 w-4 h-4" onchange="evaluarChecklist()">
                        <div>
                            <span class="font-bold block text-slate-900">6. Cinturones de seguridad, claxon y cierre de puertas</span>
                            <span class="text-xs text-slate-500">Tira de todos los cinturones para comprobar el bloqueo automático.</span>
                        </div>
                    </label>
                </div>
                <div id="res-preitv" class="mt-4 p-4 rounded-xl bg-amber-50 border border-amber-200 text-sm font-semibold text-amber-900"></div>
            </div>
        </section>

        <!-- ==================== SECCIÓN 6: ¿DESGUACE, AUTODOC O TALLER? (CATÁLOGO DE 16 PIEZAS REALES) ==================== -->
        <section id="sec-desguace" class="space-y-6 hidden">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold mb-1 text-slate-900">6. Calculadora maestra de recambios: ¿desguace, Autodoc o taller (Norauto / Feu Vert)?</h2>
                <p class="text-xs text-slate-500 mb-4">Compara una pieza usada, una nueva montada por tu cuenta y una reparación en taller. Los importes precargados son ejemplos editables, no precios en tiempo real ni ofertas verificadas. Sustitúyelos por presupuestos reales, confirma la referencia exacta y añade envío, desplazamientos, impuestos y cualquier gasto adicional que corresponda.</p>

                <div class="mb-4">
                    <label class="block text-xs font-bold text-slate-700 mb-1">Seleccionar pieza del catálogo (carga valores ilustrativos editables):</label>
                    <select id="pieza-catalogo" onchange="cargarPiezaCatalogo()" class="w-full p-2.5 border rounded-xl font-bold text-xs sm:text-sm bg-slate-50">
                        <option value="mecanica,50,145,1.5,alternador,0,0,52,0">Alternador (estimación editable)</option>
                        <option value="mecanica,40,115,1.2,motor+de+arranque,0,0,52,0">Motor de arranque (estimación editable)</option>
                        <option value="mecanica,85,240,2.5,compresor+aire+acondicionado,0,0,52,0">Compresor de aire acondicionado (estimación editable)</option>
                        <option value="mecanica,140,380,3.5,turbocompresor,0,0,52,0">Turbocompresor (estimación editable)</option>
                        <option value="mecanica,220,950,5.0,caja+de+cambios,0,0,52,0">Caja de cambios manual (estimación editable)</option>
                        <option value="mecanica,75,230,2.5,cremallera+direccion,0,0,52,0">Cremallera de dirección (estimación editable)</option>
                        <option value="carroceria,35,110,0.5,faro+delantero,0,0,52,0">Faro delantero principal (estimación editable)</option>
                        <option value="carroceria,25,65,0.3,piloto+trasero,0,0,52,0">Piloto trasero (estimación editable)</option>
                        <option value="carroceria,30,85,0.4,retrovisor+exterior,0,0,52,0">Espejo retrovisor completo (estimación editable)</option>
                        <option value="carroceria,65,190,1.5,paragolpes,0,0,52,0">Paragolpes delantero o trasero (estimación editable)</option>
                        <option value="carroceria,30,75,1.2,elevalunas+electrico,0,0,52,0">Mecanismo elevalunas eléctrico (estimación editable)</option>
                        <option value="mecanica,40,115,1.5,valvula+egr,0,0,52,0">Válvula EGR (estimación editable; verifica diagnosis)</option>
                        <option value="desgaste,35,85,1.5,discos+y+pastillas+de+freno,0,0,52,0">Juego de discos y pastillas de freno (compara piezas nuevas)</option>
                        <option value="desgaste,50,130,2.0,amortiguadores,0,0,52,0">Pareja de amortiguadores (compara piezas nuevas)</option>
                        <option value="desgaste,90,340,5.5,kit+embrague+bimasa,0,0,52,0">Kit de embrague + volante bimasa (compara piezas nuevas)</option>
                        <option value="desgaste,45,110,3.5,kit+distribucion+bomba+agua,0,0,52,0">Kit correa de distribución + bomba de agua (compara piezas nuevas)</option>
                    </select>
                </div>

                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Familia de pieza</label>
                        <select id="rep-tipo" onchange="calcularDesguace()" class="w-full p-2.5 border rounded-lg font-bold bg-white text-xs">
                            <option value="carroceria">Carrocería, óptica o interior</option>
                            <option value="mecanica" selected>Mecánica / eléctrica OEM</option>
                            <option value="desgaste">Frenos, embrague, correas o filtros</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Precio en desguace (€)</label>
                        <input type="number" id="rep-desguace" value="50" min="0" max="100000" step="0.01" oninput="calcularDesguace()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Precio nuevo Autodoc (€)</label>
                        <input type="number" id="rep-autodoc" value="145" min="0" max="100000" step="0.01" oninput="calcularDesguace()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Horas de mano de obra</label>
                        <input type="number" step="0.1" min="0" max="100" id="rep-horas" value="1.5" oninput="calcularDesguace()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Transporte / envío pieza usada (€)</label>
                        <input type="number" id="rep-logistica-usado" value="0" min="0" max="100000" step="0.01" oninput="calcularDesguace()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Envío pieza nueva (€)</label>
                        <input type="number" id="rep-envio-nuevo" value="0" min="0" max="100000" step="0.01" oninput="calcularDesguace()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Tarifa estimada taller (€/h)</label>
                        <input type="number" id="rep-tarifa-hora" value="52" min="0" max="1000" step="0.5" oninput="calcularDesguace()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Recargo de taller sobre pieza (%)</label>
                        <input type="number" id="rep-recargo-taller" value="0" min="0" max="300" step="1" oninput="calcularDesguace()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                </div>
                <p class="mt-3 text-xs text-slate-500">El coste de taller es una simulación: precio de la pieza nueva, envío, recargo editable y mano de obra. No sustituye un presupuesto cerrado y no incluye diagnosis, consumibles, impuestos ni trabajos adicionales salvo que los añadas a los importes.</p>
                <div id="res-desguace" class="mt-6 p-5 rounded-xl bg-slate-50 border border-slate-200"></div>

                <!-- Enlaces directos a los grandes desguaces cerca de Aranjuez / Madrid Sur y tiendas online -->
                <div class="mt-6 pt-5 border-t border-slate-200">
                    <h3 class="text-xs font-bold text-slate-700 mb-3">Buscar referencias y consultar disponibilidad (abre cada proveedor para confirmar stock, precio y condiciones):</h3>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                        <a id="link-pieza-autodoc" href="https://www.autodoc.es/search?keyword=alternador" target="_blank" rel="nofollow sponsored" class="p-2.5 bg-orange-500 hover:bg-orange-600 text-slate-950 font-bold rounded-lg text-center transition">1. Ver nuevo en Autodoc →</a>
                        <a href="https://www.desguaceslatorre.es/" target="_blank" rel="nofollow" class="p-2.5 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-lg text-center transition">2. Desguaces La Torre (A-42)</a>
                        <a href="https://www.elchoque.com/" target="_blank" rel="nofollow" class="p-2.5 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-lg text-center transition">3. Pol. Aimayr (S. Martín Vega)</a>
                        <a href="https://www.recambioverde.es/" target="_blank" rel="nofollow" class="p-2.5 bg-emerald-700 hover:bg-emerald-800 text-white font-semibold rounded-lg text-center transition">4. Buscador RecambioVerde</a>
                    </div>
                </div>
            </div>
        </section>

        <!-- COMPARADOR MULTITIENDA (MUCHONEUMÁTICO + AUTODOC + NORAUTO/FEU VERT + AMAZON) -->
        <section class="mt-8 bg-gradient-to-br from-slate-900 to-slate-800 text-white p-6 rounded-2xl shadow-md no-print">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                <div>
                    <h2 class="text-lg font-bold text-amber-400">Comparador de tiendas recomendadas para __CAR_CONTEXT_NAME__</h2>
                    <p class="text-xs text-slate-300">Selecciona la tienda ideal según busques neumático con envío gratis, recambio general, montaje en taller cercano o urgencia 24 h.</p>
                </div>
                <span class="text-xs bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full w-fit">Selección mecánica experta</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <a id="cta-muchoneumatico" href="https://www.muchoneumatico.com/buscar?controller=search&s=__VAL_A1__+__VAL_P1__+__VAL_L1__" target="_blank" rel="nofollow sponsored" class="bg-slate-800 hover:bg-slate-700 p-4 rounded-xl border border-slate-700 transition flex flex-col justify-between">
                    <div>
                        <span class="text-xs text-sky-400 font-semibold">Especialista en ruedas</span>
                        <h3 id="txt-cta-mucho" class="font-bold text-sm mt-1">Muchoneumático __VAL_A1__/__VAL_P1__ R__VAL_L1__</h3>
                        <p class="text-xs text-slate-300 mt-1">Gran stock en primeras marcas y segundas líneas con envío gratuito.</p>
                    </div>
                    <span class="mt-4 inline-block text-center bg-sky-500 hover:bg-sky-600 text-slate-950 font-bold text-xs py-2 rounded-lg">Ver en Muchoneumático →</span>
                </a>

                <a id="cta-autodoc" href="https://www.autodoc.es/search?keyword=__CAR_AUTODOC_QUERY__" target="_blank" rel="nofollow sponsored" class="bg-slate-800 hover:bg-slate-700 p-4 rounded-xl border border-slate-700 transition flex flex-col justify-between">
                    <div>
                        <span class="text-xs text-orange-400 font-semibold">Recambios en general</span>
                        <h3 class="font-bold text-sm mt-1">Catálogo Autodoc (__CAR_SHORT_NAME__)</h3>
                        <p class="text-xs text-slate-300 mt-1">El mayor catálogo europeo de filtros, frenos, suspensión, aceites y correas.</p>
                    </div>
                    <span class="mt-4 inline-block text-center bg-orange-500 hover:bg-orange-600 text-slate-950 font-bold text-xs py-2 rounded-lg">Buscar en Autodoc →</span>
                </a>

                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 flex flex-col justify-between">
                    <div>
                        <span class="text-xs text-emerald-400 font-semibold">Talleres por cercanía y ofertas</span>
                        <h3 id="txt-cta-norauto" class="font-bold text-sm mt-1">Montaje __VAL_A2__/__VAL_P2__ R__VAL_L2__</h3>
                        <p class="text-xs text-slate-300 mt-1">Compra online tus neumáticos o batería con cita de montaje en tu centro más cercano.</p>
                    </div>
                    <div class="grid grid-cols-2 gap-2 mt-4">
                        <a id="cta-norauto" href="https://www.norauto.es/c/47595-neumaticos.html?q=__VAL_A2__%2F__VAL_P2__R__VAL_L2__" target="_blank" rel="nofollow sponsored" class="text-center bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs py-2 rounded-lg transition">Norauto →</a>
                        <a id="cta-feuvert" href="https://www.feuvert.es/neumaticos?q=__VAL_A2__+__VAL_P2__+__VAL_L2__" target="_blank" rel="nofollow sponsored" class="text-center bg-slate-600 hover:bg-slate-500 text-white font-bold text-xs py-2 rounded-lg transition">Feu Vert →</a>
                    </div>
                </div>

                <a id="cta-neumatico-orig" href="https://www.amazon.es/s?k=neumaticos+__VAL_A1__+__VAL_P1__+R__VAL_L1__&tag=__AMAZON_TAG__" target="_blank" rel="nofollow sponsored" class="bg-slate-800 hover:bg-slate-700 p-4 rounded-xl border border-slate-700 transition flex flex-col justify-between">
                    <div>
                        <span class="text-xs text-amber-400 font-semibold">Envío 24 h y pre-ITV</span>
                        <h3 id="txt-cta-orig" class="font-bold text-sm mt-1">Amazon: __VAL_A1__/__VAL_P1__ R__VAL_L1__ y V16</h3>
                        <p class="text-xs text-slate-300 mt-1">Neumáticos, baliza V16 conectada DGT, escobillas y diagnosis OBD2.</p>
                    </div>
                    <span class="mt-4 inline-block text-center bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs py-2 rounded-lg">Ver en Amazon →</span>
                </a>
            </div>
        </section>

        __PRECALC_TABLE_HTML__

        <article class="mt-8 bg-white p-6 rounded-2xl border border-slate-200 text-sm text-slate-600 space-y-3">
            __SEO_TEXT_BLOCK__
        </article>

        <nav class="mt-8 bg-slate-100 p-6 rounded-2xl border border-slate-200 no-print">
            <h3 class="text-xs font-bold text-slate-500 mb-3">Guías de desguaces, modelos de coche, medidas ITV y rutas</h3>
            <div class="flex flex-wrap gap-2">
                __INTERNAL_LINKS_HTML__
            </div>
        </nav>

    </main>

    <footer class="bg-slate-900 text-slate-400 text-xs py-8 mt-12 no-print">
        <div class="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div>
                <p class="font-bold text-slate-200">__SITE_NAME__ © 2026</p>
                <p class="mt-1">Comparador independiente. Participamos en programas de afiliación (Amazon UE y tiendas del sector motor).</p>
            </div>
            <div class="flex flex-wrap gap-4">
                <a href="index.html" class="hover:text-white transition">Inicio</a>
                <a href="desguaces-itv-aranjuez-comarca-las-vegas.html" class="hover:text-white transition">Desguaces Madrid Sur y Aranjuez</a>
                <a href="mapa-web.html" class="hover:text-white transition">Mapa web</a>
                <a href="aviso-legal.html" class="hover:text-white transition">Aviso legal</a>
                <a href="privacidad-cookies.html" class="hover:text-white transition">Privacidad y cookies</a>
                <button type="button" onclick="mostrarPreferenciasCookies()" class="hover:text-white transition underline">Configurar cookies</button>
            </div>
        </div>
    </footer>

    <div id="cookie-banner" role="dialog" aria-label="Preferencias de privacidad" aria-live="polite" class="fixed bottom-0 inset-x-0 bg-slate-950/95 text-white p-4 border-t border-slate-800 z-50 hidden no-print">
        <div class="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
            <p class="text-slate-300">Google Analytics solo se cargará si aceptas la medición estadística. Si eliges rechazarla, la etiqueta no se carga. La decisión puede cambiarse desde «Configurar cookies». Consulta la <a href="privacidad-cookies.html" class="underline text-amber-400">Política de privacidad y cookies</a>.</p>
            <div class="flex gap-2 shrink-0">
                <button type="button" onclick="gestionarCookies('essential')" class="px-3 py-2 rounded border border-slate-500 hover:bg-slate-800 transition font-semibold">Rechazar analítica</button>
                <button type="button" onclick="gestionarCookies('analytics')" class="px-3 py-2 rounded border border-slate-500 hover:bg-slate-800 transition font-semibold">Aceptar analítica</button>
            </div>
        </div>
    </div>

    <script>
        const AMAZON_TAG = "__AMAZON_TAG__";
        const GOOGLE_ANALYTICS_ID = "__GOOGLE_ANALYTICS_ID__";
        const AUTOCALC_CONSENT_KEY = "autocalc_privacidad_v2";
        const TAB_INICIAL = "__INITIAL_TAB__";
        const GARGANTAS = {155:'4.5"-5.5"',165:'4.5"-6.0"',175:'5.0"-6.0"',185:'5.0"-6.5"',195:'5.5"-7.0"',205:'5.5"-7.5"',215:'6.0"-7.5"',225:'6.0"-8.0"',235:'6.5"-8.5"',245:'7.0"-9.0"',255:'7.5"-9.5"',265:'8.0"-10.0"',275:'8.5"-10.5"'};

        function leerNumeroCampo(id) {
            const campo = document.getElementById(id);
            if (!campo || String(campo.value).trim() === '') return null;
            const valor = Number(campo.value);
            return Number.isFinite(valor) ? valor : null;
        }

        function mostrarErrorCalculo(id, mensaje) {
            const caja = document.getElementById(id);
            if (!caja) return;
            caja.className = 'mt-4 p-4 rounded-xl bg-rose-50 border border-rose-200 text-sm font-semibold text-rose-800';
            caja.textContent = mensaje;
        }

        function escaparHTML(valor) {
            return String(valor ?? '').replace(/[&<>"']/g, caracter => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;'
            })[caracter]);
        }

        const DICCIONARIO_OBD = {
            "P0401": {
                titulo: "P0401 / P0402 — Fallo de caudal en válvula EGR",
                causa: "Carbonilla acumulada obstruyendo la válvula de recirculación de gases de escape o membrana perforada.",
                itv: "Rechazo directo (Defecto Grave) en lectura OBD y aumento de emisiones NOx.",
                solucion: "Limpiar con spray descarbonizador de admisión/EGR o sustituir la válvula EGR completa.",
                query: "valvula+egr+limpiador"
            },
            "P2002": {
                titulo: "P2002 / P2463 — Saturación de hollín en filtro de partículas (DPF / FAP)",
                causa: "Exceso de trayectos cortos urbanos que impiden completar la regeneración térmica o sensor diferencial de presión averiado.",
                itv: "Rechazo grave en prueba de opacidad de humos y lectura OBD.",
                solucion: "Añadir aditivo regenerador de filtro de partículas, forzar regeneración en carretera a 3.000 rpm o sustituir sensor de presión DPF.",
                query: "aditivo+limpiador+filtro+particulas+dpf"
            },
            "P0420": {
                titulo: "P0420 — Baja eficiencia del catalizador (Banco 1)",
                causa: "Desgaste del monolito cerámico del catalizador o lectura errónea de la segunda sonda lambda trasera.",
                itv: "Defecto grave en prueba de gases (CO alto en gasolina) y testigo MIL encendido.",
                solucion: "Comprobar primero la sonda lambda posterior antes de sustituir el catalizador.",
                query: "sonda+lambda+catalizador"
            },
            "P0101": {
                titulo: "P0101 — Rango incorrecto en sensor de masa de aire (caudalímetro MAF)",
                causa: "Hilo térmico del caudalímetro sucio por polvo/aceite o toma de aire parásita en el manguito de admisión.",
                itv: "Pérdida de potencia, tirones y fallo registrado en centralita.",
                solucion: "Limpiar con spray de residuo cero para sensores MAF o cambiar el caudalímetro (10 min).",
                query: "caudalimetro+sensor+maf"
            },
            "P0380": {
                titulo: "P0380 / P0670 — Avería en calentadores o caja de precalentamiento diésel",
                causa: "Uno o varios calentadores cortados (resistencia infinita) o relé de precalentamiento dañado.",
                itv: "En muchos vehículos enciende el testigo de avería o parpadea el muelle, causando rechazo en lectura OBD.",
                solucion: "Medir continuidad con multímetro y sustituir el juego de calentadores.",
                query: "bujias+precalentamiento+calentadores+diesel"
            },
            "P0135": {
                titulo: "P0135 — Fallo en calentador de sonda lambda (sensor O2)",
                causa: "Resistencia interna de precalentamiento de la sonda lambda fundida.",
                itv: "Mezcla aire/combustible imprecisa en frío y fallo grave en lectura OBD de la ITV.",
                solucion: "Sustituir la sonda lambda afectada con llave hexagonal de 22 mm.",
                query: "sonda+lambda+universal"
            },
            "P0299": {
                titulo: "P0299 — Presión de sobrealimentación del turbo inferior a la demandada",
                causa: "Manguito del intercooler rajado, electroválvula N75 defectuosa o geometría variable del turbo atascada por carbonilla.",
                itv: "El coche entra en modo protección (limp mode), humea negro y registra fallo en ECU.",
                solucion: "Revisar fugas en tubos de vacío/intercooler y comprobar la electroválvula de control del turbo.",
                query: "electrovalvula+control+presion+turbo"
            }
        };

        function cambiarTab(tab) {
            ['itv', 'consumo', 'amortizacion', 'dgt', 'preitv', 'desguace'].forEach(t => {
                const sec = document.getElementById('sec-' + t);
                const btn = document.getElementById('tab-' + t);
                if (sec && btn) {
                    sec.classList.add('hidden');
                    btn.className = 'py-2.5 px-2 rounded-lg font-semibold text-xs text-slate-600 hover:text-slate-900 transition';
                }
            });
            const activeSec = document.getElementById('sec-' + tab);
            const activeBtn = document.getElementById('tab-' + tab);
            if (activeSec && activeBtn) {
                activeSec.classList.remove('hidden');
                activeBtn.className = 'py-2.5 px-2 rounded-lg font-semibold text-xs bg-white text-slate-900 shadow-sm transition';
            }
            if (tab === 'consumo' && !window.gasolinerasCargadas) {
                window.gasolinerasCargadas = true;
                cargarGasolinerasMunicipio();
            }
        }

        // 1B. Calculadora de ET y ancho de vías
        function calcularET() {
            const j1 = leerNumeroCampo('et-j1');
            const et1 = leerNumeroCampo('et-off1');
            const j2 = leerNumeroCampo('et-j2');
            const et2 = leerNumeroCampo('et-off2');
            if (j1 === null || j2 === null || et1 === null || et2 === null ||
                j1 < 4 || j1 > 15 || j2 < 4 || j2 > 15 ||
                et1 < -100 || et1 > 150 || et2 < -100 || et2 > 150) {
                mostrarErrorCalculo('res-et', 'Introduce anchuras de llanta de 4 a 15 pulgadas y ET entre −100 y 150 mm. El ET puede ser cero o negativo.');
                return;
            }

            const w1 = j1 * 25.4;
            const w2 = j2 * 25.4;
            const deltaInterior = ((w2 - w1) / 2) - (et1 - et2);
            const deltaExterior = ((w2 - w1) / 2) + (et1 - et2);
            const cambioAnchoVias = (et1 - et2) * 2;
            const dentroUmbralOrientativo = Math.abs(cambioAnchoVias) <= 30;

            const txtInt = deltaInterior > 0
                ? `Se acerca ${deltaInterior.toFixed(1)} mm al amortiguador`
                : `Gana ${Math.abs(deltaInterior).toFixed(1)} mm de holgura interior`;
            const txtExt = deltaExterior > 0
                ? `Sobresale ${deltaExterior.toFixed(1)} mm más hacia la aleta`
                : `Se mete ${Math.abs(deltaExterior).toFixed(1)} mm hacia dentro`;

            document.getElementById('res-et').innerHTML = `
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center text-xs sm:text-sm">
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Borde interior (suspensión)</div>
                        <div class="font-bold text-slate-900 mt-1">${txtInt}</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Borde exterior (aleta)</div>
                        <div class="font-bold text-amber-600 mt-1">${txtExt}</div>
                    </div>
                    <div class="p-3 rounded-lg border ${dentroUmbralOrientativo ? 'bg-emerald-50 border-emerald-200 text-emerald-900' : 'bg-rose-50 border-rose-200 text-rose-900'}">
                        <div class="text-xs opacity-75">Variación estimada del ancho de vías</div>
                        <div class="font-extrabold mt-1">${cambioAnchoVias > 0 ? '+' : ''}${cambioAnchoVias.toFixed(0)} mm (${dentroUmbralOrientativo ? 'dentro del umbral orientativo de 30 mm' : 'supera el umbral orientativo de 30 mm'})</div>
                    </div>
                </div>
                <p class="mt-3 text-xs text-slate-500">El umbral de 30 mm es una referencia inicial, no una declaración de legalidad. La admisión depende de la modificación completa, las medidas del vehículo, la ausencia de interferencias y los requisitos de homologación e ITV.</p>
            `;
        }

        // 2B. Consumo real del depósito
        function calcularConsumoReal() {
            const litros = leerNumeroCampo('real-litros');
            const km = leerNumeroCampo('real-km');
            const precio = leerNumeroCampo('real-precio');
            if (litros === null || km === null || precio === null ||
                litros < 0 || km <= 0 || precio < 0) {
                mostrarErrorCalculo('res-consumo-real', 'Introduce litros y precio no negativos, y una distancia recorrida mayor que cero.');
                return;
            }

            const l100 = (litros / km) * 100;
            const coste100 = l100 * precio;
            const kmPorLitro = litros > 0 ? km / litros : 0;

            document.getElementById('res-consumo-real').innerHTML = `
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center">
                    <div class="bg-white p-3 rounded-lg border border-emerald-200">
                        <div class="text-xs text-slate-500">Consumo real medido</div>
                        <div class="text-xl font-extrabold text-emerald-700">${l100.toFixed(2)} L/100 km</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border border-emerald-200">
                        <div class="text-xs text-slate-500">Coste real cada 100 km</div>
                        <div class="text-xl font-bold text-slate-900">${coste100.toFixed(2)} €/100 km</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border border-emerald-200">
                        <div class="text-xs text-slate-500">Rendimiento por litro</div>
                        <div class="text-xl font-bold text-amber-600">${kmPorLitro.toFixed(1)} km/L</div>
                    </div>
                </div>
            `;
        }

        // 2C. API Oficial del Ministerio para precios de gasolineras en tiempo real
        async function cargarGasolinerasMunicipio() {
            const idMun = document.getElementById('municipio-gas').value;
            const cont = document.getElementById('contenedor-gasolineras');
            cont.innerHTML = `<div class="p-4 text-center text-slate-500">Conectando con la sede electrónica del Ministerio para obtener los precios de hoy...</div>`;
            try {
                const resp = await fetch(`https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroMunicipio/${encodeURIComponent(idMun)}`);
                if (!resp.ok) throw new Error('La API de carburantes ha respondido con un error HTTP.');
                const data = await resp.json();
                const lista = data.ListaEESSPrecio || [];
                if (!lista.length) {
                    cont.innerHTML = `<div class="p-3 bg-slate-100 rounded-lg">No hay estaciones registradas en este municipio en este momento.</div>`;
                    return;
                }
                const parsePrecio = (str) => {
                    if (typeof str !== 'string') return null;
                    const valor = str.trim().replace(',', '.');
                    if (!/^\d{1,2}(?:\.\d{1,3})?$/.test(valor)) return null;
                    const numero = Number(valor);
                    return Number.isFinite(numero) && numero >= 0.5 && numero <= 10 ? numero : null;
                };
                lista.sort((a, b) =>
                    (parsePrecio(a["Precio Gasoleo A"]) ?? parsePrecio(a["Precio Gasolina 95 E5"]) ?? 99) -
                    (parsePrecio(b["Precio Gasoleo A"]) ?? parsePrecio(b["Precio Gasolina 95 E5"]) ?? 99)
                );

                const top = lista.slice(0, 8);
                let filas = top.map(e => {
                    const pDieselNum = parsePrecio(e["Precio Gasoleo A"]);
                    const pGas95Num = parsePrecio(e["Precio Gasolina 95 E5"]);
                    const pDiesel = pDieselNum === null ? "—" : pDieselNum.toFixed(3).replace('.', ',');
                    const pGas95 = pGas95Num === null ? "—" : pGas95Num.toFixed(3).replace('.', ',');
                    const nombre = escaparHTML(e["Rótulo"] || "Estación sin nombre");
                    const direccion = escaparHTML(e["Dirección"] || "Dirección no disponible");
                    const localidad = escaparHTML(e["Localidad"] || "");
                    const botonDiesel = pDieselNum === null ? "" : `<button type="button" onclick="usarPrecioViaje('diesel', ${pDieselNum})" class="text-[11px] bg-slate-800 hover:bg-slate-700 text-white px-2 py-1 rounded">Usar diésel</button>`;
                    const botonGasolina = pGas95Num === null ? "" : `<button type="button" onclick="usarPrecioViaje('gasolina', ${pGas95Num})" class="text-[11px] bg-amber-600 hover:bg-amber-700 text-white px-2 py-1 rounded">Usar gasolina</button>`;
                    return `
                        <tr class="border-b border-slate-100 hover:bg-slate-50">
                            <td class="py-2 px-2 font-bold text-slate-900">${nombre}</td>
                            <td class="py-2 px-2 text-slate-600">${direccion}${localidad ? ` (${localidad})` : ''}</td>
                            <td class="py-2 px-2 text-center font-bold text-emerald-700">${pDiesel} €/L</td>
                            <td class="py-2 px-2 text-center font-bold text-amber-700">${pGas95} €/L</td>
                            <td class="py-2 px-2 text-right"><div class="flex flex-wrap justify-end gap-1">${botonDiesel}${botonGasolina}</div></td>
                        </tr>
                    `;
                }).join('');

                cont.innerHTML = `
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="border-b-2 border-slate-200 text-slate-500">
                                    <th class="py-2 px-2">Estación</th>
                                    <th class="py-2 px-2">Dirección</th>
                                    <th class="py-2 px-2 text-center">Diésel A</th>
                                    <th class="py-2 px-2 text-center">Gasolina 95</th>
                                    <th class="py-2 px-2 text-right">Aplicar</th>
                                </tr>
                            </thead>
                            <tbody>${filas}</tbody>
                        </table>
                    </div>
                `;
            } catch (err) {
                cont.innerHTML = `<div class="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-900">El servidor del Ministerio no responde en este instante. Puedes introducir el precio por litro manualmente arriba.</div>`;
            }
        }

        function usarPrecioViaje(tipoCombustible, precio) {
            if (!['diesel', 'gasolina'].includes(tipoCombustible) ||
                !Number.isFinite(precio) || precio < 0.5 || precio > 10) return;
            const campoPrecioViaje = document.getElementById('precio-litro');
            if (!campoPrecioViaje) return;
            campoPrecioViaje.value = precio.toFixed(3);
            calcularConsumo();
            const caja = document.getElementById('res-consumo');
            if (caja) {
                const avisoAnterior = caja.querySelector('.aviso-precio-aplicado');
                if (avisoAnterior) avisoAnterior.remove();
                const aviso = document.createElement('p');
                aviso.className = 'aviso-precio-aplicado mt-3 text-xs text-slate-500';
                aviso.textContent = 'Precio de ' + (tipoCombustible === 'diesel' ? 'diésel A' : 'gasolina 95 E5') + ' aplicado solo a la calculadora del viaje. La calculadora de consumo real conserva el precio que hayas introducido.';
                caja.appendChild(aviso);
            }
        }

        // 4A. Datador de matrículas españolas (BBB = Sep 2000 hasta hoy)
        function calcularMatricula() {
            const inputLetras = document.getElementById('mat-letras');
            if (!inputLetras) return;
            const letras = inputLetras.value.toUpperCase().replace(/[^BCDFGHJKLMNPRSTVWXYZ]/g, '');
            inputLetras.value = letras;
            const box = document.getElementById('res-matricula');

            if (letras.length !== 3) {
                box.innerHTML = `<p class="text-xs text-rose-700 font-semibold">Introduce las 3 consonantes válidas de la matrícula (sin vocales ni Ñ/Q, ej. JXK, HBB, MNP).</p>`;
                return;
            }

            const alfabeto = "BCDFGHJKLMNPRSTVWXYZ";
            const v1 = alfabeto.indexOf(letras[0]);
            const v2 = alfabeto.indexOf(letras[1]);
            const v3 = alfabeto.indexOf(letras[2]);
            const indice = (v1 * 400) + (v2 * 20) + v3; // 0 (BBB) a 7999

            // Hitos orientativos de la serie alfanumérica (índice base 20 -> año.mes); la interpolación no es una consulta oficial por matrícula.
            const hitos = [
                [0, 2000.6666667], [140, 2001.0], [420, 2002.0], [680, 2003.0],
                [980, 2004.0], [1310, 2005.0], [1650, 2006.0], [2010, 2007.0],
                [2350, 2008.0], [2580, 2009.0], [2740, 2010.0], [2900, 2011.0],
                [3040, 2012.0], [3150, 2013.0], [3260, 2014.0], [3420, 2015.0],
                [3620, 2016.0], [3860, 2017.0], [4120, 2018.0], [4390, 2019.0],
                [4620, 2020.0], [4790, 2021.0], [4960, 2022.0], [5140, 2023.0],
                [5340, 2024.0], [5550, 2025.0], [5770, 2026.0], [6000, 2027.0]
            ];

            let fechaEst = hitos[0][1];
            let intervaloEncontrado = false;
            for (let i = 0; i < hitos.length - 1; i++) {
                if (indice >= hitos[i][0] && indice <= hitos[i+1][0]) {
                    const ratio = (indice - hitos[i][0]) / (hitos[i+1][0] - hitos[i][0]);
                    fechaEst = hitos[i][1] + ratio * (hitos[i+1][1] - hitos[i][1]);
                    intervaloEncontrado = true;
                    break;
                }
            }
            if (!intervaloEncontrado && indice > hitos[hitos.length - 1][0]) {
                const anterior = hitos[hitos.length - 2];
                const ultimo = hitos[hitos.length - 1];
                const ritmoAnual = (ultimo[1] - anterior[1]) / (ultimo[0] - anterior[0]);
                fechaEst = ultimo[1] + (indice - ultimo[0]) * ritmoAnual;
            }

            const anioMat = Math.floor(fechaEst);
            const mesIndex = Math.min(11, Math.max(0, Math.floor((fechaEst - anioMat) * 12)));
            const meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
            const ahora = new Date();
            const diasMes = new Date(ahora.getFullYear(), ahora.getMonth() + 1, 0).getDate();
            const fraccionActual = (ahora.getMonth() + (ahora.getDate() / diasMes)) / 12;
            const edad = Math.max(0, (ahora.getFullYear() + fraccionActual - fechaEst));

            let frecuenciaITV = "Anual (cada año por tener más de 10 años)";
            if (edad < 4) frecuenciaITV = `Exento hasta los 4 años (1.ª ITV en ${anioMat + 4})`;
            else if (edad < 10) frecuenciaITV = "Bienal (cada 2 años hasta cumplir los 10 años)";

            // Sincronizar con la calculadora de año DGT inferior
            document.getElementById('dgt-anio').value = anioMat;
            calcularDGT();

            box.innerHTML = `
                <p class="mb-3 text-xs text-slate-500">La fecha se calcula por interpolación entre hitos y puede diferir de la fecha real. No determina por sí sola la próxima ITV ni sustituye la consulta de la documentación del vehículo.</p>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Fecha estimada de matriculación (aproximación)</div>
                        <div class="text-lg font-extrabold text-slate-900 capitalize">${meses[mesIndex]} de ${anioMat}</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Antigüedad aproximada</div>
                        <div class="text-lg font-bold text-amber-600">${edad.toFixed(1)} años</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Periodicidad de ITV (turismo)</div>
                        <div class="text-xs font-bold text-emerald-800 mt-1">${frecuenciaITV}</div>
                    </div>
                </div>
            `;
        }

        // 5A. Mostrar código de fallo OBD2
        function mostrarFalloOBD() {
            const sel = document.getElementById('obd-select');
            if (!sel) return;
            const info = DICCIONARIO_OBD[sel.value];
            document.getElementById('res-obd').innerHTML = `
                <h3 class="font-bold text-sm text-slate-900">${info.titulo}</h3>
                <p class="text-xs text-slate-600 mt-1"><strong>Causa mecánica habitual:</strong> ${info.causa}</p>
                <p class="text-xs text-rose-700 font-semibold mt-1"><strong>Impacto en la estación ITV:</strong> ${info.itv}</p>
                <p class="text-xs text-emerald-800 font-medium mt-1"><strong>Solución recomendada:</strong> ${info.solucion}</p>
                <div class="flex flex-wrap gap-2 mt-3">
                    <a href="https://www.autodoc.es/search?keyword=${info.query}" target="_blank" rel="nofollow sponsored" class="text-xs bg-orange-500 hover:bg-orange-600 text-slate-950 font-bold px-3 py-1.5 rounded-lg transition">Buscar recambio en Autodoc →</a>
                    <a href="https://www.amazon.es/s?k=${info.query}&tag=${AMAZON_TAG}" target="_blank" rel="nofollow sponsored" class="text-xs bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold px-3 py-1.5 rounded-lg transition">Ver aditivos / recambio en Amazon →</a>
                </div>
            `;
        }

        function evaluarChecklist() {
            const total = document.querySelectorAll('.chk-itv').length;
            const marcados = document.querySelectorAll('.chk-itv:checked').length;
            const box = document.getElementById('res-preitv');
            if (!box) return;
            if (marcados === total) {
                box.className = 'mt-4 p-4 rounded-xl bg-emerald-50 border border-emerald-300 text-sm font-bold text-emerald-900';
                box.innerText = `Checklist completado: ${total} comprobaciones revisadas. Esto no garantiza el resultado de la ITV.`;
            } else {
                box.className = 'mt-4 p-4 rounded-xl bg-amber-50 border border-amber-200 text-sm font-semibold text-amber-900';
                box.innerText = `Progreso del checklist: ${marcados} de ${total} comprobaciones revisadas. Revisa las pendientes; el resultado depende de la inspección.`;
            }
        }

        // 6. Catálogo de piezas y calculadora Desguace vs. Autodoc vs. Taller
        function cargarPiezaCatalogo() {
            const selector = document.getElementById('pieza-catalogo');
            if (!selector || !selector.value) return;

            const p = selector.value.split(',');
            if (p.length < 9) {
                mostrarErrorCalculo('res-desguace', 'No se han podido leer los valores del catálogo. Comprueba la opción seleccionada.');
                return;
            }

            const campos = {
                'rep-tipo': p[0],
                'rep-desguace': p[1],
                'rep-autodoc': p[2],
                'rep-horas': p[3],
                'rep-logistica-usado': p[5],
                'rep-envio-nuevo': p[6],
                'rep-tarifa-hora': p[7],
                'rep-recargo-taller': p[8]
            };
            Object.entries(campos).forEach(([id, valor]) => {
                const campo = document.getElementById(id);
                if (campo) campo.value = valor;
            });

            const consulta = p[4].split('+').join(' ');
            const linkAutodoc = document.getElementById('link-pieza-autodoc');
            if (linkAutodoc) {
                linkAutodoc.href = 'https://www.autodoc.es/search?keyword=' + encodeURIComponent(consulta);
            }

            calcularDesguace();
        }

        function calcularDesguace() {
            const elTipo = document.getElementById('rep-tipo');
            if (!elTipo) return;

            const tipo = elTipo.value;
            const precioUsado = leerNumeroCampo('rep-desguace');
            const precioNuevo = leerNumeroCampo('rep-autodoc');
            const horas = leerNumeroCampo('rep-horas');
            const logisticaUsado = leerNumeroCampo('rep-logistica-usado');
            const envioNuevo = leerNumeroCampo('rep-envio-nuevo');
            const tarifaHora = leerNumeroCampo('rep-tarifa-hora');
            const recargoTaller = leerNumeroCampo('rep-recargo-taller');

            const valores = [precioUsado, precioNuevo, horas, logisticaUsado, envioNuevo, tarifaHora, recargoTaller];
            if (valores.some(valor => valor === null) ||
                valores.some(valor => valor < 0) ||
                precioUsado > 100000 || precioNuevo > 100000 ||
                logisticaUsado > 100000 || envioNuevo > 100000 ||
                horas > 100 || tarifaHora > 1000 || recargoTaller > 300 ||
                !['carroceria', 'mecanica', 'desgaste'].includes(tipo)) {
                mostrarErrorCalculo('res-desguace', 'Revisa los importes: precios y costes entre 0 y 100.000 €, horas entre 0 y 100, tarifa entre 0 y 1.000 €/h y recargo entre 0 y 300 %.');
                return;
            }

            const costeUsadoDIY = precioUsado + logisticaUsado;
            const costeNuevoDIY = precioNuevo + envioNuevo;
            const manoObraTaller = horas * tarifaHora;
            const recargoPiezaTaller = precioNuevo * recargoTaller / 100;
            const costeTaller = precioNuevo + envioNuevo + recargoPiezaTaller + manoObraTaller;

            const opciones = [
                { nombre: 'Pieza usada + montaje propio', total: costeUsadoDIY, clave: 'usado' },
                { nombre: 'Pieza nueva + montaje propio', total: costeNuevoDIY, clave: 'nuevo' },
                { nombre: 'Pieza nueva + taller', total: costeTaller, clave: 'taller' }
            ];
            const opcionesComparables = tipo === 'desgaste'
                ? opciones.filter(opcion => opcion.clave !== 'usado')
                : opciones;
            const minimo = Math.min(...opcionesComparables.map(opcion => opcion.total));
            const ganadoras = opcionesComparables.filter(opcion => Math.abs(opcion.total - minimo) < 0.01);
            const fmt = valor => valor.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' });

            let recomendacion;
            let claseRecomendacion;
            if (tipo === 'desgaste') {
                claseRecomendacion = 'bg-amber-50 text-amber-900 border-amber-200';
                recomendacion = ganadoras.length > 1
                    ? 'Las alternativas con pieza nueva están prácticamente empatadas (' + fmt(minimo) + '). Compara referencia exacta, garantía, calidad y montaje. Para frenos, amortiguadores, distribución y otros componentes críticos, evita la pieza usada.'
                    : 'Según tus importes, la alternativa nueva más económica es ' + ganadoras[0].nombre.toLowerCase() + ' (' + fmt(minimo) + '). Para esta familia de seguridad/desgaste, no recomendamos la pieza usada.';
            } else if (ganadoras.length > 1) {
                claseRecomendacion = 'bg-amber-50 text-amber-900 border-amber-200';
                recomendacion = 'Las alternativas más económicas están prácticamente empatadas (' + fmt(minimo) + '). Decide según compatibilidad, estado, garantía, plazo y coste de montaje.';
            } else {
                claseRecomendacion = 'bg-emerald-50 text-emerald-900 border-emerald-200';
                recomendacion = 'Con los datos que has introducido, la opción más económica es ' + ganadoras[0].nombre.toLowerCase() + ' (' + fmt(minimo) + '), antes de los costes que falten. Verifica compatibilidad, estado, devolución y garantía antes de comprar.';
            }

            function tarjeta(titulo, total, detalle, nota, clave, advertencia) {
                const seleccionada = ganadoras.some(opcion => opcion.clave === clave);
                const borde = seleccionada ? 'border-emerald-400 ring-1 ring-emerald-200' : 'border-slate-200';
                const aviso = advertencia ? '<div class="mt-3 text-xs font-bold text-rose-700">' + advertencia + '</div>' : '';
                return '<div class="bg-white p-4 rounded-xl border ' + borde + '">' +
                    '<div class="text-xs text-slate-500">' + titulo + '</div>' +
                    '<div class="text-2xl font-extrabold text-slate-900 mt-1">' + fmt(total) + '</div>' +
                    '<div class="mt-2 text-[11px] text-slate-500">' + detalle + '</div>' +
                    '<div class="mt-2 text-[11px] text-slate-500">' + nota + '</div>' +
                    aviso + '</div>';
            }

            const diferenciaUsadoNuevo = costeUsadoDIY - costeNuevoDIY;
            const diferenciaNuevoTaller = costeNuevoDIY - costeTaller;
            const cajaResultado = document.getElementById('res-desguace');
            if (!cajaResultado) return;
            cajaResultado.className = 'mt-6 p-5 rounded-xl bg-slate-50 border border-slate-200';
            cajaResultado.innerHTML =
                '<div class="p-3.5 rounded-xl border font-semibold text-xs sm:text-sm mb-4 ' + claseRecomendacion + '">' + recomendacion + '</div>' +
                '<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">' +
                    tarjeta('1. Pieza usada + montaje propio', costeUsadoDIY,
                        'Pieza ' + fmt(precioUsado) + ' + transporte/gestión ' + fmt(logisticaUsado),
                        'Verifica referencia OEM, estado, prueba, devolución y garantía ofrecida por el vendedor.',
                        'usado',
                        tipo === 'desgaste' ? 'No recomendada para esta familia crítica.' : '') +
                    tarjeta('2. Pieza nueva + montaje propio', costeNuevoDIY,
                        'Pieza ' + fmt(precioNuevo) + ' + envío ' + fmt(envioNuevo),
                        'Confirma la referencia con marca, modelo, año, motor y número OEM/VIN cuando proceda.',
                        'nuevo', '') +
                    tarjeta('3. Pieza nueva + taller', costeTaller,
                        'Pieza ' + fmt(precioNuevo) + ' + recargo ' + fmt(recargoPiezaTaller) + ' + envío ' + fmt(envioNuevo) + ' + mano de obra ' + fmt(manoObraTaller),
                        horas.toLocaleString('es-ES') + ' h × ' + fmt(tarifaHora) + '/h. Simulación editable; no es una oferta de un taller real.',
                        'taller', '') +
                '</div>' +
                '<div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">' +
                    '<div class="p-3 rounded-lg bg-white border"><div class="text-slate-500">Diferencia usado frente a nuevo DIY</div><div class="font-bold ' + (diferenciaUsadoNuevo <= 0 ? 'text-emerald-700' : 'text-amber-700') + '">' +
                        (diferenciaUsadoNuevo <= 0 ? 'Usado cuesta ' + fmt(Math.abs(diferenciaUsadoNuevo)) + ' menos o igual' : 'Usado cuesta ' + fmt(diferenciaUsadoNuevo) + ' más') +
                    '</div></div>' +
                    '<div class="p-3 rounded-lg bg-white border"><div class="text-slate-500">Diferencia nuevo DIY frente a taller</div><div class="font-bold">' +
                        (diferenciaNuevoTaller > 0 ? 'El taller cuesta ' + fmt(diferenciaNuevoTaller) + ' menos' : diferenciaNuevoTaller < 0 ? 'El taller cuesta ' + fmt(Math.abs(diferenciaNuevoTaller)) + ' más' : 'Mismo coste estimado') +
                    '</div></div>' +
                '</div>' +
                '<p class="mt-4 text-[11px] leading-relaxed text-slate-500">Estimación con tus datos. Los precios del catálogo son ejemplos y pueden no coincidir con el mercado. No incluye automáticamente IVA adicional, diagnosis, consumibles, devolución de casco, transporte imprevisto, herramienta, alineación, programación/codificación ni otras operaciones, salvo que las añadas a los importes. El coste final y la garantía dependen del vendedor y del taller.</p>';
        }

        function diametroNeumatico(ancho, perfil, llanta) {
            return (2 * ancho * (perfil / 100)) + (llanta * 25.4);
        }

        function aplicarPresetCoche() {
            const val = document.getElementById('preset-coche').value;
            if (!val) return;
            const p = val.split(',');
            document.getElementById('ancho1').value = p[0];
            document.getElementById('perfil1').value = p[1];
            document.getElementById('llanta1').value = p[2];
            document.getElementById('ancho2').value = p[3];
            document.getElementById('perfil2').value = p[4];
            document.getElementById('llanta2').value = p[5];
            calcularITV();
        }

        function cargarMedidaCandidata(ancho, perfil, llanta) {
            document.getElementById('ancho2').value = ancho;
            document.getElementById('perfil2').value = perfil;
            document.getElementById('llanta2').value = llanta;
            cambiarTab('itv');
            calcularITV();
            document.getElementById('sec-itv').scrollIntoView({ behavior: 'smooth' });
        }

        function dibujarComparadorSVG(a1, p1, l1, d1, a2, p2, l2, d2) {
            const cont = document.getElementById('svg-comparador');
            if (!cont) return;
            const escala = 110 / Math.max(d1, d2, 500);
            const rExt1 = (d1 / 2) * escala;
            const rLlanta1 = ((l1 * 25.4) / 2) * escala;
            const rExt2 = (d2 / 2) * escala;
            const rLlanta2 = ((l2 * 25.4) / 2) * escala;

            const w1 = a1 * escala * 0.65;
            const w2 = a2 * escala * 0.65;

            cont.innerHTML = `
                <svg viewBox="0 0 420 150" class="w-full max-w-lg h-36">
                    <text x="95" y="15" text-anchor="middle" class="text-[10px] fill-slate-500 font-semibold">Diámetro lateral</text>
                    <circle cx="95" cy="82" r="${rExt1.toFixed(1)}" fill="none" stroke="#334155" stroke-width="8" opacity="0.85"/>
                    <circle cx="95" cy="82" r="${rLlanta1.toFixed(1)}" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="3,2"/>
                    <circle cx="95" cy="82" r="${rExt2.toFixed(1)}" fill="none" stroke="#f59e0b" stroke-width="4"/>
                    <circle cx="95" cy="82" r="${rLlanta2.toFixed(1)}" fill="none" stroke="#d97706" stroke-width="1.5"/>

                    <text x="295" y="15" text-anchor="middle" class="text-[10px] fill-slate-500 font-semibold">Ancho de pisada (${a1} vs. ${a2} mm)</text>
                    <rect x="${(260 - w1/2).toFixed(1)}" y="${(82 - rExt1).toFixed(1)}" width="${w1.toFixed(1)}" height="${(rExt1*2).toFixed(1)}" rx="6" fill="#334155" opacity="0.85"/>
                    <rect x="${(330 - w2/2).toFixed(1)}" y="${(82 - rExt2).toFixed(1)}" width="${w2.toFixed(1)}" height="${(rExt2*2).toFixed(1)}" rx="6" fill="#f59e0b" opacity="0.9"/>
                </svg>
            `;
        }

        function calcularITV() {
            const elA1 = document.getElementById('ancho1');
            if (!elA1) return;
            const a1 = leerNumeroCampo('ancho1');
            const p1 = leerNumeroCampo('perfil1');
            const l1 = leerNumeroCampo('llanta1');
            const a2 = leerNumeroCampo('ancho2');
            const p2 = leerNumeroCampo('perfil2');
            const l2 = leerNumeroCampo('llanta2');
            const c1 = leerNumeroCampo('carga1');
            const c2 = leerNumeroCampo('carga2');
            const v1 = leerNumeroCampo('vel1');
            const v2 = leerNumeroCampo('vel2');
            const medidas = [a1, p1, l1, a2, p2, l2, c1, c2, v1, v2];
            if (medidas.some(valor => valor === null) ||
                !Number.isInteger(a1) || !Number.isInteger(a2) ||
                !Number.isInteger(p1) || !Number.isInteger(p2) ||
                !Number.isInteger(l1) || !Number.isInteger(l2) ||
                !Number.isInteger(c1) || !Number.isInteger(c2) ||
                !Number.isInteger(v1) || !Number.isInteger(v2) ||
                a1 < 100 || a1 > 355 || a2 < 100 || a2 > 355 ||
                p1 < 20 || p1 > 100 || p2 < 20 || p2 > 100 ||
                l1 < 10 || l1 > 25 || l2 < 10 || l2 > 25 ||
                c1 < 60 || c1 > 125 || c2 < 60 || c2 > 125 ||
                v1 < 80 || v1 > 350 || v2 < 80 || v2 > 350) {
                mostrarErrorCalculo('res-itv', 'Revisa las medidas y los índices: ancho 100–355 mm, perfil 20–100 %, llanta 10–25 pulgadas, carga 60–125 y velocidad 80–350 km/h. Usa enteros en estos campos.');
                return;
            }

            const d1 = diametroNeumatico(a1, p1, l1);
            const d2 = diametroNeumatico(a2, p2, l2);
            const diffPorcentaje = ((d2 - d1) / d1) * 100;
            const deltaAltura = (d2 - d1) / 2;
            const velReal120 = 120 * (d2 / d1);

            const okDiametro = Math.abs(diffPorcentaje) <= 3.0;
            const okCarga = c2 >= c1;
            const okVelocidad = v2 >= v1;
            const esEquivalente = okDiametro && okCarga && okVelocidad;
            const gargantaRec = GARGANTAS[a2] || '6.0" - 8.5"';

            let motivoAviso = '';
            if (!okDiametro) motivoAviso += '<li>La variación del diámetro supera el límite de referencia del ±3 %.</li>';
            if (!okCarga) motivoAviso += `<li>El índice de carga introducido (${c2}) es inferior al de referencia (${c1}).</li>`;
            if (!okVelocidad) motivoAviso += '<li>El índice de velocidad introducido es inferior al de referencia; comprueba las excepciones y condiciones aplicables con un especialista o la ITV.</li>';

            const box = document.getElementById('res-itv');
            box.className = 'mt-6 p-5 rounded-xl border ' + (esEquivalente ? 'bg-emerald-50 border-emerald-300 text-emerald-950' : 'bg-rose-50 border-rose-300 text-rose-950');

            box.innerHTML = `
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b ${esEquivalente ? 'border-emerald-200' : 'border-rose-200'}">
                    <span class="text-lg font-extrabold">${esEquivalente ? 'CUMPLE LOS CRITERIOS BÁSICOS CALCULADOS' : 'NO CUMPLE UNO O MÁS CRITERIOS BÁSICOS'}</span>
                    <span class="text-sm font-bold px-3 py-1 rounded-full ${okDiametro ? 'bg-emerald-200 text-emerald-900' : 'bg-rose-200 text-rose-900'}">
                        Variación: ${diffPorcentaje > 0 ? '+' : ''}${diffPorcentaje.toFixed(2)} %
                    </span>
                </div>
                <p class="mt-3 text-xs leading-relaxed">Este resultado es un prechequeo dimensional y de índices con los valores introducidos; no es una aprobación oficial ni verifica por sí solo homologación, medidas admitidas en la ficha técnica, perfil de llanta, ausencia de interferencias u otros requisitos. Confirma la compatibilidad antes de comprar o montar.</p>
                ${motivoAviso ? `<ul class="mt-3 text-xs list-disc list-inside text-rose-800 font-medium">${motivoAviso}</ul>` : ''}
                <div class="grid grid-cols-2 sm:grid-cols-5 gap-3 mt-4 text-sm">
                    <div class="bg-white/80 p-2.5 rounded-lg">
                        <div class="text-xs opacity-75">Diámetro orig.</div>
                        <div class="font-bold">${d1.toFixed(1)} mm</div>
                    </div>
                    <div class="bg-white/80 p-2.5 rounded-lg">
                        <div class="text-xs opacity-75">Diámetro nuevo</div>
                        <div class="font-bold">${d2.toFixed(1)} mm</div>
                    </div>
                    <div class="bg-white/80 p-2.5 rounded-lg">
                        <div class="text-xs opacity-75">Altura coche</div>
                        <div class="font-bold">${deltaAltura > 0 ? '+' : ''}${deltaAltura.toFixed(1)} mm</div>
                    </div>
                    <div class="bg-white/80 p-2.5 rounded-lg">
                        <div class="text-xs opacity-75">Ancho de llanta</div>
                        <div class="font-bold">${gargantaRec}</div>
                    </div>
                    <div class="bg-white/80 p-2.5 rounded-lg col-span-2 sm:col-span-1">
                        <div class="text-xs opacity-75">Vel. real (a 120)</div>
                        <div class="font-bold">${velReal120.toFixed(1)} km/h</div>
                    </div>
                </div>
            `;

            dibujarComparadorSVG(a1, p1, l1, d1, a2, p2, l2, d2);

            document.getElementById('cta-muchoneumatico').href = `https://www.muchoneumatico.com/buscar?controller=search&s=${a1}+${p1}+${l1}`;
            document.getElementById('txt-cta-mucho').innerText = `Muchoneumático ${a1}/${p1} R${l1}`;
            document.getElementById('cta-norauto').href = `https://www.norauto.es/c/47595-neumaticos.html?q=${a2}%2F${p2}R${l2}`;
            document.getElementById('cta-feuvert').href = `https://www.feuvert.es/neumaticos?q=${a2}+${p2}+${l2}`;
            document.getElementById('txt-cta-norauto').innerText = `Montaje ${a2}/${p2} R${l2}`;
            document.getElementById('cta-neumatico-orig').href = `https://www.amazon.es/s?k=neumaticos+${a1}+${p1}+R${l1}&tag=${AMAZON_TAG}`;
            document.getElementById('txt-cta-orig').innerText = `Amazon: ${a1}/${p1} R${l1} y V16`;
        }

        async function copiarEnlaceCalculo() {
            const a1 = document.getElementById('ancho1').value;
            const p1 = document.getElementById('perfil1').value;
            const l1 = document.getElementById('llanta1').value;
            const a2 = document.getElementById('ancho2').value;
            const p2 = document.getElementById('perfil2').value;
            const l2 = document.getElementById('llanta2').value;
            const params = new URLSearchParams({a1, p1, l1, a2, p2, l2});
            const url = `${window.location.origin}${window.location.pathname}?${params.toString()}`;
            const btn = document.getElementById('btn-compartir');
            try {
                if (!navigator.clipboard || typeof navigator.clipboard.writeText !== 'function') throw new Error('Clipboard no disponible');
                await navigator.clipboard.writeText(url);
                btn.innerText = '¡Enlace copiado!';
            } catch (error) {
                window.prompt('Copia este enlace para compartir el cálculo:', url);
                btn.innerText = 'Copia el enlace mostrado';
            }
            setTimeout(() => { btn.innerText = 'Copiar enlace'; }, 2500);
        }

        function leerParametrosURL() {
            const params = new URLSearchParams(window.location.search);
            if (params.has('a1')) document.getElementById('ancho1').value = params.get('a1');
            if (params.has('p1')) document.getElementById('perfil1').value = params.get('p1');
            if (params.has('l1')) document.getElementById('llanta1').value = params.get('l1');
            if (params.has('a2')) document.getElementById('ancho2').value = params.get('a2');
            if (params.has('p2')) document.getElementById('perfil2').value = params.get('p2');
            if (params.has('l2')) document.getElementById('llanta2').value = params.get('l2');
        }

        function calcularConsumo() {
            const elKm = document.getElementById('km-viaje');
            if (!elKm) return;
            const km = leerNumeroCampo('km-viaje');
            const l100 = leerNumeroCampo('litros-100');
            const precio = leerNumeroCampo('precio-litro');
            const peajes = leerNumeroCampo('peajes-viaje');
            const vel = leerNumeroCampo('vel-viaje');
            const personas = leerNumeroCampo('ocupantes');
            if (km === null || l100 === null || precio === null || peajes === null || vel === null || personas === null ||
                km < 0 || l100 < 0 || precio < 0 || peajes < 0 || vel <= 0 ||
                !Number.isInteger(personas) || personas < 1) {
                mostrarErrorCalculo('res-consumo', 'Revisa los datos: distancias, consumo, precio y peajes no pueden ser negativos; la velocidad debe ser mayor que cero y los ocupantes un entero positivo.');
                return;
            }

            const litrosTotales = (km / 100) * l100;
            const costeCombustible = litrosTotales * precio;
            const costeDirectoViaje = costeCombustible + peajes;
            const costeConDesgaste = costeDirectoViaje + (km * 0.06);
            const costePorPersona = costeDirectoViaje / personas;

            const horasTotales = km / vel;
            const h = Math.floor(horasTotales);
            const m = Math.round((horasTotales - h) * 60);

            document.getElementById('res-consumo').innerHTML = `
                <div class="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Combustible + peajes</div>
                        <div class="text-xl font-bold text-slate-900">${costeDirectoViaje.toFixed(2)} €</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Por ocupante (${personas})</div>
                        <div class="text-xl font-bold text-amber-600">${costePorPersona.toFixed(2)} €</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Litros necesarios</div>
                        <div class="text-xl font-bold text-slate-900">${litrosTotales.toFixed(1)} L</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Tiempo estimado</div>
                        <div class="text-lg font-bold text-slate-900">${h} h ${m} min</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border col-span-2 sm:col-span-1">
                        <div class="text-xs text-slate-500">Total con desgaste</div>
                        <div class="text-lg font-bold text-slate-700">${costeConDesgaste.toFixed(2)} €</div>
                    </div>
                </div>
            `;
        }

        function calcularAmortizacion() {
            const elKmAnual = document.getElementById('km-anual');
            if (!elKmAnual) return;
            const kmAnual = leerNumeroCampo('km-anual');
            const difPrecio = leerNumeroCampo('dif-precio');
            const aniosUso = leerNumeroCampo('anios-uso');
            const consA = leerNumeroCampo('cons-a');
            const precA = leerNumeroCampo('prec-a');
            const mantA = leerNumeroCampo('mant-a');
            const consB = leerNumeroCampo('cons-b');
            const precB = leerNumeroCampo('prec-b');
            const mantB = leerNumeroCampo('mant-b');
            const valores = [kmAnual, difPrecio, aniosUso, consA, precA, mantA, consB, precB, mantB];
            if (valores.some(valor => valor === null) || kmAnual <= 0 || difPrecio < 0 || aniosUso <= 0 ||
                [consA, precA, mantA, consB, precB, mantB].some(valor => valor < 0)) {
                mostrarErrorCalculo('res-amortizacion', 'Introduce kilómetros anuales y años de uso mayores que cero. El sobreprecio, los consumos, precios de combustible y mantenimientos no pueden ser negativos.');
                return;
            }

            const gastoAnualA = ((kmAnual / 100) * consA * precA) + mantA;
            const gastoAnualB = ((kmAnual / 100) * consB * precB) + mantB;
            const ahorroAnualNeto = gastoAnualA - gastoAnualB;
            const ahorroPorKm = ahorroAnualNeto / kmAnual;
            const balanceFinUso = (ahorroAnualNeto * aniosUso) - difPrecio;

            const box = document.getElementById('res-amortizacion');

            if (ahorroAnualNeto <= 0) {
                box.className = 'mt-4 p-4 rounded-xl bg-amber-50 border border-amber-200 text-sm font-semibold text-amber-900';
                box.textContent = 'Con estos datos (incluyendo mantenimiento), el vehículo B no genera ahorro anual respecto al vehículo A. No existe un plazo de amortización positivo.';
                return;
            }

            const kmParaAmortizar = difPrecio / ahorroPorKm;
            const aniosParaAmortizar = difPrecio / ahorroAnualNeto;

            box.innerHTML = `
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Ahorro neto anual</div>
                        <div class="text-xl font-bold text-emerald-600">${ahorroAnualNeto.toFixed(0)} €/año</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Km para amortizar</div>
                        <div class="text-xl font-bold text-slate-900">${Math.round(kmParaAmortizar).toLocaleString('es-ES')} km</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Punto de equilibrio</div>
                        <div class="text-xl font-bold text-amber-600">${aniosParaAmortizar.toFixed(1)} años</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Balance a los ${aniosUso} años</div>
                        <div class="text-xl font-extrabold ${balanceFinUso >= 0 ? 'text-emerald-700' : 'text-rose-700'}">${balanceFinUso >= 0 ? '+' : ''}${balanceFinUso.toFixed(0)} €</div>
                    </div>
                </div>
            `;
        }

        // 4B. Caballos fiscales (fórmula del Anexo V del RGV) + orientación DGT + impuestos.
        function calcularDGT() {
            const elMotor = document.getElementById('dgt-motor');
            if (!elMotor) return;
            const motor = elMotor.value;
            const anio = leerNumeroCampo('dgt-anio');
            const cc = leerNumeroCampo('dgt-cc');
            const cil = leerNumeroCampo('dgt-cil');
            const co2 = leerNumeroCampo('dgt-co2');
            const base = leerNumeroCampo('dgt-base');
            const anioActual = new Date().getFullYear();
            const cvfNoEstimableConEstosDatos = motor === 'electrico' || motor === 'phev';

            if (anio === null || !Number.isInteger(anio) || anio < 1980 || anio > anioActual + 1 ||
                co2 === null || co2 < 0 || base === null || base < 0 ||
                (!cvfNoEstimableConEstosDatos && (cc === null || cc <= 0 || cil === null || !Number.isInteger(cil) || cil < 1 || cil > 16))) {
                mostrarErrorCalculo('res-dgt', 'Revisa año, cilindrada, cilindros, emisiones y base imponible. Usa valores numéricos no negativos y un año de matriculación válido.');
                return;
            }

            // El Anexo V usa una fórmula distinta para motores eléctricos; para eléctricos puros y PHEV
            // no inferimos la potencia fiscal a partir de la cilindrada térmica.
            const cvf = cvfNoEstimableConEstosDatos
                ? null
                : Math.floor((0.08 * Math.pow(cc / cil, 0.6) * cil) * 100) / 100;

            // El tramo IVTM se muestra sin cuota; cada ayuntamiento puede aplicar coeficientes y bonificaciones.
            let tramoIVTM = "Consulta la ficha técnica";
            if (cvf !== null) {
                if (cvf < 8) tramoIVTM = "Menos de 8 CVF";
                else if (cvf < 12) tramoIVTM = "8–11,99 CVF";
                else if (cvf < 16) tramoIVTM = "12–15,99 CVF";
                else if (cvf < 20) tramoIVTM = "16–19,99 CVF";
                else tramoIVTM = "20 CVF o más";
            }

            // Una clasificación por año/motor solo puede ser orientativa; confirma el distintivo por matrícula.
            let etiqueta = "Sin distintivo estimado; confirmar en DGT";
            let colorEtiqueta = "bg-slate-200 text-slate-800";

            if (motor === "electrico") {
                etiqueta = "CERO probable para BEV; confirma por matrícula";
                colorEtiqueta = "bg-sky-200 text-sky-950";
            } else if (motor === "phev") {
                etiqueta = "CERO si autonomía eléctrica homologada ≥40 km; si no, ECO sujeto a Euro";
                colorEtiqueta = "bg-teal-200 text-teal-950";
            } else if (motor === "hibrido") {
                etiqueta = "ECO posible si cumple la norma Euro aplicable";
                colorEtiqueta = "bg-teal-200 text-teal-950";
            } else if (motor === "gasolina") {
                if (anio >= 2006) {
                    etiqueta = "C probable por año; confirma norma Euro";
                    colorEtiqueta = "bg-emerald-200 text-emerald-950";
                } else if (anio >= 2001) {
                    etiqueta = "B probable por año; confirma norma Euro";
                    colorEtiqueta = "bg-amber-200 text-amber-950";
                }
            } else if (motor === "diesel") {
                if (anio >= 2016) {
                    etiqueta = "C probable por año; confirma norma Euro";
                    colorEtiqueta = "bg-emerald-200 text-emerald-950";
                } else if (anio === 2015) {
                    etiqueta = "B o C según fecha y homologación; confirma en DGT";
                    colorEtiqueta = "bg-amber-200 text-amber-950";
                } else if (anio >= 2006) {
                    etiqueta = "B probable por año; confirma norma Euro";
                    colorEtiqueta = "bg-amber-200 text-amber-950";
                }
            }

            let tipoImpositivo = 0;
            if (motor !== 'electrico') {
                if (co2 > 120 && co2 < 160) tipoImpositivo = 4.75;
                else if (co2 >= 160 && co2 < 200) tipoImpositivo = 9.75;
                else if (co2 >= 200) tipoImpositivo = 14.75;
            }
            const cuotaImpuesto = base * (tipoImpositivo / 100);

            document.getElementById('res-dgt').innerHTML = `
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center items-center">
                    <div class="p-3 rounded-lg font-bold ${colorEtiqueta}">
                        <div class="text-xs opacity-75">Distintivo DGT (orientativo)</div>
                        <div class="text-xs sm:text-sm mt-1">${etiqueta}</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Potencia fiscal (BOE)</div>
                        <div class="text-xl font-extrabold text-slate-900">${cvf === null ? 'No estimable con estos datos' : cvf.toFixed(2) + ' CVF'}</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Tramo fiscal IVTM (sin cuota local)</div>
                        <div class="text-xs font-bold text-slate-800 mt-1">${tramoIVTM}</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">IEDMT de referencia (${tipoImpositivo}%)</div>
                        <div class="text-xl font-bold text-amber-600">${cuotaImpuesto.toFixed(0)} €</div>
                    </div>
                </div>
            `;
        }

        function leerPreferenciaPrivacidad() {
            try {
                const guardada = localStorage.getItem(AUTOCALC_CONSENT_KEY);
                if (!guardada) return null;
                const datos = JSON.parse(guardada);
                const maxEdadMs = 180 * 24 * 60 * 60 * 1000;
                if (!datos || !['analytics', 'essential'].includes(datos.choice) ||
                    !Number.isFinite(datos.timestamp) || Date.now() - datos.timestamp > maxEdadMs ||
                    datos.timestamp > Date.now()) {
                    localStorage.removeItem(AUTOCALC_CONSENT_KEY);
                    return null;
                }
                return datos.choice;
            } catch (error) {
                return null;
            }
        }

        function guardarPreferenciaPrivacidad(valor) {
            try {
                localStorage.setItem(AUTOCALC_CONSENT_KEY, JSON.stringify({
                    choice: valor,
                    timestamp: Date.now()
                }));
            } catch (error) {
                // Si el navegador bloquea el almacenamiento local, la elección solo se aplica en esta página.
            }
        }

        function eliminarCookiesAnalitica() {
            const cookies = document.cookie ? document.cookie.split(';') : [];
            const secure = window.location.protocol === 'https:' ? '; Secure' : '';
            cookies.forEach((cookie) => {
                const nombre = cookie.split('=')[0].trim();
                if (!/^_ga(?:_|$)/.test(nombre)) return;
                const expirada = nombre + '=; Max-Age=0; path=/; SameSite=Lax' + secure;
                document.cookie = expirada;
                if (window.location.hostname) {
                    document.cookie = expirada + '; domain=' + window.location.hostname;
                }
            });
        }

        function actualizarAnalitica(permitir) {
            if (!GOOGLE_ANALYTICS_ID) return;

            const claveDesactivacion = 'ga-disable-' + GOOGLE_ANALYTICS_ID;
            window[claveDesactivacion] = !permitir;

            if (!permitir) {
                if (typeof window.gtag === 'function') {
                    window.gtag('consent', 'update', {
                        analytics_storage: 'denied',
                        ad_storage: 'denied',
                        ad_user_data: 'denied',
                        ad_personalization: 'denied'
                    });
                }
                eliminarCookiesAnalitica();
                return;
            }

            if (document.querySelector('script[data-autocalc-analytics]')) {
                if (typeof window.gtag === 'function') {
                    window.gtag('consent', 'update', { analytics_storage: 'granted' });
                }
                return;
            }

            window.dataLayer = window.dataLayer || [];
            window.gtag = window.gtag || function() { window.dataLayer.push(arguments); };
            window.gtag('consent', 'default', {
                analytics_storage: 'denied',
                ad_storage: 'denied',
                ad_user_data: 'denied',
                ad_personalization: 'denied',
                wait_for_update: 500
            });
            window.gtag('js', new Date());
            window.gtag('consent', 'update', {
                analytics_storage: 'granted',
                ad_storage: 'denied',
                ad_user_data: 'denied',
                ad_personalization: 'denied'
            });
            window.gtag('config', GOOGLE_ANALYTICS_ID, {
                allow_google_signals: false,
                allow_ad_personalization_signals: false
            });

            const script = document.createElement('script');
            script.async = true;
            script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GOOGLE_ANALYTICS_ID);
            script.dataset.autocalcAnalytics = 'true';
            document.head.appendChild(script);
        }

        function gestionarCookies(modo) {
            const aceptarAnalitica = modo === 'analytics';
            guardarPreferenciaPrivacidad(aceptarAnalitica ? 'analytics' : 'essential');
            actualizarAnalitica(aceptarAnalitica);
            document.getElementById('cookie-banner').classList.add('hidden');
        }

        function mostrarPreferenciasCookies() {
            document.getElementById('cookie-banner').classList.remove('hidden');
        }

        function filtrarMapaWeb() {
            const input = document.getElementById('buscador-mapa');
            if (!input) return;
            const filtro = input.value.toLowerCase();
            document.querySelectorAll('.item-mapa').forEach(el => {
                el.style.display = el.innerText.toLowerCase().includes(filtro) ? '' : 'none';
            });
        }

        window.addEventListener('DOMContentLoaded', () => {
            leerParametrosURL();
            cambiarTab(TAB_INICIAL);
            calcularITV();
            calcularET();
            calcularConsumo();
            calcularConsumoReal();
            calcularAmortizacion();
            calcularMatricula();
            calcularDGT();
            mostrarFalloOBD();
            evaluarChecklist();
            calcularDesguace();
            const preferenciaPrivacidad = leerPreferenciaPrivacidad();
            if (preferenciaPrivacidad === 'analytics') {
                actualizarAnalitica(true);
            } else if (preferenciaPrivacidad === 'essential') {
                // Analytics no se ha cargado; borrar posibles cookies heredadas de la versión anterior.
                eliminarCookiesAnalitica();
            } else {
                // Los consentimientos antiguos no se consideran válidos y sus cookies se limpian antes de volver a preguntar.
                eliminarCookiesAnalitica();
                document.getElementById('cookie-banner').classList.remove('hidden');
            }
        });
    </script>
</body>
</html>
"""


def render_page(
    filename, title, meta_desc, h1, subtitle,
    a1, p1, l1, a2, p2, l2, km, l100, initial_tab,
    table_html, seo_text, internal_links, faqs,
    car_context_name="tu vehículo",
    car_short_name="recambios OEM",
    car_autodoc_query="filtros+pastillas+freno",
    robots="index, follow"
):
    canonical = f"{DOMINIO}/" if filename == "index.html" else f"{DOMINIO}/{filename}"
    adsense_script = ""
    if ADSENSE_CLIENT:
        adsense_script = f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>'

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "SoftwareApplication",
                "name": title,
                "applicationCategory": "UtilitiesApplication",
                "operatingSystem": "Web",
                "url": canonical,
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in faqs
                ]
            }
        ]
    }

    html = PLANTILLA_HTML
    replacements = {
        "__SITE_NAME__": SITE_NAME,
        "__PAGE_TITLE__": title,
        "__META_DESC__": meta_desc,
        "__CANONICAL_URL__": canonical,
        "__ROBOTS_META__": robots,
        "__ADSENSE_HEAD__": adsense_script,
        "__SCHEMA_JSON__": json.dumps(schema, ensure_ascii=False),
        "__H1_TITLE__": h1,
        "__HERO_SUBTITLE__": subtitle,
        "__VAL_A1__": str(a1),
        "__VAL_P1__": str(p1),
        "__VAL_L1__": str(l1),
        "__VAL_A2__": str(a2),
        "__VAL_P2__": str(p2),
        "__VAL_L2__": str(l2),
        "__VAL_KM__": str(km),
        "__VAL_L100__": str(l100),
        "__INITIAL_TAB__": initial_tab,
        "__PRECALC_TABLE_HTML__": table_html,
        "__SEO_TEXT_BLOCK__": seo_text,
        "__INTERNAL_LINKS_HTML__": internal_links,
        "__AMAZON_TAG__": AMAZON_TAG,
        "__GOOGLE_ANALYTICS_ID__": GOOGLE_ANALYTICS_ID,
        "__GOOGLE_SITE_VERIFICATION_TAG__": GOOGLE_SITE_VERIFICATION_TAG,
        "__CAR_CONTEXT_NAME__": car_context_name,
        "__CAR_SHORT_NAME__": car_short_name,
        "__CAR_AUTODOC_QUERY__": car_autodoc_query
    }

    for k, v in replacements.items():
        html = html.replace(k, v)

    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as out:
        out.write(html)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sitemap_urls = []

    favicon_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="#0f172a" stroke="#f59e0b" stroke-width="4"/><circle cx="32" cy="32" r="14" fill="none" stroke="#f59e0b" stroke-width="3"/></svg>'
    with open(os.path.join(OUTPUT_DIR, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(favicon_svg)

    chips = []
    for slug_z, nombre_z, _, _, _ in ZONAS_DESGUACES_ITV:
        chips.append(f'<a href="desguaces-itv-{slug_z}.html" class="text-xs bg-amber-50 hover:bg-amber-200 text-slate-900 font-semibold px-2.5 py-1 rounded border border-amber-300 transition">Desguaces e ITV: {nombre_z}</a>')

    for slug_c, nombre_c, _, _, _, _, _, _, _ in MODELOS_COCHES[:16]:
        chips.append(f'<a href="neumaticos-itv-{slug_c}.html" class="text-xs bg-white hover:bg-amber-100 text-slate-700 px-2.5 py-1 rounded border border-slate-300 transition">ITV {nombre_c}</a>')

    vistas = set()
    for a1, p1, l1, _, _, _, _ in MEDIDAS_ESPANA:
        if (a1, p1, l1) not in vistas and len(chips) < 42:
            vistas.add((a1, p1, l1))
            slug = f"equivalencia-neumaticos-{a1}-{p1}-r{l1}.html"
            chips.append(f'<a href="{slug}" class="text-xs bg-white hover:bg-amber-100 text-slate-700 px-2.5 py-1 rounded border border-slate-300 transition">Neumáticos {a1}/{p1} R{l1}</a>')

    internal_links_html = "\n".join(chips)

    faqs_home = [
        ("¿Cómo saber la fecha de matriculación de un coche por su matrícula?",
         "En la pestaña 4 (Matrículas, CVF y DGT) puedes introducir las 3 letras de cualquier matrícula española desde el año 2000 para obtener el mes y año exacto de matriculación, su etiqueta DGT y cuándo le corresponde pasar la ITV."),
        ("¿Cómo se calculan los caballos fiscales (CVF) de un coche en España?",
         "Se aplica la fórmula oficial del Anexo V del Reglamento General de Vehículos: CVF = 0,08 × (cilindrada / número de cilindros)^0,6 × número de cilindros.")
    ]
    seo_home = """
        <h2 class="text-base font-bold text-slate-900">Portal técnico del motor: equivalencias ITV, matrículas, gasolineras en tiempo real y recambios</h2>
        <p>En <strong>AutoCalc España</strong> dispones de todas las calculadoras esenciales para el conductor y el mecánico: equivalencia de neumáticos ITV (±3 %) y desplazamiento ET de llantas, precio de gasolineras hoy en tiempo real conectado al Ministerio, cálculo de consumo real de depósito, datador de matrículas españolas, calculadora de potencia fiscal (caballos fiscales CVF), diccionario de averías OBD2 y comparador de recambios entre <strong>Autodoc, Muchoneumático, Norauto, Feu Vert, Amazon y grandes desguaces</strong>.</p>
    """
    render_page(
        "index.html",
        f"Calculadora de neumáticos ITV, matrículas, consumo y gasolineras | {SITE_NAME}",
        "Calculadoras de motor: equivalencia de neumáticos ITV y ET, fecha por matrícula, caballos fiscales CVF, gasolineras baratas hoy, consumo real y recambios.",
        "Calculadoras técnicas de ITV, matrículas, gasolineras y recambios",
        "Equivalencias ITV y ET, datador de matrículas, caballos fiscales, gasolineras en vivo y comparador Autodoc, Muchoneumático, Norauto y desguaces.",
        205, 55, 16, 225, 45, 17, 450, 5.8, "itv",
        generar_tabla_equivalencias_html(205, 55, 16), seo_home, internal_links_html, faqs_home
    )
    sitemap_urls.append(("index.html", f"{DOMINIO}/", "Portada principal - Suite completa de calculadoras de motor"))

    procesadas = set()
    for a1, p1, l1, a2, p2, l2, modelos in MEDIDAS_ESPANA:
        if (a1, p1, l1) in procesadas:
            continue
        procesadas.add((a1, p1, l1))

        slug = f"equivalencia-neumaticos-{a1}-{p1}-r{l1}.html"
        d1 = calcular_diametro(a1, p1, l1)
        d2 = calcular_diametro(a2, p2, l2)
        diff = ((d2 - d1) / d1) * 100.0
        garganta = GARGANTA_POR_ANCHO.get(a1, '6.0" - 7.5"')

        seo_medida = f"""
            <h2 class="text-base font-bold text-slate-900">Ficha técnica y comparativa de precios del neumático {a1}/{p1} R{l1}</h2>
            <p>Esta página usa <strong>{a1}/{p1} R{l1}</strong> como medida de referencia y relaciona modelos que pueden encontrarse en catálogos con esa medida: <em>{modelos}</em>. El montaje real depende de versión, año, acabado y ficha técnica; esta lista no garantiza que sea medida de serie. Su diámetro exterior calculado es <strong>{d1:.1f} mm</strong> y la garganta orientativa indicada es <strong>{garganta}</strong>.</p>
            <p>Puedes comparar ofertas en <strong>Muchoneumático</strong>, <strong>Amazon</strong>, <strong>Norauto</strong> y <strong>Feu Vert</strong>. Comprueba que la medida que compres está admitida para tu versión antes de pedirla: la medida candidata <strong>{a2}/{p2} R{l2}</strong> presenta una variación de diámetro del {diff:+.2f} %, pero el porcentaje por sí solo no confirma la equivalencia reglamentaria ni la compatibilidad.</p>
        """
        faqs_medida = [
            (f"¿Qué medidas son equivalentes a {a1}/{p1} R{l1} en la ITV?",
             f"El intervalo entre {d1*0.97:.1f} mm y {d1*1.03:.1f} mm representa únicamente el ±3 % matemático del diámetro de referencia. No basta para declarar equivalencia ITV: confirma las medidas admitidas, índices de carga y velocidad, y el resto de requisitos aplicables."),
            (f"¿Dónde comprar neumáticos {a1}/{p1} R{l1} al mejor precio?",
             f"En la tabla superior puedes comparar precios directos en Muchoneumático (especialista en ruedas), Norauto y Feu Vert (con montaje en taller) y Amazon España.")
        ]

        render_page(
            slug,
            f"Comparador de neumáticos {a1}/{p1} R{l1} | Diámetro, medidas y precios",
            f"Compara diámetros de neumáticos respecto a {a1}/{p1} R{l1} ({d1:.1f} mm), consulta medidas de referencia y precios. Verifica ficha técnica, homologación e índices antes de comprar.",
            f"Comparador de diámetro de neumáticos {a1}/{p1} R{l1}",
            f"Diámetro: {d1:.1f} mm · Garganta: {garganta} · Común en: {modelos}.",
            a1, p1, l1, a2, p2, l2, 450, 5.8, "itv",
            generar_tabla_equivalencias_html(a1, p1, l1), seo_medida, internal_links_html, faqs_medida,
            car_context_name=f"la medida {a1}/{p1} R{l1}",
            car_short_name=f"{a1}/{p1} R{l1}",
            car_autodoc_query=f"neumaticos+{a1}+{p1}+R{l1}"
        )
        sitemap_urls.append((slug, f"{DOMINIO}/{slug}", f"Equivalencia de neumáticos {a1}/{p1} R{l1} ({modelos})"))

    for slug_c, nombre_c, a1, p1, l1, a2, p2, l2, l100 in MODELOS_COCHES:
        archivo_c = f"neumaticos-itv-{slug_c}.html"
        d1 = calcular_diametro(a1, p1, l1)
        d2 = calcular_diametro(a2, p2, l2)
        diff = ((d2 - d1) / d1) * 100.0
        garganta = GARGANTA_POR_ANCHO.get(a1, '6.0" - 7.5"')
        q_autodoc = nombre_c.replace(" ", "+")

        seo_coche = f"""
            <h2 class="text-base font-bold text-slate-900">Neumáticos equivalentes, recambios Autodoc y desguaces para {nombre_c}</h2>
            <p>Como referencia inicial para el <strong>{nombre_c}</strong>, se comparan las medidas <strong>{a1}/{p1} R{l1}</strong> y <strong>{a2}/{p2} R{l2}</strong> (variación de diámetro: {diff:+.2f} %). Las medidas montadas y admitidas dependen de la versión, el año y la ficha técnica. El porcentaje de diámetro por sí solo no confirma equivalencia ni validez para ITV: verifica homologación, índice de carga, código de velocidad, llanta y espacio disponible.</p>
            <p><strong>Consejo de ahorro en mantenimiento para {nombre_c}:</strong> para recambios de desgaste, compara el precio final, la referencia exacta, el envío y el montaje en distintos proveedores; para neumáticos, comprueba también la disponibilidad de montaje; y para piezas de carrocería, faros o retrovisores, contrasta en los desguaces el estado, la garantía y la compatibilidad de la pieza.</p>
        """
        faqs_coche = [
            (f"¿Qué neumáticos equivalentes puede montar un {nombre_c} para pasar la ITV?",
             f"Como referencia, {a2}/{p2} R{l2} presenta una variación de diámetro del {diff:+.2f} % respecto a {a1}/{p1} R{l1}. Es solo un filtro dimensional: confirma la medida en la ficha técnica y verifica los demás requisitos de homologación e ITV."),
            (f"¿Dónde comprar recambios baratos para {nombre_c}: Autodoc, Norauto o desguace?",
             f"Para consumibles y mecánica nueva (frenos, embrague, filtros) conviene Autodoc; para montaje rápido en el día destaca Norauto o Feu Vert; y para piezas de carrocería o módulos originales OEM de {nombre_c} el coste puede ser menor en desguaces, según estado, compatibilidad, disponibilidad y garantía.")
        ]

        render_page(
            archivo_c,
            f"Neumáticos equivalentes y recambios {nombre_c} ITV | Autodoc, Norauto y desguace",
            f"Medidas de neumáticos equivalentes en ITV para {nombre_c} ({a1}/{p1} R{l1} a {a2}/{p2} R{l2}) y comparador de recambios en Autodoc, Muchoneumático y Norauto.",
            f"Neumáticos equivalentes y recambios ITV para {nombre_c}",
            f"Medidas de referencia: {a1}/{p1} R{l1} y {a2}/{p2} R{l2} · Variación de diámetro: {diff:+.2f} % (debe verificarse en ficha técnica; no certifica equivalencia ITV).",
            a1, p1, l1, a2, p2, l2, 450, l100, "itv",
            generar_tabla_equivalencias_html(a1, p1, l1), seo_coche, internal_links_html, faqs_coche,
            car_context_name=nombre_c,
            car_short_name=nombre_c,
            car_autodoc_query=q_autodoc
        )
        sitemap_urls.append((archivo_c, f"{DOMINIO}/{archivo_c}", f"Neumáticos y recambios ITV para {nombre_c} ({a1}/{p1} R{l1})"))

    for slug_z, nombre_z, dist_z, desguaces_z, itv_z in ZONAS_DESGUACES_ITV:
        archivo_z = f"desguaces-itv-{slug_z}.html"
        seo_zona = f"""
            <h2 class="text-base font-bold text-slate-900">Guía práctica de desguaces, recambios y estaciones ITV en {nombre_z}</h2>
            <p><strong>Distancia y accesos:</strong> {dist_z}.</p>
            <p><strong>Principales núcleos de desguaces cercanos:</strong> {desguaces_z}. Pueden ser una alternativa para piezas de carrocería y componentes recuperados. El ahorro depende de la referencia, el estado, la disponibilidad, el transporte y la garantía; comprueba compatibilidad antes de comprar.</p>
            <p><strong>Estaciones ITV y talleres de montaje rápido en la zona:</strong> {itv_z}. Recuerda que para elementos de desgaste o seguridad (neumáticos, pastillas y discos de freno, amortiguadores, escobillas o filtros) siempre es recomendable pedir recambio nuevo en <strong>Autodoc</strong>, comprar neumáticos en <strong>Muchoneumático</strong> o acudir con cita a <strong>Norauto y Feu Vert</strong>.</p>
        """
        faqs_zona = [
            (f"¿Qué piezas compensa comprar en los desguaces cercanos a {nombre_z}?",
             f"En los centros de {desguaces_z} compensa comprar carrocería, ópticas, retrovisores, llantas sueltas, cuadros de instrumentos y motores de arranque; nunca elementos de desgaste como frenos o neumáticos."),
            (f"¿Dónde pasar la ITV y montar neumáticos cerca de {nombre_z}?",
             f"Cuentas con {itv_z}, además de envío directo a domicilio o taller concertado a través de Muchoneumático y Autodoc.")
        ]

        render_page(
            archivo_z,
            f"Desguaces, recambios e ITV en {nombre_z} | Comparador con Autodoc y Norauto",
            f"Guía y calculadora de ahorro en reparaciones para {nombre_z}: compara precios entre desguaces ({desguaces_z}), Autodoc, Muchoneumático y Norauto.",
            f"Desguaces, recambios e ITV en {nombre_z}",
            f"Compara cuándo compensa ir a desguace ({dist_z}) frente a pedir pieza nueva en Autodoc o montar en Norauto / Feu Vert.",
            205, 55, 16, 225, 45, 17, 48, 5.5, "desguace",
            generar_tabla_equivalencias_html(205, 55, 16), seo_zona, internal_links_html, faqs_zona,
            car_context_name=nombre_z,
            car_short_name="tu coche",
            car_autodoc_query="kit+mantenimiento+filtros+frenos"
        )
        sitemap_urls.append((archivo_z, f"{DOMINIO}/{archivo_z}", f"Guía de desguaces, talleres e ITV: {nombre_z}"))

    for orig, dest, km, l100 in RUTAS_ESPANA:
        slug_r = f"calcular-consumo-{orig.lower().replace(' ', '-')}-{dest.lower().replace(' ', '-')}.html"
        litros = (km / 100.0) * l100
        precio_referencia = 1.56  # Supuesto didáctico; no es el precio actual del combustible.
        coste = litros * precio_referencia

        seo_ruta = f"""
            <h2 class="text-base font-bold text-slate-900">Gasto de combustible en la ruta {orig} - {dest} ({km} km)</h2>
            <p>Estimación orientativa del trayecto entre <strong>{orig} y {dest}</strong>: unos <strong>{km} km</strong>. Con un consumo supuesto de {l100} L/100 km, necesitarías <strong>{litros:.1f} litros</strong>. El ejemplo arroja <strong>{coste:.2f} €</strong> usando un precio de referencia de {precio_referencia:.2f} €/L, que no representa el precio actual ni incluye peajes u otros gastos. Ajusta el precio en la calculadora según tu repostaje.</p>
        """
        faqs_ruta = [
            (f"¿Cuánto cuesta ir en coche de {orig} a {dest}?",
             f"Ejemplo para {orig}–{dest}: {litros:.1f} litros con un consumo supuesto de {l100} L/100 km. El coste orientativo de {coste:.2f} € utiliza {precio_referencia:.2f} €/L como referencia, no un precio actual.")
        ]

        render_page(
            slug_r,
            f"Calcular gasolina y coste de viaje {orig} - {dest} ({km} km)",
            f"Calcula cuántos litros y euros cuesta viajar en coche de {orig} a {dest} ({km} km) y divide el gasto por ocupante.",
            f"Coste de combustible: de {orig} a {dest} ({km} km)",
            f"Estimación para {km} km: {litros:.1f} litros. Ejemplo con precio de referencia de {precio_referencia:.2f} €/L: {coste:.2f} €; actualiza el precio antes de usarlo para presupuestar.",
            205, 55, 16, 225, 45, 17, km, l100, "consumo",
            "", seo_ruta, internal_links_html, faqs_ruta
        )
        sitemap_urls.append((slug_r, f"{DOMINIO}/{slug_r}", f"Calculadora de viaje {orig} a {dest} ({km} km)"))

    items_html = "".join([
        f'<li class="item-mapa py-2 px-3 bg-slate-50 rounded-lg border border-slate-200 hover:border-amber-400 transition">'
        f'<a href="{archivo}" class="text-slate-800 hover:text-amber-600 font-medium text-sm block">{label}</a></li>'
        for archivo, _, label in sitemap_urls
    ])
    bloque_mapa = f"""
    <div class="mt-8 bg-white p-6 rounded-2xl border border-slate-200">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <h2 class="text-lg font-bold text-slate-900">Buscador instantáneo ({len(sitemap_urls)} calculadoras y guías activas)</h2>
            <input type="text" id="buscador-mapa" oninput="filtrarMapaWeb()" placeholder="Buscar coche, medida o zona (ej. Aranjuez, Aimayr, Corsa, Primera...)" class="p-2.5 border rounded-xl text-sm w-full sm:w-80">
        </div>
        <ul class="grid grid-cols-1 md:grid-cols-2 gap-2">{items_html}</ul>
    </div>
    """
    render_page(
        "mapa-web.html",
        f"Buscador de medidas ITV, modelos de coche y desguaces | {SITE_NAME}",
        "Encuentra al instante la tabla de equivalencia de neumáticos de tu coche, guías de desguaces o calcula el gasto de combustible de tu ruta.",
        "Índice general y buscador por coche, medida ITV y zona",
        f"Filtra en tiempo real entre nuestras {len(sitemap_urls)} herramientas técnicas preconfiguradas.",
        205, 55, 16, 225, 45, 17, 450, 5.8, "itv",
        bloque_mapa, "", internal_links_html, faqs_home
    )

    contacto_publico = (
        f'<strong>{EMAIL_CONTACTO}</strong>'
        if EMAIL_CONTACTO and "tudominio" not in EMAIL_CONTACTO.lower()
        else '<strong>Pendiente de completar por el titular antes de la explotación comercial</strong>'
    )
    texto_legal = f"""
        <h2 class="text-lg font-bold text-slate-900">Aviso legal y condiciones de uso</h2>
        <p><strong>Portal:</strong> {SITE_NAME} ({DOMINIO}). <strong>Contacto:</strong> {contacto_publico}.</p>
        <p>El titular debe completar y revisar la información identificativa y los datos de contacto de este aviso antes de la explotación comercial. Este sitio ofrece cálculos informativos, no asesoramiento técnico ni una certificación administrativa.</p>
        <p>Los cálculos de equivalencia de neumáticos e impuestos son orientativos. Una diferencia de diámetro de ±3 % no demuestra por sí sola que una medida sea equivalente o admisible en ITV. Verifique ficha técnica, homologación, índice de carga, código de velocidad, compatibilidad mecánica y normativa aplicable antes de realizar modificaciones.</p>
    """
    render_page(
        "aviso-legal.html", f"Aviso legal | {SITE_NAME}", "Aviso legal y condiciones de uso del portal.",
        "Aviso legal y condiciones de uso", "Información legal conforme a la normativa LSSI-CE.",
        205, 55, 16, 225, 45, 17, 450, 5.8, "itv", "", texto_legal, internal_links_html, faqs_home, robots="noindex, follow"
    )

    texto_privacidad = f"""
        <h2 class="text-lg font-bold text-slate-900">Política de privacidad, cookies y afiliación</h2>
        <p><strong>1. Titular y contacto:</strong> {contacto_publico}. La identidad del responsable y los datos de contacto deben completarse y revisarse por el titular antes de la explotación comercial.</p>
        <p><strong>2. Analítica:</strong> Google Analytics 4 (si está configurado) solo se carga tras aceptar expresamente la opción «Aceptar analítica». Si se elige «Rechazar analítica», la etiqueta no se carga; si se revoca una aceptación durante la visita, se envía la señal de denegación cuando procede y se intenta eliminar las cookies de Analytics accesibles desde este dominio. La elección se recuerda en el almacenamiento local del navegador.</p>
        <p><strong>3. Cambiar la decisión:</strong> puede volver a abrir el aviso desde el enlace «Configurar cookies» del pie de página y cambiar su elección. Los enlaces a sitios de terceros se rigen también por las políticas de esos proveedores.</p>
        <p><strong>4. Publicidad:</strong> Google AdSense no está activado en la configuración actual. No deberá habilitarse hasta integrar una plataforma de gestión del consentimiento certificada por Google y compatible con el marco TCF para servir anuncios personalizados en los territorios en los que Google lo exige.</p>
        <p><strong>5. Afiliación:</strong> {SITE_NAME} incluye enlaces a comercios del sector del automóvil y participa en programas de afiliación, entre ellos Amazon. Si se compra desde algunos enlaces, el sitio puede recibir una comisión, sin coste adicional para el usuario. Las condiciones, precios, disponibilidad y posibles tecnologías de seguimiento dependen del comercio de destino.</p>
        <p>Este texto describe la implementación técnica del sitio, pero no sustituye la revisión legal del titular ni completa por sí solo la información necesaria sobre responsable, base jurídica, conservación de datos y ejercicio de derechos.</p>
    """
    render_page(
        "privacidad-cookies.html", f"Política de privacidad y cookies | {SITE_NAME}", "Política de privacidad, cookies y divulgación de afiliados.",
        "Política de privacidad y cookies (RGPD)", "Transparencia sobre cookies, Google AdSense y programas de afiliación.",
        205, 55, 16, 225, 45, 17, 450, 5.8, "itv", "", texto_privacidad, internal_links_html, faqs_home, robots="noindex, follow"
    )

    hoy = date.today().isoformat()
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for _, full_url, _ in sitemap_urls:
        xml += f"  <url>\n    <loc>{full_url}</loc>\n    <lastmod>{hoy}</lastmod>\n    <changefreq>monthly</changefreq>\n  </url>\n"
    xml += "</urlset>\n"

    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)

    with open(os.path.join(OUTPUT_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {DOMINIO}/sitemap.xml\n")

    # CNAME no configura GitHub Pages cuando se publica mediante Actions, pero
    # queda en el artefacto como registro coherente del modo de dominio elegido.
    cname_path = os.path.join(OUTPUT_DIR, "CNAME")
    if USE_CUSTOM_DOMAIN:
        with open(cname_path, "w", encoding="utf-8") as f:
            f.write(f"{CUSTOM_DOMAIN}\n")
    elif os.path.exists(cname_path):
        os.remove(cname_path)

    ads_txt_path = os.path.join(OUTPUT_DIR, "ads.txt")
    if ADSENSE_CLIENT:
        if not (ADSENSE_CLIENT.startswith("ca-pub-") and ADSENSE_CLIENT[7:].isdigit()):
            raise ValueError(
                "El valor adsense_client debe tener el formato ca-pub- seguido del identificador numérico de editor."
            )
        ads_pub = ADSENSE_CLIENT[3:]
        with open(ads_txt_path, "w", encoding="utf-8") as f:
            f.write(f"google.com, {ads_pub}, DIRECT, f08c47fec0942fa0\n")
    elif os.path.exists(ads_txt_path):
        # No publicar un registro ads.txt ficticio si AdSense aún no está configurado.
        os.remove(ads_txt_path)

    print(f"[OK] Portal v5.0 (Edicion dieselogasolina.com) generado en ./public con {len(sitemap_urls)} paginas SEO.")


if __name__ == "__main__":
    main()