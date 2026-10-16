#!/usr/bin/env python3
"""Regression checks for tire candidate dimensions and catalog integrity."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from catalogo import MEDIDAS_ESPANA, MODELOS_COCHES, RUTAS_ESPANA, GARGANTA_POR_ANCHO  # noqa: E402


def diameter(width: int, profile: int, rim: int) -> float:
    return 25.4 * rim + 2 * width * profile / 100


def validate_pair(label: str, width1: int, profile1: int, rim1: int,
                  width2: int, profile2: int, rim2: int) -> None:
    dimensions = (width1, profile1, rim1, width2, profile2, rim2)
    if any(not isinstance(value, int) for value in dimensions):
        raise AssertionError(f"{label}: las medidas deben ser enteros.")
    for width, profile, rim in ((width1, profile1, rim1), (width2, profile2, rim2)):
        if not 100 <= width <= 355:
            raise AssertionError(f"{label}: ancho fuera de rango plausible: {width}")
        if not 20 <= profile <= 100:
            raise AssertionError(f"{label}: perfil fuera de rango plausible: {profile}")
        if not 10 <= rim <= 25:
            raise AssertionError(f"{label}: diámetro de llanta fuera de rango plausible: {rim}")

    d1 = diameter(width1, profile1, rim1)
    d2 = diameter(width2, profile2, rim2)
    diff = (d2 - d1) / d1 * 100
    if abs(diff) > 3.0 + 1e-9:
        raise AssertionError(
            f"{label}: la medida candidata queda fuera del ±3 % matemático "
            f"({width1}/{profile1} R{rim1} → {width2}/{profile2} R{rim2}: {diff:+.2f} %)."
        )


def main() -> int:
    if not MEDIDAS_ESPANA:
        raise AssertionError("MEDIDAS_ESPANA no puede estar vacío.")
    if not MODELOS_COCHES:
        raise AssertionError("MODELOS_COCHES no puede estar vacío.")

    for index, row in enumerate(MEDIDAS_ESPANA, start=1):
        if len(row) != 7:
            raise AssertionError(f"MEDIDAS_ESPANA[{index}] debe tener 7 campos.")
        validate_pair(
            f"MEDIDAS_ESPANA[{index}]",
            row[0], row[1], row[2], row[3], row[4], row[5]
        )

    slugs = [row[0] for row in MODELOS_COCHES]
    if len(slugs) != len(set(slugs)):
        raise AssertionError("MODELOS_COCHES contiene slugs duplicados.")

    for index, row in enumerate(MODELOS_COCHES, start=1):
        if len(row) != 9:
            raise AssertionError(f"MODELOS_COCHES[{index}] debe tener 9 campos.")
        validate_pair(
            f"MODELOS_COCHES[{row[0]}]",
            row[2], row[3], row[4], row[5], row[6], row[7]
        )
        if not isinstance(row[8], (int, float)) or not 1 <= row[8] <= 40:
            raise AssertionError(f"{row[0]}: consumo de referencia fuera de rango.")

    if not RUTAS_ESPANA:
        raise AssertionError("RUTAS_ESPANA no puede estar vacío.")
    for origen, destino, km, consumo in RUTAS_ESPANA:
        if not origen.strip() or not destino.strip() or km <= 0 or not 1 <= consumo <= 40:
            raise AssertionError(f"Ruta inválida: {origen}–{destino} ({km} km, {consumo} L/100 km).")

    for ancho, garganta in GARGANTA_POR_ANCHO.items():
        if not 100 <= ancho <= 355 or not isinstance(garganta, str) or not garganta.strip():
            raise AssertionError(f"Rango de garganta inválido para ancho {ancho}.")

    print(
        f"[OK] Catálogo revisado: {len(MEDIDAS_ESPANA)} pares de medidas, "
        f"{len(MODELOS_COCHES)} modelos y {len(RUTAS_ESPANA)} rutas."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
