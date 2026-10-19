#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas del validador del índice compacto EEA."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("validar_indice_eea.py")
SPEC = importlib.util.spec_from_file_location("validar_indice_eea", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def sample():
    return {
        "schema_version": 1,
        "variant_count": 2,
        "records": [
            {"id": "eea-1", "manufacturer": "SEAT", "commercial_name": "LEON",
             "power_kw": 110, "mass_kg": 1400, "registration_count": 4},
            {"id": "eea-2", "manufacturer": "AUDI", "commercial_name": "A3",
             "co2_wltp_g_km": 0, "registration_count": 1},
        ],
    }


class ValidateIndexTests(unittest.TestCase):
    def test_accepts_valid_index_and_optional_missing_values(self):
        report = MODULE.validate_index(sample())
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["record_count"], 2)
        self.assertTrue(report["warnings"])

    def test_rejects_duplicate_ids(self):
        data = sample()
        data["records"][1]["id"] = "eea-1"
        report = MODULE.validate_index(data)
        self.assertFalse(report["valid"])
        self.assertTrue(any("ID duplicado" in error for error in report["errors"]))

    def test_rejects_count_mismatch(self):
        data = sample()
        data["variant_count"] = 3
        report = MODULE.validate_index(data)
        self.assertFalse(report["valid"])
        self.assertFalse(report["count_matches"])

    def test_rejects_suspicious_numeric_values(self):
        data = sample()
        data["records"][0]["power_kw"] = -12
        report = MODULE.validate_index(data)
        self.assertFalse(report["valid"])
        self.assertIn("power_kw", report["suspicious_numeric_values"])

    def test_rejects_missing_identity(self):
        data = sample()
        data["records"][0]["manufacturer"] = ""
        report = MODULE.validate_index(data)
        self.assertFalse(report["valid"])


if __name__ == "__main__":
    unittest.main()
