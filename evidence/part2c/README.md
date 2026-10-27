# Astronaut Extension Validation

Run date: 27 October 2026, Asia/Shanghai.

Implementation commit: `b84b6d3e092696b4713180232aa0cff482e51a7e`.
Base handoff commit: `0efdb054d9ec37bed51ce26e7a5fa6e24530c471`.

The source hashes and environment are recorded in [validation.json](validation.json).
All three base PDDL files match the collaborator's handoff manifest. No original
base source or evidence files were overwritten.

## Mission runs

Planner: Pyperplan 2.1, greedy best-first search with hFF, Python 3.9.6.

| Mission | Plan actions | All goals checked | Independent step-by-step replay |
| --- | ---: | --- | --- |
| Mission 1, original domain | 10 | Passed | Passed |
| Mission 2, original domain | 20 | Passed | Passed |
| Mission 3, extended domain | 24 | Passed | Passed |

The plan lengths describe the plans actually returned, not shortest-plan claims.
The JSON records one run's parse, grounding, and search time for each mission;
these timings are not a repeated benchmark or a planner comparison.

## Astronaut restrictions

The independent rule model checked 24,380 typed action instances across 23
selected coherent states. All 180 permitted instances had the expected effects,
and all 24,200 forbidden instances were inapplicable.

The checks include wrong-room deployment, wrong-room image and scan
transmission, wrong-room storage, wrong-lander's astronauts, co-located landers,
and cross-lander room connections. They also check that movement removes the
previous astronaut location and that all inherited memory and sample rules hold.
The synthetic states use identifiers different from the supplied missions.
This is targeted validation, not an exhaustive reachability proof.

## Where the restrictions affect the saved Mission 3 plan

| Step | Action or dependency |
| --- | --- |
| 1 | Bob moves from lander2's control room to its docking bay |
| 2 | Bob's presence permits rover2 deployment |
| 4 | Bob is still in the docking bay when rover2 stores its sample |
| 8 | Bob returns to the control room |
| 9 and 11 | Rover2 transmits its image and scan while Bob is in that room |
| 17 | Alice moves from lander1's docking bay to its control room |
| 18 and 22 | Rover1 transmits its image and scan while Alice is in that room |
| 23 | Alice returns to the docking bay |
| 24 | Rover1 stores its sample with Alice present |

Thus, the saved plan contains four astronaut movements and achieves all six
goals. The [state trace](mission3-trace.json) records each gated action's receiving
lander, astronaut, room, required room type, and most recent room-change step.

## Files and reproduction

- [Mission 3 plan](mission3.plan), [planner log](mission3.log), and [state trace](mission3-trace.json).
- [Mission 1 regression plan](base-mission1.plan), [log](base-mission1.log), and [trace](base-mission1-trace.json).
- [Mission 2 regression plan](base-mission2.plan), [log](base-mission2.log), and [trace](base-mission2-trace.json).
- [Machine-readable validation summary](validation.json).

From the repository root:

```sh
.venv/bin/python tools/validate_extension.py --output /tmp/part2c-rerun
```

A different valid plan is acceptable. See
[the implementation and run instructions](../../docs/PART2C_IMPLEMENTATION.md)
for setup and interface details. The final PDDL submission tree still contains
exactly the five starter filenames; plans and traces are separate evidence files.
