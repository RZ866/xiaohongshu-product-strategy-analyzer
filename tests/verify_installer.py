"""Run actual official installer with local ZIP download substitution, no network."""
import argparse,importlib.util,subprocess,sys,tempfile
from pathlib import Path

def run(installer,package):
    installer=Path(installer);sys.path.insert(0,str(installer.parent))
    spec=importlib.util.spec_from_file_location('official_installer',installer)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    requested=[]
    def local(url): requested.append(url);return Path(package).read_bytes()
    module._request=local;name='xiaohongshu-product-strategy-analyzer'
    with tempfile.TemporaryDirectory(prefix='product-skill-install-') as tmp:
        args=['--url','https://github.com/example-owner/'+name,'--path','.','--name',name,'--method','download','--dest',tmp]
        assert module.main(args)==0
        installed=Path(tmp)/name
        for p in ['SKILL.md','scripts/engine.py','assets/report.html','references/report-contract.md']: assert (installed/p).is_file()
        assert not (installed/'.qa').exists()
        assert requested==['https://codeload.github.com/example-owner/'+name+'/zip/main']
        dest=Path(tmp)/'generated'
        subprocess.run([sys.executable,'scripts/generate_report.py','examples/positive/input.json','--output',str(dest)],cwd=installed,check=True,capture_output=True)
        assert (dest/'xiaohongshu-product-strategy-report.html').exists()
        assert (dest/'data-record.csv').exists()
        assert module.main(args)==1  # Intentional duplicate destination rejection.
    print('PASS official installer: local ZIP substitution, root path, copy, installed rendering, duplicate guard. NOT a live GitHub test.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--installer',required=True);p.add_argument('--package',required=True)
    args=p.parse_args();run(args.installer,args.package)
