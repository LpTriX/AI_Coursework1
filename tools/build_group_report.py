"""Compile the editable Group 38 LaTeX report, updating cover metadata only."""
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT/'reports/group38-latex'
OUT = ROOT/'output/pdf/OUC_CW_1_38_DRAFT.pdf'

def escape(value):
    chars = {'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$',
             '#':r'\#','_':r'\_','{':r'\{','}':r'\}',
             '~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(chars.get(c,c) for c in value)

def main():
    config=json.loads((ROOT/'reports/group38.json').read_text())
    rows=[escape(m['name'])+' & '+escape(m['student_id'] or 'PENDING')+' & '+
          escape(m['hwu_username'] or 'PENDING')+r'\\' for m in config['members']]
    video=config['video_url'].strip()
    link=(r'\url{'+video+'}') if video else 'PENDING - both members must present; maximum eight minutes.'
    metadata=[r'\newcommand{\GroupName}{'+escape(config['group'])+'}',
              r'\newcommand{\MemberRows}{'+'\n'.join(rows)+'}',
              r'\newcommand{\VideoLink}{'+link+'}',
              r'\newcommand{\ReportStatus}{'+('REVIEW DRAFT' if video else 'DRAFT - video link pending')+'}']
    (PROJECT/'metadata.tex').write_text('\n'.join(metadata)+'\n')
    build_dir=ROOT/'tmp/pdfs/group38-build';build_dir.mkdir(parents=True,exist_ok=True)
    for _ in range(2):
        result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',
                               '-output-directory',str(build_dir),'main.tex'],
                              cwd=PROJECT,text=True,capture_output=True)
        if result.returncode:raise RuntimeError(result.stdout[-4500:])
    log=(build_dir/'main.log').read_text()
    bad=[line for line in log.splitlines() if 'Overfull' in line or 'undefined references' in line]
    if bad:raise RuntimeError('\n'.join(bad))
    aux=(build_dir/'main.aux').read_text()
    def page(label):
        match=re.search(r'\\newlabel\{'+re.escape(label)+r'\}\{\{[^}]*\}\{(\d+)\}',aux)
        if not match:raise RuntimeError('Missing page boundary: '+label)
        return int(match.group(1))
    part1=page('part2-start')-page('part1-start')
    part2=page('references-start')-page('part2-start')
    if not (0<part1<=4 and 0<part2<=3):
        raise RuntimeError(f'Page limits exceeded: Part 1={part1}, Part 2={part2}')
    print(f'Page check: Part 1={part1}/4; Part 2={part2}/3.')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(build_dir/'main.pdf',OUT)
    print(OUT)
    print('Editable report source retained; cover metadata loaded from reports/group38.json.')

if __name__=='__main__':main()
