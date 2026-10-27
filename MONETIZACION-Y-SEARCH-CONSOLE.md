# Monetización, afiliación y Search Console de AutoCalc España

Última revisión: 17 de octubre de 2026.

## 1. Estado actual del proyecto

- Dominio principal configurado en el generador: `https://autocalc.es`.
- **HTTPS:** el usuario confirma que ya dispone de HTTPS; la captura más reciente de GitHub Pages muestra `Enforce HTTPS` marcado. GitHub todavía muestra `DNS Check in Progress`, así que no volver a pedir al titular que active HTTPS ni que compre un certificado. Conviene seguir revisando el estado DNS si algún servicio externo aún no puede acceder al dominio.
- **Solicitud de publisher en Awin enviada el 17 de octubre de 2026; revisión pendiente.** Después de la aceptación de la red hay que solicitar AUTODOC y Norauto por separado; no hay todavía campañas aprobadas ni enlaces de seguimiento reales en `config.json`.
- `contact_email` está vacío. El aviso legal se muestra expresamente pendiente de completar; antes de vender publicidad, completa el correo real del responsable y revisa la información identificativa/legal.
- Identificador de Amazon configurado en enlaces: `autocalces-21`. La configuración del identificador no demuestra por sí sola que la cuenta esté aprobada o en buen estado; confirmar el estado en la consola de Amazon Afiliados.
- Los enlaces a AUTODOC, Norauto, Oscaro, Aurgi, Feu Vert, eBay, Costco, Muchoneumático y desguaces permanecen directos mientras no se configure el seguimiento oficial de una campaña aprobada.
- El código de editor de AdSense facilitado por el titular (`ca-pub-1754459878527476`) ya está configurado en el generador y `ads.txt` se genera con su entrada. La entrega de anuncios sigue desactivada (`adsense_ads_enabled = false`) y `google_certified_cmp_configured = false`. El banner propio de Analytics no es una CMP certificada de Google para anuncios.

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

El código que facilita Google para verificar el sitio está ya integrado y se genera `ads.txt`. Esto no significa que el sitio esté aprobado ni que los anuncios estén activos. Mantén `adsense_ads_enabled = false` hasta que AdSense apruebe el dominio y se haya integrado y probado una CMP certificada. Antes de solicitar la revisión final, comprueba en la consola de AdSense que el código se detecta. Antes de activar la entrega de anuncios:

- Confirma que el sitio es accesible por HTTPS, y comprueba que `robots.txt`, el sitemap, la política de privacidad y el aviso legal están correctos.
- Completa y revisa los datos identificativos y de contacto del responsable. El código actual avisa de que esa información debe completarse; no publiques datos de ejemplo.
- Refuerza el contenido editorial original y útil. Evita generar muchas páginas casi idénticas cuyo principal objetivo sean los enlaces de compra: Google define la afiliación superficial y el contenido escalado de poco valor como riesgos para la calidad de búsqueda.
- Solicita AdSense y espera a que el sitio sea aceptado.
- Para publicar anuncios a usuarios del EEE, Reino Unido o Suiza, integra una **CMP certificada por Google y compatible con IAB TCF** según los requisitos aplicables. El aviso actual de AutoCalc gestiona el consentimiento de Google Analytics; no es por sí mismo una CMP certificada para AdSense.
- El identificador real `ca-pub-1754459878527476` ya está configurado para conectar/verificar el sitio y generar `ads.txt`. No cambies `adsense_ads_enabled` a `true` hasta que el sitio esté aprobado, el contacto legal esté completo y se haya integrado y probado una CMP certificada. No actives manualmente anuncios automáticos mientras esos pasos sigan pendientes.

