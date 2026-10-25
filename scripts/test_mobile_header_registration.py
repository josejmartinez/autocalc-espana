#!/usr/bin/env python3
"""Regression checks for compact mobile navigation and safe registration-date estimates."""
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(ROOT/"src"/"build.py")],cwd=ROOT,check=True)
html=(ROOT/"public"/"index.html").read_text(encoding="utf-8")
assert 'sm:sticky top-0' in html, "Header should not be sticky on small screens"
assert 'overflow-x-auto sm:overflow-visible' in html, "Mobile navigation should scroll horizontally instead of wrapping into a tall banner"
assert 'hidden sm:inline-flex' in html, "Secondary actions should be hidden on small screens"
assert 'id="mat-num" value=""' in html and 'id="mat-letras" value=""' in html, "Registration inputs must not prefill a misleading plate"
assert 'id="mat-rematriculado"' in html, "Rematriculated vehicles need an explicit safe path"
assert 'No estimamos la antigüedad a partir de la placa actual' in html, "Rematriculated vehicles must not get an inferred age"
assert 'El año de la placa actual no debe sobrescribir los datos del vehículo.' in html, "Plate estimate must not override the vehicle year used for environmental estimates"
assert 'Solicitar informe oficial del vehículo' in html and 'Consultar distintivo DGT' in html, "Official DGT verification links must be present"
print("UX móvil y matrícula: navegación compacta, campos vacíos, rematriculación y enlaces oficiales validados.")
