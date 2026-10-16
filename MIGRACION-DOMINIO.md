# Migración de AutoCalc España a autocalc.es

El sitio seguirá publicado en GitHub Pages mientras el dominio se activa. **No cambies** `use_custom_domain` a `true` hasta que el dominio esté dado de alta y GitHub Pages tenga validado el dominio y las DNS.

## Cómo está preparado el código

En `config.json`:

- `domain`: URL actual de GitHub Pages y destino de vuelta si hay que revertir.
- `custom_domain`: dominio reservado para el sitio, ahora `autocalc.es`.
- `use_custom_domain`: interruptor de la migración. Sigue en `false`.

Al activar el interruptor, el generador actualiza automáticamente las URL canónicas, Open Graph, el sitemap, `robots.txt` y el archivo `CNAME`. El flujo de GitHub Actions prueba ambos modos y restaura la configuración activa antes de validar el artefacto. Como la web se publica mediante GitHub Actions, **el archivo CNAME por sí solo no configura el dominio en GitHub**: también hay que guardarlo en Settings → Pages.

## Pasos cuando Piensa Solutions confirme el alta

1. **No toques la configuración actual todavía.** Comprueba que el dominio aparece activo en el área de cliente de Piensa Solutions.
2. En GitHub, abre el repositorio `josejmartinez/autocalc-espana` → **Settings → Pages**. En «Custom domain», añade `autocalc.es` y guarda. GitHub recomienda añadir el dominio al sitio antes de configurarlo en el proveedor DNS, para reducir el riesgo de que otra persona pueda alojarlo.
3. En la gestión DNS de Piensa Solutions, configura para el dominio raíz (`@`) estos cuatro registros **A**:

   - `185.199.108.153`
   - `185.199.109.153`
   - `185.199.110.153`
   - `185.199.111.153`

   Añade `www` como **CNAME** a `josejmartinez.github.io` (sin el nombre del repositorio). Quita únicamente los registros de parking o A/AAAA que entren en conflicto con estos registros; **no borres MX ni TXT de correo u otros servicios**. No configures un CNAME en el dominio raíz.
4. Espera a que GitHub Pages muestre que la comprobación DNS es correcta. Activa **Enforce HTTPS** cuando esté disponible. Los cambios DNS pueden tardar hasta 24 horas en propagarse.
5. Actualiza tu copia local en IntelliJ y cambia únicamente `"use_custom_domain": false` a `"use_custom_domain": true` en `config.json`. Después:

   ```powershell
   git switch main
   git pull origin main
   git add config.json
   git commit -m "chore: activar el dominio autocalc.es"
   git push origin main
   ```

   Si editas el archivo por GitHub web en vez de IntelliJ, asegúrate de sincronizar luego la copia local con `git pull origin main`.
6. Espera a que GitHub Actions termine en verde y comprueba `https://autocalc.es/`, `https://autocalc.es/robots.txt` y `https://autocalc.es/sitemap.xml`. En el sitemap y en las etiquetas canónicas ya deberán aparecer las URL de `autocalc.es`.
7. En Google Search Console, añade la propiedad del nuevo dominio. Una propiedad de dominio se suele verificar con un registro TXT en DNS; el meta-token configurado en el HTML corresponde a la verificación de tipo prefijo de URL. Envía el nuevo sitemap cuando la web sea accesible por HTTPS.

## Si hay problemas y necesitas volver a GitHub Pages

1. En Settings → Pages, retira temporalmente `autocalc.es` como dominio personalizado si está causando una redirección a una web que todavía no responde.
2. Cambia `use_custom_domain` a `false` en `config.json`, confirma el cambio y haz `git push origin main`.
3. Comprueba que el último despliegue de Actions termina correctamente y que vuelven a publicarse las URL de `https://josejmartinez.github.io/autocalc-espana`.

## Referencia oficial

Consulta [la guía oficial de GitHub para configurar dominios personalizados en GitHub Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) antes de cambiar DNS o activar HTTPS.
