#!/usr/bin/env python3
"""Regression test for GitHub Pages <-> custom-domain generation.

The test temporarily changes config.json, generates both modes and restores the
exact original configuration before returning. It leaves ./public generated
for the original (active) configuration.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.json"
BUILD_SCRIPT = ROOT / "src" / "build.py"
PUBLIC = ROOT / "public"


def write_config(data: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_build() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=ROOT, check=True)


def validate_mode(config: dict, custom_enabled: bool) -> None:
    custom_domain = str(config.get("custom_domain", "")).strip().lower().rstrip(".")
    github_url = str(config.get("github_pages_url") or config.get("domain") or "").strip().rstrip("/")
    expected_domain = f"https://{custom_domain}" if custom_enabled else github_url

    if not expected_domain.startswith("https://"):
        raise AssertionError(f"Dominio esperado inválido: {expected_domain!r}")

    index = (PUBLIC / "index.html").read_text(encoding="utf-8")
    sitemap = (PUBLIC / "sitemap.xml").read_text(encoding="utf-8")
    robots = (PUBLIC / "robots.txt").read_text(encoding="utf-8")

    if f'<link rel="canonical" href="{expected_domain}/"' not in index:
        raise AssertionError(f"Canonical de portada incorrecta; esperaba {expected_domain}/")
    if f'<meta property="og:url" content="{expected_domain}/"' not in index:
        raise AssertionError("La URL Open Graph no coincide con el dominio activo.")
    if f"<loc>{expected_domain}/" not in sitemap:
        raise AssertionError("El sitemap no contiene el dominio activo.")
    if f"Sitemap: {expected_domain}/sitemap.xml" not in robots:
        raise AssertionError("robots.txt no apunta al sitemap del dominio activo.")

    cname = PUBLIC / "CNAME"
    if custom_enabled:
        if not cname.is_file() or cname.read_text(encoding="utf-8").strip() != custom_domain:
            raise AssertionError("CNAME no coincide con custom_domain.")
    elif cname.exists():
        raise AssertionError("Se encontró un CNAME residual con el modo GitHub Pages activo.")

    if "__GOOGLE_SITE_VERIFICATION_TAG__" in index:
        raise AssertionError("Quedó un marcador de plantilla sin sustituir.")


def main() -> int:
    original_text = CONFIG_PATH.read_text(encoding="utf-8")
    original_config = json.loads(original_text)
    custom_domain = str(original_config.get("custom_domain", "")).strip().lower().rstrip(".")
    github_url = str(original_config.get("github_pages_url") or original_config.get("domain") or "").strip().rstrip("/")

    if not custom_domain:
        raise AssertionError("config.json debe definir custom_domain, por ejemplo autocalc.es.")
    if not github_url.startswith("https://"):
        raise AssertionError("config.json debe conservar una URL HTTPS de GitHub Pages en domain.")

    try:
        for custom_enabled in (True, False):
            test_config = dict(original_config)
            test_config["use_custom_domain"] = custom_enabled
            write_config(test_config)
            run_build()
            validate_mode(test_config, custom_enabled)
            label = f"https://{custom_domain}" if custom_enabled else github_url
            print(f"[OK] Generación validada para {label}")
    finally:
        # Restore configuration byte-for-byte and re-create the output for the
        # active deployment mode, even if one of the assertions fails.
        CONFIG_PATH.write_text(original_text, encoding="utf-8")
        run_build()

    validate_mode(original_config, original_config.get("use_custom_domain", False) is True)
    print("[OK] Configuración y carpeta public restauradas al modo activo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
