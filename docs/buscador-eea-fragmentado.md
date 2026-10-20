# Buscador EEA por fragmentos

El índice EEA compacto (~36 MB para la edición inicial de 90.922 variantes) no debe descargarse completo en el navegador. El fragmentador genera un manifiesto pequeño y un JSON por fabricante; la interfaz solo solicita el fragmento del fabricante seleccionado.

## Generar

Después de importar y exportar el índice compacto:

```powershell
python scripts/fragmentar_indice_eea.py --input "build\eea-search-index.json" --output-dir "build\eea-shards"
```

Salida: `build/eea-shards/manifest.json` y un archivo JSON por fabricante. El manifiesto incluye metadatos del conjunto, número de variantes y la ruta del fragmento de cada fabricante. Los nombres incluyen un hash corto para evitar colisiones tras normalizar marcas.

## Integración con el portal

Cuando existe `build/eea-shards/manifest.json`, `src/build.py` copia los fragmentos a `public/eea-data/` y genera `buscador-vehiculos-eea.html`. La página descarga primero solo el manifiesto y después carga un único fragmento, bajo demanda, al elegir fabricante. Si el catálogo no está disponible, la página no se genera; el despliegue normal no depende de datos EEA ni cambia las calculadoras existentes.

`build/` y los datos originales deben permanecer fuera del control de versiones. No se debe confundir este catálogo de matriculaciones de turismos nuevos con el parque completo de vehículos ni usarlo como fuente de medidas de neumáticos, ET, homologación o compatibilidad ITV. Los datos técnicos se muestran como referencia de la fuente EEA, no como certificación de compatibilidad.

## Pruebas

```powershell
python scripts/test_fragmentar_indice_eea.py
```
