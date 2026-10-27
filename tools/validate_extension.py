#!/usr/bin/env python3
"""Validate Mission 3 and astronaut restrictions with an independent rule model.

Run with Python 3.9+ after installing requirements-planning.txt. Outputs are
written only to evidence/part2c; the collaborator's base evidence is preserved.
"""

import argparse
import contextlib
from collections import Counter
from datetime import datetime
import hashlib
import importlib.metadata
import io
import itertools
import json
import logging
from pathlib import Path
import platform
import subprocess
import time
from zoneinfo import ZoneInfo

from pyperplan.heuristics.relaxation import hFFHeuristic
from pyperplan.planner import search_plan
from pyperplan.search import greedy_best_first_search

import validate_base as base

ROOT = Path(__file__).resolve().parents[1]
PART_C = ROOT / 'PDDL' / 'PartC'
BASE = ROOT / 'PDDL' / 'PartA&B'
BASE_COMMIT = '0efdb054d9ec37bed51ce26e7a5fa6e24530c471'
BASE_ARITIES = {'deploy': 3, 'move': 3, 'capture-image': 2, 'perform-scan': 2,
                'transmit-image': 4, 'transmit-scan': 4,
                'collect-sample': 2, 'store-sample': 4}
GATED = {'deploy': 'docking-bay', 'store-sample': 'docking-bay',
         'transmit-image': 'control-room', 'transmit-scan': 'control-room'}
STATIC = {'connected', 'belongs-to', 'lander-at', 'astronaut-belongs-to',
          'room-of', 'docking-bay', 'control-room', 'room-connected'}


def invariants(state):
    """Check both base capacities and unique, correctly owned astronaut rooms."""
    base.invariants(state)
    astronauts = {x[1] for x in state if x[0] == 'astronaut-belongs-to'}
    for astronaut in astronauts:
        owners = [x[2] for x in state if x[:2] == ('astronaut-belongs-to', astronaut)]
        rooms = [x[2] for x in state if x[:2] == ('astronaut-at', astronaut)]
        assert len(owners) == len(rooms) == 1, ('astronaut location/ownership', astronaut)
        assert ('room-of', rooms[0], owners[0]) in state, ('wrong lander', astronaut)


def spec_step(state, action_text):
    """Evaluate the written rules without reading the domain action conditions."""
    words = action_text.strip('()').split()
    name, args = words[0], words[1:]
    state = frozenset(state)

    def require(*facts):
        if not all(fact in state for fact in facts):
            raise ValueError('Forbidden action: ' + action_text)

    if name == 'move-astronaut':
        astronaut, lander, start, end = args
        require(('astronaut-belongs-to', astronaut, lander),
                ('room-of', start, lander), ('room-of', end, lander),
                ('room-connected', start, end), ('astronaut-at', astronaut, start))
        result = (state - {('astronaut-at', astronaut, start)}) | {('astronaut-at', astronaut, end)}
    else:
        arity = BASE_ARITIES[name]
        if name in GATED:
            assert len(args) == arity + 2, ('action arity', action_text)
            astronaut, room = args[arity:]
            lander = args[1]
            require(('astronaut-belongs-to', astronaut, lander), ('room-of', room, lander),
                    (GATED[name], room), ('astronaut-at', astronaut, room))
        else:
            assert len(args) == arity, ('action arity', action_text)
        original = '(' + ' '.join((name, *args[:arity])) + ')'
        result = base.spec_step(state, original)
    invariants(result)
    return frozenset(result)


def compare_step(domain, state, action_text):
    operator = base.instantiate(domain, action_text)
    try:
        expected = spec_step(state, action_text)
    except ValueError:
        assert not operator.applicable(base.as_strings(state)), ('should be forbidden', action_text)
        return None
    assert operator.applicable(base.as_strings(state)), ('should be permitted', action_text)
    assert operator.apply(base.as_strings(state)) == base.as_strings(expected), ('wrong effects', action_text)
    return expected


def replay(domain_path, problem_path, actions):
    domain, problem = base.parse(domain_path, problem_path)
    state = frozenset(base.atom(x) for x in problem.initial_state)
    invariants(state)
    trace, previous = [], {}
    for index, text in enumerate(actions, 1):
        before = state
        state = compare_step(domain, state, text)
        assert state is not None, ('inapplicable plan step', index, text)
        words = text.strip('()').split()
        gate = None
        if words[0] in GATED:
            astronaut, room = words[-2:]
            gate = {'astronaut': astronaut, 'room': room, 'lander': words[2],
                    'required_room_type': GATED[words[0]],
                    'astronaut_present_before_action': ('astronaut-at', astronaut, room) in before,
                    'most_recent_astronaut_move_step': previous.get(astronaut)}
        if words[0] == 'move-astronaut':
            previous[words[1]] = index
        trace.append({'step': index, 'action': text, 'astronaut_gate': gate,
                      'dynamic_state': sorted('(' + ' '.join(x) + ')' for x in state if x[0] not in STATIC)})
    goals = {base.atom(x) for x in problem.goal}
    assert goals <= state, ('missing goals', goals - state)
    return trace


