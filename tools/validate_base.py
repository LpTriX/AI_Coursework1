#!/usr/bin/env python3
"""Run the base missions and compare PDDL transitions with an independent rule model.

Install requirements-planning.txt first. Run from any directory with Python 3.9+.
Extra test instances are temporary; the PDDL submission tree retains five files.
"""
import contextlib
import hashlib
import importlib.metadata
import io
import itertools
import json
import logging
import platform
import re
import subprocess
import tempfile
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pyperplan.grounding import ground
from pyperplan.heuristics.relaxation import hFFHeuristic
from pyperplan.pddl.parser import Parser
from pyperplan.planner import search_plan
from pyperplan.search import greedy_best_first_search
from pyperplan.task import Operator

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'PDDL' / 'PartA&B'
OUT = ROOT / 'evidence' / 'base-pddl'


def atom(p):
    return (p.name, *(entry[0] for entry in p.signature))


def parse(domain, problem):
    parser = Parser(str(domain), str(problem))
    dom = parser.parse_domain()
    return dom, parser.parse_problem(dom)


def instantiate(domain, action_text):
    words = action_text.strip('()').split()
    action = domain.actions[words[0]]
    assert len(words) - 1 == len(action.signature)
    binding = dict(zip((x[0] for x in action.signature), words[1:]))

    def fact(p):
        return '(' + ' '.join((p.name, *(binding.get(x[0], x[0]) for x in p.signature))) + ')'

    return Operator('(' + ' '.join(words) + ')',
                    {fact(x) for x in action.precondition},
                    {fact(x) for x in action.effect.addlist},
                    {fact(x) for x in action.effect.dellist})


def as_strings(state):
    return frozenset('(' + ' '.join(x) + ')' for x in state)


def invariants(state):
    rovers = {x[1] for x in state if x[0] == 'belongs-to'}
    landers = {x[2] for x in state if x[0] == 'belongs-to'}
    for rover in rovers:
        owners = [x[2] for x in state if x[:2] == ('belongs-to', rover)]
        assert len(owners) == 1, ('ownership', rover)
        locations = [x for x in state if x[0] in ('aboard', 'rover-at') and x[1] == rover]
        assert len(locations) == 1, ('rover location', rover)
        if locations[0][0] == 'aboard':
            assert locations[0][2] == owners[0]
        held_data = [x for x in state if x[0] in ('carrying-image', 'carrying-scan') and x[1] == rover]
        assert len(held_data) + int(('memory-free', rover) in state) == 1
        held_samples = [x for x in state if x[:2] == ('carrying-sample', rover)]
        assert len(held_samples) + int(('sample-free', rover) in state) == 1
    for lander in landers:
        assert sum(x[:2] == ('lander-at', lander) for x in state) == 1
        stored = [x for x in state if x[0] == 'sample-stored' and x[2] == lander]
        assert len(stored) + int(('storage-free', lander) in state) == 1


def spec_step(state, action_text):
    """Specification oracle, deliberately independent of PDDL preconditions/effects."""
    words = action_text.strip('()').split()
    name, args = words[0], words[1:]
    s = set(state)

    def require(*facts):
        if not all(x in s for x in facts):
            raise ValueError('Forbidden action: ' + action_text)

    if name == 'deploy':
        r, l, w = args
        require(('belongs-to', r, l), ('aboard', r, l), ('lander-at', l, w))
        s.remove(('aboard', r, l))
        s.add(('rover-at', r, w))
    elif name == 'move':
        r, start, end = args
        require(('rover-at', r, start), ('connected', start, end))
        s.remove(('rover-at', r, start))
        s.add(('rover-at', r, end))
    elif name in ('capture-image', 'perform-scan'):
        r, source = args
        require(('rover-at', r, source), ('memory-free', r))
        s.remove(('memory-free', r))
        s.add(('carrying-image' if name == 'capture-image' else 'carrying-scan', r, source))
    elif name in ('transmit-image', 'transmit-scan'):
        r, l, source, current = args
        kind = 'image' if name == 'transmit-image' else 'scan'
        require(('belongs-to', r, l), ('rover-at', r, current), ('carrying-' + kind, r, source))
        s.remove(('carrying-' + kind, r, source))
        s.update({('memory-free', r), (kind + '-saved', source, l)})
    elif name == 'collect-sample':
        r, source = args
        require(('rover-at', r, source), ('sample-free', r))
        s.remove(('sample-free', r))
        s.add(('carrying-sample', r, source))
    elif name == 'store-sample':
        r, l, source, current = args
        require(('belongs-to', r, l), ('rover-at', r, current),
                ('lander-at', l, current), ('carrying-sample', r, source), ('storage-free', l))
        s.remove(('carrying-sample', r, source))
        s.remove(('storage-free', l))
        s.update({('sample-free', r), ('sample-stored', source, l)})
    else:
        raise AssertionError('Unknown action ' + name)
    invariants(s)
    return frozenset(s)


