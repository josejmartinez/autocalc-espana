# Migración de AutoCalc España a autocalc.es

**Estado (17 de octubre de 2026):** el dominio `autocalc.es` ya está registrado en Piensa Solutions. La rama `chore/activate-autocalc-domain` prepara el cambio de URL canónica, Open Graph, sitemap, `robots.txt` y `CNAME`; el dominio de producción no cambia hasta fusionar esta rama.

## Orden seguro para publicar el dominio

Haz estos pasos seguidos. **No fusiones la rama ni actives el modo de dominio propio en producción hasta que las DNS resuelvan correctamente.**

### 1. Añade el dominio en GitHub Pages

1. Abre el repositorio [josejmartinez/autocalc-espana](https://github.com/josejmartinez/autocalc-espana).
2. Ve a **Settings → Pages**.
3. En **Custom domain**, escribe `autocalc.es` y pulsa **Save**. Si ya aparece, no lo dupliques.
4. No cambies la rama ni el método de publicación: el sitio se publica mediante GitHub Actions.

GitHub recomienda registrar el dominio en Pages antes de apuntar las DNS para reducir el riesgo de que otra persona lo asocie a su sitio.

### 2. Configura las DNS en Piensa Solutions

En el Área de Cliente, abre el producto del dominio **autocalc.es** y entra en el panel de control o gestor de DNS. En los registros de la zona DNS, configura:

| Tipo | Nombre / host | Valor / destino |
|---|---|---|
| A | `@` (o el campo de nombre vacío para el dominio raíz, según el formulario) | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `josejmartinez.github.io` |

Deja el TTL por defecto si no sabes qué valor usar. El CNAME de `www` apunta al dominio de usuario de GitHub, **sin** añadir `/autocalc-espana`.

Antes de guardar, revisa si hay registros A/AAAA del dominio raíz que apunten al aparcamiento de Piensa Solutions o a otra IP. Retira únicamente los que entren en conflicto. **No borres registros MX ni TXT** ni cambies servidores NS: podrían ser necesarios para correo o verificaciones de otros servicios. No añadas un CNAME en el dominio raíz.

No es necesario activar el hosting WordPress de Piensa Solutions: el alojamiento de la web seguirá siendo GitHub Pages.

### 3. Comprueba que las DNS ya llegan a GitHub

En Windows, abre PowerShell y ejecuta:

```powershell
Resolve-DnsName autocalc.es -Type A
Resolve-DnsName www.autocalc.es -Type CNAME
```

Para el dominio raíz deben aparecer las cuatro IP de GitHub Pages indicadas arriba; `www.autocalc.es` debe apuntar a `josejmartinez.github.io`. La propagación puede tardar hasta 24 horas.

### 4. Activa la versión preparada en el repositorio

Cuando los registros ya resuelvan bien:

1. Abre la [rama preparada](https://github.com/josejmartinez/autocalc-espana/tree/chore/activate-autocalc-domain) y su pull request si ya está creado.
2. Comprueba que las verificaciones de GitHub Actions terminan en verde y fusiona la PR.
3. En **Settings → Pages**, confirma que el dominio personalizado sigue siendo `autocalc.es`.
4. Cuando GitHub Pages permita marcar **Enforce HTTPS**, actívalo. No habilites HTTPS en una web de terceros ni configures una redirección desde Piensa Solutions; HTTPS lo emitirá GitHub Pages.

La activación del código cambia automáticamente las URL canónicas, Open Graph, el sitemap, `robots.txt` y el archivo `CNAME`. No hace falta editar esos archivos generados manualmente.

### 5. Verifica la publicación y el SEO

Cuando termine el despliegue, abre estas direcciones:

- [https://autocalc.es/](https://autocalc.es/)
- [https://autocalc.es/robots.txt](https://autocalc.es/robots.txt)
- [https://autocalc.es/sitemap.xml](https://autocalc.es/sitemap.xml)
- [https://www.autocalc.es/](https://www.autocalc.es/) (debe llegar al dominio principal)

Comprueba que la portada carga con HTTPS y que el sitemap utiliza `https://autocalc.es/`, no la dirección antigua de GitHub Pages.

En Google Search Console, añade `autocalc.es` como propiedad de dominio y usa el TXT de verificación que te proporcione Google. No elimines el actual `google-site-verification` del HTML: puede seguir siendo útil para una propiedad de prefijo de URL. Envía `https://autocalc.es/sitemap.xml` cuando la nueva web responda correctamente.

## Reversión si surge un problema

La URL de GitHub Pages se conserva en `config.json` como referencia de respaldo. Si el dominio propio no funciona, retira temporalmente `autocalc.es` de **Settings → Pages**, cambia `use_custom_domain` a `false`, publica ese cambio y comprueba el último despliegue de Actions. No borres registros DNS o de correo a ciegas.

## Referencias oficiales

- [GitHub Pages: gestionar un dominio personalizado](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [Piensa Solutions: dominios y gestor DNS](https://www.piensasolutions.com/dominios)
