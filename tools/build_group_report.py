"""Build the Group 38 review PDF in the Lab4 single-column LaTeX style.

Requires ReportLab for content assembly and pdflatex for typesetting.
"""
import json
import re
import shutil
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'reports/group38.json'
OUT = ROOT / 'output/pdf/OUC_CW_1_38_DRAFT.pdf'
STYLE = ParagraphStyle('body', fontName='Helvetica', fontSize=11, leading=15, spaceAfter=9)
TITLE = ParagraphStyle('title', parent=STYLE, fontSize=21, leading=26, spaceAfter=16)
HEADING = ParagraphStyle('heading', parent=STYLE, fontSize=14, leading=18, spaceBefore=6, spaceAfter=10)
SMALL = ParagraphStyle('small', parent=STYLE, fontSize=11, leading=14)


def para(text, style=STYLE):
    return Paragraph(escape(text), style)


def table(rows, widths=None):
    data = [[para(str(value), SMALL) for value in row] for row in rows]
    result = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    result.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e9eef4')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,0), (-1,0), 0.6, colors.grey),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    return result


def build():
    config = json.loads(CONFIG.read_text())
    benchmark = [json.loads((ROOT/'reference/part1b/results'/name).read_text())
                 for name in ('benchmark.json', 'benchmark_rowmajor.json')]
    story = []
    sections = []
    def page(title, *paragraphs):
        if story: story.append(PageBreak())
        sections.append(title)
        story.append(para(title, TITLE))
        story.extend(para(text) for text in paragraphs)
    def heading(title, text):
        story.append(para(title, HEADING)); story.append(para(text))

    page('Coursework 1: Search and Automated Planning',
         config['group'], 'REVIEW DRAFT - incomplete member details and video link')
    story.append(table([['Member', 'Student ID', 'HWU username']] +
                       [[m['name'], m['student_id'] or 'PENDING', m['hwu_username'] or 'PENDING']
                        for m in config['members']], [6*cm,5*cm,5*cm]))
    story.append(Spacer(1,18))
    story.append(para('Video demonstration: ' + (config['video_url'] or 'PENDING - both members must present; maximum eight minutes.')))
    heading('Reading guide', 'Part 1 occupies the next three pages; Part 2 occupies the following two pages. '
            'The title page and reference list are outside those limits. Measurements refer to the '
            'saved runs, not a new timing comparison. This draft requires review by both members.')

    page('Part 1A: Sudoku as a CSP',
         'Sudoku has 81 variables X(r,c), one per cell, where r and c range from 1 to 9. '
         'An empty cell has domain {1,...,9}; a given digit fixes its cell to a singleton domain. '
         'Zero denotes an empty input cell and is never a solution value [1-3].',
         'There are 27 AllDifferent constraints: one for each of nine rows, nine columns and '
         'nine 3-by-3 boxes. Together with the domains, these require each unit to contain '
         'every digit exactly once. A completion must preserve all original givens.',
         'Let m be the number of empty cells. Enumerating every digit assignment gives 9^m '
         'complete candidates. Under fixed-size board checking, this yields a coarse O(9^m) '
         'upper bound. The unpruned backtracking tree has at most 1+9+...+9^m nodes and the '
         'same coarse exponential bound. Counting constraint-checking work separately '
         'multiplies this bound by the cost per node. This is a search-size argument for a '
         'fixed 9-by-9 board, not an asymptotic hardness result for fixed-size Sudoku [2,4].',
         'Backtracking rejects a partial assignment as soon as it violates a constraint. '
         'Later assignments cannot remove an existing duplicate, so every extension of '
         'that branch can be skipped. Finding a conflict with k cells unassigned can avoid '
         'up to 9^k complete assignments. Pruning usually reduces practical work but does '
         'not establish a polynomial worst-case running time.',
         'Minimum remaining values (MRV) selects an empty cell with the smallest current '
         'domain [2,4]. The implemented solver recomputes candidates from the current board. '
         'It does not maintain propagated domains or enforce arc consistency. Separating '
         'those techniques matters when explaining where the measured speed differences arise.')

    page('Part 1B: Method and implementation',
         'The Python solver uses depth-first backtracking with MRV. The board is a list of '
         'nine integer lists. solve() validates and copies its input so the caller retains '
         'the original puzzle. TXT and CSV readers accept nine rows with nine digits each; '
         'zero denotes a blank. Malformed input and conflicting givens are rejected.',
         'For each empty cell, candidates() removes all values already present in its row, '
         'column and box from {1,...,9}. At a search node, MRV scans all empty cells. An '
         'empty candidate set immediately rejects the branch; otherwise the smallest '
         'candidate set determines the next cell. Ties use top-to-bottom, left-to-right '
         'order, and candidate digits are tried in ascending order.',
         'An attempted assignment changes one cell. If recursion fails, that cell is reset '
         'to zero before the next digit is tried. No maintained domains need restoring. '
         'A complete board is accepted; exhausting all legal branches reports no solution. '
         'This finite exhaustive search is complete, although difficult inputs can be slow. '
         'A row-major option supplies a controlled variable-ordering comparison.',
         'The CLI returns status 0 for a completion, 1 for no solution and 2 for an input '
         'error. A separate completion counter stops after two solutions when testing '
         'uniqueness; finding one solution alone does not establish uniqueness.')
    heading('Interface additions',
            'The Tkinter interface provides Load, Solve, Reset and Clear. Load preserves '
            'the original puzzle for Reset; Clear removes the board and loaded original. '
            'Given digits are black and added digits blue. Duplicate values are highlighted '
            'in red, and selecting an empty cell displays its current candidates. Candidate '
            'information expresses local legality, not a guarantee of a complete solution. '
            'These additions help explain the model without changing the search. '
            'Search is synchronous, so expensive inputs can temporarily block the window.')
    heading('Correctness checks',
            'Seventeen solver tests cover parsing, malformed/conflicting input, solved '
            'boards, few blanks, several puzzles, no solution, deterministic behaviour, '
            'input preservation and CLI return codes. A separate set-based oracle checks '
            'rows, columns, boxes and givens. Six interface-state checks cover conflict '
            'marking, candidate display, Clear after manual edits and Reset after solving. '
            'The interface tests use widget doubles; native window rendering and event '
            'bindings still need manual demonstration.')

    page('Part 1B: Evaluation and A* analysis',
         'The saved experiment used CPython 3.9.6 on macOS/Darwin 27.0.0 arm64, with five '
         'repetitions per puzzle and ordering, and no warm-up. Timing includes the complete '
         'solve() call, including validation and copying. File reading, earlier validation, '
         'printing and independent solution checks are excluded. The five inputs were '
         'constructed locally; no external difficulty labels are claimed.')
    rows = [['Puzzle / ordering', 'Median ms', 'Nodes', 'Backtracks']]
    for data in benchmark:
        for case in data['cases']:
            if data['cell_order']=='row-major' and case['puzzle'] not in ('p1.txt','p2.txt'): continue
            stats=case['runs'][0]['stats']
            rows.append([case['puzzle']+' / '+data['cell_order'],
                         f"{case['summary']['median_seconds']*1000:.3f}",
                         str(stats['nodes']),str(stats['backtracks'])])
    story.append(table(rows,[7*cm,3*cm,3*cm,3*cm]));story.append(Spacer(1,8))
    story.append(para('Nodes count search calls; backtracks count failed placements undone. '
                      'On p2, MRV visits 594 nodes versus 349,303 for row-major and is about '
                      '37 times faster in these runs. On p1, row-major is faster despite '
                      'more nodes: MRV candidate scans have overhead. These two examples '
                      'do not establish general superiority. The no-solution case fails '
                      'immediately and does not test deep unsatisfiable search.'))
    heading('Theoretical A* formulation',
            'A state is a consistent partial board. An action assigns one legal digit to '
            'one blank cell at unit cost; a goal is a full valid board. Let h be the number '
            'of remaining blanks. It is admissible and consistent: any completion requires '
            'exactly one action per remaining blank. With m initial blanks, g+h=m at every '
            'reachable state. Thus f cannot distinguish branches, and expansion order '
            'depends on tie-breaking. FIFO tie-breaking behaves breadth first and retains '
            'an unexpanded frontier that can require exponential memory; depth-first '
            'backtracking retains a path. No A* implementation or performance measurement '
            'is claimed. Forward checking, AC-3 and exact-cover search are possible '
            'alternatives [2,4], but their performance was not measured here.')

    page('Part 2A/B: Domain and mission design',
         'The reusable lunar domain uses STRIPS and typing [1,5]. Types are rover, lander '
         'and waypoint. belongs-to assigns each rover to one lander; lander-at fixes a '
         'landing site; connected represents a directed road. aboard represents an '
         'undeployed rover, while rover-at gives a deployed rover position. Actions use '
         'parameters, rather than hard-coded rover, lander or waypoint identifiers.',
         'Deployment removes aboard and places the rover at its own lander site. Movement '
         'requires an existing directed edge and replaces the old rover position. A '
         'lander never moves after landing. Well-formed initial ownership and locations '
         'are assumed. Single arrows in the supplied maps are not made bidirectional.',
         'One shared memory-free token prevents carrying two unsent data items: taking '
         'either an image or scan consumes it. Sending requires the corresponding held '
         'data, rover ownership and current position, restores the token and records '
         'image-saved or scan-saved at the receiving lander. Sending is wireless; rover '
         'and lander do not need to share a waypoint.',
         'A separate sample-free token permits at most one carried sample, independently '
         'of data memory. A sample goal is achieved only by store-sample, requiring the '
         'rover at its own lander. Storage consumes the lander storage-free token and '
         'restores the rover sample slot. No action restores lander storage, so each '
         'lander can store at most one sample.')
    heading('Mission configuration',
            'Mission 1 fixes Lander 1 at WP1 with Rover 1 aboard and uses the six directed '
            'edges of Figure 2. It saves the WP5 image and WP3 scan at Lander 1 and stores '
            'the WP1 sample there. Mission 2 starts Rover 1 deployed at WP2 with Lander 1; '
            'Lander 2 is fixed at WP1 with Rover 2 aboard. Its nine directed edges follow '
            'Figure 3. Lander 1 receives the WP3 image, WP6 scan and WP5 sample; Lander 2 '
            'receives the WP2 image, WP4 scan and WP1 sample. Choosing WP1 for Lander 2 '
            'is permitted by the specification.')
    heading('Base validation',
            'Pyperplan 2.1 with greedy best-first search and hFF found plans of 10 and '
            '20 actions for Missions 1 and 2. Each was independently replayed against '
            'the specification rules. Saved base checks compared 2,496 typed action '
            'instances in 16 coherent states. A renamed three-rover instance produced '
            'a valid 23-action plan. These are targeted tests, not exhaustive proofs '
            'or claims of shortest plans.')

    page('Part 2C: Astronaut extension',
         'The extended domain adds astronaut and room types. astronaut-belongs-to assigns '
         'an astronaut to a lander; room-of records room ownership. docking-bay and '
         'control-room classify rooms, room-connected describes internal links, and '
         'astronaut-at records the current room. Every lander has distinct docking and '
         'control rooms, connected in both directions.',
         'The move-astronaut action requires the astronaut at the source, a connecting '
         'edge and both rooms belonging to that astronaut\'s lander. It deletes the old '
         'location and adds the new one. Even a supplied cross-lander adjacency cannot '
         'permit movement into another lander because room ownership is also checked.',
         'Deployment and sample storage require an astronaut in the receiving lander\'s '
         'docking bay. Both data-transmission actions require an astronaut in its control '
         'room. The added astronaut and room parameters are checked for ownership, room '
         'role and current presence. Existing rover movement, acquisition, memory and '
         'sample rules remain unchanged; no astronaut is needed simply to drive or '
         'acquire data.',
         'Mission 3 preserves Mission 2\'s map, rover/lander setup and all six goals. '
         'Alice belongs to Lander 1 and starts in its docking bay; Bob belongs to Lander '
         '2 and starts in its control room. The unchanged base setup and required '
         'astronaut facts are verified by the validation tool.')
    heading('How the extension changes the plan',
            'The saved 24-action plan contains four astronaut moves. Bob first moves '
            'from control room to docking bay, permitting deployment and later sample '
            'storage, then returns to the control room for transmissions. Alice moves '
            'from docking bay to control room to permit transmissions, then returns '
            'to the docking bay before sample storage. Each dependent action is checked '
            'against the corresponding lander and room state; astronaut location '
            'therefore changes applicability rather than serving as a decorative fact.')
    heading('Extension validation and limits',
            'All three missions plan and independently replay successfully. In 23 '
            'constructed coherent states, 24,380 typed action instances were checked: '
            '180 allowed instances had the expected effects and 24,200 forbidden '
            'instances were rejected. Cases include wrong astronauts, room types, '
            'cross-lander movement, co-located landers and inherited capacity rules. '
            'Both astronauts move in Mission 3 and every restricted action has a '
            'matching astronaut and room. These checks assume valid initial states '
            'and do not explore every reachable state.')

    page('References',
         '[1] F29AI teaching team. Coursework 1: Search and Automated Planning. 2026. '
         'Supplied coursework specification, especially pp. 2, 4-10 and 12-17.',
         '[2] Russell, S. and Norvig, P. Constraint Satisfaction Problems. AIMA teaching '
         'slides, public file labelled Chapter 5. '
         'https://aima.cs.berkeley.edu/4th-ed/slides-pdf/chapter05.pdf',
         '[3] UC Berkeley CS188. 2.1 Constraint Satisfaction Problems. '
         'https://inst.eecs.berkeley.edu/~cs188/textbook/csp/csps.html',
         '[4] UC Berkeley CS188. 2.2 Solving Constraint Satisfaction Problems. '
         'https://inst.eecs.berkeley.edu/~cs188/textbook/csp/solving.html',
         '[5] Pyperplan contributors. Pyperplan, version 2.1. '
         'https://github.com/aibasel/pyperplan',
         'Experiment sources: reference/part1b/results/benchmark.json and '
         'benchmark_rowmajor.json. Planning sources: evidence/base-pddl/ and '
         'evidence/part2c/. The repository retains raw plans, traces, source hashes '
         'and measurement conditions. The reference entries were retained from '
         'the existing contribution draft; no new access date is asserted.')

    write_lab_style(story, config)
    print(OUT)


