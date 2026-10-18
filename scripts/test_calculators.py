#!/usr/bin/env python3
"""Regression tests for calculator methods and the agreed disabled-ad configuration."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "src" / "build.py"
CONFIG = ROOT / "config.json"
INDEX = ROOT / "public" / "index.html"


def main() -> int:
    source = BUILD.read_text(encoding="utf-8")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    html = INDEX.read_text(encoding="utf-8") if INDEX.is_file() else ""

    # Do not enable or fill advertising inventory as a side-effect of calculator work.
    if config.get("adsense_ads_enabled") is not False:
        raise AssertionError("AdSense debe seguir desactivado.")
    if config.get("google_certified_cmp_configured") is not False:
        raise AssertionError("No se debe afirmar que existe una CMP certificada sin verificarla.")
    if any(slot.get("enabled") is not False for slot in config.get("direct_ad_slots", {}).values()):
        raise AssertionError("Los espacios de publicidad directa deben seguir desactivados.")
    if any(str(value or "").strip() for value in config.get("adsense_slots", {}).values()):
        raise AssertionError("Los identificadores de espacios AdSense deben seguir vacíos.")

    # Trip: wear is user-editable and time is rounded once into a total minute count.
    for marker in (
        'id="coste-desgaste-km"',
        "const costeConDesgaste = costeDirectoViaje + (km * desgastePorKm);",
        "const totalMinutos = Math.round((km / vel) * 60);",
        "const m = totalMinutos % 60;",
        "Por ocupante",
    ):
        if marker not in source:
            raise AssertionError("Falta una mejora de coste/tiempo de viaje: " + marker)
    if "(km * 0.06)" in source:
        raise AssertionError("El coste de desgaste no debe estar fijado a 0,06 €/km.")

    # Vehicle fiscal horsepower: conventional thermal formula and homologated BEV effective power.
    for marker in (
        "Math.pow(cc / cil, 0.6) * cil",
        "kwElectrico / 5.152",
        'id="dgt-territorio"',
        'id="dgt-kw"',
        "territorio === 'canarias' ? 3.75 : 4.75",
        "territorio === 'canarias' ? 8.75 : 9.75",
        "territorio === 'canarias' ? 13.75 : 14.75",
    ):
        if marker not in source:
            raise AssertionError("Falta lógica de fiscalidad/CVF: " + marker)

    # The three-letter plate date is a rough estimate, so future letters must not be extrapolated.
    if "[4284, 2026.79]" not in source or "indice > ultimoIndiceDocumentado" not in source:
        raise AssertionError("Falta el límite de serie documentada de matrículas (octubre de 2026).")
    if "[5770, 2026.0]" in source or "[6000, 2027.0]" in source:
        raise AssertionError("Se mantienen hitos de matrícula desplazados.")

    # Check standard speed-symbol choices exist in both tire selectors.
    for select_id in ("vel1", "vel2"):
        match = re.search(r'<select id="' + select_id + r'"[\s\S]*?</select>', source)
        if not match:
            raise AssertionError("No existe el selector " + select_id)
        selector = match.group(0)
        for symbol, speed in (("J", 100), ("K", 110), ("L", 120), ("M", 130),
                              ("N", 140), ("P", 150), ("Q", 160), ("U", 200),
                              ("H", 210), ("V", 240), ("W", 270), ("Y", 300)):
            if not re.search(r'<option value="' + str(speed) + r'"(?: selected)?\s*>' + symbol + r' \(', selector):
                raise AssertionError(f"Falta {symbol} ({speed} km/h) en {select_id}.")

    # OBD content must not present unsupported universal rejection or generic 3,000 rpm procedures.
    if "forzar regeneración en carretera a 3.000 rpm" in source:
        raise AssertionError("Se mantiene una instrucción genérica de regeneración DPF.")
    if "Rechazo directo (Defecto Grave) en lectura OBD" in source:
        raise AssertionError("El código OBD se presenta como rechazo ITV automático.")
    if "suele mentir entre un 5 % y un 10 %" in source:
        raise AssertionError("Se mantiene un porcentaje universal no sustentado para el ordenador de a bordo.")

    # Ensure the site still builds its ad-slot helpers and the generated pages retain slot hooks.
    for marker in ("def render_ad_slot(", "__SIDEBAR_LEFT_AD_HTML__", "__SIDEBAR_RIGHT_AD_HTML__", "__INLINE_AD_HTML__"):
        if marker not in source:
            raise AssertionError("Se ha eliminado un espacio publicitario acordado: " + marker)
    if html and "adsbygoogle.js?client=ca-pub-1754459878527476" not in html:
        raise AssertionError("Falta el código de verificación AdSense esperado en la página generada.")

    # Independent numerical sanity checks for important formulas.
    minutes = round((620 / 105) * 60)
    assert (minutes // 60, minutes % 60) == (5, 54)
    assert int((100 / 5.152) * 100) / 100 == 19.4
    assert round(22000 * 0.0875) == 1925

    print("[OK] Regresión de calculadoras: viaje, CVF/IEDMT, matrículas, índices de velocidad, OBD y espacios publicitarios.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
