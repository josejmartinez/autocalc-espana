#!/usr/bin/env python3
"""Parse inline JavaScript from every generated HTML file with Node.js."""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SCRIPT_RE = re.compile(r"<script\b([^>]*)>(.*?)</script\s*>", re.IGNORECASE | re.DOTALL)
SRC_RE = re.compile(r"\bsrc\s*=", re.IGNORECASE)
TYPE_JSON_RE = re.compile(r"""type\s*=\s*["']application/ld\+json["']""", re.IGNORECASE)


def main() -> int:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js no está disponible para verificar la sintaxis del JavaScript generado.")

    pages = sorted(PUBLIC.glob("*.html"))
    if not pages:
        raise AssertionError("No hay páginas HTML generadas.")

    checked = 0
    with tempfile.TemporaryDirectory(prefix="autocalc-js-check-") as temp:
        temp_dir = Path(temp)
        for page in pages:
            html = page.read_text(encoding="utf-8")
            for index, (attrs, code) in enumerate(SCRIPT_RE.findall(html)):
                if not code.strip() or SRC_RE.search(attrs) or TYPE_JSON_RE.search(attrs):
                    continue
                script_path = temp_dir / f"{page.stem}-{index}.js"
                script_path.write_text(code, encoding="utf-8")
                result = subprocess.run(
                    [node, "--check", str(script_path)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if result.returncode != 0:
                    raise AssertionError(
                        f"JavaScript inválido en {page.name}, script {index}:\n"
                        f"{result.stdout}\n{result.stderr}"
                    )
                checked += 1

    print(f"[OK] Sintaxis JavaScript válida en {checked} scripts inline de {len(pages)} páginas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