def compare_step(domain, state, action_text):
    op = instantiate(domain, action_text)
    try:
        expected = spec_step(state, action_text)
    except ValueError:
        assert not op.applicable(as_strings(state)), action_text + ' should be forbidden'
        return None
    assert op.applicable(as_strings(state)), action_text + ' should be allowed'
    assert op.apply(as_strings(state)) == as_strings(expected), action_text + ' wrong effects'
    return expected


def verify_plan(domain_path, problem_path, actions):
    domain, problem = parse(domain_path, problem_path)
    state = frozenset(atom(x) for x in problem.initial_state)
    invariants(state)
    trace = []
    for i, action in enumerate(actions, 1):
        state = compare_step(domain, state, action)
        assert state is not None, 'Inapplicable plan step'
        trace.append({'step': i, 'action': action,
                      'dynamic_state': sorted('(' + ' '.join(x) + ')' for x in state
                                              if x[0] not in ('connected', 'belongs-to', 'lander-at'))})
    goals = {atom(x) for x in problem.goal}
    assert goals <= state, ('missing goals', goals - state)
    return trace


def solve(domain_path, problem_path, output_stem):
    log = io.StringIO()
    handler = logging.StreamHandler(log)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    start = time.perf_counter()
    try:
        with contextlib.redirect_stdout(log):
            plan = search_plan(str(domain_path), str(problem_path), greedy_best_first_search, hFFHeuristic)
    finally:
        elapsed = time.perf_counter() - start
        logger.removeHandler(handler)
    assert plan is not None, 'No plan for ' + str(problem_path)
    actions = [x.name for x in plan]
    trace = verify_plan(domain_path, problem_path, actions)
    (OUT / (output_stem + '.plan')).write_text('\n'.join(actions) + '\n')
    (OUT / (output_stem + '.log')).write_text(log.getvalue())
    (OUT / (output_stem + '-trace.json')).write_text(json.dumps(trace, indent=2) + '\n')
    return {'plan_length': len(plan), 'elapsed_seconds_parse_ground_search': elapsed,
            'all_goals_verified': True, 'all_steps_checked_against_independent_rules': True,
            'action_counts': dict(sorted(Counter(x.strip('()').split()[0] for x in actions).items()))}


