#!/usr/bin/env python3
"""Genera la landing exclusivamente desde datos aprobados (stdlib Python)."""
import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'avances.json'
PROJECTS = ROOT / 'data' / 'proyectos.json'
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
    progress=data['progreso']['criterios']
    assert len(progress) == 8, 'El indicador necesita ocho criterios'
    assert len({x['nombre'] for x in progress}) == len(progress), 'Criterios duplicados'
    assert all(x['estado'] in ('completado','en_curso','pendiente') for x in progress)
    return date

def render_sections(data):
    cut = data['corte_pruebas']
    milestones=data['progreso']['criterios']
    done=sum(x['estado']=='completado' for x in milestones)
    total=len(milestones)
    percent=round(done*100/total)
    status_labels={'completado':('✓',''),'en_curso':('◐','wait'),'pendiente':('○','future')}
    progress_rows=''.join(f'<li><span class="symbol {status_labels[x["estado"]][1]}" aria-hidden="true">{status_labels[x["estado"]][0]}</span><span>{esc(x["nombre"])}</span></li>' for x in milestones)
    progress_block=f'''<div class="progress-layout"><div class="progress-panel"><div class="progress-head"><strong>Avance de hitos verificables</strong><span class="status pending">Laboratorio · NO_GO producción</span></div><div class="progress-value">{percent}%</div><strong>{done} de {total} hitos completados</strong><div class="progress-track" role="progressbar" aria-valuenow="{percent}" aria-valuemin="0" aria-valuemax="100" aria-label="Porcentaje de hitos de validación completados"><div class="progress-fill" style="width:{percent}%"></div></div><p class="small">{esc(data['progreso']['nota'])}</p><div class="progress-legend"><span><b>✓</b> Validado</span><span><b>◐</b> En proceso</span><span><b>○</b> Pendiente</span></div></div><div class="progress-panel"><h3 style="margin-top:0">¿Qué falta para terminar esta etapa?</h3><ul class="milestone-list">{progress_rows}</ul></div></div>'''
    metrics = f'''<section id="avances"><div class="wrap"><div class="kicker">03 / Avances comprobados</div><h2 class="section-title">El progreso se demuestra con pruebas.</h2><p class="section-intro">Resultados fechados y acotados. El porcentaje representa el cumplimiento de criterios públicos, no la finalización de la plataforma.</p>{progress_block}<div class="cards" style="margin-top:22px">
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
    return metrics,timeline,roadmap

def render_projects(data):
    assert isinstance(data.get('proyectos'), list) and data['proyectos'], 'Sin proyectos'
    ids = set()
    cards = []
    for item in data['proyectos']:
        for key in ('id', 'icono', 'nombre', 'categoria', 'estado', 'descripcion', 'detalle'):
            assert isinstance(item.get(key), str) and item[key].strip(), f'Campo de proyecto inválido: {key}'
        assert item['id'] not in ids, 'Proyecto duplicado'
        ids.add(item['id'])
        links=item.get('enlaces',[])
        assert isinstance(links,list)
        buttons=[]
        for link in links:
            assert isinstance(link,dict) and link.get('url','').startswith('https://')
            assert '"' not in link['url'] and '<' not in link['url']
            buttons.append(f'<a class="project-link" href="{esc(link["url"])}" target="_blank" rel="noopener noreferrer">{esc(link["texto"])} ↗</a>')
        if not buttons:
            buttons.append('<span class="project-unavailable">Redes sociales: enlaces oficiales por confirmar</span>')
        cards.append(f'''<article class="card portfolio-card" id="proyecto-{esc(item['id'])}"><div class="project-top"><span class="project-symbol" aria-hidden="true">{esc(item['icono'])}</span><span class="status {'pending' if item['estado'] in ('Planificación','Laboratorio') else ''}">{esc(item['estado'])}</span></div><div class="project-category">{esc(item['categoria'])}</div><h3>{esc(item['nombre'])}</h3><p class="project-summary">{esc(item['descripcion'])}</p><p class="project-detail">{esc(item['detalle'])}</p><div class="project-cta">{''.join(buttons)}</div></article>''')
    return ('<section id="mis-proyectos"><div class="wrap"><div class="kicker">06 / Ecosistema Knonpower</div>'
            '<h2 class="section-title">Mis proyectos, de un vistazo.</h2>'
            '<p class="section-intro portfolio-lead">Descubre en qué trabajo, qué resuelve cada iniciativa y dónde puedes seguirla. Los enlaces sociales aparecen solo cuando están confirmados.</p>'
            '<div class="cards">'+''.join(cards)+'</div><p class="portfolio-note">'+esc(data['exploracion'])+'</p></div></section>')

def main():
    data=json.loads(DATA.read_text(encoding='utf-8'))
    projects=json.loads(PROJECTS.read_text(encoding='utf-8'))
    validate(data)
    page=TEMPLATE.read_text(encoding='utf-8')
    assert page.count('{{SECCION_AVANCES}}') == 1 and page.count('{{SECCION_BITACORA}}') == 1 and page.count('{{SECCION_FUTURO}}') == 1
    assert page.count('{{SECCION_PROYECTOS}}') == 1
    metrics,timeline,roadmap=render_sections(data)
    completed=sum(x['estado']=='completado' for x in data['progreso']['criterios'])
    pct=round(completed*100/len(data['progreso']['criterios']))
    page=(page.replace('{{PROGRESO_PORCENTAJE}}',f'{pct}%').replace('{{SECCION_AVANCES}}',metrics).replace('{{SECCION_BITACORA}}',timeline).replace('{{SECCION_FUTURO}}',roadmap).replace('{{SECCION_PROYECTOS}}',render_projects(projects)).replace('{{FECHA_ACTUALIZACION}}',esc(display_date(data['actualizado']))))
    assert '{{' not in page, 'Placeholder sin sustituir'
    OUTPUT.write_text(page,encoding='utf-8')
    print(f'BUILD_OK={OUTPUT} HITOS={len(data["hitos"])}')

if __name__ == '__main__':
    main()
