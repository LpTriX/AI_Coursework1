# Part 2C: Astronaut Extension

The extension lives in `PDDL/PartC/domain-ext.pddl` and
`PDDL/PartC/mission3.pddl`. The domain and problem names stay
`lunar-extended` and `lunar-mission-3`.

## Base version

This builds on Chengtian Gong's handoff commit
`0efdb054d9ec37bed51ce26e7a5fa6e24530c471`. The three files in `PDDL/PartA&B`
are unchanged. Their ownership, movement, data-memory, sample-carrying and
lander-storage rules all still apply in the extended domain.

Mission 3 keeps Mission 2's rover and lander starts, nine directed roads and
six goals. Lander 1 and the deployed rover1 start at wp2. Lander 2 is at wp1,
with rover2 aboard it.

## Added representation

Two new types: `astronaut` and `room`.

| Predicate | Parameter order | Meaning |
| --- | --- | --- |
| `astronaut-belongs-to` | astronaut, lander | Fixed astronaut assignment |
| `room-of` | room, lander | Fixed room ownership |
| `docking-bay` | room | The room is a docking bay |
| `control-room` | room | The room is a control room |
| `room-connected` | from-room, to-room | A permitted directed internal move |
| `astronaut-at` | astronaut, room | The astronaut's current room |

Each lander has its own docking bay and control room, connected to each other
both ways. Alice belongs to lander1 and starts in `l1-docking-bay`; Bob belongs
to lander2 and starts in `l2-control-room`.

Each astronaut starts with one owner and one room. Moving deletes the old room
fact and adds the destination. Both rooms must belong to the astronaut's own
lander, so even a wrongly supplied cross-lander connection would not let an
astronaut leave their lander. Contradictory ownership or duplicate starting
locations are treated as invalid problem input, not something the domain has to
cope with.

## Action interfaces

The original parameters keep their order and meaning. Four actions gain an
`astronaut, room` pair:

| Action | Parameter order | Additional requirement |
| --- | --- | --- |
| `deploy` | rover, lander, waypoint, astronaut, room | Correct lander's docking bay |
| `transmit-image` | rover, receiving-lander, source-waypoint, current-waypoint, astronaut, room | Correct lander's control room |
| `transmit-scan` | rover, receiving-lander, source-waypoint, current-waypoint, astronaut, room | Correct lander's control room |
| `store-sample` | rover, receiving-lander, source-waypoint, current-waypoint, astronaut, room | Correct lander's docking bay |

Each affected action checks that the astronaut and room belong to the receiving
lander, that the room has the right role, and that the astronaut is currently in
it. All the original preconditions and effects stay. Transmission is still
wireless, so the rover does not have to be near the lander.

The new action `move-astronaut(astronaut, lander, from-room, to-room)` needs the
astronaut to be in the from-room, and both rooms connected and belonging to that
astronaut's lander. Rover movement, imaging, scanning and sample collection never
need an astronaut.

Only `:strips` and `:typing` are used. No derived predicates, negative
preconditions or hard-coded mission identifiers.

## Run and validate

From the repository root, install the pinned planner in the local environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-planning.txt
.venv/bin/python tools/validate_extension.py
```

For a single planner run:

```sh
.venv/bin/pyperplan -s gbf -H hff PDDL/PartC/domain-ext.pddl PDDL/PartC/mission3.pddl
```

The validator first checks that Mission 3 keeps Mission 2's setup and that the
base-file hashes match the handoff. It then compares typed action instances
against an independent rule model, and finally plans and independently replays
all three missions.

The test states use different identifiers and include landers at the same
waypoint. Checks cover the wrong astronaut, wrong room type, cross-lander
movement, removal of old locations, and the inherited memory and sample rules.
These tests do not cover every reachable state.

Output is written to `evidence/part2c`: plans, planner logs, per-step state
traces, source hashes, environment details and a machine-readable summary.
Existing `evidence/base-pddl` files are not overwritten. Use `--output` with a
different directory to keep extra runs.

The [saved validation run](../evidence/part2c/README.md) contains successful
plans and independent replays for all three missions, plus the targeted action
applicability checks. Mission 3's saved plan has 24 actions, including four
astronaut movements.

## Demonstration checklist

- Show Bob leaving the control room before deployment becomes possible.
- Show a transmission with the receiving lander's astronaut in its control room.
- Show sample storage with the matching astronaut in its docking bay.
- Explain that an astronaut in the other lander cannot satisfy a local condition.
- Inspect the trace's `astronaut_gate` entries and final six goals.

The saved plan may perform these operations in a different valid order. We did
not ask the planner to prove that its plan is shortest.
