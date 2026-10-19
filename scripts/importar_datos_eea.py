#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Importa un CSV oficial EEA de turismos/furgonetas y genera datos normalizados + informe.

Uso:
  python scripts/importar_datos_eea.py --input data/eea_cars.csv --kind cars --year 2025
  python scripts/importar_datos_eea.py --input data/eea_cars.csv --kind cars --year 2025 --country ES

El CSV se descarga manualmente desde la página oficial EEA. No se inventa una URL
de descarga ni se depende de endpoints internos que puedan cambiar.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

EEA_CARS = "https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b"
EEA_VANS = "https://www.eea.europa.eu/en/datahub/datahubitem-view/9636827c-bd0c-40f5-814e-c4065c11c9a0"
SCHEMA_VERSION = 1

ALIASES = {
    "country": ["country", "country_code", "countrycode", "reporting_country", "member_state", "ms"],
    "manufacturer": ["manufacturer", "manufacturer_name", "manufacturername", "make", "brand", "brand_name", "mk"],
    "commercial_name": ["commercial_name", "commercialname", "vehicle_model", "model", "name", "commercial_vehicle_type", "cn"],
    "type_approval": ["type_approval", "type_approval_number", "typeapprovalnumber", "approval_number", "wvta", "tan"],
    "type": ["type", "vehicle_type", "vehicletype", "t"],
    "variant": ["variant", "vehicle_variant", "va"],
    "version": ["version", "vehicle_version", "ve"],
    "year": ["year", "registration_year", "reporting_year", "year_of_registration"],
    "fuel": ["fuel", "fuel_type", "fueltype", "fuel_type_name", "energy_source", "ft"],
    "co2_g_km": ["co2", "co2_g_km", "co2_emissions", "co2_emission", "specific_co2_emissions", "co2_emissions_g_km", "ewltp_g_km"],
    "power_kw": ["power_kw", "engine_power_kw", "maximum_net_power", "max_net_power", "rated_power_kw", "ep_kw"],
    "engine_cc": ["engine_cc", "engine_capacity", "cylinder_capacity", "engine_displacement", "displacement_cc", "ec_cm3"],
    "mass_kg": ["mass_kg", "mass", "mass_in_running_order", "mass_in_service", "vehicle_mass", "m_kg"],
    "wheelbase_mm": ["wheelbase_mm", "wheelbase", "wheel_base"],
    "width_mm": ["width_mm", "width"],
    "height_mm": ["height_mm", "height"],
    "length_mm": ["length_mm", "length"],
    "approval_country": ["approval_country", "type_approval_country"],
}

NUMERIC_FIELDS = ("co2_g_km", "power_kw", "engine_cc", "mass_kg", "wheelbase_mm", "width_mm", "height_mm", "length_mm")
COUNTRY_ALIASES = {"ES": {"ES", "ESP", "SPAIN", "ESPAÑA", "ESPANA", "724"}}


def norm_key(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.strip().lower())
    value = "".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")


def parse_number(value):
    if value is None:
        return None
    value = str(value).strip()
    if not value or value.lower() in {"na", "n/a", "null", "none", "-", ".."}:
        return None
    # EEA CSVs can use decimal comma; only accept simple numeric cells.
    value = value.replace(" ", "")
    if "," in value and "." not in value:
        value = value.replace(",", ".")
    try:
        number = float(value)
    except ValueError:
        return None
    if number != number or abs(number) == float("inf"):
        return None
    return int(number) if number.is_integer() else number


def choose_columns(headers):
    by_norm = {norm_key(h): h for h in headers}
    selected = {}
    for field, aliases in ALIASES.items():
        for alias in aliases:
            if norm_key(alias) in by_norm:
                selected[field] = by_norm[norm_key(alias)]
                break
    return selected


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        first_line = stream.readline()
        if not first_line:
            raise ValueError("El archivo está vacío.")
        candidates = (",", ";", "\\t", "|")
        delimiter = max(candidates, key=first_line.count)
        if first_line.count(delimiter) == 0:
            raise ValueError("No se reconoce el separador del CSV.")
        stream.seek(0)
        reader = csv.DictReader(stream, delimiter=delimiter)
        if not reader.fieldnames:
            raise ValueError("El archivo no tiene cabecera CSV.")
        return reader.fieldnames, list(reader)