Referencia: [requisitos de CMP de Google AdSense para publishers](https://support.google.com/adsense/answer/13554116?hl=es).

## 6. Plan de monetización por prioridad

1. **Ahora:** Search Console, HTTPS y verificación de Amazon; revisar los clics de salida en GA4 con consentimiento.
2. **Primera ampliación:** solicitar Awin y buscar campañas españolas relevantes de recambios, neumáticos y taller. Activar únicamente las campañas aprobadas.
3. **Segunda ampliación:** revisar eBay Partner Network y otras redes con campañas para recambio usado, herramientas OBD, diagnosis, baterías, cargadores y equipamiento del automóvil. Confirmar disponibilidad y términos dentro de cada plataforma.
4. **Publicidad display:** solicitar AdSense cuando la web tenga HTTPS estable, datos legales completos, política de privacidad revisada, contenido original sólido y CMP certificada.
5. **Optimización:** revisar mensual los clics y comisiones por proveedor, retirar campañas que no conviertan, no sesgar las recomendaciones al proveedor que más pague y mantener comparaciones transparentes de precio total, envío, montaje, compatibilidad y garantía.

No existe un ingreso garantizado: las comisiones dependen de que el usuario compre, de las reglas de atribución, la aprobación de la venta y el tráfico real.

## 7. Plan comercial actualizado: prioridad de campañas

**Orden operativo propuesto (no significa que la campaña esté aprobada ni abierta en España):**

1. **AUTODOC** — prioridad máxima para recambios nuevos. Solicitar programa desde Awin y/o el formulario de partners que AUTODOC facilite. Empezar con enlaces a categorías y búsquedas con contexto de vehículo.
2. **Norauto** — prioridad máxima para neumáticos, baterías, montaje y servicios de taller. Buscar la campaña española en Awin y solicitar admisión.
3. **Oscaro** — prioridad alta para recambios nuevos. Comprobar campañas disponibles y solicitar admisión. La ficha de tienda pública no confirma por sí sola la existencia de un programa de afiliación abierto.
4. **Aurgi y Feu Vert** — candidatos para neumáticos, mantenimiento, baterías y montaje. Comprobar campaña, país, condiciones de tráfico y estructura de comisión en la red antes de configurar tracking.
5. **eBay Partner Network** — canal adicional confirmado en la documentación oficial de eBay España; tiene una solicitud propia y herramientas para crear enlaces medibles a anuncios y búsquedas. Especialmente interesante para piezas OEM usadas y nuevas, aunque hay que usar los enlaces reales generados por EPN.
6. **Muchoneumático y RecambioVerde** — solicitar o confirmar programa de publisher propio o a través de red, y guardar el deeplink solo tras una aprobación real.
7. **Costco** — prioridad baja. No hemos podido confirmar un programa público de afiliados de Costco España relacionado con automoción. En su web, «afiliación» se refiere habitualmente a la tarjeta de socio, no a un programa de publisher. Mantener el enlace como directo hasta disponer de información oficial sobre una colaboración remunerada.

### Alta en Awin

- Registra AutoCalc en [Awin Afiliados](https://www.awin.com/es/afiliados) y completa el perfil con el dominio, audiencia, tipo de contenido y fuentes de tráfico reales.
- Cuando se apruebe la cuenta de publisher, busca las marcas indicadas en el directorio y solicita cada campaña por separado. Unirse a la red no equivale a ser aceptado por un anunciante.
- No he podido verificar desde páginas públicas que las campañas de AUTODOC, Norauto, Oscaro, Aurgi o Feu Vert estén abiertas ahora mismo para España. Esa disponibilidad y sus términos deben comprobarse dentro del directorio autenticado.
- Solicita también [eBay Partner Network](https://www.ebay.es/centroparavendedores/vender-en-ebay/ebay-partner-network). El programa español explica oficialmente que el editor solicita el acceso y luego crea enlaces medibles con sus herramientas.

### Plantillas y enlaces en el código

El comparador destaca visualmente AUTODOC y Norauto al principio, y añade Oscaro, Aurgi, eBay y Costco como alternativas. Las claves de seguimiento están en `config.json`, dentro de `affiliate_link_templates`, pero permanecen vacías hasta tener el tracking oficial.

**No rellenes esas claves con enlaces normales ni con IDs supuestos.** Para los partners cuya campaña entregue un enlace fijo que no pueda expresarse como plantilla, adapta el generador al formato oficial de la red antes de activar esa campaña. En el caso de eBay, usa las herramientas de EPN para generar el enlace real.

Cuando una plantilla se activa, el sitio codifica el destino, aplica `rel="sponsored"` e identifica el enlace como afiliado. Para enlaces que aún son directos no se finge una relación remunerada.

Fuentes oficiales: [Awin Afiliados](https://www.awin.com/es/afiliados/content-creator-influencer), [FAQ de Awin](https://www.awin.com/es/faq), [eBay Partner Network España](https://www.ebay.es/centroparavendedores/vender-en-ebay/ebay-partner-network), [información de socios de Costco España](https://www.costco.es/terminos-condiciones).

## 8. Espacios publicitarios laterales y patrocinio directo

El generador admite tres posiciones: `sidebar_left`, `sidebar_right` e `inline`. La configuración se encuentra en `config.json`:

- `direct_ad_slots`: anuncios de patrocinadores directos. Para activar uno, define `enabled: true`, `advertiser`, `headline`, `target_url` HTTPS, y opcionalmente `body` e `image_url`. Si añades imagen, súbela al propio repositorio y usa una ruta local segura como `/assets/anunciante.webp`; no se aceptan imágenes remotas de terceros en el bloque directo. El anuncio se marca explícitamente como **Publicidad** y el enlace lleva `rel="sponsored"`.
- `adsense_slots`: IDs de bloque de AdSense para cada posición. Deben ser los IDs numéricos reales facilitados por AdSense. Los bloques no aparecen si falta el ID de bloque o si AdSense está desactivado.
- Las barras laterales solo se muestran en pantallas amplias (1520 px o más), para no tapar el contenido. El espacio `inline` se adapta a móvil y escritorio.
- Si no hay patrocinador directo ni bloque de AdSense configurado, la barra izquierda puede mostrar automáticamente una recomendación afiliada de AUTODOC cuando exista una plantilla de seguimiento aprobada, y la barra derecha puede hacer lo propio con Norauto. Si sus plantillas siguen vacías, ambas posiciones permanecen ocultas.
- Los tres espacios están desactivados y vacíos de forma deliberada. No muestran banners falsos.

### Activación de AdSense

El código exige un ID real `ca-pub-...`, IDs de bloque válidos y `google_certified_cmp_configured: true` antes de aceptar AdSense. Esa bandera solo debe activarse una vez que se haya elegido e integrado una CMP certificada por Google que satisfaga los requisitos aplicables. El banner actual de Analytics no sirve como sustituto de esa CMP.

Antes de solicitar publicidad programática, completa los datos legales reales y de contacto: ahora mismo `contact_email` está vacío. Revisa también privacidad y aviso legal. Para comercializar directamente los espacios, prepara un dossier con impresiones, clics y audiencia reales cuando dispongamos de suficientes datos; no inventes métricas.

## 9. Medición y criterios comerciales

- Mantén AUTODOC y Norauto como prioridades, pero recomienda la tienda según el trabajo, precio total, compatibilidad, envío, montaje, garantía y disponibilidad, no solo según la comisión.
- Usa enlaces de afiliado que lleven a una búsqueda o producto pertinente, no únicamente a la portada del comercio cuando el producto o medida ya se conoce.
- Si más adelante se incorporan precios y disponibilidad de forma automática, usa feeds o APIs permitidos por cada comercio; no raspes catálogos si sus términos no lo permiten.
- Revisa mensualmente clics de salida, conversiones aprobadas, comisiones, devoluciones y rendimiento de cada ubicación publicitaria.
- No hay garantía de ingresos. Se necesitan tráfico, compras cualificadas y aceptación de las ventas para generar comisiones.

## 10. Cierre de la sesión del 17 de octubre de 2026

- Cambios del comparador, plantillas de afiliación, promociones laterales y espacios de anuncio ya están integrados en `main`; las plantillas de seguimiento y los tres espacios de publicidad siguen vacíos/desactivados intencionadamente.
- Solicitud de Awin recibida; no hay que repetir el registro. Esperar el correo y, cuando se habilite la cuenta, solicitar AUTODOC y Norauto antes que los demás.
- En la última revisión, el contenido público se desplegó correctamente en GitHub Pages, pero el certificado HTTPS no estaba emitido. No cambies más DNS si GitHub marca DNS correcto; si sigue sin certificado después del periodo indicado por GitHub, contacta con soporte de GitHub Pages y adjunta la captura de `DNS check successful` junto con el error del certificado.
- El build bloquea la activación accidental de espacios publicitarios display cuando `contact_email` está vacío. Ese correo no se inventa: debe completarlo el titular.


## 10. Nueva auditoría editorial automatizada (octubre de 2026)

El flujo de integración continua ejecuta ahora `scripts/audit_seo_content_quality.py` después de generar las páginas y de la auditoría técnica del sitio. Genera `build/seo-content-quality-report.json` con el recuento aproximado de palabras visibles, páginas sin H1, descripciones cortas o ausentes y grupos de títulos, H1 o cuerpos exactamente repetidos.

**Cómo interpretar el informe:**
- Es una herramienta para priorizar revisión editorial, no una puntuación de Google ni un requisito oficial de longitud.
- Una página corta puede resolver bien una intención concreta; no se debe ampliar con texto de relleno solo para alcanzar un número.
- Un H1 o título similar puede ser correcto si las páginas responden a intenciones distintas, pero hay que comprobar que cada URL aporta una utilidad específica.
- No se aplica `noindex`, no se elimina ninguna URL y no se modifica el sitemap automáticamente a partir de estas señales.
- Las incidencias de Search Console deben cruzarse con la URL concreta, su canonical, contenido real, enlaces internos y estado de rastreo antes de decidir cambios.

Este informe complementa `scripts/audit_static_site.py`, que ya revisa canonicals, enlaces locales, metadatos básicos, JSON-LD, sitemap, robots y salvaguardas de monetización. La auditoría editorial no sustituye la inspección de URL de Search Console ni garantiza indexación o aprobación de AdSense.
