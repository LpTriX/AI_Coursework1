# Part 2C: Astronaut Extension

The extension is implemented in `PDDL/PartC/domain-ext.pddl` and
`PDDL/PartC/mission3.pddl`. The domain and problem names remain
`lunar-extended` and `lunar-mission-3`.

## Base version

The implementation extends Chengtian Gong's handoff commit
`0efdb054d9ec37bed51ce26e7a5fa6e24530c471`. The three files in `PDDL/PartA&B`
are unchanged. Their ownership, movement, data-memory, sample-carrying, and
lander-storage rules also apply in the extended domain.

Mission 3 retains Mission 2's initial rover/lander facts, nine directed roads,
and six goals. Lander 1 and the deployed rover1 start at wp2. Lander 2 is at
wp1, with rover2 initially aboard it.

## Added representation

New types: `astronaut` and `room`.

| Predicate | Parameter order | Meaning |
| --- | --- | --- |
| `astronaut-belongs-to` | astronaut, lander | Fixed astronaut assignment |
| `room-of` | room, lander | Fixed room ownership |
| `docking-bay` | room | The room is a docking bay |
| `control-room` | room | The room is a control room |
| `room-connected` | from-room, to-room | A permitted directed internal move |
| `astronaut-at` | astronaut, room | The astronaut's current room |

Each lander has a distinct docking bay and control room. Each pair of internal
rooms is connected in both directions. Alice belongs to lander1 and starts in
`l1-docking-bay`; Bob belongs to lander2 and starts in `l2-control-room`.

The initial facts give each astronaut one owner and one room. Movement deletes
the previous room fact and adds the destination. Both rooms must belong to the
astronaut's own lander, even if a problem accidentally supplies a cross-lander
connection. Contradictory ownership or duplicate initial locations are not
treated as valid problem inputs.

## Action interfaces

The original parameters retain their order and meaning. Four actions append
`astronaut, room`:

| Action | Parameter order | Additional requirement |
| --- | --- | --- |
| `deploy` | rover, lander, waypoint, astronaut, room | Correct lander's docking bay |
| `transmit-image` | rover, receiving-lander, source-waypoint, current-waypoint, astronaut, room | Correct lander's control room |
| `transmit-scan` | rover, receiving-lander, source-waypoint, current-waypoint, astronaut, room | Correct lander's control room |
| `store-sample` | rover, receiving-lander, source-waypoint, current-waypoint, astronaut, room | Correct lander's docking bay |

Each gated action checks astronaut ownership, room ownership, room type, and
the astronaut's current presence. All original preconditions and effects remain.
Transmission stays wireless; no rover/lander proximity condition is added.

The new action `move-astronaut(astronaut, lander, from-room, to-room)` requires
the astronaut to be in the source room and both connected rooms to belong to
the assigned lander. Rover movement, imaging, scanning, and sample collection
do not acquire unrelated astronaut requirements.

Only `:strips` and `:typing` are used. No additional requirements, derived
predicates, negative preconditions, or hard-coded mission identifiers are needed.

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

The full validator checks Mission 3's setup against Mission 2, verifies the
base-file hashes, and compares typed action instances with an independent
rule model. It also plans and independently replays all three missions.

Its synthetic states use different identifiers and co-located landers. Checks
cover the wrong astronaut, wrong room type, cross-lander movement, removal of
old locations, and the inherited memory and sample restrictions. These are
targeted tests rather than an exhaustive proof over all reachable states.

Output is written to `evidence/part2c`, with plans, planner logs, per-step state
traces, source hashes, environment details, and a machine-readable summary.
Existing `evidence/base-pddl` files are not overwritten. Use `--output` with a
different directory to retain additional runs.

The [saved validation run](../evidence/part2c/README.md) contains successful
plans and independent replays for all three missions, plus the targeted action
applicability checks. Mission 3's saved plan has 24 actions, including four
astronaut movements.

## Demonstration checklist

- Show Bob leaving the control room before deployment becomes possible.
- Show a transmission with the receiving lander's astronaut in its control room.
- Show sample storage with the corresponding astronaut in its docking bay.
- Explain that an astronaut in the other lander cannot satisfy a local condition.
- Inspect the trace's `astronaut_gate` entries and final six goals.

The saved plan may perform these operations in a different valid order. The
planner is not asked to prove that its returned plan is shortest.
