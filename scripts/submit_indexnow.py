#!/usr/bin/env python3
"""Submit the current AutoCalc sitemap URLs to IndexNow after deployment."""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.json"
SITEMAP_PATH = ROOT / "public" / "sitemap.xml"
PUBLIC_DIR = ROOT / "public"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
KEY_RE = re.compile(r"^[A-Fa-f0-9-]{8,128}$")
BATCH_SIZE = 10_000


def read_sitemap_urls(sitemap_path: Path, host: str) -> list[str]:
    """Return unique HTTPS URLs belonging to the exact configured host."""
    tree = ET.parse(sitemap_path)
    urls: list[str] = []
    seen: set[str] = set()
    for loc in tree.findall(".//sm:loc", SITEMAP_NS):
        url = (loc.text or "").strip()
        parsed = urlsplit(url)
        if parsed.scheme != "https" or (parsed.hostname or "").lower() != host.lower():
            raise ValueError(f"URL del sitemap fuera del dominio HTTPS activo: {url!r}")
        if url not in seen:
            seen.add(url)
            urls.append(url)
    if not urls:
        raise ValueError("El sitemap no contiene URL para enviar a IndexNow.")
    return urls


def build_payload(host: str, key: str, urls: list[str]) -> dict[str, object]:
    if not KEY_RE.fullmatch(key):
        raise ValueError("La clave IndexNow no tiene el formato hexadecimal permitido.")
    return {
        "host": host,
        "key": key,
        "keyLocation": f"https://{host}/{key}.txt",
        "urlList": urls,
    }


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if config.get("use_custom_domain") is not True:
        print("[INFO] IndexNow omitido: el modo de dominio personalizado está desactivado.")
        return 0

    host = str(config.get("custom_domain", "")).strip().lower().rstrip(".")
    key = str(config.get("indexnow_key", "") or "").strip()
    if not host or not KEY_RE.fullmatch(key):
        raise ValueError("Falta custom_domain o indexnow_key válido en config.json.")

    key_file = PUBLIC_DIR / f"{key}.txt"
    if not key_file.is_file() or key_file.read_text(encoding="utf-8").strip() != key:
        raise FileNotFoundError(
            f"No se ha publicado el archivo de verificación IndexNow esperado: {key_file.name}"
        )

    urls = read_sitemap_urls(SITEMAP_PATH, host)
    total_sent = 0
    for offset in range(0, len(urls), BATCH_SIZE):
        batch = urls[offset:offset + BATCH_SIZE]
        payload = build_payload(host, key, batch)
        request = urllib.request.Request(
            INDEXNOW_ENDPOINT,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = response.status
                detail = response.read(500).decode("utf-8", errors="replace").strip()
        except urllib.error.HTTPError as exc:
            detail = exc.read(500).decode("utf-8", errors="replace").strip()
            raise RuntimeError(
                f"IndexNow rechazó el lote ({exc.code}). Respuesta: {detail or '(vacía)'}"
            ) from exc

        if status not in (200, 202):
            raise RuntimeError(
                f"IndexNow devolvió HTTP {status}. Respuesta: {detail or '(vacía)'}"
            )
        total_sent += len(batch)
        print(f"[OK] IndexNow aceptó {len(batch)} URL (HTTP {status}).")

    print(
        f"[OK] Notificadas {total_sent} URL de {host}. "
        "La aceptación no garantiza que se indexen."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
