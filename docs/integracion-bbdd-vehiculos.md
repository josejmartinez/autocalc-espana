# Integración de una base de datos real de vehículos

## Objetivo

Sustituir progresivamente los ejemplos orientativos hardcodeados de `src/catalogo.py` por un catálogo consultable de vehículos reales, con procedencia, mercado y nivel de confianza explícitos. Mantener AutoCalc España como web estática en GitHub Pages y conservar intactos los huecos de publicidad.

## Conclusión de la investigación

No existe una única fuente pública que ofrezca, gratis y con cobertura exhaustiva de España, todas las versiones y todos los datos técnicos (motor, potencia, medidas homologadas, neumáticos, emisiones, masas, etc.). La solución fiable es combinar fuentes por campo y guardar la procedencia de cada dato.

### Fuentes evaluadas

1. **VehiclesDB (catálogo de identidad; CC BY 4.0)**  
   https://github.com/vehiclesdb/vehiclesdb  
   Catálogo abierto de marcas/modelos con cobertura multinacional, tipos de vehículo y evidencia por país. Útil como índice de marca/modelo y para resolver nombres. No equivale a una ficha técnica por motor/acabado. La atribución visible a VehiclesDB es condición de la licencia y debe mantenerse si se usa el dataset.

2. **Agencia Europea de Medio Ambiente (EEA), datos oficiales de turismos y furgonetas nuevos**  
   Turismos: https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b  
   Furgonetas: https://www.eea.europa.eu/en/datahub/datahubitem-view/9636827c-bd0c-40f5-814e-c4065c11c9a0  
   Los ficheros anuales pueden contener marca/nombre comercial, tipo, variante y versión, emisiones de CO₂, masa, batalla, vías, combustible y, según el registro, potencia y cilindrada. Son datos de vehículos nuevos registrados y reportados en Europa; no constituyen un catálogo universal de todos los años/mercados y hay que respetar las notas de calidad, unidades y licencia de cada descarga. Son una fuente especialmente útil para enriquecer fichas europeas.

3. **DGT / informes de vehículos**  
   https://sede.dgt.gob.es/es/vehiculos/informacion-de-vehiculos/informe-de-un-vehiculo/  
   La DGT ofrece informes de datos técnicos de vehículos matriculados en España. La integración profesional automatizada se realiza mediante servicios sujetos a autorización/condiciones; no debe suponerse que existe una API pública gratuita de consulta masiva. No basar el producto en scraping de la sede.

4. **NHTSA vPIC (fuente complementaria, no principal para España)**  
   https://vpic.nhtsa.dot.gov/api/  
   API pública sin registro para descodificación VIN y datos declarados por fabricantes en el contexto de EE. UU. Es útil para ciertos VIN y atributos, pero su cobertura es incompleta para versiones europeas y no debe presentarse como autoridad para medidas o homologación española.

5. **Proveedor comercial de especificaciones**  
   Como alternativa para datos profundos por acabado/motor, evaluar un proveedor comercial con cobertura explícita de España/Europa, derecho de uso comercial y permiso de almacenamiento/caché. No integrar una API de pago hasta revisar contrato, cobertura por campo, límites, precio y condiciones de redistribución.

## Arquitectura propuesta

### Fase A — Catálogo de identidad y procedencia

- Usar VehiclesDB como índice de marcas/modelos, fijando una versión concreta (no `latest` en producción sin control).
- Mantener un enlace de atribución visible «Vehicle data by VehiclesDB» en la web y registrar versión/fecha de actualización.
- Cada registro interno tendrá un ID estable y campos `make`, `model`, `generation` (si existe), `model_year_from`, `model_year_to`, `market`, `body_type`, `source`, `source_url`, `retrieved_at` y `confidence`.
- No convertir un nombre de modelo en una versión/motor concreta si la fuente no lo confirma.

### Fase B — Especificaciones técnicas europeas

- Importar los ficheros EEA anuales de turismos y furgonetas en un proceso reproducible.
- Conservar el dato bruto original o una referencia a él; normalizar por separado unidades y campos.
- Separar la identidad de vehículo de la configuración homologada: marca + modelo comercial no identifica de forma única un motor, acabado, neumático o potencia.
- Usar claves compuestas de homologación/tipo/variante/versión cuando estén disponibles. Nunca deduplicar únicamente por nombre comercial.
- Registrar para cada campo la fuente, el año del dataset, la unidad original y las transformaciones aplicadas.
- Añadir pruebas para duplicados, unidades, nulos, valores fuera de rango y cambios de esquema.

### Fase C — Experiencia de usuario y calculadoras

- Incorporar un buscador progresivo marca → modelo → año → motor/versión.
- Mostrar una ficha con atributos disponibles y un indicador «dato oficial / fuente pública / estimación / no disponible».
- Las calculadoras solo autocompletarán campos respaldados por una coincidencia inequívoca; el usuario podrá corregirlos.
- En neumáticos, ET y compatibilidad de llantas, no mostrar una combinación como legal u homologada salvo que exista evidencia específica de la versión/homologación. Las medidas de catálogo genérico seguirán siendo orientativas.
- Si hay varias versiones posibles, preguntar al usuario en vez de elegir una automáticamente.

## Compatibilidad con GitHub Pages

GitHub Pages no ejecuta un servidor ni una base de datos dinámica. Para mantener el despliegue estático y sin costes de servidor:
1. descargar y normalizar fuentes durante un proceso de actualización separado;
2. generar un JSON pequeño y optimizado para la web;
3. publicarlo junto al sitio estático, con versión y fecha;
4. añadir un flujo manual/programado de actualización, validación y revisión antes de publicar.

No descargar la base completa desde el navegador en cada visita: empeora rendimiento, privacidad, resiliencia y dependencia de terceros. Tampoco incluir claves privadas en JavaScript público.

Si en el futuro se necesitan búsquedas complejas, perfiles de usuario, matrícula/VIN en tiempo real o consultas a un proveedor privado, habrá que añadir una API/backend y valorar su coste y cumplimiento de privacidad.

## Orden de implantación recomendado

1. Incorporar y probar un catálogo de identidad abierto con atribución.
2. Construir el importador EEA y medir cobertura real de turismos/furgonetas en España.
3. Generar un informe de calidad (número de registros, años, proporción con potencia/cilindrada/CO₂/masa/medidas, duplicados y huecos).
4. Con ese informe, decidir qué campos pueden alimentar cada calculadora y qué huecos requieren proveedor comercial.
5. Integrar el selector de vehículo de forma incremental, sin eliminar las entradas manuales ni los métodos actuales hasta que las pruebas demuestren equivalencia.

## Criterios de aceptación

- Cada especificación visible tiene fuente y unidad trazables.
- Se distingue «no disponible» de cero y de una estimación.
- No se publican como oficiales datos de marketing, valores genéricos o inferencias por nombre de modelo.
- Las pruebas de generación, calculadoras, enlaces, privacidad y espacios publicitarios siguen pasando.
- Los tres huecos publicitarios existentes no se mueven ni se activan como parte de este trabajo.
- Ningún cambio llega a `main` ni a producción sin revisión del PR y ejecución correcta de CI.

## Estado

Esta nota documenta la investigación y la arquitectura previa a la importación. No añade todavía datos inventados ni modifica el comportamiento de las calculadoras. La siguiente entrega de código debe ser el importador reproducible y un informe de cobertura; después se puede conectar el selector con datos reales.
