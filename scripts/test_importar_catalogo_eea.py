#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas del agregador EEA con el esquema real de turismos."""
import csv, json, subprocess, sys, tempfile, unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("importar_catalogo_eea.py")

class EEACatalogueTests(unittest.TestCase):
    def test_aggregates_configurations_and_keeps_variants_separate(self):
        header = ["ID","Country","Mp","Man","Tan","T","Va","Ve","Mk","Cn","Ct","Cr","m (kg)","Mt","Enedc (g/km)","Ewltp (g/km)","Ft","Fm","ec (cm3)","ep (KW)","z (Wh/km)","Ernedc (g/km)","Erwltp (g/km)","Status","year","Date of registration","Fuel consumption","Electric range (km)"]
        rows = [
            ["1","ES","parent","maker","approval","T1","A","V1","SEAT","LEON","M1","M1","1400","1500","120","125","petrol","M","1498","110","","","","P","2025","2025-01-01","5.4",""],
            ["2","ES","parent","maker","approval","T1","A","V1","SEAT","LEON","M1","M1","1400","1500","120","125","petrol","M","1498","110","","","","P","2025","2025-01-03","5.4",""],
            ["3","ES","parent","maker","approval","T1","B","V2","SEAT","LEON","M1","M1","1500","1600","120","125","petrol","M","1498","110","","","","P","2025","2025-02-01","5.4",""],
            ["4","DE","parent","maker","approval","T1","A","V1","SEAT","LEON","M1","M1","1400","1500","120","125","petrol","M","1498","110","","","","P","2025","2025-01-01","5.4",""],
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "source.csv"; output = root / "catalogue.json"; report = root / "report.json"
            with source.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f); writer.writerow(header); writer.writerows(rows)
            result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), "--year", "2025", "--country", "ES", "--status", "P", "--output", str(output), "--report", str(report)], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(output.read_text(encoding="utf-8")); audit = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(data["registration_rows_selected"], 3)
            self.assertEqual(data["variant_count"], 2)
            self.assertEqual(sorted(r["registration_count"] for r in data["records"]), [1, 2])
            self.assertEqual(audit["counters"]["rows_read"], 4)
            self.assertEqual(audit["counters"]["rows_selected"], 3)
            self.assertEqual(audit["recognized_columns"]["power_kw"], "ep (KW)")
            self.assertEqual(data["records"][0]["source_status"], "P")

    def test_rejects_unrecognized_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "bad.csv"
            source.write_text("foo,bar\nx,y\n", encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), "--output", str(root/"out.json"), "--report", str(root/"report.json")], text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Faltan columnas obligatorias", result.stderr)

if __name__ == "__main__":
    unittest.main()
