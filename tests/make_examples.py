import json
import sys
from pathlib import Path
from cases import variants,screenshot_case
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from generate_report import write_outputs

if __name__=='__main__':
    for name,data in variants().items():
        dest=ROOT/'examples'/name; dest.mkdir(parents=True,exist_ok=True)
        (dest/'input.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        result=write_outputs(data,dest,dest)
        print(name,result['decision'])
    (ROOT/'examples/sample-report.html').write_bytes((ROOT/'examples/positive/xiaohongshu-product-strategy-report.html').read_bytes())
    media=ROOT/'examples/media/product-card.png'
    if media.exists():
        d=screenshot_case(); dest=ROOT/'examples/screenshot'; dest.mkdir(exist_ok=True)
        (dest/'product-card.png').write_bytes(media.read_bytes())
        (dest/'input.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
        print('screenshot',write_outputs(d,dest,dest,True)['decision'])
    hostile=variants()['positive']; hostile['product']['name']='<script>window.pwned=1</script>'
    from generate_report import render
    qa=ROOT/'.qa'; qa.mkdir(exist_ok=True)
    (qa/'hostile.html').write_text(render(hostile)[0],encoding='utf-8')
