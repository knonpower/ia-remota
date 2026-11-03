#!/usr/bin/env python3
"""Genera la landing exclusivamente desde datos aprobados (stdlib Python)."""
import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'avances.json'
TEMPLATE = ROOT / 'template.html'
OUTPUT = ROOT / 'index.html'

MONTHS = ('enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre').split()

def esc(value):
    return html.escape(str(value), quote=True)

def as_date(value):
    return dt.date.fromisoformat(value)

def display_date(value):
    d = as_date(value)
    return f'{d.day} de {MONTHS[d.month-1]} de {d.year}'

def validate(data):
    date = as_date(data['actualizado'])
    cut = data['corte_pruebas']
    as_date(cut['fecha'])
    assert sum(cut[k] for k in ('pass', 'fail', 'error', 'skip')) == cut['total'], 'Conteo de regresión inconsistente'
    assert all(isinstance(cut[k], int) and cut[k] >= 0 for k in ('total', 'pass', 'fail', 'error', 'skip'))
    ids = set()
    for item in data['hitos']:
        as_date(item['fecha'])
        assert item['id'] not in ids, 'ID repetido'
        ids.add(item['id'])
        for key in ('titulo','resumen','estado'):
            assert isinstance(item[key], str) and item[key].strip()
    for item in data['pendientes']:
        assert item['titulo'].strip() and item['detalle'].strip()
    return date

def render_sections(data):
    cut = data['corte_pruebas']
    metrics = f'''<section id="avances"><div class="wrap"><div class="kicker">03 / Avances comprobados</div><h2 class="section-title">El progreso se demuestra con pruebas.</h2><p class="section-intro">Resultados fechados y acotados. No son un porcentaje global de avance.</p><div class="cards">
<article class="card"><div class="metric">{cut['pass']}</div><h3>Pruebas PASS</h3><p>{cut['total']} pruebas · {cut['fail']} FAIL · {cut['error']} ERROR · {cut['skip']} SKIP.</p><p class="small">Corte: {esc(display_date(cut['fecha']))}</p></article>
<article class="card"><div class="metric">F2 / F3</div><h3>Recuperación y admisión</h3><p>Autenticación, IPC, reintentos y deduplicación validados en alcances concretos de laboratorio.</p><p class="small">No equivale a certificación completa E2E.</p></article>
<article class="card"><div class="metric">NO_GO</div><h3>Producción protegida</h3><p>Despliegue y ejecución autónoma no habilitados. Pruebas aisladas y autorización por operación.</p><p class="small">Estado de laboratorio</p></article></div><div class="disclaimer"><strong>Alcance:</strong> {esc(cut['descripcion'])} Otras corridas pueden tener resultados distintos y no se suman aquí.</div></div></section>'''
    events=[]
    for item in sorted(data['hitos'], key=lambda i: i['fecha']):
        events.append(f'''<article class="event"><time datetime="{esc(item['fecha'])}">{esc(display_date(item['fecha']))}</time><h3>{esc(item['titulo'])}</h3><p>{esc(item['resumen'])}</p><span class="event-status">{esc(item['estado'])}</span></article>''')
    timeline = '<section id="bitacora"><div class="wrap"><div class="kicker">04 / Bitácora pública</div><h2 class="section-title">Construcción paso a paso.</h2><p class="section-intro">Resumen editorial de hitos revisados para publicación, no acceso directo a Notion privado.</p><div class="timeline">'+''.join(events)+'</div></div></section>'
    steps=[]
    for idx,item in enumerate(data['pendientes'],1):
        steps.append(f'''<div class="step"><b>{idx:02d}</b><div><strong>{esc(item['titulo'])}</strong><p>{esc(item['detalle'])}</p></div></div>''')
    roadmap='<section id="futuro"><div class="wrap"><div class="kicker">05 / Siguientes hitos</div><h2 class="section-title">Lo que todavía falta construir.</h2><div class="roadmap">'+''.join(steps)+'</div></div></section>'
    return '\n'.join((metrics,timeline,roadmap))

def main():
    data=json.loads(DATA.read_text(encoding='utf-8'))
    validate(data)
    page=TEMPLATE.read_text(encoding='utf-8')
    assert page.count('{{SECCIONES_ACTUALIZABLES}}') == 1
    page=page.replace('{{SECCIONES_ACTUALIZABLES}}',render_sections(data)).replace('{{FECHA_ACTUALIZACION}}',esc(display_date(data['actualizado'])))
    assert '{{' not in page, 'Placeholder sin sustituir'
    OUTPUT.write_text(page,encoding='utf-8')
    print(f'BUILD_OK={OUTPUT} HITOS={len(data["hitos"])}')

if __name__ == '__main__':
    main()
