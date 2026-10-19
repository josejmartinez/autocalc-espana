#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas del exportador de índice compacto EEA."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("exportar_indice_eea.py")

class SearchIndexTests(unittest.TestCase):
    def test_exports_sorted_compact_records_and_omits_unverified_fuel_consumption(self):
        source = {
            "dataset": "EEA passenger cars",
            "source_url": "https://example.invalid/eea",
            "country": "ES",
            "registration_year": 2025,
            "source_status": "P",
            "notice": "Datos de matriculaciones nuevas.",
            "records": [
                {"id": "2", "manufacturer": "SEAT", "commercial_name": "LEON", "fuel": "petrol",
                 "power_kw": 110, "fuel_consumption": 5.4, "registration_count": 3},
                {"id": "1", "manufacturer": "AUDI", "commercial_name": "A3", "fuel": "electric",
                 "electricity_wh_km": 160, "fuel_consumption": None, "registration_count": 2},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp, out = root / "input.json", root / "index.json"
            inp.write_text(json.dumps(source), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(inp), "--output", str(out)],
                                    text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["variant_count"], 2)
            self.assertEqual([r["manufacturer"] for r in data["records"]], ["AUDI", "SEAT"])
            self.assertNotIn("fuel_consumption", data["records"][0])
            self.assertEqual(data["records"][1]["power_kw"], 110)

    def test_rejects_missing_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp, out = root / "input.json", root / "index.json"
            inp.write_text('{"records":[]}', encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(inp), "--output", str(out)],
                                    text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no contiene records", result.stderr)

if __name__ == "__main__":
    unittest.main()
