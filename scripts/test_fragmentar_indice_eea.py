#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas del fragmentador EEA por fabricante."""
import json
import tempfile
import unittest
from pathlib import Path

from fragmentar_indice_eea import fragmentar, safe_slug


class ShardingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_manifest_and_shards(self):
        source = {
            "dataset": "EEA test",
            "variant_count": 3,
            "records": [
                {"id": "1", "manufacturer": "A B", "commercial_name": "Model 2"},
                {"id": "2", "manufacturer": "A B", "commercial_name": "Model 1"},
                {"id": "3", "manufacturer": "A/B", "commercial_name": "Roadster"},
            ],
        }
        manifest = fragmentar(source, self.root / "shards")
        self.assertEqual(manifest["variant_count"], 3)
        self.assertEqual(manifest["manufacturer_count"], 2)
        self.assertEqual([m["name"] for m in manifest["manufacturers"]], ["A B", "A/B"])
        for manufacturer in manifest["manufacturers"]:
            payload = json.loads((self.root / "shards" / manufacturer["file"]).read_text(encoding="utf-8"))
            self.assertEqual(payload["manufacturer"], manufacturer["name"])
            self.assertEqual(payload["variant_count"], len(payload["records"]))
        ab = next(m for m in manifest["manufacturers"] if m["name"] == "A B")
        records = json.loads((self.root / "shards" / ab["file"]).read_text(encoding="utf-8"))["records"]
        self.assertEqual([r["commercial_name"] for r in records], ["Model 1", "Model 2"])

    def test_same_normalized_name_does_not_collide(self):
        self.assertNotEqual(safe_slug("A/B"), safe_slug("A B"))

    def test_rejects_empty_or_invalid_records(self):
        with self.assertRaises(ValueError):
            fragmentar({"records": []}, self.root / "empty")
        with self.assertRaises(ValueError):
            fragmentar({"records": [{"manufacturer": "A"}]}, self.root / "invalid")


if __name__ == "__main__":
    unittest.main()
