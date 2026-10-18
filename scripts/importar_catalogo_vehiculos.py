#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Descarga y normaliza el catálogo abierto de identidad VehiclesDB.

No aporta especificaciones de motor/homologación: solo marcas/modelos y metadatos
que existan en la fuente. La salida debe llevar atribución visible en la web.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_URL = "https://cdn.jsdelivr.net/gh/vehiclesdb/vehiclesdb@2026.10.3/dist/vehicles.json"
SOURCE_HOME = "https://github.com/vehiclesdb/vehiclesdb"
ATTRIBUTION = "Vehicle data by VehiclesDB"
SCHEMA_VERSION = 1


def load_payload(path: Path | None, url: str = SOURCE_URL) -> dict[str, Any]:
    if path:
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "AutoCalc-Espana/1.0 (vehicle catalog importer)"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("El catálogo de origen debe ser un objeto JSON.")
    return payload


def normalize(payload: dict[str, Any], retrieved_at: str | None = None) -> dict[str, Any]:
    """Normalize the public nested makes/models projection without inventing specs."""
    makes = payload.get("makes")
    if not isinstance(makes, list):
        raise ValueError("El JSON de origen no contiene una lista 'makes' reconocible.")

    vehicles = []
    for make in makes:
        if not isinstance(make, dict) or not isinstance(make.get("models"), list):
            continue
        make_name = str(make.get("name") or "").strip()
        make_slug = str(make.get("slug") or "").strip()
        if not make_name or not make_slug:
            continue
        for model in make["models"]:
            if not isinstance(model, dict):
                continue
            kind = str(model.get("kind") or "car").strip().lower()
            if kind != "car":
                continue
            model_name = str(model.get("name") or "").strip()
            model_slug = str(model.get("slug") or "").strip()
            if not model_name or not model_slug:
                continue
            record = {
                "id": str(model.get("id") or f"car/{make_slug}/{model_slug}"),
                "kind": "car",
                "make": make_name,
                "make_slug": make_slug,
                "model": model_name,
                "model_slug": model_slug,
            }
            for field in ("body_types", "availability", "popularity", "sources", "xrefs"):
                if field in model:
                    record[field] = model[field]
            vehicles.append(record)

    # Deduplicate by stable identity, preferring the first source record.
    deduplicated = {}
    for vehicle in vehicles:
        deduplicated.setdefault(vehicle["id"], vehicle)
    result_vehicles = sorted(
        deduplicated.values(),
        key=lambda v: (v["make"].casefold(), v["model"].casefold(), v["id"]),
    )
    if not result_vehicles:
        raise ValueError("La importación no produjo modelos de turismo; no se publicará una salida vacía.")

    return {
        "schema_version": SCHEMA_VERSION,
        "dataset": "VehiclesDB",
        "dataset_version": str(payload.get("version") or payload.get("dataset_version") or "unknown"),
        "source_url": SOURCE_URL,
        "source_home": SOURCE_HOME,
        "license": "CC BY 4.0",
        "attribution": ATTRIBUTION,
        "retrieved_at": retrieved_at or datetime.now(timezone.utc).isoformat(),
        "record_count": len(result_vehicles),
        "vehicles": result_vehicles,
        "notice": (
            "Este catálogo identifica marcas y modelos; no es una ficha técnica por versión. "
            "No inferir potencia, cilindrada, emisiones, neumáticos ni homologación a partir del nombre."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="JSON de VehiclesDB descargado previamente (útil para CI/offline).")
    parser.add_argument("--url", default=SOURCE_URL, help="URL de origen versionada.")
    parser.add_argument("--output", type=Path, default=Path("public/data/catalogo-vehiculos.json"))
    args = parser.parse_args()

    try:
        payload = load_payload(args.input, args.url)
        # If a caller deliberately pins another release, preserve that source URL in metadata.
        result = normalize(payload)
        result["source_url"] = args.url
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        print(f"Catálogo generado: {result['record_count']} modelos; versión {result['dataset_version']}; {args.output}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error al importar catálogo de vehículos: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
