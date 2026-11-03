# Knonpower IA Remota — Landing V1.2

Web estática desacoplada de infraestructura privada, con bitácora controlada. No hospedar sobre HP ProLiant, ESXi, NAS ni Raspberry sin auditoría independiente.

## Usar localmente

```bash
python3 -m unittest discover -s tests -v
python3 scripts/package_site.py
python3 -m http.server 8080 --directory public
```

Abrir `http://localhost:8080`. No requiere paquetes pip o npm. `template.html` + `data/avances.json` generan `index.html`; únicamente `public/` se publica.

## Fuente editorial de Notion

Base editorial creada en Notion dentro de *Knonpower Web — Plataforma Digital V1.0*:

- Página: https://app.notion.com/p/305064bed2c743bca5c8ab820496e5b2
- ID de **data source**: `ee73960b-e8e9-423f-a426-7ad19cf02f7b`
- Propiedades: `Titulo`, `Fecha`, `Resumen publico`, `Publicar web`, `Revision editorial`, `Estado`, `Referencia publica`.
- Cuatro hitos de ejemplo fueron creados como **Borrador**, `Publicar web` desactivado.

Para conectar la API oficial de Notion, crear una integración con capacidad **Read content**, compartir únicamente la base editorial y configurar en una consola local segura:

```bash
export NOTION_TOKEN='valor-privado-de-integracion'
export NOTION_PUBLIC_DATA_SOURCE_ID='ee73960b-e8e9-423f-a426-7ad19cf02f7b'
python3 scripts/sync_notion.py
```

El script usa `Notion-Version: 2025-09-03` y `POST /v1/data_sources/{id}/query`, y solo incluye filas con **Revision editorial = Aprobado** y **Publicar web = marcado**. Genera `data/notion-revision.json` (ignorado por Git) para revisión manual. **No modifica `avances.json`, no despliega ni publica automáticamente.** Revisar textos para secretos, direcciones y datos sensibles. Después de revisión, copiar únicamente hitos autorizados a `data/avances.json` y ejecutar pruebas + `package_site.py`.

Los hitos ya visibles en `avances.json` proceden de un resumen editorial previo; **no están sincronizados** con la nueva base de Notion.

## GitHub Pages, al autorizar publicación

1. Crear repositorio público *exclusivo para la web*, nunca reutilizar el repositorio privado de IA Remota.
2. Subir este proyecto sin tokens ni archivos `data/notion-revision.json`.
3. En el repositorio: Settings → Pages → Source: **GitHub Actions**.
4. Al enviar cambios a `main` o ejecutar el workflow manual, `pages.yml` valida pruebas, genera `public/` y publica exclusivamente esa carpeta. No necesita secretos Notion en GitHub.
5. Revisar URL publicada y contenido; añadir dominio personalizado solo si se controla su DNS.

## Restricciones

- `PRODUCTION=NO_GO` para IA Remota; ningún agente conectado a esta web pública.
- No mostrar direcciones LAN, rutas privadas, credenciales, logs, certificados ni firmas.
- No sumar conteos de regresiones diferentes, ni declarar laboratorio como producción.
- No enlazar a páginas Notion internas: si se desea documentación pública, crear una página separada y autorizar explícitamente su publicación en Notion.
