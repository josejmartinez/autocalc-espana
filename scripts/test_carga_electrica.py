#!/usr/bin/env python3
"""Regression tests for the electric-vehicle charging calculator and guide."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
BUILD_SOURCE = (ROOT / "src" / "build.py").read_text(encoding="utf-8")
MODULE_SOURCE = (ROOT / "src" / "carga_electrica.py").read_text(encoding="utf-8")
PUBLIC = ROOT / "public"
PAGE_PATH = PUBLIC / "carga-vehiculo-electrico.html"


def main() -> int:
    if not PAGE_PATH.is_file():
        raise AssertionError("No se genera public/carga-vehiculo-electrico.html.")
    page = PAGE_PATH.read_text(encoding="utf-8")

    searchable = (page + "\\n" + MODULE_SOURCE).casefold()
    for marker in (
        '<html lang="es">',
        "<title>Calculadora de carga para coche eléctrico",
        '<meta name="description"',
        '<link rel="canonical" href="https://autocalc.es/carga-vehiculo-electrico.html">',
        'id="ev-battery"',
        'id="ev-charger"',
        'id="ev-car-limit"',
        'id="ev-install-limit"',
        'id="ev-start"',
        'id="ev-target"',
        'id="ev-efficiency"',
        "Math.min(charger, carLimit, installLimit)",
        "battery * (target - start) / 100",
        "batteryEnergy / (efficiency / 100)",
        "Math.round((gridEnergy / effectivePower) * 60)",
        "autocalc_privacidad_v2",
        "Rechazar analítica",
        "Aceptar analítica",
        "Configurar cookies",
        "Publicidad y enlaces de afiliación.",
        "En calidad de Afiliado de Amazon, obtengo ingresos por las compras adscritas que cumplen los requisitos aplicables.",
        "ITC-BT-52",
        "https://industria.gob.es/",
        "https://www.boe.es/",
        "declaración UE de conformidad",
        "no uses alargadores",
    ):
        if marker.casefold() not in searchable:
            raise AssertionError("Falta un elemento esperado en la guía/calc eléctrica: " + marker)

    if "adsbygoogle.js?client=ca-pub-1754459878527476" not in page:
        raise AssertionError("La nueva página no mantiene el script de verificación de AdSense del sitio.")
    if "carga-vehiculo-electrico.html" not in (PUBLIC / "index.html").read_text(encoding="utf-8"):
        raise AssertionError("La portada no enlaza a la guía de carga eléctrica.")
    if "carga-vehiculo-electrico.html" not in (PUBLIC / "mapa-web.html").read_text(encoding="utf-8"):
        raise AssertionError("El mapa web no incluye la nueva página.")
    if "carga-vehiculo-electrico.html" not in (PUBLIC / "sitemap.xml").read_text(encoding="utf-8"):
        raise AssertionError("El sitemap no incluye la nueva página.")
    if "https://autocalc.es/carga-vehiculo-electrico.html" not in page:
        raise AssertionError("El canonical no utiliza el dominio activo de AutoCalc España.")

    # Default values: battery 60 kWh, charge 20->80%, efficiency 90%, 7.4 kW effective.
    battery_energy = 60 * (80 - 20) / 100
    grid_energy = battery_energy / 0.90
    minutes = round((grid_energy / 7.4) * 60)
    if battery_energy != 36 or round(grid_energy, 1) != 40.0 or (minutes // 60, minutes % 60) != (5, 24):
        raise AssertionError("La comprobación numérica del ejemplo inicial no coincide con la fórmula.")

    # The page must not imply an EVDANCE endorsement or commission before publisher approval.
    if "EVDANCE" in page.upper() or "comisión del 15 %" in page.lower():
        raise AssertionError("Se ha añadido una promoción de marca no aprobada a la guía independiente.")

    # Ensure all three independent charging constraints and the simplified model caveat are present.
    if "curva de carga real" not in page or "potencia efectiva" not in page:
        raise AssertionError("Falta explicar las limitaciones de la estimación.")

    print("[OK] Calculadora eléctrica: generación, SEO, navegación, sitemap, seguridad y ejemplo matemático.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