def semantic_checks(domain):
    """Test every typed binding in selected coherent, mission-independent states."""
    initial = frozenset({
        ('belongs-to', 'r', 'l'), ('belongs-to', 'other', 'second'),
        ('lander-at', 'l', 'a'), ('lander-at', 'second', 'a'),
        ('aboard', 'r', 'l'), ('aboard', 'other', 'second'),
        ('memory-free', 'r'), ('memory-free', 'other'),
        ('sample-free', 'r'), ('sample-free', 'other'),
        ('storage-free', 'l'), ('storage-free', 'second'),
        ('connected', 'a', 'b'), ('connected', 'b', 'c'), ('connected', 'c', 'a'),
        ('astronaut-belongs-to', 'crew-a', 'l'), ('astronaut-belongs-to', 'crew-b', 'second'),
        ('room-of', 'bay-a', 'l'), ('room-of', 'control-a', 'l'),
        ('room-of', 'bay-b', 'second'), ('room-of', 'control-b', 'second'),
        ('docking-bay', 'bay-a'), ('docking-bay', 'bay-b'),
        ('control-room', 'control-a'), ('control-room', 'control-b'),
        ('room-connected', 'bay-a', 'control-a'), ('room-connected', 'control-a', 'bay-a'),
        ('room-connected', 'bay-b', 'control-b'), ('room-connected', 'control-b', 'bay-b'),
        ('astronaut-at', 'crew-a', 'bay-a'), ('astronaut-at', 'crew-b', 'control-b')})
    sequence = [
        '(move-astronaut crew-b second control-b bay-b)',
        '(deploy other second a crew-b bay-b)', '(deploy r l a crew-a bay-a)',
        '(capture-image r a)', '(collect-sample r a)', '(move r a b)',
        '(move-astronaut crew-a l bay-a control-a)',
        '(transmit-image r l a b crew-a control-a)', '(perform-scan r b)',
        '(move r b c)', '(transmit-scan r l b c crew-a control-a)', '(move r c a)',
        '(move-astronaut crew-a l control-a bay-a)', '(store-sample r l a a crew-a bay-a)',
        '(collect-sample r a)', '(capture-image other a)',
        '(move-astronaut crew-b second bay-b control-b)',
        '(transmit-image other second a a crew-b control-b)', '(collect-sample other a)',
        '(move-astronaut crew-b second control-b bay-b)',
        '(store-sample other second a a crew-b bay-b)']
    states = [initial]
    for action in sequence:
        states.append(spec_step(states[-1], action))
    # Even an erroneous cross-lander adjacency must not allow an astronaut
    # to leave their lander: room ownership is an independent restriction.
    states.append(initial | {('room-connected', 'bay-a', 'control-b')})
    objects = {'rover': ['r', 'other'], 'lander': ['l', 'second'], 'waypoint': ['a', 'b', 'c'],
               'astronaut': ['crew-a', 'crew-b'], 'room': ['bay-a', 'control-a', 'bay-b', 'control-b']}
    assert set(domain.actions) == set(BASE_ARITIES) | {'move-astronaut'}
    counts = Counter()
    for state in states:
        invariants(state)
        for name, schema in domain.actions.items():
            choices = [objects[types[0].name] for _, types in schema.signature]
            for args in itertools.product(*choices):
                result = compare_step(domain, state, '(' + ' '.join((name, *args)) + ')')
                counts['action_instances_checked'] += 1
                counts['permitted_with_correct_effects' if result is not None else 'forbidden'] += 1
    return {'coherent_states': len(states), **dict(counts), 'coverage': [
        'deployment and storage require the correct docking bay',
        'both transmission actions require the correct control room',
        'astronaut and room must belong to the receiving lander',
        'co-located landers cannot exchange astronauts or rover ownership',
        'cross-lander astronaut movement is forbidden even with an adjacency edge',
        'old astronaut location is removed on movement',
        'base memory, sample, storage, movement and acquisition restrictions retained',
        'wireless transmission allows current waypoint to differ from source and lander',
        'synthetic object identifiers instead of mission-specific constants']}


