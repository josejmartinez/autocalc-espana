# Monetización, afiliación y Search Console de AutoCalc España

Última revisión: 17 de octubre de 2026.

## 1. Estado actual del proyecto

- Dominio principal configurado: `https://autocalc.es`.
- Identificador de Amazon configurado en enlaces: `autocalces-21`. La configuración del identificador no demuestra por sí sola que la cuenta esté aprobada o en buen estado; confirmar el estado en la consola de Amazon Afiliados.
- Enlaces de AUTODOC, Norauto, Feu Vert y Muchoneumático: enlaces directos mientras no se añada una plantilla de seguimiento asignada por el programa.
- AdSense: desactivado (`adsense_client` vacío). La web tiene un control de consentimiento propio para Analytics, pero no es una CMP certificada de Google para anuncios.

## 2. Google Search Console tras la migración

Hazlo cuando `https://autocalc.es/` funcione correctamente con HTTPS:

1. En [Google Search Console](https://search.google.com/search-console/), añade una **propiedad de dominio** con el valor `autocalc.es` (sin protocolo ni ruta).
2. Google te dará un registro TXT de verificación. Añádelo en Piensa Solutions → Dominio → Registros DNS con nombre `@` (o el campo raíz que indique el panel) y el valor exacto que facilite Google. No uses un token inventado ni reutilices uno sin comprobar que corresponde a esta propiedad.
3. Conserva ese TXT mientras quieras mantener la propiedad verificada. No elimines registros TXT existentes de otras verificaciones.
4. Opcionalmente, añade también la propiedad de prefijo de URL `https://autocalc.es/` para inspeccionar URL concretas. La etiqueta `google-site-verification` configurada en el HTML solo verifica una propiedad si el token corresponde a ella.
5. En la propiedad nueva, ve a **Sitemaps** y envía `https://autocalc.es/sitemap.xml`. Comprueba el resultado del envío y la inspección de la portada.
6. Conserva la propiedad antigua `https://josejmartinez.github.io/autocalc-espana/` para comparar los datos de la migración. No la elimines. Como la URL antigua está bajo una ruta de un dominio de GitHub, la herramienta «Cambio de dirección» puede no ser aplicable como lo sería entre dos dominios propios; utilízala solo si Search Console ofrece esa opción para las propiedades verificadas y los requisitos se cumplen.
7. En **GA4 → Administrar → Flujos de datos → flujo web**, actualiza la URL del sitio a `https://autocalc.es` si todavía muestra la URL antigua. Conserva el ID de medición existente (`G-QN5542F4NX`) si quieres mantener las estadísticas en la misma propiedad; no crees otra etiqueta sin una razón.

Referencias: [traslados de sitios con cambio de URL](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes?hl=es), [crear y enviar un sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap?hl=es).

## 3. Amazon Afiliados España

La web utiliza el identificador `autocalces-21` en los enlaces de búsqueda de Amazon. Antes de dar por activa la afiliación, entra en la consola y confirma que la cuenta está aceptada y que el identificador corresponde al sitio correcto.

El generador incluye en las páginas la declaración exigida por Amazon:

> En calidad de Afiliado de Amazon, obtengo ingresos por las compras adscritas que cumplen los requisitos aplicables.

Además, los enlaces con seguimiento de Amazon se identifican como enlaces de afiliado y llevan `rel="sponsored"`. No elimines esa declaración del sitio. No inventes precios, imágenes, valoraciones ni datos de catálogo de Amazon; por ahora enlazamos a búsquedas y no mostramos precios Amazon procedentes de una API.

Amazon indica que revisa la solicitud tras obtener al menos tres ventas cualificadas durante los primeros 180 días, y que espera contenido original, público y reciente; su ayuda menciona, por regla general, al menos diez publicaciones en la web. Confirma en la consola los requisitos aplicables a tu cuenta y no compres desde tus propios enlaces para intentar generar comisiones.

Referencia: [políticas del Programa de Afiliados](https://afiliados.amazon.es/help/operating/policies/) y [proceso de revisión](https://afiliados.amazon.es/help/node/topic/G8TW5AE9XL2VX9VM).

## 4. AUTODOC, Norauto, Feu Vert, Muchoneumático y desguaces

No añadas un supuesto identificador de afiliado ni construyas URL de tracking a mano. El proceso recomendado es:

1. Regístrate como publisher en [Awin](https://www.awin.com/es/afiliados) y completa el perfil con `https://autocalc.es/`, el tipo de contenido y las fuentes de tráfico reales.
2. En el directorio de anunciantes busca campañas de España de AUTODOC, Norauto, Feu Vert, Muchoneumático y RecambioVerde. La disponibilidad territorial y aceptación del publisher deben confirmarse dentro de la cuenta. Las páginas públicas localizadas durante esta revisión incluyen AUTODOC NL y NORAUTO IT; eso **no** demuestra que las campañas españolas estén abiertas.
3. Revisa las condiciones de cada campaña: países aceptados, comisión, duración de atribución, reglas sobre anuncios de búsqueda de pago, uso de marca, cupones, deeplinks y restricciones de tráfico.
4. Una vez aprobado, usa el generador oficial de enlaces profundos de la red y guarda la plantilla de seguimiento que te proporcione el programa.

### Cómo incorporar una plantilla aprobada

El archivo `config.json` contiene `affiliate_link_templates`. Las entradas están vacías de forma deliberada. Solo después de la aprobación puedes rellenar el campo de un comercio con su plantilla HTTPS oficial, usando el marcador `{destination}` donde la red espere la URL de destino. El generador codifica esa URL al aplicar el marcador.

Ejemplo ilustrativo de la forma esperada por el código —**no es una URL de tracking real y no debe publicarse tal cual**:

```json
{
  "autodoc": "https://tracking.example/click?destination={destination}",
  "norauto": "",
  "feuvert": "",
  "muchoneumatico": "",
  "recambioverde": "",
  "desguaceslatorre": "",
  "elchoque": ""
}
```

No copies el dominio ni los parámetros del ejemplo. Si una red facilita un deeplink fijo sin parámetro de destino, no lo fuerces a esta forma: conserva la configuración vacía y adapta el generador a la documentación real de la red antes de activarlo. Mientras la plantilla esté vacía, los enlaces de la tienda permanecen directos y el sitio no los presenta como afiliados.

La implementación añade automáticamente `rel="sponsored"` y una marca visible «Enlace de afiliado» solo a Amazon con su tag y a los comercios con plantilla de seguimiento configurada. Para los enlaces comerciales directos conserva `nofollow`/protecciones de nueva pestaña, pero no afirma que haya una relación pagada.

Google recomienda etiquetar los enlaces de afiliación con `rel="sponsored"`: [guía oficial de enlaces salientes](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links?hl=es).

## 5. Publicidad display: AdSense

No activar AdSense aún. Antes:

- Confirma que el sitio es accesible por HTTPS, y comprueba que `robots.txt`, el sitemap, la política de privacidad y el aviso legal están correctos.
- Completa y revisa los datos identificativos y de contacto del responsable. El código actual avisa de que esa información debe completarse; no publiques datos de ejemplo.
- Refuerza el contenido editorial original y útil. Evita generar muchas páginas casi idénticas cuyo principal objetivo sean los enlaces de compra: Google define la afiliación superficial y el contenido escalado de poco valor como riesgos para la calidad de búsqueda.
- Solicita AdSense y espera a que el sitio sea aceptado.
- Para publicar anuncios a usuarios del EEE, Reino Unido o Suiza, integra una **CMP certificada por Google y compatible con IAB TCF** según los requisitos aplicables. El aviso actual de AutoCalc gestiona el consentimiento de Google Analytics; no es por sí mismo una CMP certificada para AdSense.
- Solo cuando haya aprobación, CMP integrada y revisión de privacidad, establece `adsense_client` con el identificador real `ca-pub-...` y cambia `google_certified_cmp_configured` a `true` después de verificar la integración. El generador creará el registro `ads.txt` a partir de ese ID. No uses identificadores ficticios.

Referencia: [requisitos de CMP de Google AdSense para publishers](https://support.google.com/adsense/answer/13554116?hl=es).

## 6. Plan de monetización por prioridad

1. **Ahora:** Search Console, HTTPS y verificación de Amazon; revisar los clics de salida en GA4 con consentimiento.
2. **Primera ampliación:** solicitar Awin y buscar campañas españolas relevantes de recambios, neumáticos y taller. Activar únicamente las campañas aprobadas.
3. **Segunda ampliación:** revisar eBay Partner Network y otras redes con campañas para recambio usado, herramientas OBD, diagnosis, baterías, cargadores y equipamiento del automóvil. Confirmar disponibilidad y términos dentro de cada plataforma.
4. **Publicidad display:** solicitar AdSense cuando la web tenga HTTPS estable, datos legales completos, política de privacidad revisada, contenido original sólido y CMP certificada.
5. **Optimización:** revisar mensual los clics y comisiones por proveedor, retirar campañas que no conviertan, no sesgar las recomendaciones al proveedor que más pague y mantener comparaciones transparentes de precio total, envío, montaje, compatibilidad y garantía.

No existe un ingreso garantizado: las comisiones dependen de que el usuario compre, de las reglas de atribución, la aprobación de la venta y el tráfico real.
