#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas unitarias sin red para el importador de VehiclesDB."""
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("importar_catalogo_vehiculos.py")
SPEC = importlib.util.spec_from_file_location("importar_catalogo_vehiculos", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class VehicleCatalogImportTests(unittest.TestCase):
    def test_keeps_cars_and_source_provenance_without_inventing_specs(self):
        payload = {
            "version": "test-1",
            "makes": [
                {
                    "name": "SEAT",
                    "slug": "seat",
                    "models": [
                        {"id": "car/seat/leon", "name": "León", "slug": "leon", "kind": "car",
                         "availability": {"countries": ["es"]}, "sources": ["registry"]},
                        {"id": "motorcycle/seat/example", "name": "Example", "slug": "example", "kind": "motorcycle"},
                        {"name": " ", "slug": "invalid", "kind": "car"},
                    ],
                },
                {"name": "Missing models", "slug": "missing", "models": []},
            ],
        }
        result = MODULE.normalize(payload, "2026-10-18T00:00:00+00:00")
        self.assertEqual(result["record_count"], 1)
        self.assertEqual(result["vehicles"][0]["id"], "car/seat/leon")
        self.assertEqual(result["vehicles"][0]["make"], "SEAT")
        self.assertEqual(result["vehicles"][0]["model"], "León")
        self.assertEqual(result["vehicles"][0]["sources"], ["registry"])
        self.assertNotIn("power_kw", result["vehicles"][0])
        self.assertEqual(result["license"], "CC BY 4.0")
        self.assertIn("VehiclesDB", result["attribution"])

    def test_rejects_unrecognized_schema(self):
        with self.assertRaisesRegex(ValueError, "makes"):
            MODULE.normalize({"models": []})

    def test_rejects_empty_result(self):
        with self.assertRaisesRegex(ValueError, "salida vacía"):
            MODULE.normalize({"makes": [{"name": "SEAT", "slug": "seat", "models": []}]})


if __name__ == "__main__":
    unittest.main()
