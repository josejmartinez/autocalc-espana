#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera un catálogo compacto de variantes EEA a partir de un CSV grande.

Lee el CSV fila a fila y agrega registros de matriculación por configuración
técnica. No publica el resultado en la web: genera artefactos para revisión.
"""
from __future__ import annotations
import argparse, csv, json, re, sys, unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SOURCE_URL = "https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b"
ALIASES = {
    "id": ["ID"], "country": ["Country"], "manufacturer": ["Mk"],
    "commercial_name": ["Cn"], "manufacturer_name": ["Man"],
    "manufacturer_parent": ["Mp"], "type_approval": ["Tan"], "type": ["T"],
    "variant": ["Va"], "version": ["Ve"], "vehicle_category": ["Ct"],
    "vehicle_class": ["Cr"], "mass_kg": ["m (kg)"], "wltp_test_mass_kg": ["Mt"],
    "co2_wltp_g_km": ["Ewltp (g/km)"], "co2_nedc_g_km": ["Enedc (g/km)"],
    "fuel": ["Ft"], "fuel_mode": ["Fm"], "engine_cc": ["ec (cm3)"],
    "power_kw": ["ep (KW)"], "electricity_wh_km": ["z (Wh/km)"],
    "status": ["Status"], "year": ["year"], "registration_date": ["Date of registration"],
    "fuel_consumption": ["Fuel consumption"], "electric_range_km": ["Electric range (km)"],
    "emissions_reduction_wltp_g_km": ["Erwltp (g/km)"], "emissions_reduction_nedc_g_km": ["Ernedc (g/km)"],
}
CONFIG_FIELDS = (
    "manufacturer", "commercial_name", "type_approval", "type", "variant", "version",
    "vehicle_category", "vehicle_class", "mass_kg", "wltp_test_mass_kg", "co2_wltp_g_km",
    "co2_nedc_g_km", "fuel", "fuel_mode", "engine_cc", "power_kw", "electricity_wh_km",
    "fuel_consumption", "electric_range_km", "emissions_reduction_wltp_g_km", "emissions_reduction_nedc_g_km",
)
NUMERIC_FIELDS = {
    "mass_kg", "wltp_test_mass_kg", "co2_wltp_g_km", "co2_nedc_g_km", "engine_cc",
    "power_kw", "electricity_wh_km", "fuel_consumption", "electric_range_km",
    "emissions_reduction_wltp_g_km", "emissions_reduction_nedc_g_km",
}
COUNTRY_ALIASES = {"ES": {"ES", "ESP", "SPAIN", "ESPAÑA", "ESPANA", "724"}}

def norm_key(value):
    value = unicodedata.normalize("NFKD", value.strip().lower())
    value = "".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")

def detect_delimiter(header):
    candidates = (",", ";", "\t", "|")
    delimiter = max(candidates, key=header.count)
    if header.count(delimiter) == 0:
        raise ValueError("No se reconoce el separador del CSV.")
    return delimiter

def parse_number(value):
    raw = (value or "").strip()
    if not raw or raw.lower() in {"na", "n/a", "null", "none", "-", ".."}:
        return None
    try:
        number = float(raw)
    except ValueError:
        return None
    if not (number == number and abs(number) != float("inf")):
        return None
    return int(number) if number.is_integer() else number

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--country", default="ES")
    parser.add_argument("--status", default="P", choices=("P", "F", "ALL"))
    parser.add_argument("--output", type=Path, default=Path("build/eea-variants.json"))
    parser.add_argument("--report", type=Path, default=Path("build/eea-variants-report.json"))
    args = parser.parse_args()
    variants, counters, missing, country_values = {}, Counter(), Counter(), Counter()
    columns = {}
    try:
        with args.input.open("r", encoding="utf-8-sig", newline="") as stream:
            first_line = stream.readline()
            if not first_line:
                raise ValueError("El CSV está vacío.")
            delimiter = detect_delimiter(first_line)
            stream.seek(0)
            reader = csv.DictReader(stream, delimiter=delimiter)
            headers = reader.fieldnames or []
            by_norm = {norm_key(h): h for h in headers}
            for field, names in ALIASES.items():
                for name in names:
                    if norm_key(name) in by_norm:
                        columns[field] = by_norm[norm_key(name)]
                        break
            absent = {"country", "manufacturer", "commercial_name", "year", "status"} - set(columns)
            if absent:
                raise ValueError("Faltan columnas obligatorias del esquema EEA: " + ", ".join(sorted(absent)))
            allowed_country = COUNTRY_ALIASES.get(args.country.upper(), {args.country.upper()})
            for row in reader:
                counters["rows_read"] += 1
                def get(field):
                    header = columns.get(field)
                    return (row.get(header) or "").strip() if header else ""
                country = get("country")
                if country:
                    country_values[country] += 1
                if country.upper() not in allowed_country or get("year") != str(args.year):
                    continue
                status = get("status").upper()
                if args.status != "ALL" and status != args.status:
                    continue
                counters["rows_selected"] += 1
                values = {}
                for field in CONFIG_FIELDS:
                    raw = get(field)
                    if field in NUMERIC_FIELDS:
                        value = parse_number(raw)
                        if raw and value is None:
                            missing["invalid:" + field] += 1
                        values[field] = value
                    else:
                        values[field] = raw or None
                    if values[field] is None:
                        missing[field] += 1
                if not values["manufacturer"] or not values["commercial_name"]:
                    counters["rows_without_identity"] += 1
                    continue
                fingerprint = tuple(values[field] for field in CONFIG_FIELDS)
                item = variants.get(fingerprint)
                if item is None:
                    item = {
                        "id": "eea-" + str(len(variants) + 1).zfill(7),
                        **values, "country": country, "registration_year": args.year,
                        "status": status, "source": "European Environment Agency",
                        "source_url": SOURCE_URL, "source_dataset_year": args.year,
                        "source_status": status, "registration_count": 0,
                        "first_registration_date": None, "last_registration_date": None,
                    }
                    variants[fingerprint] = item
                item["registration_count"] += 1
                date = get("registration_date") or None
                if date:
                    if item["first_registration_date"] is None or date < item["first_registration_date"]:
                        item["first_registration_date"] = date
                    if item["last_registration_date"] is None or date > item["last_registration_date"]:
                        item["last_registration_date"] = date
                counters["rows_aggregated"] += 1
                if counters["rows_read"] % 500000 == 0:
                    print(f"Leídas {counters['rows_read']:,}; seleccionadas {counters['rows_selected']:,}; variantes {len(variants):,}")
        if not variants:
            raise ValueError("No se generaron variantes; revisa país, año, estado y esquema.")
        generated_at = datetime.now(timezone.utc).isoformat()
        notice = ("Fuente de vehículos nuevos registrados; no representa todo el parque circulante. "
                  "No certifica medidas de neumáticos, compatibilidad de llantas ni legalidad ITV. "
                  "Los campos Mt, Erwltp y Ernedc se identifican como masa de ensayo WLTP y reducciones de emisiones por tecnologías innovadoras, respectivamente; no deben confundirse con masa en orden de marcha ni con emisiones directas de un vehículo eléctrico. Las unidades y definiciones de otros campos deben contrastarse con la tabla EEA de esta edición.")
        output = {
            "schema_version": 1, "dataset": "EEA monitoring of CO2 emissions from passenger cars",
            "source_url": SOURCE_URL, "generated_at": generated_at, "country": args.country.upper(),
            "registration_year": args.year, "source_status": args.status,
            "variant_count": len(variants), "registration_rows_selected": counters["rows_selected"],
            "notice": notice, "records": list(variants.values()),
        }
        report = {
            "generated_at": generated_at, "input_file": args.input.name, "source_url": SOURCE_URL,
            "filters": {"country": args.country.upper(), "year": args.year, "status": args.status},
            "counters": dict(counters), "unique_variants": len(variants),
            "recognized_columns": columns, "available_columns": headers,
            "country_values_top": country_values.most_common(25),
            "missing_or_invalid_counts": dict(missing), "limitations": notice,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Filas leídas: {counters['rows_read']:,}")
        print(f"Filas seleccionadas: {counters['rows_selected']:,}")
        print(f"Variantes agregadas: {len(variants):,}")
        print(f"Catálogo: {args.output}")
        print(f"Informe: {args.report}")
        return 0
    except (OSError, csv.Error, ValueError) as exc:
        print(f"Error generando catálogo EEA: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
