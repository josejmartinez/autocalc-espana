#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor generador estático AutoCalc España v2.0
Incluye: 4 calculadoras, comparador visual SVG, validador de carga/velocidad ITV,
enlaces compartibles, ortotipografía española, ads.txt y favicon.svg.
"""

import os
import json
from datetime import date
from catalogo import MEDIDAS_ESPANA, RUTAS_ESPANA, GARGANTA_POR_ANCHO

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
                    url_amz = f"https://www.amazon.es/s?k=neumaticos+{ancho}+{perfil}+R{llanta}&tag={AMAZON_TAG}"

                    fila_html = f"""
                    <tr class="border-b border-slate-100 hover:bg-slate-50 transition">
                        <td class="py-2.5 px-3 font-bold text-slate-900">
                            <button onclick="cargarMedidaCandidata({ancho},{perfil},{llanta})" class="text-left hover:text-amber-600 underline decoration-dotted" title="Probar esta medida en el comparador">
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
                            <a href="{url_amz}" target="_blank" rel="nofollow sponsored" class="text-xs bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold px-2.5 py-1 rounded transition">Ver precios →</a>
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
                <p class="text-xs text-slate-500">Diámetro original: <strong>{d_orig:.1f} mm</strong> · Rango legal permitido en ITV: <strong>{d_orig*0.97:.1f} mm a {d_orig*1.03:.1f} mm</strong> (pulsa en cualquier medida para simularla arriba)</p>
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
                    <th class="py-2 px-3 text-right font-semibold">Ofertas</th>
                </tr>
            </thead>
            <tbody>{filas_top}</tbody>
        </table>
    </div>
    """


PLANTILLA_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__PAGE_TITLE__</title>
    <meta name="description" content="__META_DESC__">
    <link rel="canonical" href="__CANONICAL_URL__">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <meta name="robots" content="__ROBOTS_META__">
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
                    <span class="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">ITV y DGT</span>
                </a>
            </div>
            <div class="flex items-center gap-2 w-full sm:w-auto justify-end">
                <a href="mapa-web.html" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-2 rounded-lg border border-slate-700 transition">Buscador de medidas</a>
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

        <!-- Selector de pestañas -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-2 mb-6 bg-slate-200 p-1.5 rounded-xl no-print">
            <button onclick="cambiarTab('itv')" id="tab-itv" class="py-2.5 px-3 rounded-lg font-semibold text-xs sm:text-sm bg-white text-slate-900 shadow-sm transition">
                1. Equivalencia ITV (±3 %)
            </button>
            <button onclick="cambiarTab('consumo')" id="tab-consumo" class="py-2.5 px-3 rounded-lg font-semibold text-xs sm:text-sm text-slate-600 hover:text-slate-900 transition">
                2. Coste de viaje y consumo
            </button>
            <button onclick="cambiarTab('amortizacion')" id="tab-amortizacion" class="py-2.5 px-3 rounded-lg font-semibold text-xs sm:text-sm text-slate-600 hover:text-slate-900 transition">
                3. Diésel o híbrido vs. gasolina
            </button>
            <button onclick="cambiarTab('dgt')" id="tab-dgt" class="py-2.5 px-3 rounded-lg font-semibold text-xs sm:text-sm text-slate-600 hover:text-slate-900 transition">
                4. Etiqueta DGT e impuesto CO₂
            </button>
        </div>

        <!-- 1. CALCULADORA ITV NEUMÁTICOS -->
        <section id="sec-itv" class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <!-- Selector rápido por vehículo -->
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-5 pb-4 border-b border-slate-100 no-print">
                <label for="preset-coche" class="text-xs font-semibold text-slate-600">Autocompletar medida original según modelo de coche:</label>
                <select id="preset-coche" onchange="aplicarPresetCoche()" class="p-2 border rounded-lg text-xs bg-slate-50 font-medium text-slate-800 w-full sm:w-72">
                    <option value="">— Seleccionar vehículo de referencia —</option>
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
                <!-- Medida original -->
                <div class="bg-slate-50 p-4 rounded-xl border border-slate-200">
                    <h2 class="font-bold text-xs text-slate-700 mb-3">Medida en ficha técnica (original)</h2>
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

                <!-- Medida nueva -->
                <div class="bg-slate-50 p-4 rounded-xl border border-slate-200">
                    <h2 class="font-bold text-xs text-slate-700 mb-3">Medida nueva a comprobar</h2>
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

            <!-- Resultado numérico ITV -->
            <div id="res-itv" class="mt-6 p-5 rounded-xl border"></div>

            <!-- Comparador gráfico visual SVG a escala -->
            <div class="mt-6 bg-slate-50 p-4 rounded-xl border border-slate-200">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="text-xs font-bold text-slate-700">Comparación visual a escala (diámetro lateral y anchura de pisada)</h3>
                    <div class="flex gap-4 text-xs">
                        <span class="flex items-center gap-1"><span class="w-3 h-3 inline-block rounded-full bg-slate-700"></span> Original</span>
                        <span class="flex items-center gap-1"><span class="w-3 h-3 inline-block rounded-full bg-amber-500"></span> Nueva medida</span>
                    </div>
                </div>
                <div id="svg-comparador" class="w-full flex justify-center py-2"></div>
            </div>
        </section>

        <!-- 2. CALCULADORA CONSUMO -->
        <section id="sec-consumo" class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hidden">
            <h2 class="text-lg font-bold mb-4 text-slate-900">Calculadora de gasto de combustible y coste por ocupante</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                    <label class="block text-xs font-medium text-slate-600 mb-1">Distancia total (km)</label>
                    <input type="number" id="km-viaje" value="__VAL_KM__" oninput="calcularConsumo()" class="w-full p-2.5 border rounded-lg font-bold">
                </div>
                <div>
                    <label class="block text-xs font-medium text-slate-600 mb-1">Consumo real (L/100 km)</label>
                    <input type="number" step="0.1" id="litros-100" value="__VAL_L100__" oninput="calcularConsumo()" class="w-full p-2.5 border rounded-lg font-bold">
                </div>
                <div>
                    <label class="block text-xs font-medium text-slate-600 mb-1">Precio combustible (€/L)</label>
                    <input type="number" step="0.01" id="precio-litro" value="1.58" oninput="calcularConsumo()" class="w-full p-2.5 border rounded-lg font-bold">
                </div>
                <div>
                    <label class="block text-xs font-medium text-slate-600 mb-1">Personas en el coche</label>
                    <input type="number" id="ocupantes" value="2" min="1" oninput="calcularConsumo()" class="w-full p-2.5 border rounded-lg font-bold">
                </div>
            </div>
            <div id="res-consumo" class="mt-6 p-5 rounded-xl bg-slate-50 border border-slate-200"></div>
        </section>

        <!-- 3. CALCULADORA AMORTIZACIÓN -->
        <section id="sec-amortizacion" class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hidden">
            <h2 class="text-lg font-bold mb-4 text-slate-900">Calculadora de rentabilidad: ¿cuándo se amortiza un diésel, híbrido o GLP?</h2>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
                <div>
                    <label class="block text-xs font-medium text-slate-600 mb-1">Kilómetros al año</label>
                    <input type="number" id="km-anual" value="15000" oninput="calcularAmortizacion()" class="w-full p-2.5 border rounded-lg font-bold">
                </div>
                <div class="sm:col-span-2">
                    <label class="block text-xs font-medium text-slate-600 mb-1">Diferencia de precio de compra (€)</label>
                    <input type="number" id="dif-precio" value="2500" oninput="calcularAmortizacion()" class="w-full p-2.5 border rounded-lg font-bold">
                </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-slate-50 p-4 rounded-xl border">
                    <h3 class="font-semibold text-sm mb-2">Opción A (gasolina)</h3>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs text-slate-600">Consumo (L/100 km)</label>
                            <input type="number" step="0.1" id="cons-a" value="6.8" oninput="calcularAmortizacion()" class="w-full p-2 border rounded-lg">
                        </div>
                        <div>
                            <label class="block text-xs text-slate-600">Precio (€/L)</label>
                            <input type="number" step="0.01" id="prec-a" value="1.62" oninput="calcularAmortizacion()" class="w-full p-2 border rounded-lg">
                        </div>
                    </div>
                </div>
                <div class="bg-slate-50 p-4 rounded-xl border">
                    <h3 class="font-semibold text-sm mb-2">Opción B (diésel / híbrido / GLP)</h3>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs text-slate-600">Consumo (L/100 km)</label>
                            <input type="number" step="0.1" id="cons-b" value="4.8" oninput="calcularAmortizacion()" class="w-full p-2 border rounded-lg">
                        </div>
                        <div>
                            <label class="block text-xs text-slate-600">Precio (€/L)</label>
                            <input type="number" step="0.01" id="prec-b" value="1.51" oninput="calcularAmortizacion()" class="w-full p-2 border rounded-lg">
                        </div>
                    </div>
                </div>
            </div>
            <div id="res-amortizacion" class="mt-6 p-5 rounded-xl bg-slate-50 border border-slate-200"></div>
        </section>

        <!-- 4. CALCULADORA ETIQUETA DGT E IMPUESTO DE MATRICULACIÓN CO2 -->
        <section id="sec-dgt" class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hidden">
            <h2 class="text-lg font-bold mb-2 text-slate-900">Simulador de distintivo ambiental DGT e impuesto de matriculación (CO₂)</h2>
            <p class="text-xs text-slate-500 mb-4">Comprueba qué etiqueta de la DGT corresponde por año y motorización, y calcula el impuesto de matriculación según emisiones WLTP.</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                    <label class="block text-xs font-medium text-slate-600 mb-1">Tipo de motor</label>
                    <select id="dgt-motor" onchange="calcularDGT()" class="w-full p-2.5 border rounded-lg font-bold bg-white">
                        <option value="gasolina">Gasolina</option>
                        <option value="diesel">Diésel</option>
                        <option value="hibrido">Híbrido (HEV / MHEV / GLP)</option>
                        <option value="cero">Eléctrico BEV / PHEV (>40 km)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-medium text-slate-600 mb-1">Año de 1.ª matriculación</label>
                    <input type="number" id="dgt-anio" value="2012" min="1980" max="2027" oninput="calcularDGT()" class="w-full p-2.5 border rounded-lg font-bold">
                </div>
                <div>
                    <label class="block text-xs font-medium text-slate-600 mb-1">Emisiones CO₂ (g/km)</label>
                    <input type="number" id="dgt-co2" value="132" oninput="calcularDGT()" class="w-full p-2.5 border rounded-lg font-bold">
                </div>
                <div>
                    <label class="block text-xs font-medium text-slate-600 mb-1">Base imponible del coche (€)</label>
                    <input type="number" id="dgt-base" value="22000" oninput="calcularDGT()" class="w-full p-2.5 border rounded-lg font-bold">
                </div>
            </div>
            <div id="res-dgt" class="mt-6 p-5 rounded-xl bg-slate-50 border border-slate-200"></div>
        </section>

        <!-- BLOQUE DE AFILIACIÓN DINÁMICA (AMAZON MOTOR 7 %) -->
        <section class="mt-8 bg-gradient-to-br from-slate-900 to-slate-800 text-white p-6 rounded-2xl shadow-md no-print">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                <h2 class="text-lg font-bold text-amber-400">Recambios y accesorios compatibles con tu medida</h2>
                <span class="text-xs bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full w-fit">Envío rápido en Amazon España</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <a id="cta-neumatico-orig" href="https://www.amazon.es/s?k=neumaticos+__VAL_A1__+__VAL_P1__+R__VAL_L1__&tag=__AMAZON_TAG__" target="_blank" rel="nofollow sponsored" class="bg-slate-800 hover:bg-slate-700 p-4 rounded-xl border border-slate-700 transition flex flex-col justify-between">
                    <div>
                        <span class="text-xs text-amber-400 font-semibold">Medida original</span>
                        <h3 id="txt-cta-orig" class="font-bold text-sm mt-1">Neumáticos __VAL_A1__/__VAL_P1__ R__VAL_L1__</h3>
                        <p class="text-xs text-slate-300 mt-1">Primeras marcas y neumáticos económicos con etiqueta europea.</p>
                    </div>
                    <span class="mt-4 inline-block text-center bg-amber-500 text-slate-950 font-bold text-xs py-2 rounded-lg">Ver precios →</span>
                </a>

                <a id="cta-neumatico-nuevo" href="https://www.amazon.es/s?k=neumaticos+__VAL_A2__+__VAL_P2__+R__VAL_L2__&tag=__AMAZON_TAG__" target="_blank" rel="nofollow sponsored" class="bg-slate-800 hover:bg-slate-700 p-4 rounded-xl border border-slate-700 transition flex flex-col justify-between">
                    <div>
                        <span class="text-xs text-emerald-400 font-semibold">Medida equivalente ITV</span>
                        <h3 id="txt-cta-nuevo" class="font-bold text-sm mt-1">Neumáticos __VAL_A2__/__VAL_P2__ R__VAL_L2__</h3>
                        <p class="text-xs text-slate-300 mt-1">Montaje directo legal en ITV dentro del ±3 % permitido.</p>
                    </div>
                    <span class="mt-4 inline-block text-center bg-amber-500 text-slate-950 font-bold text-xs py-2 rounded-lg">Ver ofertas →</span>
                </a>

                <a id="cta-cadenas" href="https://www.amazon.es/s?k=cadenas+nieve+textiles+__VAL_A1__+__VAL_P1__+R__VAL_L1__&tag=__AMAZON_TAG__" target="_blank" rel="nofollow sponsored" class="bg-slate-800 hover:bg-slate-700 p-4 rounded-xl border border-slate-700 transition flex flex-col justify-between">
                    <div>
                        <span class="text-xs text-amber-400 font-semibold">Homologadas DGT</span>
                        <h3 id="txt-cta-cadenas" class="font-bold text-sm mt-1">Cadenas y fundas __VAL_A1__/__VAL_P1__ R__VAL_L1__</h3>
                        <p class="text-xs text-slate-300 mt-1">Aptas para llantas de aleación y sistemas ABS/ESP.</p>
                    </div>
                    <span class="mt-4 inline-block text-center bg-amber-500 text-slate-950 font-bold text-xs py-2 rounded-lg">Comprobar talla →</span>
                </a>

                <a href="https://www.amazon.es/s?k=diagnosis+obd2+multimarca+español&tag=__AMAZON_TAG__" target="_blank" rel="nofollow sponsored" class="bg-slate-800 hover:bg-slate-700 p-4 rounded-xl border border-slate-700 transition flex flex-col justify-between">
                    <div>
                        <span class="text-xs text-amber-400 font-semibold">Pre-ITV en casa</span>
                        <h3 class="font-bold text-sm mt-1">Máquina de diagnosis OBD2</h3>
                        <p class="text-xs text-slate-300 mt-1">Revisa fallos de gases y borra códigos de avería antes de la ITV.</p>
                    </div>
                    <span class="mt-4 inline-block text-center bg-amber-500 text-slate-950 font-bold text-xs py-2 rounded-lg">Ver en Amazon →</span>
                </a>
            </div>
        </section>

        __PRECALC_TABLE_HTML__

        <article class="mt-8 bg-white p-6 rounded-2xl border border-slate-200 text-sm text-slate-600 space-y-3">
            __SEO_TEXT_BLOCK__
        </article>

        <nav class="mt-8 bg-slate-100 p-6 rounded-2xl border border-slate-200 no-print">
            <h3 class="text-xs font-bold text-slate-500 mb-3">Consultas frecuentes de ITV y consumo en España</h3>
            <div class="flex flex-wrap gap-2">
                __INTERNAL_LINKS_HTML__
            </div>
        </nav>

    </main>

    <footer class="bg-slate-900 text-slate-400 text-xs py-8 mt-12 no-print">
        <div class="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div>
                <p class="font-bold text-slate-200">__SITE_NAME__ © 2026</p>
                <p class="mt-1">Participamos en el Programa de Afiliados de Amazon de la UE.</p>
            </div>
            <div class="flex flex-wrap gap-4">
                <a href="index.html" class="hover:text-white transition">Inicio</a>
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

        function cambiarTab(tab) {
            ['itv', 'consumo', 'amortizacion', 'dgt'].forEach(t => {
                const sec = document.getElementById('sec-' + t);
                const btn = document.getElementById('tab-' + t);
                if (sec && btn) {
                    sec.classList.add('hidden');
                    btn.className = 'py-2.5 px-3 rounded-lg font-semibold text-xs sm:text-sm text-slate-600 hover:text-slate-900 transition';
                }
            });
            const activeSec = document.getElementById('sec-' + tab);
            const activeBtn = document.getElementById('tab-' + tab);
            if (activeSec && activeBtn) {
                activeSec.classList.remove('hidden');
                activeBtn.className = 'py-2.5 px-3 rounded-lg font-semibold text-xs sm:text-sm bg-white text-slate-900 shadow-sm transition';
            }
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
                    <!-- Vista lateral superpuesta -->
                    <text x="95" y="15" text-anchor="middle" class="text-[10px] fill-slate-500 font-semibold">Diámetro lateral</text>
                    <circle cx="95" cy="82" r="${rExt1.toFixed(1)}" fill="none" stroke="#334155" stroke-width="8" opacity="0.85"/>
                    <circle cx="95" cy="82" r="${rLlanta1.toFixed(1)}" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="3,2"/>
                    <circle cx="95" cy="82" r="${rExt2.toFixed(1)}" fill="none" stroke="#f59e0b" stroke-width="4"/>
                    <circle cx="95" cy="82" r="${rLlanta2.toFixed(1)}" fill="none" stroke="#d97706" stroke-width="1.5"/>

                    <!-- Vista de banda de rodadura (ancho) -->
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

            document.getElementById('cta-neumatico-orig').href = `https://www.amazon.es/s?k=neumaticos+${a1}+${p1}+R${l1}&tag=${AMAZON_TAG}`;
            document.getElementById('txt-cta-orig').innerText = `Neumáticos ${a1}/${p1} R${l1}`;
            document.getElementById('cta-neumatico-nuevo').href = `https://www.amazon.es/s?k=neumaticos+${a2}+${p2}+R${l2}&tag=${AMAZON_TAG}`;
            document.getElementById('txt-cta-nuevo').innerText = `Neumáticos ${a2}/${p2} R${l2}`;
            document.getElementById('cta-cadenas').href = `https://www.amazon.es/s?k=cadenas+nieve+textiles+${a1}+${p1}+R${l1}&tag=${AMAZON_TAG}`;
            document.getElementById('txt-cta-cadenas').innerText = `Cadenas y fundas ${a1}/${p1} R${l1}`;
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
            const personas = Math.max(1, parseInt(document.getElementById('ocupantes').value) || 1);

            const litrosTotales = (km / 100) * l100;
            const costeTotal = litrosTotales * precio;
            const costePorPersona = costeTotal / personas;
            const costePorKm = km > 0 ? costeTotal / km : 0;

            document.getElementById('res-consumo').innerHTML = `
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Coste total del viaje</div>
                        <div class="text-xl font-bold text-slate-900">${costeTotal.toFixed(2)} €</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Por ocupante (${personas})</div>
                        <div class="text-xl font-bold text-amber-600">${costePorPersona.toFixed(2)} €</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Litros totales</div>
                        <div class="text-xl font-bold text-slate-900">${litrosTotales.toFixed(1)} L</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Coste por km</div>
                        <div class="text-xl font-bold text-slate-900">${costePorKm.toFixed(3)} €/km</div>
                    </div>
                </div>
            `;
        }

        function calcularAmortizacion() {
            const elKmAnual = document.getElementById('km-anual');
            if (!elKmAnual) return;
            const kmAnual = parseFloat(elKmAnual.value) || 1;
            const difPrecio = parseFloat(document.getElementById('dif-precio').value) || 0;
            const consA = parseFloat(document.getElementById('cons-a').value) || 0;
            const precA = parseFloat(document.getElementById('prec-a').value) || 0;
            const consB = parseFloat(document.getElementById('cons-b').value) || 0;
            const precB = parseFloat(document.getElementById('prec-b').value) || 0;

            const ahorroPorKm = ((consA * precA) - (consB * precB)) / 100;
            const box = document.getElementById('res-amortizacion');

            if (ahorroPorKm <= 0) {
                box.innerHTML = `<p class="text-rose-700 font-semibold text-sm">Con estos datos, la opción B no ahorra dinero por kilómetro respecto a la opción A.</p>`;
                return;
            }

            const kmParaAmortizar = difPrecio / ahorroPorKm;
            const aniosParaAmortizar = kmParaAmortizar / kmAnual;
            const ahorroAnual = ahorroPorKm * kmAnual;

            box.innerHTML = `
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Ahorro anual</div>
                        <div class="text-xl font-bold text-emerald-600">${ahorroAnual.toFixed(0)} €/año</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Km para amortizar</div>
                        <div class="text-xl font-bold text-slate-900">${Math.round(kmParaAmortizar).toLocaleString('es-ES')} km</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Tiempo de retorno</div>
                        <div class="text-xl font-bold text-amber-600">${aniosParaAmortizar.toFixed(1)} años</div>
                    </div>
                </div>
            `;
        }

        function calcularDGT() {
            const elMotor = document.getElementById('dgt-motor');
            if (!elMotor) return;
            const motor = elMotor.value;
            const anio = parseInt(document.getElementById('dgt-anio').value) || 2015;
            const co2 = parseFloat(document.getElementById('dgt-co2').value) || 0;
            const base = parseFloat(document.getElementById('dgt-base').value) || 0;

            let etiqueta = "Sin distintivo (A)";
            let colorEtiqueta = "bg-slate-200 text-slate-800";

            if (motor === "cero") {
                etiqueta = "Etiqueta CERO emisiones (azul)";
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
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center items-center">
                    <div class="p-3 rounded-lg font-bold ${colorEtiqueta}">
                        <div class="text-xs opacity-75">Distintivo DGT</div>
                        <div class="text-sm mt-1">${etiqueta}</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Tramo impuesto CO₂ (${co2} g/km)</div>
                        <div class="text-xl font-bold text-slate-900">${tipoImpositivo.toFixed(2)} %</div>
                    </div>
                    <div class="bg-white p-3 rounded-lg border">
                        <div class="text-xs text-slate-500">Impuesto de matriculación</div>
                        <div class="text-xl font-bold text-amber-600">${cuotaImpuesto.toFixed(2)} €</div>
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
            calcularConsumo();
            calcularAmortizacion();
            calcularDGT();
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
    table_html, seo_text, internal_links, faqs, robots="index, follow"
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
        "__AMAZON_TAG__": AMAZON_TAG
    }

    for k, v in replacements.items():
        html = html.replace(k, v)

    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as out:
        out.write(html)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sitemap_urls = []

    # Crear icono SVG para evitar errores 404 en el navegador
    favicon_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="#0f172a" stroke="#f59e0b" stroke-width="4"/><circle cx="32" cy="32" r="14" fill="none" stroke="#f59e0b" stroke-width="3"/></svg>'
    with open(os.path.join(OUTPUT_DIR, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(favicon_svg)

    chips = []
    vistas = set()
    for a1, p1, l1, a2, p2, l2, _ in MEDIDAS_ESPANA:
        if (a1, p1, l1) not in vistas:
            vistas.add((a1, p1, l1))
            slug = f"equivalencia-neumaticos-{a1}-{p1}-r{l1}.html"
            chips.append(f'<a href="{slug}" class="text-xs bg-white hover:bg-amber-100 text-slate-700 px-2.5 py-1 rounded border border-slate-300 transition">Neumáticos {a1}/{p1} R{l1}</a>')

    for orig, dest, _, _ in RUTAS_ESPANA[:10]:
        slug_r = f"calcular-consumo-{orig.lower().replace(' ', '-')}-{dest.lower().replace(' ', '-')}.html"
        chips.append(f'<a href="{slug_r}" class="text-xs bg-white hover:bg-amber-100 text-slate-700 px-2.5 py-1 rounded border border-slate-300 transition">Viaje {orig} - {dest}</a>')

    internal_links_html = "\n".join(chips[:38])

    faqs_home = [
        ("¿Qué margen permite la ITV para neumáticos equivalentes en España?",
         "La ITV permite una tolerancia máxima del ±3 % en el diámetro exterior respecto a la medida en ficha técnica, manteniendo índice de carga y velocidad iguales o superiores."),
        ("¿Cuándo están exentos los coches del impuesto de matriculación por CO2?",
         "En España están exentos (0 %) todos los vehículos cuyas emisiones homologadas de CO2 sean iguales o inferiores a 120 g/km.")
    ]
    seo_home = """
        <h2 class="text-base font-bold text-slate-900">Guía técnica de equivalencia de neumáticos ITV, consumo y etiquetas DGT</h2>
        <p>Con nuestras 4 calculadoras técnicas verificadas conforme al Manual de Procedimiento de Inspección de las Estaciones ITV y la Agencia Tributaria podrás comprobar equivalencias de ruedas sin homologar (±3 %), índice de carga, código de velocidad, ancho de garganta en pulgadas, gasto exacto de combustible por ocupante y tramos del impuesto de matriculación.</p>
    """
    render_page(
        "index.html",
        f"Calculadora de equivalencia de neumáticos ITV, consumo y DGT | {SITE_NAME}",
        "Comprueba la equivalencia de neumáticos para la ITV (±3 %), ancho de llanta, consumo de combustible por ruta y etiqueta ambiental DGT.",
        "Calculadoras técnicas de ITV, neumáticos, consumo y DGT",
        "Comprueba al instante medidas equivalentes sin homologar (±3 %), gasto por viaje, amortización diésel/híbrido e impuesto CO₂.",
        205, 55, 16, 225, 45, 17, 450, 5.8, "itv",
        generar_tabla_equivalencias_html(205, 55, 16), seo_home, internal_links_html, faqs_home
    )
    sitemap_urls.append(("index.html", f"{DOMINIO}/", "Portada principal - 4 calculadoras de motor e ITV"))

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
            <h2 class="text-base font-bold text-slate-900">Ficha técnica y equivalencias del neumático {a1}/{p1} R{l1}</h2>
            <p>La medida <strong>{a1}/{p1} R{l1}</strong> se monta de serie en modelos muy habituales en España como <em>{modelos}</em>. Presenta un diámetro exterior de <strong>{d1:.1f} mm</strong> y requiere un ancho de garganta de llanta recomendado de <strong>{garganta}</strong>.</p>
            <p>Para superar la ITV sin proyecto de reforma, el neumático equivalente debe medir entre <strong>{d1*0.97:.1f} mm y {d1*1.03:.1f} mm</strong>. Una de las conversiones más demandadas es pasar a <strong>{a2}/{p2} R{l2}</strong> ({d2:.1f} mm, variación del {diff:+.2f} %).</p>
        """
        faqs_medida = [
            (f"¿Qué medidas son equivalentes a {a1}/{p1} R{l1} en la ITV?",
             f"Son equivalentes todas las medidas con un diámetro entre {d1*0.97:.1f} mm y {d1*1.03:.1f} mm (±3 %), destacando la {a2}/{p2} R{l2} ({diff:+.2f} %)."),
            (f"¿Qué ancho de llanta necesita un neumático {a1}/{p1} R{l1}?",
             f"Para un ancho de banda de {a1} mm se recomienda una garganta de llanta de {garganta} pulgadas.")
        ]

        render_page(
            slug,
            f"Equivalencia de neumáticos {a1}/{p1} R{l1} en ITV | Tabla y medidas compatibles",
            f"Tabla de neumáticos equivalentes a {a1}/{p1} R{l1} ({d1:.1f} mm) aptos para ITV sin homologar. Modelos habituales: {modelos}.",
            f"Equivalencia de neumáticos {a1}/{p1} R{l1} en ITV",
            f"Diámetro: {d1:.1f} mm · Garganta de llanta: {garganta} · Común en: {modelos}.",
            a1, p1, l1, a2, p2, l2, 450, 5.8, "itv",
            generar_tabla_equivalencias_html(a1, p1, l1), seo_medida, internal_links_html, faqs_medida
        )
        sitemap_urls.append((slug, f"{DOMINIO}/{slug}", f"Equivalencia de neumáticos {a1}/{p1} R{l1} ({modelos})"))

    for orig, dest, km, l100 in RUTAS_ESPANA:
        slug_r = f"calcular-consumo-{orig.lower().replace(' ', '-')}-{dest.lower().replace(' ', '-')}.html"
        litros = (km / 100.0) * l100
        coste = litros * 1.58

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
            <h2 class="text-lg font-bold text-slate-900">Buscador instantáneo ({len(sitemap_urls)} calculadoras activas)</h2>
            <input type="text" id="buscador-mapa" oninput="filtrarMapaWeb()" placeholder="Buscar medida o modelo (ej. 175/65, Corsa, Primera, Madrid...)" class="p-2.5 border rounded-xl text-sm w-full sm:w-80">
        </div>
        <ul class="grid grid-cols-1 md:grid-cols-2 gap-2">{items_html}</ul>
    </div>
    """
    render_page(
        "mapa-web.html",
        f"Buscador de medidas ITV y mapa web | {SITE_NAME}",
        "Encuentra al instante la tabla de equivalencia de neumáticos de tu coche o calcula el gasto de combustible de tu ruta.",
        "Índice general y buscador de medidas ITV",
        f"Filtra en tiempo real entre nuestras {len(sitemap_urls)} calculadoras técnicas preconfiguradas.",
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
        <p><strong>1. Afiliación de Amazon:</strong> {SITE_NAME} participa en el Programa de Afiliados de Amazon de la UE, un programa de publicidad para afiliados diseñado para ofrecer a sitios web un modo de obtener comisiones por publicidad, publicitando e incluyendo enlaces a Amazon.es.</p>
        <p><strong>2. Cookies y publicidad (Google AdSense):</strong> Utilizamos almacenamiento local para recordar su preferencia de privacidad y, en su caso, proveedores como Google utilizan cookies para mostrar anuncios relevantes basados en visitas anteriores. Puede desactivar las cookies personalizadas en la configuración de su navegador o en Configuración de anuncios de Google.</p>
    """
    render_page(
        "privacidad-cookies.html", f"Política de privacidad y cookies | {SITE_NAME}", "Política de privacidad, cookies y divulgación de afiliados.",
        "Política de privacidad y cookies (RGPD)", "Transparencia sobre cookies, Google AdSense y Amazon Afiliados.",
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

    # Generar archivo ads.txt si hay cliente de AdSense configurado
    ads_pub = ADSENSE_CLIENT.replace("ca-", "") if ADSENSE_CLIENT else "pub-0000000000000000"
    with open(os.path.join(OUTPUT_DIR, "ads.txt"), "w", encoding="utf-8") as f:
        f.write(f"google.com, {ads_pub}, DIRECT, f08c47fec0942fa0\n")

    print(f"[OK] Portal v2.0 generado en ./public con {len(sitemap_urls)} páginas SEO, gráfico SVG, ads.txt y ortotipografía corregida.")


if __name__ == "__main__":
    main()