def verify_mission_setup(domain, problem):
    base_domain, mission2 = base.parse(BASE / 'domain.pddl', BASE / 'mission2.pddl')
    base_names = set(base_domain.predicates)
    base_initial = {base.atom(x) for x in mission2.initial_state}
    extended_initial = {base.atom(x) for x in problem.initial_state}
    assert {x for x in extended_initial if x[0] in base_names} == base_initial
    assert {base.atom(x) for x in problem.goal} == {base.atom(x) for x in mission2.goal}
    assert len(problem.goal) == 6
    assert domain.name == 'lunar-extended' and problem.name == 'lunar-mission-3'
    assert ('astronaut-belongs-to', 'alice', 'lander1') in extended_initial
    assert ('astronaut-belongs-to', 'bob', 'lander2') in extended_initial
    assert ('astronaut-at', 'alice', 'l1-docking-bay') in extended_initial
    assert ('astronaut-at', 'bob', 'l2-control-room') in extended_initial
    for schema in domain.actions.values():
        parameters = {x[0] for x in schema.signature}
        for predicate in [*schema.precondition, *schema.effect.addlist, *schema.effect.dellist]:
            assert all(x[0] in parameters for x in predicate.signature), 'hard-coded action argument'
    manifest = json.loads((ROOT / 'evidence/base-pddl/validation.json').read_text())
    for filename, expected in manifest['sha256'].items():
        assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == expected, filename
    return {'base_initial_facts_unchanged': True, 'six_goals_unchanged': True,
            'required_astronaut_setup_verified': True, 'generic_action_arguments': True,
            'base_source_hashes_match_handoff': True}


def plan_and_save(domain_path, problem_path, out, stem, extended=False):
    log = io.StringIO()
    handler = logging.StreamHandler(log)
    logger = logging.getLogger()
    old_level = logger.level
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    start = time.perf_counter()
    try:
        with contextlib.redirect_stdout(log):
            plan = search_plan(str(domain_path), str(problem_path), greedy_best_first_search, hFFHeuristic)
    finally:
        elapsed = time.perf_counter() - start
        logger.removeHandler(handler)
        logger.setLevel(old_level)
    assert plan is not None, ('no plan', str(problem_path))
    actions = [x.name for x in plan]
    trace = replay(domain_path, problem_path, actions) if extended else base.verify_plan(domain_path, problem_path, actions)
    (out / (stem + '.plan')).write_text('\n'.join(actions) + '\n')
    (out / (stem + '.log')).write_text(log.getvalue())
    (out / (stem + '-trace.json')).write_text(json.dumps(trace, indent=2) + '\n')
    counts = Counter(x.strip('()').split()[0] for x in actions)
    result = {'plan_length': len(actions), 'elapsed_seconds_parse_ground_search': elapsed,
              'all_goals_verified': True, 'all_steps_checked_against_independent_rules': True,
              'action_counts': dict(sorted(counts.items()))}
    if extended:
        moved = {text.strip('()').split()[1] for text in actions if text.startswith('(move-astronaut ')}
        assert moved == {'alice', 'bob'}, ('expected both astronauts to move', moved)
        result['both_astronauts_move'] = True
        result['all_gated_actions_have_matching_astronaut_and_room'] = all(
            entry['astronaut_gate']['astronaut_present_before_action'] for entry in trace if entry['astronaut_gate'])
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'evidence' / 'part2c')
    args = parser.parse_args(argv)
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    domain_path, problem_path = PART_C / 'domain-ext.pddl', PART_C / 'mission3.pddl'
    domain, problem = base.parse(domain_path, problem_path)
    results = {'planner': 'Pyperplan ' + importlib.metadata.version('pyperplan'),
               'search': 'greedy best-first', 'heuristic': 'hFF',
               'python': platform.python_version(), 'platform': platform.platform(),
               'run_at_asia_shanghai': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
               'base_handoff_commit': BASE_COMMIT,
               'implementation_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'mission_setup': verify_mission_setup(domain, problem),
               'semantic_checks': semantic_checks(domain), 'missions': {}}
    print('Astronaut and base-rule applicability checks passed.', flush=True)
    for name in ['mission1', 'mission2']:
        results['missions'][name] = plan_and_save(BASE / 'domain.pddl', BASE / (name + '.pddl'), out, 'base-' + name)
        print(name + ' planned and independently replayed.', flush=True)
    results['missions']['mission3'] = plan_and_save(domain_path, problem_path, out, 'mission3', extended=True)
    files = [BASE / 'domain.pddl', BASE / 'mission1.pddl', BASE / 'mission2.pddl',
             domain_path, problem_path, Path(__file__)]
    results['sha256'] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    results['limitations'] = ['Targeted states and typed bindings are not exhaustive reachability analysis.',
                              'Plan length is not an optimality claim; timing is a single local run.',
                              'Well-formed initial ownership and room-location facts are assumed.']
    (out / 'validation.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
