#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exporta un índice EEA compacto y apto para un buscador estático."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PUBLIC_FIELDS = (
    "id", "manufacturer", "commercial_name", "type_approval", "type",
    "variant", "version", "vehicle_category", "fuel", "fuel_mode",
    "engine_cc", "power_kw", "mass_kg", "wltp_test_mass_kg",
    "co2_wltp_g_km", "electricity_wh_km", "electric_range_km",
    "registration_count",
)

def export_index(source: dict) -> dict:
    records = source.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("El catálogo de entrada no contiene records válidos.")
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Cada elemento de records debe ser un objeto.")
        if not record.get("manufacturer") or not record.get("commercial_name"):
            raise ValueError("Hay una variante sin marca o nombre comercial.")
    reduced = [
        {key: record.get(key) for key in PUBLIC_FIELDS}
        for record in sorted(records, key=lambda item: (
            str(item.get("manufacturer") or "").casefold(),
            str(item.get("commercial_name") or "").casefold(),
            str(item.get("type") or ""),
            str(item.get("variant") or ""),
            str(item.get("version") or ""),
        ))
    ]
    return {
        "schema_version": 1,
        "dataset": source.get("dataset", "EEA passenger cars"),
        "source_url": source.get("source_url"),
        "generated_at": source.get("generated_at"),
        "country": source.get("country"),
        "registration_year": source.get("registration_year"),
        "source_status": source.get("source_status"),
        "variant_count": len(reduced),
        "notice": source.get("notice", ""),
        "records": reduced,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="JSON completo generado por importar_catalogo_eea.py")
    parser.add_argument("--output", type=Path, default=Path("build/eea-search-index.json"))
    args = parser.parse_args()
    try:
        source = json.loads(args.input.read_text(encoding="utf-8"))
        result = export_index(source)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\\n", encoding="utf-8")
        print(f"Índice de búsqueda: {args.output} ({result['variant_count']:,} variantes)")
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Error exportando índice EEA: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
