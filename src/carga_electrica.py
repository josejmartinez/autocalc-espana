#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Página independiente y calculadora de carga para vehículos eléctricos."""
from __future__ import annotations

import json
import os
from html import escape


EV_PAGE = r"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Calculadora de carga para coche eléctrico: tiempo, kWh y potencia | AutoCalc España</title>
  <meta name="description" content="Calcula el tiempo aproximado de carga de tu coche eléctrico según batería, porcentaje inicial y final, potencia del cargador, límite del vehículo y eficiencia. Guía de 2,3 a 22 kW.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="__CANONICAL__">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Calculadora de carga para coche eléctrico | AutoCalc España">
  <meta property="og:description" content="Estima tiempo de carga y energía de red, y compara potencias domésticas de recarga.">
  <meta property="og:url" content="__CANONICAL__">
  <meta name="theme-color" content="#0f172a">
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  __VERIFY_TAG__
  <script src="https://cdn.tailwindcss.com"></script>
  __ADSENSE_HEAD__
  <script type="application/ld+json">__SCHEMA__</script>
  <style>
    html { scroll-behavior: smooth; }
    :focus-visible { outline: 3px solid #f59e0b; outline-offset: 3px; }
    .field { width:100%; border:1px solid #cbd5e1; border-radius:.75rem; padding:.7rem .8rem; background:white; color:#0f172a; }
    .field:focus { border-color:#d97706; outline:2px solid #fbbf24; outline-offset:1px; }
    .result-card { min-height:118px; }
    .prose-auto p { margin-top:.75rem; margin-bottom:.75rem; line-height:1.7; }
    .prose-auto li { margin-top:.4rem; line-height:1.65; }
    .prose-auto h2 { font-size:1.25rem; font-weight:800; color:#0f172a; margin-top:1.5rem; margin-bottom:.5rem; }
    .prose-auto h3 { font-size:1rem; font-weight:750; color:#0f172a; margin-top:1rem; }
    @media print { header, footer, #cookie-banner, .no-print { display:none!important; } body { background:#fff!important; } .print-card { box-shadow:none!important; } }
  </style>
</head>
<body class="min-h-screen bg-slate-50 text-slate-800 font-sans">
<header class="bg-slate-900 text-white shadow-md no-print">
  <div class="mx-auto max-w-6xl px-4 py-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
    <a href="index.html" class="flex items-center gap-2" aria-label="AutoCalc España, inicio">
      <span class="text-2xl font-extrabold tracking-tight text-amber-400">AutoCalc España</span>
      <span class="hidden md:inline text-xs bg-slate-800 text-slate-300 px-2 py-1 rounded border border-slate-700">Portal técnico del motor</span>
    </a>
    <nav class="flex flex-wrap gap-2 text-xs font-semibold" aria-label="Navegación principal">
      <a href="index.html" class="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 hover:bg-slate-700">Calculadoras</a>
      <a href="mapa-web.html" class="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 hover:bg-slate-700">Mapa web</a>
      <a href="desguaces-itv-aranjuez-comarca-las-vegas.html" class="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 hover:bg-slate-700">Talleres y recambios</a>
    </nav>
  </div>
</header>

<main class="mx-auto max-w-6xl w-full px-4 py-7 sm:py-10">
  <nav class="mb-4 text-xs text-slate-500 no-print" aria-label="Migas de pan">
    <a href="index.html" class="underline hover:text-amber-700">Inicio</a><span class="mx-2">/</span><span aria-current="page">Carga de coche eléctrico</span>
  </nav>
  <section class="rounded-3xl bg-slate-900 text-white p-6 sm:p-9 shadow-sm">
    <p class="text-xs font-bold uppercase tracking-[.16em] text-amber-300">Herramienta gratuita · España</p>
    <h1 class="mt-3 text-3xl sm:text-4xl font-extrabold tracking-tight">Calculadora de carga para coche eléctrico</h1>
    <p class="mt-4 max-w-3xl text-sm sm:text-base text-slate-300 leading-7">Estima cuánto tardará la recarga según la batería útil, el porcentaje de carga, la potencia del equipo y el límite de carga en corriente alterna (AC) del vehículo. La estimación muestra también la energía aproximada tomada de la red.</p>
    <div class="mt-5 flex flex-wrap gap-2 text-xs">
      <span class="rounded-full bg-slate-800 px-3 py-1.5 border border-slate-700">2,3–22 kW</span>
      <span class="rounded-full bg-slate-800 px-3 py-1.5 border border-slate-700">Tiempo y kWh</span>
      <span class="rounded-full bg-slate-800 px-3 py-1.5 border border-slate-700">Sin registro</span>
    </div>
  </section>

  <section class="mt-7 grid gap-6 lg:grid-cols-[1.1fr_.9fr] items-start" aria-labelledby="titulo-calculadora">
    <div class="print-card rounded-2xl border border-slate-200 bg-white p-5 sm:p-7 shadow-sm">
      <div class="mb-5">
        <h2 id="titulo-calculadora" class="text-xl font-extrabold text-slate-900">Calcula tu recarga</h2>
        <p class="mt-1 text-sm text-slate-600">Introduce la capacidad útil y los límites de potencia que correspondan a tu coche y a tu instalación.</p>
      </div>
      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label for="ev-battery" class="block text-sm font-semibold mb-1.5">Capacidad útil de batería (kWh)</label>
          <input id="ev-battery" class="field" type="number" min="1" max="250" step="0.1" value="60" inputmode="decimal">
          <p class="mt-1 text-xs text-slate-500">Usa la capacidad útil, no necesariamente la capacidad bruta anunciada.</p>
        </div>
        <div>
          <label for="ev-charger" class="block text-sm font-semibold mb-1.5">Potencia nominal del cargador (kW)</label>
          <input id="ev-charger" class="field" type="number" min="0.1" max="100" step="0.1" value="7.4" inputmode="decimal">
        </div>
        <div>
          <label for="ev-car-limit" class="block text-sm font-semibold mb-1.5">Máxima potencia AC admitida por el coche (kW)</label>
          <input id="ev-car-limit" class="field" type="number" min="0.1" max="100" step="0.1" value="11" inputmode="decimal">
          <p class="mt-1 text-xs text-slate-500">Consulta la ficha técnica de tu modelo y versión.</p>
        </div>
        <div>
          <label for="ev-install-limit" class="block text-sm font-semibold mb-1.5">Límite destinado a la recarga (kW)</label>
          <input id="ev-install-limit" class="field" type="number" min="0.1" max="100" step="0.1" value="7.4" inputmode="decimal">
          <p class="mt-1 text-xs text-slate-500">Es el límite efectivo del circuito o de la gestión de carga, si lo conoces; no es necesariamente la potencia contratada total.</p>
        </div>
        <div>
          <label for="ev-start" class="block text-sm font-semibold mb-1.5">Batería al empezar (%)</label>
          <input id="ev-start" class="field" type="number" min="0" max="100" step="1" value="20" inputmode="numeric">
        </div>
        <div>
          <label for="ev-target" class="block text-sm font-semibold mb-1.5">Carga objetivo (%)</label>
          <input id="ev-target" class="field" type="number" min="0" max="100" step="1" value="80" inputmode="numeric">
        </div>
        <div>
          <label for="ev-price" class="block text-sm font-semibold mb-1.5">Precio de energía (€/kWh)</label>
          <input id="ev-price" class="field" type="number" min="0" max="5" step="0.01" value="0.20" inputmode="decimal">
          <p class="mt-1 text-xs text-slate-500">Introduce el precio efectivo por kWh que quieras usar para la estimación.</p>
        </div>
        <div class="sm:col-span-2">
          <div class="flex items-center justify-between gap-3">
            <label for="ev-efficiency" class="block text-sm font-semibold">Eficiencia global estimada</label>
            <output id="ev-efficiency-value" for="ev-efficiency" class="text-sm font-bold text-slate-900">90 %</output>
          </div>
          <input id="ev-efficiency" class="mt-3 w-full accent-amber-500" type="range" min="80" max="98" step="1" value="90">
          <div class="flex justify-between text-xs text-slate-500"><span>80 %</span><span>98 %</span></div>
        </div>
      </div>
      <p id="ev-error" class="hidden mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800" role="alert"></p>
      <div class="mt-5 flex flex-wrap gap-2 no-print">
        <button type="button" id="ev-reset" class="rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-bold hover:bg-slate-50">Restablecer ejemplo</button>
        <button type="button" id="ev-print" class="rounded-xl bg-amber-500 px-4 py-2.5 text-sm font-bold text-slate-950 hover:bg-amber-400">Guardar / imprimir</button>
      </div>
    </div>

    <aside class="rounded-2xl border border-slate-200 bg-white p-5 sm:p-7 shadow-sm" aria-live="polite" aria-atomic="true">
      <h2 class="text-xl font-extrabold text-slate-900">Resultado estimado</h2>
      <p class="mt-1 text-sm text-slate-600">La potencia aplicada es la menor de los tres límites introducidos.</p>
      <div class="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
        <div class="result-card rounded-xl bg-amber-50 border border-amber-100 p-4">
          <p class="text-xs font-bold text-amber-900 uppercase tracking-wide">Tiempo de carga</p>
          <p id="ev-time" class="mt-2 text-2xl sm:text-3xl font-extrabold text-slate-900">5 h 24 min</p>
          <p class="mt-1 text-xs text-slate-600">Estimación matemática</p>
        </div>
        <div class="result-card rounded-xl bg-slate-50 border border-slate-200 p-4">
          <p class="text-xs font-bold text-slate-600 uppercase tracking-wide">Potencia AC efectiva</p>
          <p id="ev-effective-power" class="mt-2 text-2xl sm:text-3xl font-extrabold text-slate-900">7,4 kW</p>
          <p class="mt-1 text-xs text-slate-600">Mínimo de cargador, coche e instalación</p>
        </div>
        <div class="result-card rounded-xl bg-slate-50 border border-slate-200 p-4">
          <p class="text-xs font-bold text-slate-600 uppercase tracking-wide">Energía a la batería</p>
          <p id="ev-battery-energy" class="mt-2 text-2xl font-extrabold text-slate-900">36,0 kWh</p>
          <p class="mt-1 text-xs text-slate-600">Incremento de carga solicitado</p>
        </div>
        <div class="result-card rounded-xl bg-slate-50 border border-slate-200 p-4">
          <p class="text-xs font-bold text-slate-600 uppercase tracking-wide">Energía aproximada de red</p>
          <p id="ev-grid-energy" class="mt-2 text-2xl font-extrabold text-slate-900">40,0 kWh</p>
          <p class="mt-1 text-xs text-slate-600">Incluye pérdidas estimadas</p>
        </div>
        <div class="result-card xl:col-span-2 rounded-xl bg-emerald-50 border border-emerald-100 p-4">
          <p class="text-xs font-bold text-emerald-900 uppercase tracking-wide">Coste estimado de energía</p>
          <p id="ev-cost" class="mt-2 text-2xl font-extrabold text-slate-900">8,00 €</p>
          <p class="mt-1 text-xs text-slate-600">kWh de red × precio introducido; no incluye cargos fijos</p>
        </div>
      </div>
      <div class="mt-5 rounded-xl border border-blue-100 bg-blue-50 p-4 text-sm text-blue-950">
        <strong>Importante:</strong> es una estimación simplificada. La potencia real puede variar por temperatura, gestión de carga, tensión, nivel de batería y curva de carga del vehículo.
      </div>
    </aside>
  </section>

  <section class="prose-auto mt-8 rounded-2xl border border-slate-200 bg-white p-5 sm:p-7 shadow-sm">
    <h2 class="!mt-0">Cómo interpretar la potencia de carga</h2>
    <p>La potencia anunciada en un cargador no determina por sí sola lo que recibirá la batería. En carga AC también limita el cargador interno del vehículo y puede limitar la instalación o un sistema de balanceo dinámico. Por ejemplo, si el coche acepta hasta 11 kW en AC, no cargará a 22 kW en un equipo de 22 kW solo por conectarlo a él.</p>
    <p>El cálculo usa la energía solicitada por la batería dividida entre la eficiencia indicada para estimar lo que procede de la red. Después divide esa energía por la potencia efectiva estimada. No modela la reducción de potencia que algunos vehículos aplican al acercarse al 100 %.</p>

    <h2>Comparativa orientativa de potencias domésticas</h2>
    <p>Las siguientes cifras son referencias habituales, no una recomendación de instalación. El tiempo exacto depende de los datos introducidos en la calculadora y de las capacidades reales del coche y del punto de recarga.</p>
    <div class="not-prose overflow-x-auto rounded-xl border border-slate-200">
      <table class="w-full min-w-[620px] text-sm">
        <thead class="bg-slate-100 text-left text-slate-700">
          <tr><th class="p-3">Potencia nominal</th><th class="p-3">Configuración orientativa</th><th class="p-3">Cuándo puede encajar</th><th class="p-3">Qué verificar</th></tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr><td class="p-3 font-bold">2,3 kW</td><td class="p-3">230 V · aproximadamente 10 A</td><td class="p-3">Recargas lentas con muchas horas disponibles.</td><td class="p-3">Toma, circuito, equipo y uso autorizados por el fabricante.</td></tr>
          <tr><td class="p-3 font-bold">3,7 kW</td><td class="p-3">Monofásica · aproximadamente 16 A</td><td class="p-3">Uso doméstico si el circuito está preparado.</td><td class="p-3">Línea y protecciones adecuadas; no asumir que cualquier enchufe sirve.</td></tr>
          <tr><td class="p-3 font-bold">7,4 kW</td><td class="p-3">Monofásica · aproximadamente 32 A</td><td class="p-3">Cargas nocturnas más rápidas.</td><td class="p-3">Potencia de acometida disponible, protecciones y límite AC del coche.</td></tr>
          <tr><td class="p-3 font-bold">11 kW</td><td class="p-3">Trifásica · aproximadamente 16 A por fase</td><td class="p-3">Vehículos y viviendas con suministro trifásico compatible.</td><td class="p-3">Que el coche admita carga AC trifásica y la instalación pueda suministrarla.</td></tr>
          <tr><td class="p-3 font-bold">22 kW</td><td class="p-3">Trifásica · aproximadamente 32 A por fase</td><td class="p-3">Casos con vehículo, instalación y necesidad compatibles.</td><td class="p-3">Muchos coches no aceptan 22 kW AC; confirma siempre la ficha técnica.</td></tr>
        </tbody>
      </table>
    </div>

    <h2>Comparativa de cargadores portátiles y wallbox</h2>
    <p>La diferencia no es solo la potencia: importa dónde se conecta el equipo, cómo se alimenta el circuito y si necesitas movilidad o una solución fija. La tabla compara categorías de producto; las características concretas cambian según el modelo.</p>
    <div class="not-prose overflow-x-auto rounded-xl border border-slate-200">
      <table class="w-full min-w-[680px] text-sm">
        <thead class="bg-slate-100 text-left text-slate-700">
          <tr><th class="p-3">Tipo de equipo</th><th class="p-3">Uso posible</th><th class="p-3">Ventaja principal</th><th class="p-3">Límite o precaución</th></tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr><td class="p-3 font-bold">Portátil para toma doméstica</td><td class="p-3">Recarga lenta ocasional, si el fabricante y la instalación lo permiten.</td><td class="p-3">Fácil de transportar.</td><td class="p-3">Potencia reducida; el estado del enchufe y del circuito es esencial. No uses alargadores.</td></tr>
          <tr><td class="p-3 font-bold">Portátil con toma industrial compatible</td><td class="p-3">Garajes o espacios con toma CEE adecuada; potencia según tensión y amperaje.</td><td class="p-3">Puede combinar movilidad y mayor potencia.</td><td class="p-3">No basta con que el enchufe encaje: verifica fases, intensidad, protecciones e instrucciones.</td></tr>
          <tr><td class="p-3 font-bold">Wallbox fijo monofásico</td><td class="p-3">Punto de recarga doméstico dedicado.</td><td class="p-3">Instalación estable; algunos modelos incorporan balanceo de potencia.</td><td class="p-3">Requiere dimensionar el circuito, protecciones y montaje conforme a normativa.</td></tr>
          <tr><td class="p-3 font-bold">Wallbox fijo trifásico</td><td class="p-3">Instalaciones trifásicas y vehículos compatibles con carga AC trifásica.</td><td class="p-3">Puede alcanzar 11 o 22 kW según el equipo.</td><td class="p-3">Muchos vehículos limitan la carga AC a una potencia inferior; confirma la ficha del modelo.</td></tr>
        </tbody>
      </table>
    </div>
    <p>Para comparar modelos concretos, revisa potencia real, compatibilidad de la toma, protecciones declaradas, resistencia ambiental, documentación de conformidad, garantía, soporte y coste de envío. Un mayor número de kW no significa automáticamente una mejor compra.</p>

    <h2>Cómo elegir un cargador para tu coche eléctrico</h2>
    <div class="not-prose grid gap-3 md:grid-cols-2">
      <article class="rounded-xl border border-slate-200 p-4">
        <h3 class="font-extrabold text-slate-900">1. Compatibilidad del conector</h3>
        <p class="mt-1 text-sm text-slate-600">En Europa, muchos turismos usan conector Type 2 para carga AC, pero confirma la toma y los modos de carga de la versión concreta del vehículo.</p>
      </article>
      <article class="rounded-xl border border-slate-200 p-4">
        <h3 class="font-extrabold text-slate-900">2. Potencia AC máxima del coche</h3>
        <p class="mt-1 text-sm text-slate-600">Comprueba los kW admitidos en corriente alterna, la posibilidad de carga monofásica o trifásica y si existen límites por versión o año.</p>
      </article>
      <article class="rounded-xl border border-slate-200 p-4">
        <h3 class="font-extrabold text-slate-900">3. Circuito y protecciones</h3>
        <p class="mt-1 text-sm text-slate-600">Solicita una evaluación de la instalación, protecciones, puesta a tierra y gestión de potencia. No elijas únicamente por el valor de kW impreso en la caja.</p>
      </article>
      <article class="rounded-xl border border-slate-200 p-4">
        <h3 class="font-extrabold text-slate-900">4. Documentación y posventa</h3>
        <p class="mt-1 text-sm text-slate-600">Revisa declaración UE de conformidad, manual comprensible, garantía, servicio posventa, devolución, stock y coste de envío a España.</p>
      </article>
    </div>

    <h2>Seguridad eléctrica en España</h2>
    <p>Una toma doméstica no debe darse por apta para una recarga prolongada por el simple hecho de encajar el enchufe. Usa un equipo de carga compatible con sus instrucciones y pide que un profesional cualificado revise el circuito y las protecciones. No uses alargadores, regletas ni adaptadores improvisados; detén la carga si detectas calentamiento anormal, daño o decoloración.</p>
    <p>Las instalaciones fijas de recarga deben cumplir la normativa eléctrica que les corresponda, incluida la ITC-BT-52 del Reglamento electrotécnico para baja tensión en España. Consulta la <a class="font-semibold text-amber-700 underline" href="https://industria.gob.es/Calidad-Industrial/seguridadindustrial/instalacionesindustriales/baja-tension/Documents/bt/guia_bt_52_nov17R1.pdf" target="_blank" rel="noopener noreferrer">Guía técnica oficial de aplicación de la ITC-BT-52</a> y el <a class="font-semibold text-amber-700 underline" href="https://www.boe.es/eli/es/rd/2002/08/02/842/con" target="_blank" rel="noopener noreferrer">Reglamento electrotécnico para baja tensión en el BOE</a>. La solución adecuada depende del tipo de inmueble, plaza, circuito y equipo.</p>

    <h2>Preguntas frecuentes</h2>
    <h3>¿Cuánto tarda en cargar un coche eléctrico de 60 kWh?</h3>
    <p>No hay un tiempo único. Con una batería útil de 60 kWh, una recarga del 20 al 80 % requiere almacenar 36 kWh. Con eficiencia estimada del 90 % son unos 40 kWh de red; a 7,4 kW efectivos, la estimación matemática es aproximadamente 5 horas y 24 minutos. La curva de carga real puede alargar ese tiempo.</p>
    <h3>¿Un cargador de 22 kW cargará mi coche a 22 kW?</h3>
    <p>Solo si el vehículo admite esa potencia en AC y la instalación la suministra. La potencia efectiva está limitada por el elemento más restrictivo del sistema.</p>
    <h3>¿Es mejor un cargador portátil o un wallbox?</h3>
    <p>Depende de la frecuencia de carga, la potencia necesaria y la instalación. Un equipo portátil aporta flexibilidad si se utiliza en una conexión autorizada y compatible; un wallbox fijo permite una solución dedicada y puede incorporar control dinámico de potencia. No existe una opción universalmente mejor.</p>
    <h3>¿La calculadora predice el coste de la recarga?</h3>
    <p>Sí, ofrece una aproximación multiplicando la energía de red calculada por el precio por kWh que introduzcas. No incluye términos fijos ni otros conceptos que no estén incorporados en ese precio; la factura real puede variar.</p>

    <div class="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600">
      <strong>Alcance:</strong> AutoCalc España ofrece una estimación informativa, no una certificación de compatibilidad ni un proyecto eléctrico. Verifica los datos del vehículo y las instrucciones del fabricante; para dimensionar o modificar una instalación, consulta a un profesional cualificado.
    </div>
  </section>

  <section class="no-print mt-7 rounded-2xl bg-slate-900 p-5 sm:p-6 text-white">
    <h2 class="text-lg font-extrabold">Sigue explorando AutoCalc España</h2>
    <p class="mt-1 text-sm text-slate-300">Combina esta guía con otras herramientas gratuitas del portal.</p>
    <div class="mt-4 flex flex-wrap gap-2">
      <a class="rounded-lg bg-amber-500 px-4 py-2 text-sm font-bold text-slate-950 hover:bg-amber-400" href="index.html">Abrir calculadoras de motor</a>
      <a class="rounded-lg border border-slate-600 px-4 py-2 text-sm font-bold hover:bg-slate-800" href="mapa-web.html">Buscar todas las guías</a>
    </div>
  </section>
</main>

<footer class="mt-10 bg-slate-900 py-7 text-xs text-slate-400 no-print">
  <div class="mx-auto max-w-6xl px-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
    <div>
      <p class="font-bold text-slate-200">AutoCalc España © 2026</p>
      <p class="mt-1">Calculadoras independientes para ayudar a entender el mantenimiento y uso del vehículo.</p>
      <p class="mt-2">Publicidad y enlaces de afiliación. __AMAZON_DISCLOSURE__ Los enlaces de afiliación se identificarán de forma visible cuando estén configurados y aprobados.</p>
    </div>
    <nav class="flex flex-wrap gap-4" aria-label="Enlaces legales">
      <a href="index.html" class="hover:text-white underline">Inicio</a>
      <a href="mapa-web.html" class="hover:text-white underline">Mapa web</a>
      <a href="aviso-legal.html" class="hover:text-white underline">Aviso legal</a>
      <a href="privacidad-cookies.html" class="hover:text-white underline">Privacidad y cookies</a>
      <button type="button" onclick="mostrarPreferenciasCookies()" class="hover:text-white underline">Configurar cookies</button>
    </nav>
  </div>
</footer>

<div id="cookie-banner" role="dialog" aria-label="Preferencias de privacidad" aria-live="polite" class="fixed bottom-0 inset-x-0 z-50 hidden border-t border-slate-700 bg-slate-950/95 p-4 text-white no-print">
  <div class="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 text-xs sm:flex-row">
    <p class="text-slate-300">Google Analytics solo se cargará si aceptas expresamente la medición estadística. Puedes cambiar tu elección desde «Configurar cookies». Consulta la <a href="privacidad-cookies.html" class="underline text-amber-400">Política de privacidad y cookies</a>.</p>
    <div class="flex shrink-0 gap-2">
      <button type="button" onclick="gestionarCookies('essential')" class="rounded border border-slate-500 px-3 py-2 font-semibold hover:bg-slate-800">Rechazar analítica</button>
      <button type="button" onclick="gestionarCookies('analytics')" class="rounded border border-slate-500 px-3 py-2 font-semibold hover:bg-slate-800">Aceptar analítica</button>
    </div>
  </div>
</div>

<script>
(() => {
  const ANALYTICS_ID = __ANALYTICS_ID__;
  const CONSENT_KEY = 'autocalc_privacidad_v2';

  const number = (id) => Number.parseFloat(document.getElementById(id).value);
  const fmt = (value, digits = 1) => new Intl.NumberFormat('es-ES', { maximumFractionDigits: digits }).format(value);

  function calculateCharge() {
    const battery = number('ev-battery');
    const charger = number('ev-charger');
    const carLimit = number('ev-car-limit');
    const installLimit = number('ev-install-limit');
    const start = number('ev-start');
    const target = number('ev-target');
    const efficiency = number('ev-efficiency');
    const pricePerKwh = number('ev-price');
    const error = document.getElementById('ev-error');
    document.getElementById('ev-efficiency-value').textContent = fmt(efficiency, 0) + ' %';

    const valuesValid = Number.isFinite(battery) && battery >= 1 && battery <= 250
      && Number.isFinite(charger) && charger > 0 && charger <= 100
      && Number.isFinite(carLimit) && carLimit > 0 && carLimit <= 100
      && Number.isFinite(installLimit) && installLimit > 0 && installLimit <= 100
      && Number.isFinite(start) && start >= 0 && start <= 100
      && Number.isFinite(target) && target >= 0 && target <= 100
      && Number.isFinite(efficiency) && efficiency >= 80 && efficiency <= 98
      && Number.isFinite(pricePerKwh) && pricePerKwh >= 0 && pricePerKwh <= 5;

    if (!valuesValid || target < start) {
      error.textContent = !valuesValid
        ? 'Revisa los valores: batería entre 1 y 250 kWh, potencias superiores a 0, porcentajes entre 0 y 100 y precio entre 0 y 5 €/kWh.'
        : 'La carga objetivo debe ser igual o superior al porcentaje inicial.';
      error.classList.remove('hidden');
      document.getElementById('ev-time').textContent = '—';
      document.getElementById('ev-effective-power').textContent = '—';
      document.getElementById('ev-battery-energy').textContent = '—';
      document.getElementById('ev-grid-energy').textContent = '—';
      document.getElementById('ev-cost').textContent = '—';
      return;
    }

    error.classList.add('hidden');
    const effectivePower = Math.min(charger, carLimit, installLimit);
    const batteryEnergy = battery * (target - start) / 100;
    const gridEnergy = batteryEnergy / (efficiency / 100);
    const estimatedCost = gridEnergy * pricePerKwh;
    const totalMinutes = effectivePower > 0 ? Math.round((gridEnergy / effectivePower) * 60) : 0;
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;

    document.getElementById('ev-time').textContent = hours + ' h ' + String(minutes).padStart(2, '0') + ' min';
    document.getElementById('ev-effective-power').textContent = fmt(effectivePower, 2) + ' kW';
    document.getElementById('ev-battery-energy').textContent = fmt(batteryEnergy, 1) + ' kWh';
    document.getElementById('ev-grid-energy').textContent = fmt(gridEnergy, 1) + ' kWh';
    document.getElementById('ev-cost').textContent = fmt(estimatedCost, 2) + ' €';
  }

  function readConsent() {
    try {
      const data = JSON.parse(localStorage.getItem(CONSENT_KEY) || 'null');
      const maxAge = 180 * 24 * 60 * 60 * 1000;
      if (!data || !['analytics', 'essential'].includes(data.choice)
        || !Number.isFinite(data.timestamp) || Date.now() - data.timestamp > maxAge
        || data.timestamp > Date.now()) {
        localStorage.removeItem(CONSENT_KEY);
        return null;
      }
      return data.choice;
    } catch (error) {
      return null;
    }
  }

  function removeAnalyticsCookies() {
    document.cookie.split(';').forEach((cookie) => {
      const name = cookie.split('=')[0].trim();
      if (!/^_ga(?:_|$)/.test(name)) return;
      const expired = name + '=; Max-Age=0; path=/; SameSite=Lax';
      document.cookie = expired;
      document.cookie = expired + '; domain=' + window.location.hostname;
    });
  }

  function setAnalytics(enabled) {
    if (!ANALYTICS_ID) return;
    window['ga-disable-' + ANALYTICS_ID] = !enabled;
    if (!enabled) {
      removeAnalyticsCookies();
      if (typeof window.gtag === 'function') window.gtag('consent', 'update', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
      return;
    }
    if (document.querySelector('script[data-autocalc-analytics]')) return;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function() { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', wait_for_update: 500 });
    window.gtag('js', new Date());
    window.gtag('consent', 'update', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
    window.gtag('config', ANALYTICS_ID, { allow_google_signals: false, allow_ad_personalization_signals: false });
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(ANALYTICS_ID);
    script.dataset.autocalcAnalytics = 'true';
    document.head.appendChild(script);
  }

  window.gestionarCookies = function(mode) {
    const choice = mode === 'analytics' ? 'analytics' : 'essential';
    try { localStorage.setItem(CONSENT_KEY, JSON.stringify({ choice, timestamp: Date.now() })); } catch (error) {}
    setAnalytics(choice === 'analytics');
    document.getElementById('cookie-banner').classList.add('hidden');
  };
  window.mostrarPreferenciasCookies = function() {
    document.getElementById('cookie-banner').classList.remove('hidden');
  };

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('#ev-battery,#ev-charger,#ev-car-limit,#ev-install-limit,#ev-start,#ev-target,#ev-price,#ev-efficiency')
      .forEach((control) => control.addEventListener('input', calculateCharge));
    document.getElementById('ev-reset').addEventListener('click', () => {
      document.getElementById('ev-battery').value = '60';
      document.getElementById('ev-charger').value = '7.4';
      document.getElementById('ev-car-limit').value = '11';
      document.getElementById('ev-install-limit').value = '7.4';
      document.getElementById('ev-start').value = '20';
      document.getElementById('ev-target').value = '80';
      document.getElementById('ev-price').value = '0.20';
      document.getElementById('ev-efficiency').value = '90';
      calculateCharge();
    });
    document.getElementById('ev-print').addEventListener('click', () => window.print());
    calculateCharge();

    const consent = readConsent();
    if (consent === 'analytics') setAnalytics(true);
    else if (consent === 'essential') removeAnalyticsCookies();
    else document.getElementById('cookie-banner').classList.remove('hidden');
  });
})();
</script>
</body>
</html>
"""


def render_charge_page(
    output_path: str,
    domain: str,
    site_name: str,
    adsense_client: str = "",
    analytics_id: str = "",
    verification_tag: str = "",
) -> None:
    """Write the EV calculator page using the site's active canonical domain."""
    canonical = f"{domain.rstrip('/')}/carga-vehiculo-electrico.html"
    adsense_script = ""
    if adsense_client:
        safe_client = escape(adsense_client, quote=True)
        adsense_script = (
            f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={safe_client}" '
            'crossorigin="anonymous"></script>'
        )

    faq_items = [
        (
            "¿Cuánto tarda en cargar un coche eléctrico de 60 kWh?",
            "Una recarga del 20 al 80 % almacena 36 kWh en una batería útil de 60 kWh. Con eficiencia estimada del 90 %, serían unos 40 kWh de red; a 7,4 kW efectivos, el cálculo simplificado da aproximadamente 5 horas y 24 minutos.",
        ),
        (
            "¿Un cargador de 22 kW cargará mi coche a 22 kW?",
            "Solo si el vehículo admite esa potencia en corriente alterna y la instalación la suministra. La potencia efectiva queda limitada por el elemento más restrictivo.",
        ),
        (
            "¿Es mejor un cargador portátil o un wallbox?",
            "Depende de la frecuencia de carga, potencia necesaria, equipo y características de la instalación. Un profesional cualificado puede ayudar a evaluar la solución adecuada.",
        ),
        (
            "¿La calculadora predice el coste de la recarga?",
            "La estimación de coste multiplica la energía de red por el precio por kWh introducido. No incluye términos fijos ni conceptos no incorporados en ese precio.",
        ),
    ]
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebApplication",
                "name": "Calculadora de carga para coche eléctrico",
                "applicationCategory": "UtilitiesApplication",
                "operatingSystem": "Any",
                "url": canonical,
                "description": "Estimador gratuito de tiempo y energía de carga de vehículos eléctricos.",
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": site_name, "item": f"{domain.rstrip('/')}/"},
                    {"@type": "ListItem", "position": 2, "name": "Carga de coche eléctrico", "item": canonical},
                ],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": answer}}
                    for question, answer in faq_items
                ],
            },
        ],
    }
    page = EV_PAGE
    replacements = {
        "__CANONICAL__": escape(canonical, quote=True),
        "__VERIFY_TAG__": verification_tag,
        "__ADSENSE_HEAD__": adsense_script,
        "__SCHEMA__": json.dumps(schema, ensure_ascii=False).replace("</", "<\\/"),
        "__ANALYTICS_ID__": json.dumps(analytics_id),
        "__AMAZON_DISCLOSURE__": escape(
            "En calidad de Afiliado de Amazon, obtengo ingresos por las compras adscritas que cumplen los requisitos aplicables."
        ),
    }
    for marker, value in replacements.items():
        page = page.replace(marker, value)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as output:
        output.write(page)
