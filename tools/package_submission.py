"""Assemble a review ZIP, or check whether release metadata is complete."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PDDL = ['PartA&B/domain.pddl', 'PartA&B/mission1.pddl', 'PartA&B/mission2.pddl',
        'PartC/domain-ext.pddl', 'PartC/mission3.pddl']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', action='store_true', help='build an explicitly incomplete review ZIP')
    args = parser.parse_args()
    config = json.loads((ROOT/'reports/group38.json').read_text())
    missing = [f"{member['name']}: {field}" for member in config['members']
               for field in ('student_id','hwu_username') if not member[field].strip()]
    if not config['video_url'].strip(): missing.append('accessible video URL')
    if not args.draft:
        if missing:
            print('Not ready: ' + '; '.join(missing))
            return 2
        print('Metadata present. Review the PDF, video access and course requirements before final submission.')
        return 0
    files = {'README.md':ROOT/'README.md',
             'OUC_CW_1_38_DRAFT.pdf':ROOT/'output/pdf/OUC_CW_1_38_DRAFT.pdf',
             'requirements-planning.txt':ROOT/'requirements-planning.txt'}
    for name in PDDL: files['PDDL/'+name] = ROOT/'PDDL'/name
    source = ROOT/'reference/part1b'
    for name in ('solver.py','gui.py','benchmark.py','test_solver.py','test_gui.py','README.md'):
        files['Sudoku/'+name] = source/name
    for subdir in ('puzzles','results','tools'):
        for path in (source/subdir).rglob('*'):
            if path.is_file() and path.suffix not in ('.pyc',) and '__pycache__' not in path.parts:
                files['Sudoku/'+path.relative_to(source).as_posix()] = path
    for name in ('validate_base.py','validate_extension.py'):
        files['tools/'+name] = ROOT/'tools'/name
    for path in (ROOT/'evidence').rglob('*'):
        if path.is_file(): files[path.relative_to(ROOT).as_posix()] = path
    contents = {name:path.read_bytes() for name,path in files.items()}
    package_readme = """# OUC Coursework 1 - Group 38 review package

This is a review draft. Member IDs and HWU usernames are confirmed. The video URL and final review are pending.
Do not upload this archive as a completed submission.

## Sudoku

From the Sudoku directory, with Python 3.9+:

    python3 solver.py puzzles/p2.txt --stats
    python3 gui.py
    python3 -m unittest -v test_solver test_gui

The solver uses the standard library. The GUI requires a working Tk install.
See Sudoku/README.md for input formats and interface behaviour.

## PDDL

From this archive's root:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements-planning.txt
    .venv/bin/python tools/validate_extension.py --output validation-output

The PDDL directory retains the required starter paths and contains five files.
Evidence and Sudoku/results retain actual plans and measured data.

"""
    contents['README.md'] = package_readme.encode()
    manifest = {name:hashlib.sha256(data).hexdigest() for name,data in contents.items()}
    out = ROOT/'output/F29AI CW1 OUC 38 DRAFT.zip'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,data in sorted(contents.items()): archive.writestr(name,data)
        archive.writestr('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
        archive.writestr('REVIEW_STATUS.txt','REVIEW DRAFT - NOT READY FOR SUBMISSION\nMissing: '+ '; '.join(missing)+'\nReview the report, video link and package contents.\n')
    with zipfile.ZipFile(out) as archive, tempfile.TemporaryDirectory() as directory:
        assert archive.testzip() is None
        names = archive.namelist()
        assert sorted(n for n in names if n.endswith('.pddl')) == sorted('PDDL/'+p for p in PDDL)
        assert not any(n.endswith(('.mp4','.mov','.mkv')) or '.git/' in n or '.venv/' in n for n in names)
        archive.extractall(directory)
        for name,expected in manifest.items():
            assert hashlib.sha256((Path(directory)/name).read_bytes()).hexdigest()==expected
    print(f'{out}\nVerified {len(contents)} files; exactly five PDDL files; no video or Git history.\nMissing: '+ '; '.join(missing))
    return 0

if __name__ == '__main__': raise SystemExit(main())
