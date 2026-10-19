# Índice de búsqueda del catálogo EEA

El catálogo EEA agregado no debe publicarse directamente en el buscador: contiene campos innecesarios para una consulta rápida y consume más transferencia.

## Exportación

Después de generar el catálogo completo con `scripts/importar_catalogo_eea.py`, ejecutar:

```powershell
python scripts/exportar_indice_eea.py --input "build\eea-variants.json" --output "build\eea-search-index.json"
```

El índice reducido conserva la identidad técnica de cada variante, combustible, cilindrada, potencia, masas identificadas, CO₂ WLTP, consumo eléctrico y autonomía eléctrica cuando existan. Omite el consumo de combustible porque aún debe verificarse formalmente la unidad exacta de esa columna en la edición EEA 2025.

## Límites

- La fuente representa matriculaciones de turismos nuevos del año/estado seleccionados, no todo el parque circulante.
- Las variantes no equivalen necesariamente a versiones comerciales conocidas por los usuarios.
- El índice no contiene medidas homologadas de neumáticos, ET de llantas ni compatibilidad ITV.
- No se debe conectar automáticamente ningún campo a cálculos fiscales o de neumáticos sin revisar su semántica.
- El índice se genera localmente y no se incorpora automáticamente al sitio: antes de publicar hay que medir su tamaño, revisar muestras y decidir la estrategia de entrega estática.

Fuente: [Agencia Europea de Medio Ambiente](https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b).
