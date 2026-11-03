# Publicar Knonpower IA Remota en GitHub Pages

## 1. Crear repositorio independiente

Con la cuenta `knonpower`, visitar https://github.com/new

- Repository name: `ia-remota`
- Visibility: **Public** (GitHub Pages gratuito en repositorios públicos).
- No marcar README, .gitignore ni licencia: los archivos ya vienen incluidos.
- Elegir **Create repository**.

El repositorio público debe contener **solo esta landing**, nunca el código de laboratorio de IA Remota.

## 2. Subir el proyecto

Descomprimir el ZIP en el computador y abrir terminal en la carpeta `knonpower-ia-remota` (la que contiene README.md).

```bash
git init
git branch -M main
git add .
git status --short
git commit -m "Landing publica IA Remota V1.2"
git remote add origin https://github.com/knonpower/ia-remota.git
git push -u origin main
```

GitHub solicitará autenticación cuando corresponda. Nunca pegar una contraseña o token en un chat.

## 3. Activar GitHub Pages

En https://github.com/knonpower/ia-remota/settings/pages elegir **Source: GitHub Actions**.

En la pestaña **Actions**, comprobar el workflow `Publicar landing aprobada`; si es necesario, ejecutarlo con **Run workflow**. La página se publicará en:

https://knonpower.github.io/ia-remota/

La dirección funcionará únicamente cuando el repositorio exista y el despliegue termine correctamente.

## 4. Actualizaciones

Editar `data/avances.json`, ejecutar:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/package_site.py
```

Revisar `public/index.html` localmente antes de subir cambios:

```bash
git add data/avances.json
git commit -m "Actualizar bitacora publica"
git push
```

El workflow reconstruye el HTML y publica exclusivamente `public/`.

## 5. Notion

La base editorial existe en Notion, pero su sincronización API **no está activada**. Sus registros están inicialmente en borrador, con `Publicar web` desmarcado. No incluir tokens ni dar acceso GitHub a espacios de Notion completos. Consultar README.md para el procedimiento de importación y revisión manual.

## Precauciones

No subir direcciones de red locales, certificados, claves, tokens, informes de custodia con detalles de seguridad, rutas internas ni repositorios de agentes. La web pública no debe conectarse al servidor o Raspberry Pi de IA Remota. `PRODUCTION=NO_GO` se refiere a IA Remota, no a la publicación de esta landing estática.
