#!/usr/bin/env python3
"""Structural regression checks for the section 6 parts comparator."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "public" / "index.html"
BUILD = ROOT / "src" / "build.py"
EXPECTED_IDS = {
    "pieza-catalogo", "rep-tipo", "rep-desguace", "rep-autodoc", "rep-horas",
    "rep-logistica-usado", "rep-envio-nuevo", "rep-tarifa-hora", "rep-recargo-taller",
    "res-desguace", "link-pieza-autodoc",
}


class PartsSelectParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_select = False
        self.in_option = False
        self.option_value = ""
        self.option_text: list[str] = []
        self.options: list[tuple[str, str]] = []
        self.loose_text: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs_dict = dict(attrs)
        if attrs_dict.get("id"):
            self.ids.add(attrs_dict["id"])
        if tag == "select" and attrs_dict.get("id") == "pieza-catalogo":
            if self.in_select:
                raise AssertionError("El selector de piezas está anidado.")
            self.in_select = True
        elif self.in_select and tag == "option":
            if self.in_option:
                raise AssertionError("Se encontró una opción anidada dentro de otra.")
            self.in_option = True
            self.option_value = attrs_dict.get("value", "")
            self.option_text = []

    def handle_endtag(self, tag: str) -> None:
        if self.in_select and tag == "option":
            self.options.append((self.option_value, "".join(self.option_text).strip()))
            self.in_option = False
        elif tag == "select" and self.in_select:
            self.in_select = False

    def handle_data(self, data: str) -> None:
        if self.in_select:
            if self.in_option:
                self.option_text.append(data)
            elif data.strip():
                self.loose_text.append(data.strip())


def main() -> int:
    if not INDEX.is_file():
        raise AssertionError("No existe public/index.html; ejecuta src/build.py antes del test.")

    html = INDEX.read_text(encoding="utf-8")
    build = BUILD.read_text(encoding="utf-8")
    parser = PartsSelectParser()
    parser.feed(html)
    parser.close()

    if parser.in_select or parser.in_option:
        raise AssertionError("El selector de catálogo no se cerró correctamente.")
    if parser.loose_text:
        raise AssertionError("Hay texto suelto dentro del selector de piezas: " + " | ".join(parser.loose_text))
    if len(parser.options) != 16:
        raise AssertionError(f"Se esperaban 16 piezas en el selector; encontradas {len(parser.options)}.")

    slugs: set[str] = set()
    for index, (value, label) in enumerate(parser.options, start=1):
        fields = value.split(",")
        if len(fields) != 9:
            raise AssertionError(f"Opción {index} debe contener 9 campos; contiene {len(fields)}: {label}")
        tipo, precio_usado, precio_nuevo, horas, consulta, logistica, envio, tarifa, recargo = fields
        if tipo not in {"carroceria", "mecanica", "desgaste"}:
            raise AssertionError(f"Categoría no válida en {label}: {tipo}")
        try:
            nums = [float(x) for x in (precio_usado, precio_nuevo, horas, logistica, envio, tarifa, recargo)]
        except ValueError as exc:
            raise AssertionError(f"Hay valores no numéricos en {label}") from exc
        if any(n < 0 for n in nums):
            raise AssertionError(f"Hay valores negativos en la opción {label}")
        if not consulta.strip() or not label.strip():
            raise AssertionError(f"La opción {index} no tiene búsqueda o etiqueta.")
        if label in slugs:
            raise AssertionError(f"Etiqueta duplicada en el catálogo: {label}")
        slugs.add(label)
        if "€ desguace vs." in label.lower() or "precios reales" in label.lower():
            raise AssertionError(f"La etiqueta presenta los ejemplos como precio real: {label}")

    missing_ids = EXPECTED_IDS - parser.ids
    if missing_ids:
        raise AssertionError("Faltan controles del comparador: " + ", ".join(sorted(missing_ids)))

    required_logic = (
        "function cargarPiezaCatalogo()",
        "function calcularDesguace()",
        "const costeUsadoDIY = precioUsado + logisticaUsado",
        "const costeNuevoDIY = precioNuevo + envioNuevo",
        "const costeTaller = precioNuevo + recargoPiezaTaller + manoObraTaller",
        "opciones.filter(opcion => opcion.clave !== 'usado')",
        "no recomendamos la pieza usada",
    )
    for marker in required_logic:
        if marker not in build:
            raise AssertionError("Falta lógica esperada en la sección 6: " + marker)

    for stale in ("precios medios reales en España", "autocompleta precios reales", "suele ofrecer el precio más bajo", "hasta un 70 % de ahorro"):
        if stale in html:
            raise AssertionError("Se mantiene una afirmación comercial no justificada: " + stale)

    print("[OK] Sección 6: 16 opciones correctas, controles completos y comparativa con logística, mano de obra y recargo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
