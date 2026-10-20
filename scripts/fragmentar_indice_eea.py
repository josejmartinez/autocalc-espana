#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Divide el índice EEA en fragmentos por fabricante para carga bajo demanda."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path


def safe_slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    prefix = normalized[:48] or "fabricante"
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{digest}"


def fragmentar(source: dict, output_dir: Path) -> dict:
    records = source.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("El índice de entrada no contiene records válidos.")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Cada registro debe ser un objeto.")
        manufacturer = str(record.get("manufacturer") or "").strip()
        commercial_name = str(record.get("commercial_name") or "").strip()
        if not manufacturer or not commercial_name:
            raise ValueError("Hay una variante sin fabricante o nombre comercial.")
        grouped[manufacturer].append(record)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manufacturers = []
    for manufacturer in sorted(grouped, key=str.casefold):
        shard_name = safe_slug(manufacturer) + ".json"
        variants = sorted(
            grouped[manufacturer],
            key=lambda row: (
                str(row.get("commercial_name") or "").casefold(),
                str(row.get("type") or ""),
                str(row.get("variant") or ""),
                str(row.get("version") or ""),
            ),
        )
        payload = {
            "schema_version": 1,
            "manufacturer": manufacturer,
            "variant_count": len(variants),
            "records": variants,
        }
        (output_dir / shard_name).write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        manufacturers.append({
            "name": manufacturer,
            "variant_count": len(variants),
            "file": shard_name,
        })

    manifest = {
        "schema_version": 1,
        "dataset": source.get("dataset", "EEA passenger cars"),
        "source_url": source.get("source_url"),
        "generated_at": source.get("generated_at"),
        "country": source.get("country"),
        "registration_year": source.get("registration_year"),
        "source_status": source.get("source_status"),
        "variant_count": len(records),
        "manufacturer_count": len(manufacturers),
        "manufacturers": manufacturers,
        "notice": source.get("notice", ""),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Índice compacto generado por exportar_indice_eea.py")
    parser.add_argument("--output-dir", type=Path, default=Path("build/eea-shards"))
    args = parser.parse_args()
    try:
        source = json.loads(args.input.read_text(encoding="utf-8"))
        manifest = fragmentar(source, args.output_dir)
        print(
            f"Fragmentos EEA: {manifest['manufacturer_count']} fabricantes, "
            f"{manifest['variant_count']:,} variantes -> {args.output_dir}"
        )
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Error fragmentando índice EEA: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
