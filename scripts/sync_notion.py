#!/usr/bin/env python3
"""Importa SOLO candidatos de una base editorial autorizada. Nunca publica."""
import datetime as dt
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'notion-revision.json'
VERSION = '2025-09-03'
SAFE_ID = re.compile(r'^[0-9a-fA-F-]{32,36}$')
# Indicadores de datos internos: defensa adicional, no reemplaza revisión humana.
SENSITIVE = re.compile(r'(?i)(?:\b(?:10|127|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b|/home/|/srv/|/opt/|\b(?:token|password|secret|bearer|api[_ -]?key|ssh-rsa|private key)\b|\b[A-Fa-f0-9]{40,}\b)')


def prop_text(row, key):
    p = row.get('properties', {}).get(key, {})
    values = p.get('title', []) if p.get('type') == 'title' else p.get('rich_text', [])
    return ''.join(x.get('plain_text', '') for x in values).strip()


def candidate(row):
    p = row.get('properties', {})
    if p.get('Publicar web', {}).get('checkbox') is not True:
        return None
    if (p.get('Revision editorial', {}).get('select') or {}).get('name') != 'Aprobado':
        return None
    title, summary = prop_text(row, 'Titulo'), prop_text(row, 'Resumen publico')
    date = (p.get('Fecha', {}).get('date') or {}).get('start', '')
    if not title or not summary or not date or len(title) > 140 or len(summary) > 600:
        return None
    if SENSITIVE.search(title + '\n' + summary):
        raise ValueError('Posible dato sensible en una fila aprobada: revisar Notion antes de importar')
    day = dt.date.fromisoformat(date[:10]).isoformat()
    row_id = row.get('id', '')
    if not SAFE_ID.fullmatch(row_id):
        raise ValueError('ID de página no válido')
    status = (p.get('Estado', {}).get('select') or {}).get('name', 'Documentado')
    if status not in ('Documentado', 'Verificado', 'En integracion'):
        raise ValueError('Estado no permitido')
    return {'id': 'notion-' + row_id.replace('-', ''), 'fecha': day, 'titulo': title,
            'resumen': summary, 'estado': status}


def fetch(token, source):
    if not SAFE_ID.fullmatch(source):
        raise ValueError('NOTION_PUBLIC_DATA_SOURCE_ID inválido')
    url = f'https://api.notion.com/v1/data_sources/{source}/query'
    cursor = None
    items = []
    for _ in range(30):
        payload = {'page_size': 100}
        if cursor:
            payload['start_cursor'] = cursor
        request = Request(url, data=json.dumps(payload).encode(), method='POST', headers={
            'Authorization': f'Bearer {token}', 'Notion-Version': VERSION,
            'Content-Type': 'application/json', 'User-Agent': 'Knonpower-Editorial-Sync/1.2'})
        with urlopen(request, timeout=20) as resp:
            data = json.load(resp)
        items.extend(data['results'])
        if not data.get('has_more'):
            return items
        cursor = data.get('next_cursor')
        if not cursor:
            raise ValueError('Paginación incompleta')
    raise ValueError('Más de 3000 filas: se requiere revisión')


def write_candidates(items, target=OUT):
    content = {'nota': 'CANDIDATOS SIN PUBLICAR. Revisar manualmente antes de copiar a avances.json',
               'hitos': [c for row in items if (c := candidate(row)) is not None]}
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix='.revision-', suffix='.json')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as file:
            json.dump(content, file, indent=2, ensure_ascii=False)
            file.write('\n')
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return len(content['hitos'])


def main():
    token = os.getenv('NOTION_TOKEN')
    source = os.getenv('NOTION_PUBLIC_DATA_SOURCE_ID')
    if not token or not source:
        raise SystemExit('Faltan NOTION_TOKEN y/o NOTION_PUBLIC_DATA_SOURCE_ID. No se ha modificado la web.')
    total = write_candidates(fetch(token, source))
    print(f'NOTION_CANDIDATOS={total} REVISION={OUT} WEB_SIN_CAMBIOS=true')


if __name__ == '__main__':
    main()
