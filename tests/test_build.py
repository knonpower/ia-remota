import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(path):
    spec=importlib.util.spec_from_file_location(path.stem,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

build=load(ROOT/'scripts/build.py')
notion=load(ROOT/'scripts/sync_notion.py')

class BuildTests(unittest.TestCase):
    def test_existing_data_validates(self):
        data=json.loads((ROOT/'data/avances.json').read_text())
        build.validate(data)
        sections=''.join(build.render_sections(data))
        self.assertIn(str(data['corte_pruebas']['pass']),sections)
        self.assertIn('NO_GO',sections)
    def test_failed_totals_rejected(self):
        data=json.loads((ROOT/'data/avances.json').read_text())
        data['corte_pruebas']['pass']=100
        with self.assertRaises(AssertionError):build.validate(data)
    def test_html_escaped(self):
        data=json.loads((ROOT/'data/avances.json').read_text())
        data['hitos'][0]['titulo']='<script>alert(1)</script>'
        html=''.join(build.render_sections(data))
        self.assertNotIn('<script>',html)
        self.assertIn('&lt;script&gt;',html)
    def test_notion_requires_two_gates(self):
        row={'id':'40d2a42d-216e-812b-aa93-ec0e70f8bbab','properties':{'Publicar web':{'checkbox':True},'Revision editorial':{'select':{'name':'Aprobado'}},'Titulo':{'type':'title','title':[{'plain_text':'Hito'}]},'Resumen publico':{'type':'rich_text','rich_text':[{'plain_text':'Prueba válida'}]},'Fecha':{'date':{'start':'2026-11-03'}}}}
        self.assertEqual(notion.candidate(row)['titulo'],'Hito')
        row['properties']['Publicar web']['checkbox']=False
        self.assertIsNone(notion.candidate(row))
        row['properties']['Publicar web']['checkbox']=True
        row['properties']['Revision editorial']['select']['name']='Borrador'
        self.assertIsNone(notion.candidate(row))

if __name__=='__main__':unittest.main()

class TestNotionEditorial(unittest.TestCase):
    def test_approval_required(self):
        from scripts.sync_notion import candidate
        row = {'id':'40d2a42d-216e-812b-aa93-ec0e70f8bbab', 'properties': {
            'Titulo': {'type':'title','title':[{'plain_text':'Prueba técnica'}]},
            'Resumen publico': {'type':'rich_text','rich_text':[{'plain_text':'Resultado controlado.'}]},
            'Fecha':{'date':{'start':'2026-11-03'}},
            'Revision editorial':{'select':{'name':'Borrador'}},
            'Publicar web':{'checkbox':True},
            'Estado':{'select':{'name':'Verificado'}}}}
        self.assertIsNone(candidate(row))
        row['properties']['Revision editorial']['select']['name'] = 'Aprobado'
        row['properties']['Publicar web']['checkbox'] = False
        self.assertIsNone(candidate(row))
        row['properties']['Publicar web']['checkbox'] = True
        self.assertEqual(candidate(row)['estado'],'Verificado')

    def test_sensitive_text_denied(self):
        from scripts.sync_notion import candidate
        row = {'id':'40d2a42d-216e-812b-aa93-ec0e70f8bbab', 'properties': {
            'Titulo': {'type':'title','title':[{'plain_text':'Servidor 192.168.1.83'}]},
            'Resumen publico': {'type':'rich_text','rich_text':[{'plain_text':'Prueba'}]},
            'Fecha':{'date':{'start':'2026-11-03'}},
            'Revision editorial':{'select':{'name':'Aprobado'}},
            'Publicar web':{'checkbox':True}}}
        with self.assertRaises(ValueError): candidate(row)

class PortfolioTests(unittest.TestCase):
    def test_project_section_renders(self):
        data=json.loads((ROOT/'data/proyectos.json').read_text(encoding='utf-8'))
        markup=build.render_projects(data)
        self.assertIn('id="mis-proyectos"',markup)
        for name in ('Super Magic Box','FERO','JoséLuisMetales','Hidrobee','IA Remota'):
            self.assertIn(name,markup)
    def test_portfolio_escapes_markup(self):
        data=json.loads((ROOT/'data/proyectos.json').read_text(encoding='utf-8'))
        data['proyectos'][0]['descripcion']='<script>alert(1)</script>'
        markup=build.render_projects(data)
        self.assertNotIn('<script>',markup)
        self.assertIn('&lt;script&gt;',markup)
    def test_duplicate_project_rejected(self):
        data=json.loads((ROOT/'data/proyectos.json').read_text(encoding='utf-8'))
        data['proyectos'].append(dict(data['proyectos'][0]))
        with self.assertRaises(AssertionError):build.render_projects(data)