def import_dataset(input_path: Path, kind: str, year: int | None = None, country: str | None = None):
    headers, rows = read_rows(input_path)
    columns = choose_columns(headers)
    if not any(field in columns for field in ("manufacturer", "commercial_name", "type_approval")):
        raise ValueError("No se reconocen columnas de fabricante/modelo/homologación. Revisa la cabecera del CSV EEA.")
    if country and "country" not in columns:
        raise ValueError("Se ha solicitado filtrar por país, pero el CSV no tiene una columna de país reconocible.")
    if year is not None and "year" not in columns:
        raise ValueError("Se ha solicitado filtrar por año, pero el CSV no tiene una columna de año reconocible.")

    source_url = EEA_CARS if kind == "cars" else EEA_VANS
    kept = []
    country_values = Counter()
    missing = Counter()
    for row in rows:
        def get(field):
            original = columns.get(field)
            return str(row.get(original) or "").strip() if original else ""

        raw_country = get("country")
        if raw_country:
            country_values[raw_country] += 1
        if country:
            allowed = COUNTRY_ALIASES.get(country.upper(), {country.upper()})
            if raw_country.upper() not in allowed:
                continue
        row_year = parse_number(get("year"))
        if year is not None and (row_year is None or int(row_year) != year):
            continue

        record = {
            "id": "|".join([get("country"), get("type_approval"), get("type"), get("variant"), get("version"), get("commercial_name")]).strip("|"),
            "vehicle_kind": "passenger_car" if kind == "cars" else "light_commercial_vehicle",
            "country": raw_country or None,
            "manufacturer": get("manufacturer") or None,
            "commercial_name": get("commercial_name") or None,
            "type_approval": get("type_approval") or None,
            "type": get("type") or None,
            "variant": get("variant") or None,
            "version": get("version") or None,
            "registration_year": int(row_year) if row_year is not None else year,
            "fuel": get("fuel") or None,
            "source": "European Environment Agency",
            "source_url": source_url,
            "source_file": input_path.name,
        }
        for field in NUMERIC_FIELDS:
            value = parse_number(get(field))
            if value is not None:
                record[field] = value
        if not record["id"]:
            record["id"] = "|".join(str(record.get(k) or "") for k in ("country", "manufacturer", "commercial_name", "registration_year"))
        for field in ("manufacturer", "commercial_name", "type_approval", "fuel", "co2_g_km", "power_kw", "engine_cc", "mass_kg"):
            if record.get(field) in (None, ""):
                missing[field] += 1
        kept.append(record)

    # Keep duplicates: the type/variant/version can represent genuinely distinct homologations.
    if not kept:
        raise ValueError("No hay registros después de aplicar los filtros. Comprueba país/año y el CSV.")

    def coverage(field):
        present = sum(r.get(field) not in (None, "") for r in kept)
        return {"present": present, "total": len(kept), "percent": round(100 * present / len(kept), 2)}

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_file": input_path.name,
        "dataset": "European Environment Agency CO2 monitoring",
        "kind": kind,
        "year_filter": year,
        "country_filter": country,
        "source_url": source_url,
        "source_rows": len(rows),
        "output_rows": len(kept),
        "recognized_columns": columns,
        "available_columns": headers,
        "country_values_top": country_values.most_common(25),
        "coverage": {field: coverage(field) for field in ("manufacturer", "commercial_name", "type_approval", "fuel", *NUMERIC_FIELDS)},
        "missing_counts": dict(missing),
        "limitations": [
            "La fuente cubre vehículos nuevos registrados y notificados, no todos los vehículos en circulación.",
            "La presencia de una columna depende de la edición del dataset. La normalización solo asigna columnas reconocidas por nombre.",
            "Las unidades deben verificarse con la tabla de definición de la edición concreta antes de usar estos valores en cálculos.",
            "No usar estos registros por sí solos para declarar neumáticos homologados, compatibilidad de llantas o legalidad ITV.",
            "Los datos provisionales y los valores atípicos deben revisarse según la documentación EEA.",
        ],
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "dataset": report["dataset"],
        "kind": kind,
        "source_url": source_url,
        "source_file": input_path.name,
        "generated_at": report["generated_at"],
        "record_count": len(kept),
        "records": kept,
        "notice": "Datos de vehículos nuevos registrados; no todos los vehículos en circulación están incluidos y no constituye una certificación de homologación.",
    }, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="CSV descargado desde el portal oficial EEA.")
    parser.add_argument("--kind", choices=("cars", "vans"), required=True)
    parser.add_argument("--year", type=int, help="Filtrar por año si el CSV incluye una columna reconocible.")
    parser.add_argument("--country", help="Filtrar país (por ejemplo ES); requiere una columna de país.")
    parser.add_argument("--output", type=Path, default=Path("public/data/eea-vehicles.json"))
    parser.add_argument("--report", type=Path, default=Path("reports/eea-coverage.json"))
    args = parser.parse_args()
    try:
        dataset, report = import_dataset(args.input, args.kind, args.year, args.country)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(dataset, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"EEA importado: {dataset['record_count']} registros; salida={args.output}; cobertura={args.report}")
        return 0
    except (OSError, ValueError, csv.Error) as exc:
        print(f"Error importando datos EEA: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
