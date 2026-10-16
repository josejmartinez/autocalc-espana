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
from datetime import date
from catalogo import MEDIDAS_ESPANA, MODELOS_COCHES, RUTAS_ESPANA, ZONAS_DESGUACES_ITV, GARGANTA_POR_ANCHO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "public")

with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
    CFG = json.load(f)

DOMINIO = CFG["domain"].rstrip("/")
AMAZON_TAG = CFG["amazon_tag"]
SITE_NAME = CFG["site_name"]
EMAIL_CONTACTO = CFG["contact_email"]
ADSENSE_CLIENT = CFG.get("adsense_client", "").strip()

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
                <h2 class="text-lg font-bold text-slate-900">Tabla oficial de equivalencias para {a_orig}/{p_orig} R{l_orig} (ITV ±3 %)</h2>
                <p class="text-xs text-slate-500">Diámetro original: <strong>{d_orig:.1f} mm</strong> · Rango legal permitido en ITV: <strong>{d_orig*0.97:.1f} mm a {d_orig*1.03:.1f} mm</strong> (pulsa en cualquier medida para simularla en el gráfico)</p>
            </div>
            <span class="text-xs bg-emerald-50 text-emerald-800 border border-emerald-200 px-3 py-1 rounded-full font-semibold w-fit">Sin homologar</span>
        </div>
        <table class="w-full text-left text-sm">
            <thead>
                <tr class="border-b-2 border-slate-200 text-xs text-slate-500">
                    <th class="py-2 px-3 font-semibold">Medida equivalente</th>
                    <th class="py-2 px-3 text-center font-semibold">Ancho de llanta</th>
                    <th class="py-2 px-3 text-center font-semibold">Diámetro</th>
                    <th class="py-2 px-3 text-center font-semibold">Variación ITV</th>
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
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-QN5542F4NX"></script>
    <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-QN5542F4NX');</script>
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
    <meta name="google-site-verification" content="ygUlG2Pg9SCogkqx8g4IBREETgPeDhS9pRcb2wbhPxE" />
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
                <p class="text-xs text-slate-500 mb-4">Calcula la potencia fiscal exacta según la fórmula del Anexo V del Reglamento General de Vehículos (BOE), el tramo del impuesto de circulación municipal (IVTM) y el impuesto de matriculación.</p>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Motorización</label>
                        <select id="dgt-motor" onchange="calcularDGT()" class="w-full p-2 border rounded-lg font-bold bg-white text-xs">
                            <option value="gasolina">Gasolina</option>
                            <option value="diesel" selected>Diésel</option>
                            <option value="hibrido">Híbrido / GLP (ECO)</option>
                            <option value="cero">Eléctrico / PHEV (0)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Año 1.ª matr.</label>
                        <input type="number" id="dgt-anio" value="2015" min="1980" max="2027" oninput="calcularDGT()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Cilindrada (cm³)</label>
                        <input type="number" id="dgt-cc" value="1968" oninput="calcularDGT()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">N.º cilindros</label>
                        <input type="number" id="dgt-cil" value="4" min="2" max="12" oninput="calcularDGT()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">CO₂ (g/km)</label>
                        <input type="number" id="dgt-co2" value="119" oninput="calcularDGT()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Valor coche (€)</label>
                        <input type="number" id="dgt-base" value="22000" oninput="calcularDGT()" class="w-full p-2 border rounded-lg font-bold">
                    </div>
                </div>
                <div id="res-dgt" class="mt-5 p-4 rounded-xl bg-slate-50 border border-slate-200"></div>
            </div>
        </section>

        <!-- ==================== SECCIÓN 5: CHECKLIST PRE-ITV Y BUSCADOR DE CÓDIGOS OBD2 ==================== -->
        <section id="sec-preitv" class="space-y-6 hidden">
            <!-- 5A. Buscador de códigos de avería OBD2 frecuentes en rechazo ITV -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold mb-1 text-slate-900">5A. Consultor rápido de códigos de fallo OBD2 críticos en la ITV</h2>
                <p class="text-xs text-slate-500 mb-4">Desde la entrada en vigor de la lectura OBD en las estaciones ITV, cualquier código de avería activo en la centralita (testigo MIL encendido) supone resultado desfavorable. Selecciona un código para ver causa y solución:</p>
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
                <p class="text-xs text-slate-500 mb-4">Verifica estos 6 puntos antes de salir hacia la estación ITV para evitar el 85 % de los rechazos más habituales:</p>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <label class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border cursor-pointer hover:bg-slate-100 transition">
                        <input type="checkbox" class="chk-itv mt-1 w-4 h-4" onchange="evaluarChecklist()" checked>
                        <div>
                            <span class="font-bold block text-slate-900">1. Dibujo de neumáticos (>1,6 mm) y medida dentro del ±3 %</span>
                            <span class="text-xs text-slate-500">Misma marca/modelo en cada eje, sin huevos ni cortes en los flancos.</span>
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
                <p class="text-xs text-slate-500 mb-4">Selecciona la pieza exacta que necesitas sustituir para cargar sus precios medios reales en España y descubrir dónde te ahorras más dinero sin comprometer la seguridad:</p>

                <div class="mb-4">
                    <label class="block text-xs font-bold text-slate-700 mb-1">Seleccionar pieza del catálogo rápido (autocompleta precios reales y tiempos de taller):</label>
                    <select id="pieza-catalogo" onchange="cargarPiezaCatalogo()" class="w-full p-2.5 border rounded-xl font-bold text-xs sm:text-sm bg-slate-50">
                        <option value="mecanica,50,145,1.5,alternador">Alternador (50 € desguace vs. 145 € nuevo Autodoc)</option>
                        <option value="mecanica,40,115,1.2,motor+de+arranque">Motor de arranque (40 € desguace vs. 115 € nuevo Autodoc)</option>
                        <option value="mecanica,85,240,2.5,compresor+aire+acondicionado">Compresor de aire acondicionado (85 € desguace vs. 240 € Autodoc)</option>
                        <option value="mecanica,140,380,3.5,turbocompresor">Turbocompresor (140 € desguace vs. 380 € reconstruido/nuevo)</option>
                        <option value="mecanica,220,950,5.0,caja+de+cambios">Caja de cambios manual (220 € desguace vs. 950 € reconstruida)</option>
                        <option value="mecanica,75,230,2.5,cremallera+direccion">Cremallera de dirección (75 € desguace vs. 230 € Autodoc)</option>
                        <option value="carroceria,35,110,0.5,faro+delantero">Faro delantero principal (35 € desguace vs. 110 € Autodoc)</option>
                        <option value="carroceria,25,65,0.3,piloto+trasero">Piloto trasero (25 € desguace vs. 65 € Autodoc)</option>
                        <option value="carroceria,30,85,0.4,retrovisor+exterior">Espejo retrovisor completo (30 € desguace vs. 85 € Autodoc)</option>
                        <option value="carroceria,65,190,1.5,paragolpes">Paragolpes delantero o trasero (65 € desguace vs. 190 € nuevo)</option>
                        <option value="carroceria,30,75,1.2,elevalunas+electrico">Mecanismo elevalunas eléctrico (30 € desguace vs. 75 € Autodoc)</option>
                        <option value="desgaste,40,115,1.5,valvula+egr">Válvula EGR nueva recomendada (40 € desguace vs. 115 € Autodoc)</option>
                        <option value="desgaste,35,85,1.5,discos+y+pastillas+de+freno">Juego de discos y pastillas de freno (¡Comprar siempre nuevo!)</option>
                        <option value="desgaste,50,130,2.0,amortiguadores">Pareja de amortiguadores (¡Comprar siempre nuevo en Autodoc/Norauto!)</option>
                        <option value="desgaste,90,340,5.5,kit+embrague+bimasa">Kit de embrague + volante bimasa (¡Comprar siempre nuevo en Autodoc!)</option>
                        <option value="desgaste,45,110,3.5,kit+distribucion+bomba+agua">Kit correa de distribución + bomba de agua (¡Siempre nuevo!)</option>
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
                        <input type="number" id="rep-desguace" value="50" oninput="calcularDesguace()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Precio nuevo Autodoc (€)</label>
                        <input type="number" id="rep-autodoc" value="145" oninput="calcularDesguace()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-600 mb-1">Horas de mano de obra</label>
                        <input type="number" step="0.5" id="rep-horas" value="1.5" oninput="calcularDesguace()" class="w-full p-2.5 border rounded-lg font-bold">
                    </div>
                </div>
                <div id="res-desguace" class="mt-6 p-5 rounded-xl bg-slate-50 border border-slate-200"></div>

                <!-- Enlaces directos a los grandes desguaces cerca de Aranjuez / Madrid Sur y tiendas online -->
                <div class="mt-6 pt-5 border-t border-slate-200">
                    <h3 class="text-xs font-bold text-slate-700 mb-3">Consultar stock de esta pieza en grandes desguaces (Aranjuez / Madrid Sur / Toledo) y tiendas online:</h3>
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
            </div>
        </div>
    </footer>

    <div id="cookie-banner" class="fixed bottom-0 inset-x-0 bg-slate-950/95 text-white p-4 border-t border-slate-800 z-50 hidden no-print">
        <div class="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
            <p class="text-slate-300">Utilizamos cookies propias y de terceros para recordar tus preferencias de cálculo, analizar el tráfico y mostrar enlaces patrocinados. Puedes consultar nuestra <a href="privacidad-cookies.html" class="underline text-amber-400">Política de privacidad y cookies</a>.</p>
            <div class="flex gap-2 shrink-0">
                <button onclick="gestionarCookies('essential')" class="px-3 py-2 rounded border border-slate-700 hover:bg-slate-800 transition">Solo necesarias</button>
                <button onclick="gestionarCookies('all')" class="px-4 py-2 rounded bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold transition">Aceptar todas</button>
            </div>
        </div>
    </div>

    <script>
        const AMAZON_TAG = "__AMAZON_TAG__";
        const TAB_INICIAL = "__INITIAL_TAB__";
        const GARGANTAS = {155:'4.5"-5.5"',165:'4.5"-6.0"',175:'5.0"-6.0"',185:'5.0"-6.5"',195:'5.5"-7.0"',205:'5.5"-7.5"',215:'6.0"-7.5"',225:'6.0"-8.0"',235:'6.5"-8.5"',245:'7.0"-9.0"',255:'7.5"-9.5"',265:'8.0"-10.0"',275:'8.5"-10.5"'};

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
            const j1 = parseFloat(document.getElementById('et-j1').value) || 6.5;
            const et1 = parseFloat(document.getElementById('et-off1').value) || 45;
            const j2 = parseFloat(document.getElementById('et-j2').value) || 7.5;
            const et2 = parseFloat(document.getElementById('et-off2').value) || 35;

            const w1 = j1 * 25.4;
            const w2 = j2 * 25.4;
            const deltaInterior = ((w2 - w1) / 2) - (et1 - et2);
            const deltaExterior = ((w2 - w1) / 2) + (et1 - et2);
            const cambioAnchoVias = (et1 - et2) * 2;
            const legalVias = Math.abs(cambioAnchoVias) <= 30;

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
                    <div class="p-3 rounded-lg border ${legalVias ? 'bg-emerald-50 border-emerald-200 text-emerald-900' : 'bg-rose-50 border-rose-200 text-rose-900'}">
                        <div class="text-xs opacity-75">Variación ancho de vías total</div>
                        <div class="font-extrabold mt-1">${cambioAnchoVias > 0 ? '+' : ''}${cambioAnchoVias.toFixed(0)} mm (${legalVias ? 'Legal ITV ≤30 mm' : 'Requiere homologar >30 mm'})</div>
                    </div>
                </div>
            `;
        }

        // 2B. Consumo real del depósito
        function calcularConsumoReal() {
            const litros = parseFloat(document.getElementById('real-litros').value) || 0;
            const km = parseFloat(document.getElementById('real-km').value) || 1;
            const precio = parseFloat(document.getElementById('real-precio').value) || 0;

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
                const resp = await fetch(`https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroMunicipio/${idMun}`);
                const data = await resp.json();
                const lista = data.ListaEESSPrecio || [];
                if (!lista.length) {
                    cont.innerHTML = `<div class="p-3 bg-slate-100 rounded-lg">No hay estaciones registradas en este municipio en este momento.</div>`;
                    return;
                }
                const parsePrecio = (str) => str ? parseFloat(str.replace(',', '.')) : 999;
                lista.sort((a, b) => parsePrecio(a["Precio Gasoleo A"]) - parsePrecio(b["Precio Gasoleo A"]));

                const top = lista.slice(0, 8);
                let filas = top.map(e => {
                    const pDiesel = e["Precio Gasoleo A"] || "-";
                    const pGas95 = e["Precio Gasolina 95 E5"] || "-";
                    return `
                        <tr class="border-b border-slate-100 hover:bg-slate-50">
                            <td class="py-2 px-2 font-bold text-slate-900">${e["Rótulo"]}</td>
                            <td class="py-2 px-2 text-slate-600">${e["Dirección"]} (${e["Localidad"]})</td>
                            <td class="py-2 px-2 text-center font-bold text-emerald-700">${pDiesel} €/L</td>
                            <td class="py-2 px-2 text-center font-bold text-amber-700">${pGas95} €/L</td>
                            <td class="py-2 px-2 text-right">
                                <button onclick="usarPrecioGasolinera('${pDiesel}', '${pGas95}')" class="text-[11px] bg-slate-800 hover:bg-slate-700 text-white px-2 py-1 rounded">Usar precio</button>
                            </td>
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

        function usarPrecioGasolinera(dieselStr, gas95Str) {
            const p = parseFloat((dieselStr !== "-" ? dieselStr : gas95Str).replace(',', '.'));
            if (!isNaN(p)) {
                document.getElementById('precio-litro').value = p.toFixed(3);
                document.getElementById('real-precio').value = p.toFixed(3);
                calcularConsumo();
                calcularConsumoReal();
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

            // Hitos históricos oficiales de la DGT (índice base 20 -> año.mes)
            const hitos = [
                [0, 2000.75], [140, 2001.0], [420, 2002.0], [680, 2003.0],
                [980, 2004.0], [1310, 2005.0], [1650, 2006.0], [2010, 2007.0],
                [2350, 2008.0], [2580, 2009.0], [2740, 2010.0], [2900, 2011.0],
                [3040, 2012.0], [3150, 2013.0], [3260, 2014.0], [3420, 2015.0],
                [3620, 2016.0], [3860, 2017.0], [4120, 2018.0], [4390, 2019.0],
                [4620, 2020.0], [4790, 2021.0], [4960, 2022.0], [5140, 2023.0],
                [5340, 2024.0], [5550, 2025.0], [5770, 2026.0], [6000, 2027.0]
            ];

            let fechaEst = 2026.5;
            for (let i = 0; i < hitos.length - 1; i++) {
                if (indice >= hitos[i][0] && indice <= hitos[i+1][0]) {
                    const ratio = (indice - hitos[i][0]) / (hitos[i+1][0] - hitos[i][0]);
                    fechaEst = hitos[i][1] + ratio * (hitos[i+1][1] - hitos[i][1]);
                    break;
                }
            }

            const anioMat = Math.floor(fechaEst);
            const mesIndex = Math.min(11, Math.max(0, Math.floor((fechaEst - anioMat) * 12)));
            const meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
            const edad = Math.max(0, (2026.78 - fechaEst));

            let frecuenciaITV = "Anual (cada año por tener más de 10 años)";
            if (edad < 4) frecuenciaITV = `Exento hasta los 4 años (1.ª ITV en ${anioMat + 4})`;
            else if (edad < 10) frecuenciaITV = "Bienal (cada 2 años hasta cumplir los 10 años)";

            // Sincronizar con la calculadora de año DGT inferior
            document.getElementById('dgt-anio').value = anioMat;
            calcularDGT();

            box.innerHTML = `
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Fecha estimada de matriculación</div>
                        <div class="text-lg font-extrabold text-slate-900 capitalize">${meses[mesIndex]} de ${anioMat}</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Antigüedad del vehículo</div>
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
                box.innerText = '¡Vehículo listo para inspección! Has verificado los 6 puntos críticos de rechazo en ITV.';
            } else {
                box.className = 'mt-4 p-4 rounded-xl bg-amber-50 border border-amber-200 text-sm font-semibold text-amber-900';
                box.innerText = `Progreso pre-ITV: ${marcados} de ${total} puntos críticos verificados. Revisa los pendientes antes de tu cita.`;
            }
        }

        // 6. Catálogo de piezas y calculadora Desguace vs. Autodoc vs. Taller
        function cargarPiezaCatalogo() {
            const val = document.getElementById('pieza-catalogo').value;
            if (!val) return;
            const p = val.split(',');
            document.getElementById('rep-tipo').value = p[0];
            document.getElementById('rep-desguace').value = p[1];
            document.getElementById('rep-autodoc').value = p[2];
            document.getElementById('rep-horas').value = p[3];
            const linkAutodoc = document.getElementById('link-pieza-autodoc');
            if (linkAutodoc) linkAutodoc.href = `https://www.autodoc.es/search?keyword=${p[4]}`;
            calcularDesguace();
        }

        function calcularDesguace() {
            const elTipo = document.getElementById('rep-tipo');
            if (!elTipo) return;
            const tipo = elTipo.value;
            const pDesguace = parseFloat(document.getElementById('rep-desguace').value) || 0;
            const pAutodoc = parseFloat(document.getElementById('rep-autodoc').value) || 0;
            const horas = parseFloat(document.getElementById('rep-horas').value) || 0;

            const manoObraTaller = horas * 52;
            const totalDesguaceDIY = pDesguace;
            const totalAutodocDIY = pAutodoc;
            const totalTallerMontado = (pAutodoc * 1.25) + manoObraTaller;
            const ahorroDesguace = pAutodoc - pDesguace;

            let recomendacion = "";
            let badgeColor = "bg-emerald-100 text-emerald-900 border-emerald-300";

            if (tipo === "desgaste") {
                recomendacion = "Elemento de desgaste o seguridad: NO se recomienda desguace. Pídelo nuevo en Autodoc (si lo montas tú) o acude a Norauto / Feu Vert con montaje incluido.";
                badgeColor = "bg-rose-100 text-rose-900 border-rose-300";
            } else if (ahorroDesguace < 25) {
                recomendacion = "Por una diferencia menor de 25 €, compensa estrenar recambio nuevo en Autodoc con 2 años de garantía frente a pieza usada.";
                badgeColor = "bg-amber-100 text-amber-900 border-amber-300";
            } else {
                recomendacion = `¡Compensa ir a desguace! Te ahorras ${ahorroDesguace.toFixed(0)} € respecto al recambio nuevo (ideal buscar en Polígono Aimayr de San Martín de la Vega, La Torre u Ocaña).`;
            }

            document.getElementById('res-desguace').innerHTML = `
                <div class="p-3.5 rounded-xl border font-semibold text-xs sm:text-sm mb-4 ${badgeColor}">
                    ${recomendacion}
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">1. Desguace (montaje propio)</div>
                        <div class="text-xl font-bold text-emerald-700">${totalDesguaceDIY.toFixed(0)} €</div>
                        <div class="text-[11px] text-slate-400">Pieza original recuperada OEM</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">2. Nuevo en Autodoc (DIY)</div>
                        <div class="text-xl font-bold text-orange-600">${totalAutodocDIY.toFixed(0)} €</div>
                        <div class="text-[11px] text-slate-400">Pieza nueva con garantía</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">3. Taller rápido (pieza + M.O.)</div>
                        <div class="text-xl font-bold text-slate-900">${totalTallerMontado.toFixed(0)} €</div>
                        <div class="text-[11px] text-slate-400">Estimado con ${horas} h de taller</div>
                    </div>
                </div>
            `;
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
            const a1 = parseFloat(elA1.value) || 205;
            const p1 = parseFloat(document.getElementById('perfil1').value) || 55;
            const l1 = parseFloat(document.getElementById('llanta1').value) || 16;
            const a2 = parseFloat(document.getElementById('ancho2').value) || 225;
            const p2 = parseFloat(document.getElementById('perfil2').value) || 45;
            const l2 = parseFloat(document.getElementById('llanta2').value) || 17;

            const c1 = parseInt(document.getElementById('carga1').value) || 91;
            const c2 = parseInt(document.getElementById('carga2').value) || 91;
            const v1 = parseInt(document.getElementById('vel1').value) || 240;
            const v2 = parseInt(document.getElementById('vel2').value) || 240;

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
            if (!okDiametro) motivoAviso += '<li>El diámetro supera el margen legal del ±3 %.</li>';
            if (!okCarga) motivoAviso += `<li>El índice de carga nuevo (${c2}) no puede ser inferior al original (${c1}).</li>`;
            if (!okVelocidad) motivoAviso += '<li>El código de velocidad es inferior al original (solo permitido en neumáticos de invierno M+S con etiqueta de aviso).</li>';

            const box = document.getElementById('res-itv');
            box.className = 'mt-6 p-5 rounded-xl border ' + (esEquivalente ? 'bg-emerald-50 border-emerald-300 text-emerald-950' : 'bg-rose-50 border-rose-300 text-rose-950');

            box.innerHTML = `
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b ${esEquivalente ? 'border-emerald-200' : 'border-rose-200'}">
                    <span class="text-lg font-extrabold">${esEquivalente ? 'APTO PARA ITV (medida equivalente legal)' : 'NO APTO PARA ITV (incumple requisitos)'}</span>
                    <span class="text-sm font-bold px-3 py-1 rounded-full ${okDiametro ? 'bg-emerald-200 text-emerald-900' : 'bg-rose-200 text-rose-900'}">
                        Variación: ${diffPorcentaje > 0 ? '+' : ''}${diffPorcentaje.toFixed(2)} %
                    </span>
                </div>
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

        function copiarEnlaceCalculo() {
            const a1 = document.getElementById('ancho1').value;
            const p1 = document.getElementById('perfil1').value;
            const l1 = document.getElementById('llanta1').value;
            const a2 = document.getElementById('ancho2').value;
            const p2 = document.getElementById('perfil2').value;
            const l2 = document.getElementById('llanta2').value;
            const url = `${window.location.origin}${window.location.pathname}?a1=${a1}&p1=${p1}&l1=${l1}&a2=${a2}&p2=${p2}&l2=${l2}`;
            navigator.clipboard.writeText(url);
            const btn = document.getElementById('btn-compartir');
            btn.innerText = '¡Enlace copiado!';
            setTimeout(() => { btn.innerText = 'Copiar enlace'; }, 2000);
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
            const km = parseFloat(elKm.value) || 0;
            const l100 = parseFloat(document.getElementById('litros-100').value) || 0;
            const precio = parseFloat(document.getElementById('precio-litro').value) || 0;
            const peajes = parseFloat(document.getElementById('peajes-viaje').value) || 0;
            const vel = Math.max(1, parseFloat(document.getElementById('vel-viaje').value) || 100);
            const personas = Math.max(1, parseInt(document.getElementById('ocupantes').value) || 1);

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
            const kmAnual = parseFloat(elKmAnual.value) || 1;
            const difPrecio = parseFloat(document.getElementById('dif-precio').value) || 0;
            const aniosUso = parseFloat(document.getElementById('anios-uso').value) || 8;
            const consA = parseFloat(document.getElementById('cons-a').value) || 0;
            const precA = parseFloat(document.getElementById('prec-a').value) || 0;
            const mantA = parseFloat(document.getElementById('mant-a').value) || 0;
            const consB = parseFloat(document.getElementById('cons-b').value) || 0;
            const precB = parseFloat(document.getElementById('prec-b').value) || 0;
            const mantB = parseFloat(document.getElementById('mant-b').value) || 0;

            const gastoAnualA = ((kmAnual / 100) * consA * precA) + mantA;
            const gastoAnualB = ((kmAnual / 100) * consB * precB) + mantB;
            const ahorroAnualNeto = gastoAnualA - gastoAnualB;
            const ahorroPorKm = ahorroAnualNeto / kmAnual;
            const balanceFinUso = (ahorroAnualNeto * aniosUso) - difPrecio;

            const box = document.getElementById('res-amortizacion');

            if (ahorroAnualNeto <= 0) {
                box.innerHTML = `<p class="text-rose-700 font-semibold text-sm">Con estos datos (incluyendo mantenimiento), el vehículo B no genera ahorro anual respecto al vehículo A.</p>`;
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

        // 4B. Caballos fiscales (fórmula oficial BOE) + DGT + IVTM + CO2
        function calcularDGT() {
            const elMotor = document.getElementById('dgt-motor');
            if (!elMotor) return;
            const motor = elMotor.value;
            const anio = parseInt(document.getElementById('dgt-anio').value) || 2015;
            const cc = parseFloat(document.getElementById('dgt-cc').value) || 1600;
            const cil = Math.max(1, parseInt(document.getElementById('dgt-cil').value) || 4);
            const co2 = parseFloat(document.getElementById('dgt-co2').value) || 0;
            const base = parseFloat(document.getElementById('dgt-base').value) || 0;

            // Fórmula BOE Anexo V: CVF = 0.08 * (cc / N)^0.6 * N
            const cvf = 0.08 * Math.pow(cc / cil, 0.6) * cil;

            let tramoIVTM = "De 12 a 15,99 CVF (~143 €/año)";
            if (cvf < 8) tramoIVTM = "Menos de 8 CVF (~25 €/año)";
            else if (cvf < 12) tramoIVTM = "De 8 a 11,99 CVF (~68 €/año)";
            else if (cvf >= 16 && cvf < 20) tramoIVTM = "De 16 a 19,99 CVF (~179 €/año)";
            else if (cvf >= 20) tramoIVTM = "20 CVF o más (~224 €/año)";

            let etiqueta = "Sin distintivo (A)";
            let colorEtiqueta = "bg-slate-200 text-slate-800";

            if (motor === "cero") {
                etiqueta = "CERO emisiones (azul)";
                colorEtiqueta = "bg-sky-200 text-sky-950";
            } else if (motor === "hibrido") {
                etiqueta = "Etiqueta ECO (verde/azul)";
                colorEtiqueta = "bg-teal-200 text-teal-950";
            } else if (motor === "gasolina") {
                if (anio >= 2006) {
                    etiqueta = "Etiqueta C (verde - Euro 4/5/6)";
                    colorEtiqueta = "bg-emerald-200 text-emerald-950";
                } else if (anio >= 2001) {
                    etiqueta = "Etiqueta B (amarilla - Euro 3)";
                    colorEtiqueta = "bg-amber-200 text-amber-950";
                }
            } else if (motor === "diesel") {
                if (anio >= 2015) {
                    etiqueta = "Etiqueta C (verde - Euro 6)";
                    colorEtiqueta = "bg-emerald-200 text-emerald-950";
                } else if (anio >= 2006) {
                    etiqueta = "Etiqueta B (amarilla - Euro 4/5)";
                    colorEtiqueta = "bg-amber-200 text-amber-950";
                }
            }

            let tipoImpositivo = 0;
            if (co2 > 120 && co2 <= 159) tipoImpositivo = 4.75;
            else if (co2 >= 160 && co2 <= 199) tipoImpositivo = 9.75;
            else if (co2 >= 200) tipoImpositivo = 14.75;

            const cuotaImpuesto = base * (tipoImpositivo / 100);

            document.getElementById('res-dgt').innerHTML = `
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center items-center">
                    <div class="p-3 rounded-lg font-bold ${colorEtiqueta}">
                        <div class="text-xs opacity-75">Distintivo DGT</div>
                        <div class="text-xs sm:text-sm mt-1">${etiqueta}</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Potencia fiscal (BOE)</div>
                        <div class="text-xl font-extrabold text-slate-900">${cvf.toFixed(2)} CVF</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Tramo IVTM («numerito»)</div>
                        <div class="text-xs font-bold text-slate-800 mt-1">${tramoIVTM}</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Imp. matriculación (${tipoImpositivo}%)</div>
                        <div class="text-xl font-bold text-amber-600">${cuotaImpuesto.toFixed(0)} €</div>
                    </div>
                </div>
            `;
        }

        function gestionarCookies(modo) {
            localStorage.setItem('autocalc_cookies', modo);
            document.getElementById('cookie-banner').classList.add('hidden');
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
            if (!localStorage.getItem('autocalc_cookies')) {
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
            <p>La medida <strong>{a1}/{p1} R{l1}</strong> se monta de serie en modelos como <em>{modelos}</em>. Su diámetro exterior es de <strong>{d1:.1f} mm</strong> y requiere una garganta de llanta de <strong>{garganta}</strong>.</p>
            <p>Puedes comparar ofertas online con envío gratis en <strong>Muchoneumático</strong> y <strong>Amazon</strong>, o reservar montaje directo en centros <strong>Norauto</strong> y <strong>Feu Vert</strong> tanto en la medida original como en su equivalente <strong>{a2}/{p2} R{l2}</strong> ({diff:+.2f} %).</p>
        """
        faqs_medida = [
            (f"¿Qué medidas son equivalentes a {a1}/{p1} R{l1} en la ITV?",
             f"Son equivalentes todas las medidas con un diámetro entre {d1*0.97:.1f} mm y {d1*1.03:.1f} mm (±3 %), destacando la {a2}/{p2} R{l2} ({diff:+.2f} %)."),
            (f"¿Dónde comprar neumáticos {a1}/{p1} R{l1} al mejor precio?",
             f"En la tabla superior puedes comparar precios directos en Muchoneumático (especialista en ruedas), Norauto y Feu Vert (con montaje en taller) y Amazon España.")
        ]

        render_page(
            slug,
            f"Equivalencia de neumáticos {a1}/{p1} R{l1} en ITV | Precios y medidas",
            f"Tabla de neumáticos equivalentes a {a1}/{p1} R{l1} ({d1:.1f} mm) aptos para ITV. Compara precios en Muchoneumático, Norauto, Feu Vert y Amazon.",
            f"Equivalencia de neumáticos {a1}/{p1} R{l1} en ITV",
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
            <p>El <strong>{nombre_c}</strong> equipa habitualmente en ficha técnica la medida <strong>{a1}/{p1} R{l1}</strong> ({d1:.1f} mm de diámetro y garganta de {garganta}), pudiendo montar sin homologar en ITV la medida <strong>{a2}/{p2} R{l2}</strong> ({diff:+.2f} %).</p>
            <p><strong>Consejo de ahorro en mantenimiento para {nombre_c}:</strong> para recambios de desgaste (kits de filtros, pastillas de freno, amortiguadores o brazos de suspensión), <strong>Autodoc</strong> suele ofrecer el precio más bajo; para neumáticos tienes envío rápido en <strong>Muchoneumático</strong> o montaje en centros <strong>Norauto y Feu Vert</strong>; y para piezas de carrocería, faros o espejos retrovisores te compensa consultar stock en los grandes desguaces del sur de Madrid (San Martín de la Vega o La Torre).</p>
        """
        faqs_coche = [
            (f"¿Qué neumáticos equivalentes puede montar un {nombre_c} para pasar la ITV?",
             f"Partiendo de la medida habitual {a1}/{p1} R{l1} ({d1:.1f} mm), el {nombre_c} puede montar sin homologar medidas como {a2}/{p2} R{l2} ({diff:+.2f} %)."),
            (f"¿Dónde comprar recambios baratos para {nombre_c}: Autodoc, Norauto o desguace?",
             f"Para consumibles y mecánica nueva (frenos, embrague, filtros) conviene Autodoc; para montaje rápido en el día destaca Norauto o Feu Vert; y para piezas de carrocería o módulos originales OEM de {nombre_c} el mayor ahorro está en desguaces.")
        ]

        render_page(
            archivo_c,
            f"Neumáticos equivalentes y recambios {nombre_c} ITV | Autodoc, Norauto y desguace",
            f"Medidas de neumáticos equivalentes en ITV para {nombre_c} ({a1}/{p1} R{l1} a {a2}/{p2} R{l2}) y comparador de recambios en Autodoc, Muchoneumático y Norauto.",
            f"Neumáticos equivalentes y recambios ITV para {nombre_c}",
            f"Medida base: {a1}/{p1} R{l1} ({d1:.1f} mm) · Equivalencia ITV: {a2}/{p2} R{l2} ({diff:+.2f} %).",
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
            <p><strong>Principales núcleos de desguaces cercanos:</strong> {desguaces_z}. Son la mejor alternativa para adquirir piezas originales OEM de carrocería (paragolpes, aletas, faros, retrovisores), cajas de cambio, alternadores o motores de arranque con hasta un 70 % de ahorro.</p>
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
        coste = litros * 1.56

        seo_ruta = f"""
            <h2 class="text-base font-bold text-slate-900">Gasto de combustible en la ruta {orig} - {dest} ({km} km)</h2>
            <p>El trayecto por carretera entre <strong>{orig} y {dest}</strong> cubre unos <strong>{km} km</strong>. Con un consumo medio de {l100} L/100 km, necesitarás <strong>{litros:.1f} litros</strong>, lo que equivale a unos <strong>{coste:.2f} €</strong> ({coste/2:.2f} € por persona compartiendo viaje entre 2 ocupantes).</p>
        """
        faqs_ruta = [
            (f"¿Cuánto cuesta ir en coche de {orig} a {dest}?",
             f"Para recorrer los {km} km entre {orig} y {dest} con un consumo medio de {l100} L/100 km gastarás unos {litros:.1f} litros ({coste:.2f} € aproximadamente).")
        ]

        render_page(
            slug_r,
            f"Calcular gasolina y coste de viaje {orig} - {dest} ({km} km)",
            f"Calcula cuántos litros y euros cuesta viajar en coche de {orig} a {dest} ({km} km) y divide el gasto por ocupante.",
            f"Coste de combustible: de {orig} a {dest} ({km} km)",
            f"Consumo estimado para {km} km: {litros:.1f} litros ({coste:.2f} € en total / {coste/2:.2f} € entre dos).",
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

    texto_legal = f"""
        <h2 class="text-lg font-bold text-slate-900">Aviso legal y condiciones de uso</h2>
        <p>En cumplimiento de la Ley 34/2002 (LSSI-CE), se informa de que el portal <strong>{SITE_NAME}</strong> ({DOMINIO}) es una herramienta informativa de cálculo técnico. Contacto: <strong>{EMAIL_CONTACTO}</strong>.</p>
        <p>Los cálculos de equivalencia de neumáticos (±3 %) e impuestos son orientativos conforme a los manuales públicos de inspección técnica; verifique siempre el índice de carga, el código de velocidad y la ausencia de interferencias mecánicas en su estación ITV antes de realizar modificaciones.</p>
    """
    render_page(
        "aviso-legal.html", f"Aviso legal | {SITE_NAME}", "Aviso legal y condiciones de uso del portal.",
        "Aviso legal y condiciones de uso", "Información legal conforme a la normativa LSSI-CE.",
        205, 55, 16, 225, 45, 17, 450, 5.8, "itv", "", texto_legal, internal_links_html, faqs_home, robots="noindex, follow"
    )

    texto_privacidad = f"""
        <h2 class="text-lg font-bold text-slate-900">Política de privacidad, cookies y afiliación</h2>
        <p><strong>1. Programas de afiliación:</strong> {SITE_NAME} participa en el Programa de Afiliados de Amazon de la UE y muestra enlaces comparativos a comercios especializados del sector de la automoción (como Muchoneumático, Autodoc, Norauto y Feu Vert) para facilitar la consulta de precios al usuario.</p>
        <p><strong>2. Cookies y publicidad (Google AdSense):</strong> Utilizamos almacenamiento local para recordar su preferencia de privacidad y, en su caso, proveedores como Google utilizan cookies para mostrar anuncios relevantes basados en visitas anteriores. Puede desactivar las cookies personalizadas en la configuración de su navegador o en Configuración de anuncios de Google.</p>
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