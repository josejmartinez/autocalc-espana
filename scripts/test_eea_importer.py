#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas offline del importador EEA y su informe de cobertura."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("importar_datos_eea.py")
SPEC = importlib.util.spec_from_file_location("importar_datos_eea", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class EEAImporterTests(unittest.TestCase):
    def test_normalizes_csv_and_reports_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "sample.csv"
            source.write_text(
                "Country,Manufacturer,Commercial name,Type approval number,Variant,Version,Year,CO2,Power kW,Mass\n"
                "ES,SEAT,Leon,approval-1,AB,01,2024,120,110,1400\n"
                "DE,VW,Golf,approval-2,CD,02,2024,115,96,1350\n"
                "ES,SEAT,Ibiza,approval-3,EF,03,2023,105,,1100\n",
                encoding="utf-8",
            )
            dataset, report = MODULE.import_dataset(source, "cars", 2024, "ES")
            self.assertEqual(dataset["record_count"], 1)
            self.assertEqual(dataset["records"][0]["manufacturer"], "SEAT")
            self.assertEqual(dataset["records"][0]["commercial_name"], "Leon")
            self.assertEqual(dataset["records"][0]["co2_g_km"], 120)
            self.assertEqual(dataset["records"][0]["power_kw"], 110)
            self.assertEqual(report["coverage"]["power_kw"]["percent"], 100)
            self.assertIn("no todos los vehículos", dataset["notice"].lower())

    def test_accepts_semicolon_and_decimal_comma(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "sample.csv"
            source.write_text(
                "Country;Manufacturer;Model;Year;CO2 emissions\nES;Dacia;Sandero;2025;123,5\n",
                encoding="utf-8",
            )
            dataset, _ = MODULE.import_dataset(source, "cars", 2025, "ES")
            self.assertEqual(dataset["records"][0]["co2_g_km"], 123.5)

    def test_rejects_unrecognized_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "sample.csv"
            source.write_text("foo,bar\nx,y\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "No se reconocen"):
                MODULE.import_dataset(source, "cars")

    def test_does_not_claim_homologated_tires(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "sample.csv"
            source.write_text("Manufacturer,Model\nSEAT,Leon\n", encoding="utf-8")
            dataset, report = MODULE.import_dataset(source, "cars")
            self.assertTrue(any("neumáticos homologados" in text for text in report["limitations"]))
            self.assertIsNone(dataset["records"][0]["co2_g_km"] if "co2_g_km" in dataset["records"][0] else None)


if __name__ == "__main__":
    unittest.main()
