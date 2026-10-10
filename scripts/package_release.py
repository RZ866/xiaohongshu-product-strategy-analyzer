"""Allowlist-only public package with a limited credential-pattern audit."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]
NAME='xiaohongshu-product-strategy-analyzer'
ROOT_FILES={'SKILL.md','README.md','LICENSE','CHANGELOG.md','VERSION','.gitignore','.gitattributes'}
DIRS={'agents','references','scripts','assets','examples','tests','.github'}
IGNORE={'.git','.qa','outputs','private-inputs','dist','__pycache__','.venv','node_modules'}

def public_files(root=ROOT):
    result=[]
    for p in root.rglob('*'):
        rel=p.relative_to(root)
        if any(x in IGNORE for x in rel.parts) or p.suffix=='.pyc': continue
        if p.is_symlink(): raise ValueError('Public symlink rejected')
        if p.is_file() and (rel.as_posix() in ROOT_FILES or rel.parts[0] in DIRS): result.append(p)
    return sorted(result)

def audit(files,root=ROOT):
    findings=[]
    patterns=[r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'\bghp_[A-Za-z0-9]{30,}',r'\bgithub_pat_[A-Za-z0-9_]{40,}',r'\bsk-(?:proj-)?[A-Za-z0-9_-]{35,}',r'(?i)[A-Z]:[/\\]Users[/\\][^\s/\\]+[/\\]']
    for p in files:
        if p.name.startswith('.env') or p.suffix=='.key': findings.append(p.relative_to(root).as_posix())
        if p.suffix.lower() in ('.png','.jpg','.jpeg','.webp'): continue
        value=p.read_text(encoding='utf-8-sig')
        if any(re.search(pattern,value) for pattern in patterns): findings.append(p.relative_to(root).as_posix())
    return findings

def main():
    files=public_files(); findings=audit(files)
    if findings: raise ValueError('Audit failed in files: '+','.join(findings))
    dest=ROOT/'dist'; dest.mkdir(exist_ok=True)
    path=dest/(NAME+'-v'+(ROOT/'VERSION').read_text().strip()+'.zip')
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files: z.write(p,NAME+'/'+p.relative_to(ROOT).as_posix())
    result={'files':len(files),'findings':findings,'archive':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'Allowlist and credential-pattern scan; not proof of semantic privacy.'}
    (dest/'release-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))

if __name__=='__main__': main()
