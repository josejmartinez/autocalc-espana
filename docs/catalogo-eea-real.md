# Catálogo compacto a partir del CSV real EEA de turismos

El CSV EEA descargado puede ser muy grande y contiene una fila por registro de matriculación. No debe publicarse directamente ni abrirse con Excel para procesarlo. El script scripts/importar_catalogo_eea.py lee el archivo fila a fila y agrega registros que comparten una configuración técnica completa, incluyendo homologación, tipo, variante, versión y atributos disponibles.

Ejemplo para el CSV de turismos de España de 2025, estado provisional:

```powershell
python scripts/importar_catalogo_eea.py --input "C:\RUTA\autocalc_es_2025.csv" --country ES --year 2025 --status P --output "build\eea-variants.json" --report "build\eea-variants-report.json"
```

El proceso genera un JSON de variantes y un informe de auditoría. No se integra automáticamente en la web. Antes de conectar el catálogo al buscador deben revisarse el número de variantes, la cobertura, los valores extremos y las definiciones/unidades oficiales de cada columna. La fuente EEA describe vehículos nuevos registrados; no es un catálogo completo del parque circulante ni prueba medidas homologadas de neumáticos/llantas.

Columnas mapeadas del fichero observado: Mk (marca), Cn (denominación comercial), Tan (tipo de homologación), T (tipo), Va (variante), Ve (versión), Ct/Cr (categorías), m (kg), Ewltp (g/km), Ft, ec (cm3), ep (KW), z (Wh/km), Status, year, Date of registration, Fuel consumption y Electric range (km). Las unidades y semántica de campos no evidentes deben verificarse con la definición oficial de la edición EEA antes de alimentar cálculos.