def semantic_checks(domain):
    """Compare all typed action instances in carefully selected coherent states."""
    initial = frozenset({
        ('belongs-to', 'r', 'l'), ('belongs-to', 'other', 'second'),
        ('lander-at', 'l', 'a'), ('lander-at', 'second', 'a'),
        ('aboard', 'r', 'l'), ('aboard', 'other', 'second'),
        ('memory-free', 'r'), ('memory-free', 'other'),
        ('sample-free', 'r'), ('sample-free', 'other'),
        ('storage-free', 'l'), ('storage-free', 'second'),
        ('connected', 'a', 'b'), ('connected', 'b', 'c'), ('connected', 'c', 'a')})
    sequence = [
        '(deploy r l a)', '(capture-image r a)', '(collect-sample r a)',
        '(move r a b)', '(transmit-image r l a b)', '(perform-scan r b)',
        '(move r b c)', '(transmit-scan r l b c)', '(move r c a)',
        '(store-sample r l a a)', '(collect-sample r a)', '(capture-image r a)',
        '(move r a b)', '(transmit-image r l a b)', '(deploy other second a)']
    states = [initial]
    for action in sequence:
        states.append(spec_step(states[-1], action))
    objects = {'rover': ['r', 'other'], 'lander': ['l', 'second'], 'waypoint': ['a', 'b', 'c']}
    checked = allowed = forbidden = 0
    for state in states:
        invariants(state)
        for name, schema in domain.actions.items():
            choices = [objects[types[0].name] for _, types in schema.signature]
            for args in itertools.product(*choices):
                result = compare_step(domain, state, '(' + ' '.join((name, *args)) + ')')
                checked += 1
                allowed += result is not None
                forbidden += result is None
    return {'coherent_states': len(states), 'action_instances_checked': checked,
            'allowed_with_correct_effects': allowed, 'forbidden': forbidden,
            'coverage': ['undeployed restrictions', 'single directed edges', 'unique rover location',
                         'shared image/scan memory', 'memory released after sending',
                         'wireless sending away from lander and away from data source',
                         'data cannot be sent before acquisition', 'ownership including co-located landers',
                         'sample and data slots independent', 'sample cannot be stored remotely',
                         'one carried sample', 'one stored sample per lander', 'no repeated deployment']}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    domain_path = BASE / 'domain.pddl'
    domain, mission1 = parse(domain_path, BASE / 'mission1.pddl')
    _, mission2 = parse(domain_path, BASE / 'mission2.pddl')
    expected_edges = [
        {('wp1', 'wp2'), ('wp2', 'wp3'), ('wp3', 'wp5'), ('wp5', 'wp1'), ('wp1', 'wp4'), ('wp4', 'wp3')},
        {('wp1', 'wp2'), ('wp2', 'wp1'), ('wp2', 'wp4'), ('wp4', 'wp2'), ('wp3', 'wp5'),
         ('wp5', 'wp3'), ('wp2', 'wp3'), ('wp5', 'wp6'), ('wp6', 'wp4')}]
    for problem, edges in zip([mission1, mission2], expected_edges):
        assert {atom(p)[1:] for p in problem.initial_state if p.name == 'connected'} == edges
    # Every action argument must be a parameter, not a mission-specific constant.
    for schema in domain.actions.values():
        params = {x[0] for x in schema.signature}
        for predicate in [*schema.precondition, *schema.effect.addlist, *schema.effect.dellist]:
            assert all(x[0] in params for x in predicate.signature)
    results = {'planner': 'Pyperplan ' + importlib.metadata.version('pyperplan'),
               'search': 'greedy best-first', 'heuristic': 'hFF',
               'python': platform.python_version(), 'platform': platform.platform(),
               'run_at_asia_shanghai': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
               'domain_general_parameters_verified': True, 'map_edges_verified': [6, 9],
               'semantic_checks': semantic_checks(domain), 'missions': {}}
    for name in ['mission1', 'mission2']:
        results['missions'][name] = solve(domain_path, BASE / (name + '.pddl'), name)
    # Reuse the unmodified domain with different identifiers and a third rover/lander.
    with tempfile.TemporaryDirectory(prefix='f29ai-general-') as tmp:
        text = (BASE / 'mission2.pddl').read_text()
        rename = {'rover1': 'explorer-a', 'rover2': 'explorer-b', 'lander1': 'base-a', 'lander2': 'base-b'}
        rename.update({'wp' + str(i): 'site-' + str(i) for i in range(1, 7)})
        for old, new in rename.items():
            text = re.sub(r'\b' + old + r'\b', new, text)
        text = text.replace('(:objects', '(:objects\n        explorer-c - rover\n        base-c - lander')
        text = text.replace('(:init', '(:init\n        (belongs-to explorer-c base-c)\n'
                            '        (lander-at base-c site-6)\n        (aboard explorer-c base-c)\n'
                            '        (memory-free explorer-c)\n        (sample-free explorer-c)\n'
                            '        (storage-free base-c)')
        text = text.replace('(scan-saved site-6 base-a)',
                            '(scan-saved site-6 base-a)\n        (image-saved site-6 base-c)')
        extra = Path(tmp) / 'renamed-three-rovers.pddl'
        extra.write_text(text)
        results['generality_instance'] = solve(domain_path, extra, 'generality-three-rovers')
        results['generality_instance']['description'] = 'Renamed Mission 2, third rover/lander, extra image goal'
        results['generality_instance']['problem_text'] = text
    files = [domain_path, BASE / 'mission1.pddl', BASE / 'mission2.pddl']
    results['sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    results['source_base_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (OUT / 'validation.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