def tex_escape(text):
    symbols = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
               '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
               '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    formulas = {'X(r,c)': r'$X_{r,c}$', '{1,...,9}': r'$\{1,\ldots,9\}$',
                '1+9+...+9^m': r'$1+9+\cdots+9^m$', 'O(9^m)': r'$O(9^m)$',
                '9^m': r'$9^m$', '9^k': r'$9^k$', 'g+h=m': r'$g+h=m$'}
    token_pattern = '|'.join(re.escape(token) for token in sorted(formulas,key=len,reverse=True))
    parts = re.split(r'(https?://\S+|' + token_pattern + ')', text)
    return ''.join(r'\url{'+part+'}' if part.startswith(('https://','http://'))
                   else formulas[part] if part in formulas
                   else ''.join(symbols.get(c,c) for c in part) for part in parts)


def write_lab_style(story, config):
    """Retain the report text while applying the single-column Lab4 style."""
    project = ROOT/'reports/group38-latex'
    lines = [r"""\documentclass[11pt,a4paper]{article}
\usepackage[a4paper,left=20mm,right=20mm,top=20mm,bottom=20mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,amsmath,amssymb,booktabs,array,tabularx,fancyhdr}
\usepackage[british]{babel}
\usepackage[hidelinks]{hyperref}
\hypersetup{pdftitle={OUC CW 1 38 - review draft},pdfauthor={Pinxin Liu and Chengtian Gong}}
\usepackage{caption,float,microtype}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\captionsetup{font=normalsize,labelfont=bf}
\setlength{\parindent}{0pt}
\setlength{\parskip}{.45em}
\setlength{\headheight}{14pt}
\setlength{\emergencystretch}{2em}
\renewcommand{\arraystretch}{1.18}
\pagestyle{fancy}\fancyhf{}
\fancyhead[C]{\small F29AI Coursework 1\quad OUC Group 38}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\title{Coursework 1 Report\\Search and Automated Planning}
"""]
    names = r'\quad '.join(tex_escape(member['name']) for member in config['members'])
    date = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%d %B %Y')
    lines += [r'\author{'+names+r'\\OUC CW 1 38}',r'\date{Report date: '+date+'}',
              r'\begin{document}',r'\pagenumbering{roman}',r'\begin{titlepage}',r'\maketitle\thispagestyle{plain}']
    cover = True
    skip_group = True
    table_number = 0
    for item in story:
        if isinstance(item, PageBreak):
            if cover:
                lines.append(r'\end{titlepage}\pagenumbering{arabic}')
                cover = False
            else:
                lines.append(r'\clearpage')
            continue
        if isinstance(item, Spacer):
            lines.append(r'\medskip')
            continue
        if isinstance(item, Table):
            table_number += 1
            rows = item._cellvalues
            spec = '@{}Y'+'r'*(len(rows[0])-1)+'@{}'
            caption = 'Group details' if cover else 'Saved Sudoku measurements (medians over five runs).'
            lines += [r'\begin{table}[H]\centering',r'\caption{'+caption+'}',
                      r'\begin{tabularx}{\linewidth}{'+spec+'}',r'\toprule']
            for i,row in enumerate(rows):
                values = [tex_escape(cell.getPlainText()) for cell in row]
                if i==0: values = [r'\textbf{'+v+'}' for v in values]
                lines.append(' & '.join(values)+r'\\')
                if i==0: lines.append(r'\midrule')
            lines += [r'\bottomrule',r'\end{tabularx}',r'\end{table}']
            continue
        if not isinstance(item, Paragraph):
            continue
        text = item.getPlainText()
        if cover and item.style.name=='title':
            continue
        if cover and skip_group and text==config['group']:
            skip_group = False
            continue
        if item.style.name=='title':
            headings = {
                'Part 1A: Sudoku as a CSP': r'\section{Part 1A: Sudoku as a CSP}',
                'Part 1B: Method and implementation': r'\section{Part 1B: Sudoku solver}\subsection{Method and implementation}',
                'Part 1B: Evaluation and A* analysis': r'\subsection{Evaluation and theoretical A* analysis}',
                'Part 2A/B: Domain and mission design': r'\section{Part 2A/B: Domain and mission design}',
                'Part 2C: Astronaut extension': r'\section{Part 2C: Astronaut extension}',
                'References': r'\section*{References}'}
            lines.append(headings[text])
        elif item.style.name=='heading':
            command = r'\subsection*' if cover else r'\subsubsection'
            if text in ('Mission configuration','Base validation','How the extension changes the plan','Extension validation and limits'):
                command = r'\subsection'
            lines.append(command+'{'+tex_escape(text)+'}')
        elif text.startswith('REVIEW DRAFT'):
            lines.append(r'\begin{center}\textbf{'+tex_escape(text)+r'}\end{center}')
        else:
            lines += [tex_escape(text),'']
    lines.append(r'\end{document}')
    source = project/'main.tex'
    source.write_text('\n'.join(lines)+'\n')
    build_dir = ROOT/'tmp/pdfs/latex-build'
    build_dir.mkdir(parents=True,exist_ok=True)
    for _ in range(2):
        completed = subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',
                                    '-output-directory',str(build_dir),str(source)],
                                   cwd=project,text=True,capture_output=True)
        if completed.returncode:
            raise RuntimeError(completed.stdout[-3500:])
    OUT.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(build_dir/'main.pdf',OUT)

if __name__ == '__main__': build()
