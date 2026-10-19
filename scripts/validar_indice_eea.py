#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida el índice compacto EEA antes de usarlo en el buscador estático."""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

REQUIRED_FIELDS = ("id", "manufacturer", "commercial_name")
NUMERIC_RANGES = {
    "power_kw": (0, 2000),
    "mass_kg": (300, 10000),
    "wltp_test_mass_kg": (300, 10000),
    "co2_wltp_g_km": (0, 2000),
    "electricity_wh_km": (1, 1000),
    "electric_range_km": (1, 2000),
    "engine_cc": (50, 20000),
    "registration_count": (1, 100000000),
}


def validate_index(data: object) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        raise ValueError("La raíz del índice debe ser un objeto JSON.")
    records = data.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("El índice no contiene una lista records válida y no vacía.")
    if data.get("schema_version") != 1:
        errors.append("schema_version debe ser 1.")
    if data.get("variant_count") != len(records):
        errors.append(
            f"variant_count ({data.get('variant_count')!r}) no coincide con records ({len(records)})."
        )

    seen_ids: set[str] = set()
    missing: Counter[str] = Counter()
    suspicious: Counter[str] = Counter()
    for pos, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"El registro {pos} no es un objeto.")
            continue
        for field in REQUIRED_FIELDS:
            value = record.get(field)
            if value is None or not str(value).strip():
                errors.append(f"El registro {pos} carece de {field}.")
        record_id = str(record.get("id") or "").strip()
        if record_id:
            if record_id in seen_ids:
                errors.append(f"ID duplicado: {record_id}.")
            seen_ids.add(record_id)
        for field, (minimum, maximum) in NUMERIC_RANGES.items():
            value = record.get(field)
            if value is None:
                missing[field] += 1
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                suspicious[field] += 1
            elif value < minimum or value > maximum:
                suspicious[field] += 1

    if missing:
        warnings.append("Hay campos técnicos opcionales ausentes; no se han rechazado por sí solos.")
    if suspicious:
        errors.append("Se han encontrado valores numéricos no válidos o fuera de rango.")
    return {
        "file": "eea-search-index.json",
        "schema_version": data.get("schema_version"),
        "declared_count": data.get("variant_count"),
        "actual_count": len(records),
        "count_matches": data.get("variant_count") == len(records),
        "missing_ids": sum(not str(r.get("id") or "").strip() for r in records if isinstance(r, dict)),
        "duplicate_ids": len(records) - len(seen_ids) - sum(not str(r.get("id") or "").strip() for r in records if isinstance(r, dict)),
        "missing_required_fields_or_identity": len([e for e in errors if "carece de" in e]),
        "missing_optional_numeric_fields": dict(missing),
        "suspicious_numeric_values": dict(suspicious),
        "record_count": len(records),
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=Path("build/eea-index-validation.json"))
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        report = validate_index(data)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["valid"] else 1
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Error validando índice EEA: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
