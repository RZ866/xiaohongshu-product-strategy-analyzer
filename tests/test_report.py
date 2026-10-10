import copy
import json
import re
from pathlib import Path
import tempfile
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from generate_report import render,write_outputs,REPORT,image_tag
from engine import ValidationError
from cases import case,variants

class ReportTests(unittest.TestCase):
    def test_all_fragment_links_resolve(self):
        for data in (case(),variants()['quick']):
            out,_=render(data)
            ids=set(re.findall(r'id="([^"]+)"',out))
            self.assertTrue(set(re.findall(r'href="#([^"]+)"',out)) <= ids)

    def test_html_complete(self):
        output,r=render(case())
        for sid in ['overview','score','profit','people','scenes','plays','topics','listing','plan','month','metrics','actions','evidence']:
            self.assertIn('id="'+sid+'"',output)
        self.assertIn('8.5',output); self.assertIn('内部研究指标',output)
        self.assertNotIn('{{CONTENT}}',output)

    def test_escaped_input(self):
        data=case(); payload='<script>window.pwned=1</script><img src=x onerror="alert(1)">'
        data['product']['name']=payload; data['summary']['reason']['text']=payload
        data['strategy']['topics'][0]['title']=payload; data['evidence'][0]['excerpt']=payload
        out,_=render(data)
        self.assertNotIn('<script>',out); self.assertNotIn('<img src=x',out)
        self.assertIn('&lt;script&gt;',out)

    def test_evidence_anchor(self):
        out,_=render(case()); self.assertIn('href="#e-P"',out); self.assertIn('id="e-P"',out)

    def test_quick_default_no_html(self):
        with tempfile.TemporaryDirectory() as t:
            write_outputs(variants()['quick'],Path(t),Path(t))
            self.assertFalse((Path(t)/REPORT).exists()); self.assertTrue((Path(t)/'summary.md').exists())

    def test_quick_optional_html(self):
        with tempfile.TemporaryDirectory() as t:
            write_outputs(variants()['quick'],Path(t),Path(t),True)
            self.assertTrue((Path(t)/REPORT).exists()); self.assertFalse((Path(t)/'data-record.csv').exists())

    def test_deep_files_and_gated_json(self):
        with tempfile.TemporaryDirectory() as t:
            write_outputs(variants()['negative'],Path(t),Path(t))
            for f in [REPORT,'summary.md','result.json','handoff.json','data-record.csv']: self.assertTrue((Path(t)/f).exists())
            r=json.loads((Path(t)/'result.json').read_text(encoding='utf-8'))
            self.assertIn('暂停',r['strategy']['days'][5]['steps'])

    def test_invalid_creates_no_report(self):
        with tempfile.TemporaryDirectory() as t:
            data=case(); data['strategy']['topics']=[]
            with self.assertRaises(ValidationError): write_outputs(data,Path(t),Path(t))
            self.assertFalse((Path(t)/REPORT).exists())

    def test_no_remote_assets(self):
        out,_=render(case())
        self.assertNotIn('<script',out); self.assertNotIn('src="http',out); self.assertNotIn('url(http',out)

    def test_image_fallback(self):
        with tempfile.TemporaryDirectory() as t:
            for name in ['https://example.com/x.png','../secret.png','missing.png']:
                self.assertIn('placeholder',image_tag({'image':name},Path(t)))
            (Path(t)/'bad.svg').write_text('<svg onload="alert(1)"/>')
            self.assertIn('placeholder',image_tag({'image':'bad.svg'},Path(t)))

    def test_no_absolute_image_path_in_result(self):
        with tempfile.TemporaryDirectory() as t:
            data=case(); data['product']['image']='unavailable.png'
            write_outputs(data,Path(t),Path(t))
            self.assertNotIn('"image"', (Path(t)/'result.json').read_text(encoding='utf-8'))

    def test_missing_score_no_zero_bar(self):
        out,r=render(variants()['cautious'])
        self.assertIn('竞争与差异化 · 暂无法评分',out); self.assertIsNone(r['total'])

if __name__=='__main__': unittest.main()
