# Indexación en Bing y automatización IndexNow — AutoCalc España

## 1. Alta inicial en Bing Webmaster Tools

1. Entra en [Bing Webmaster Tools](https://www.bing.com/webmasters/).
2. Selecciona **Importar desde Google Search Console** y concede el permiso que solicite Microsoft.
3. Importa la propiedad de dominio `autocalc.es` ya verificada en Search Console. Si no aparece, añádela manualmente y completa la verificación solicitada.
4. Abre **Sitemaps** y confirma que aparece `https://autocalc.es/sitemap.xml`. Si falta, envíalo manualmente.
5. Abre la herramienta de inspección de URL y prueba la portada y algunas páginas importantes de las calculadoras.

Bing puede tardar hasta 48 horas en empezar a mostrar datos del panel. Una página descubierta o enviada no necesariamente se indexa: Bing puede excluirla por canonical incorrecta, un bloqueo en `robots.txt`/meta robots, contenido duplicado o calidad insuficiente.

## 2. IndexNow se configura automáticamente en el repositorio

La configuración actual tiene una clave IndexNow en `config.json`. El generador publica un archivo de verificación en la raíz de la web, con el mismo valor en el nombre y el contenido. Es una clave pública de verificación del protocolo, no una contraseña de tu cuenta.

Tras cada despliegue exitoso de la rama `main`, el workflow:
- vuelve a generar el sitemap desde el mismo commit publicado;
- confirma que el archivo de clave coincide;
- envía las URL HTTPS del sitemap al endpoint compartido `https://api.indexnow.org/indexnow`;
- divide los envíos en lotes de hasta 10.000 URL.

La notificación IndexNow avisa a Bing y a otros buscadores participantes de cambios en las URL. No reemplaza el sitemap ni garantiza indexación, ranking o rastreo inmediato. Los avisos se ejecutan después de publicar el sitio para que el buscador no reciba una URL nueva antes de que esté disponible.

## 3. Comprobaciones periódicas

En Bing Webmaster Tools:
- **Sitemaps:** última lectura y número de URL descubiertas.
- **Site Explorer / Páginas indexadas:** revisar exclusiones y errores.
- **Inspección de URL:** comprobar las páginas más importantes.
- **SEO Reports:** revisar recomendaciones una vez que se generen datos.

En Search Console, conservar el sitemap y la inspección de URL. Mantener ambas herramientas no genera contenido duplicado: son consolas independientes que analizan la misma web.

## Referencias oficiales

- [Importar sitios de Search Console a Bing](https://www2.bing.com/webmasters/help/add-and-verify-site-12184f8b)
- [Sitemaps en Bing Webmaster Tools](https://www2.bing.com/webmasters/help/sitemaps-3b5cf6ed)
- [Configuración oficial de IndexNow en Bing](https://www2.bing.com/indexnow/getstarted)
- [Documentación del protocolo IndexNow](https://www.indexnow.org/documentation)
