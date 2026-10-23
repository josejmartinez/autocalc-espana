# Reseñas de AutoCalc España — arquitectura por fases

## Decisión de producto

Priorizar una sección de reseñas y experiencias de productos, no un foro general. El sitio público actual se genera con Python y se publica como archivos estáticos en GitHub Pages; por tanto, el primer incremento añade un hub editorial público y un contrato de datos versionado, pero **no finge que existe un sistema de cuentas o de publicación**.

## Fase 1 (incluida en esta PR)

- Página `/resenas/` adaptable a móvil, con categorías de producto, metodología y transparencia editorial.
- No mostrar estrellas, opiniones ni reseñas inventadas.
- `/resenas/reviews.json` define el contrato inicial y los estados de moderación.
- Sitemap ampliado con la landing de reseñas.
- Pruebas automatizadas del canonical, sitemap y reglas de transparencia.

## Fase 2 — reseñas dinámicas (requiere configuración de servicio)

Usar una base de datos gestionada (por ejemplo, Supabase/Postgres) y autenticación por correo con verificación. No guardar secretos en GitHub ni en JavaScript público. Antes de activar publicaciones, configurar las variables de entorno y aplicar migraciones con RLS.

Tablas previstas:

- `review_submissions`: borradores, producto, texto, valoración, contexto de uso y estado de moderación.
- `published_reviews`: solo contenido aprobado, campos públicos y fechas.
- `review_reports`: denuncias de contenido y resolución de moderación.
- `moderation_audit`: acciones administrativas con actor, fecha y motivo.

Requisitos de seguridad: RLS por defecto; el usuario solo puede modificar sus borradores; ningún usuario puede aprobar su propio contenido; moderación desde rol privado; validación de entrada y límites de tamaño; rate limiting y honeypot/Turnstile; evitar exponer email/IP; subida de imágenes limitada por tipo, tamaño y permisos; exportación y borrado conforme a privacidad; registro de consentimiento cuando proceda.

## Fase 3 — funciones diferenciales

- Formulario guiado por categoría (cargador EV, OBD2, neumático, batería, accesorio).
- «Probado por AutoCalc» solo con registro editorial de pruebas; «compra verificada» solo con verificación independiente real.
- Pros/contras estructurados, contexto del vehículo, fecha de uso y evidencia opcional.
- Ordenación útil: recientes, más útiles y mejor documentadas; no solo mayor puntuación.
- Detección de duplicados y patrones de spam como señales de revisión, nunca como rechazo automático infalible.
- Correcciones, respuesta del autor, denuncia y proceso de apelación.
- JSON-LD `Product`/`Review`/`AggregateRating` solo si los datos son elegibles, visibles y auténticos; no añadir rating agregado cuando no existan suficientes valoraciones.
- Importante: no lanzar indexación masiva de páginas vacías. Publicar páginas indexables solo con contenido sustantivo y moderado.

## Condiciones para activar la comunidad

1. Definir correo de contacto real y textos legales definitivos.
2. Crear proyecto y credenciales de producción en el proveedor elegido, fuera del repositorio.
3. Revisar privacidad, cookies, retención, derechos de usuarios y flujo de moderación.
4. Pruebas de abuso, RLS, permisos, XSS, enlaces, imágenes y recuperación de cuenta.
5. Habilitar aportaciones solo después de que las pruebas de integración y de seguridad pasen.

## Métricas

Medir reseñas aprobadas, porcentaje con contexto de uso, denuncias, tiempo de moderación, clics de salida de afiliación y retorno de usuarios. No optimizar únicamente por estrellas o conversión comercial.
