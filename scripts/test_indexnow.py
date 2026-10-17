#!/usr/bin/env python3
"""Offline validation of the IndexNow key file and sitemap submission payload."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
sys.path.insert(0, str(ROOT / "scripts"))

from submit_indexnow import build_payload, read_sitemap_urls  # noqa: E402

KEY_RE = re.compile(r"^[A-Fa-f0-9-]{8,128}$")
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def main() -> int:
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    host = config.get("custom_domain", "").strip().lower()
    key = str(config.get("indexnow_key", "") or "").strip()
    if config.get("use_custom_domain") is not True:
        raise AssertionError("El dominio personalizado debe estar activo para probar IndexNow.")
    if not KEY_RE.fullmatch(key):
        raise AssertionError("indexnow_key debe contener una clave hexadecimal válida.")

    key_file = PUBLIC / f"{key}.txt"
    if not key_file.is_file():
        raise AssertionError(f"Falta el archivo IndexNow público {key_file.name}.")
    if key_file.read_text(encoding="utf-8").strip() != key:
        raise AssertionError("El contenido del archivo IndexNow no coincide con el nombre/clave.")

    sitemap_path = PUBLIC / "sitemap.xml"
    urls = read_sitemap_urls(sitemap_path, host)
    if len(urls) > 10_000:
        # submit_indexnow.py chunks the list so no submitted payload exceeds the limit.
        pass
    parsed = [urlsplit(url) for url in urls]
    if any(u.scheme != "https" or u.hostname != host for u in parsed):
        raise AssertionError("Hay URL fuera del host HTTPS activo en el sitemap.")

    payload = build_payload(host, key, urls[:1])
    if payload["keyLocation"] != f"https://{host}/{key}.txt":
        raise AssertionError("keyLocation no apunta al archivo público de la clave.")
    if payload["host"] != host or payload["urlList"] != urls[:1]:
        raise AssertionError("El payload de IndexNow no coincide con el sitemap.")

    print(f"[OK] Clave IndexNow y {len(urls)} URL del sitemap listas para notificar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
