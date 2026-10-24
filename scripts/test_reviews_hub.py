#!/usr/bin/env python3
"""Pruebas de contrato y SEO del hub de reseñas."""
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / "scripts" / "build_reviews.py")], cwd=ROOT, check=True)
page = (ROOT / "public/resenas/index.html").read_text(encoding="utf-8")
data = json.loads((ROOT / "public/resenas/reviews.json").read_text(encoding="utf-8"))
assert '<html lang="es">' in page
assert '<title>' in page and '<meta name="description"' in page
assert '<link rel="canonical" href="https://autocalc.es/resenas/">' in page
assert "No mostramos puntuaciones ficticias" in page
assert data["schema_version"] == 1 and data["reviews"] == []
assert data["rules"]["only_approved_reviews_public"] is True
assert data["rules"]["disclose_free_samples_and_affiliate_links"] is True
root = ET.parse(ROOT / "public/sitemap.xml").getroot()
locs = [node.text for node in root.iter() if node.tag.endswith("loc")]
assert "https://autocalc.es/resenas/" in locs
print("Reseñas: contrato, transparencia, canonical y sitemap correctos.")
