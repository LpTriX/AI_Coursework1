# Base PDDL handoff — Chengtian Gong to Pinxin Liu

Prepared 25 October 2026. Status: base implementation and local tests complete;
Pinxin Liu's acceptance and Part 2C implementation are pending. These interfaces
are implemented choices ready for review, not decisions already confirmed by both members.

## Files and ownership

Gong maintains `PDDL/PartA&B/domain.pddl`, `mission1.pddl`, and `mission2.pddl`.
Pinxin Liu maintains `PDDL/PartC/domain-ext.pddl` and `mission3.pddl`.
The Part C files currently remain the original empty starter templates.

Base domain: `lunar`. Problems: `lunar-mission-1`, `lunar-mission-2`.
Extended domain: `lunar-extended`. Problem: `lunar-mission-3`.
Preserve all starter paths and internal names.

## Types and predicates: parameter order is part of the interface

Types: `rover`, `lander`, `waypoint`.

| Predicate | Parameters in order | Meaning |
| --- | --- | --- |
| `belongs-to` | rover, lander | Fixed rover ownership |
| `lander-at` | lander, waypoint | Fixed landing site |
| `connected` | from-waypoint, to-waypoint | A directed road |
| `aboard` | rover, lander | Undeployed, aboard its own lander |
| `rover-at` | rover, waypoint | Current deployed location |
| `memory-free` | rover | No unsent image or scan |
| `carrying-image` | rover, source-waypoint | An unsent image and its provenance |
| `carrying-scan` | rover, source-waypoint | An unsent scan and its provenance |
| `image-saved` | source-waypoint, receiving-lander | Successfully transmitted image |
| `scan-saved` | source-waypoint, receiving-lander | Successfully transmitted scan |
| `sample-free` | rover | No sample carried |
| `carrying-sample` | rover, source-waypoint | Carried physical sample |
| `storage-free` | lander | No sample stored yet |
| `sample-stored` | source-waypoint, receiving-lander | Sample physically stored |

`source` and `current` are different concepts and may bind to different waypoints.
Data memory and sample capacity are independent. Lander sample space is never
restored. Waypoints do not have a finite sample stock because the specification
adds no such restriction. Initial states must provide exactly one owner per rover,
exactly one aboard/location state per rover, one fixed location per lander, and
consistent capacity tokens. These are well-formed-input assumptions, preserved
by the actions; PDDL does not validate arbitrary contradictory initial states.

## Action signatures

| Action | Parameters in order |
| --- | --- |
| `deploy` | rover, lander, waypoint |
| `move` | rover, from-waypoint, to-waypoint |
| `capture-image` | rover, source-waypoint |
| `perform-scan` | rover, source-waypoint |
| `transmit-image` | rover, receiving-lander, source-waypoint, current-waypoint |
| `transmit-scan` | rover, receiving-lander, source-waypoint, current-waypoint |
| `collect-sample` | rover, source-waypoint |
| `store-sample` | rover, receiving-lander, source-waypoint, current-waypoint |

Wireless sends do not require co-location or an earlier lander visit. Storage
requires current-waypoint to equal the named lander's location. All receiving
operations check `belongs-to`. Merely capturing/scanning/collecting is not a goal.

## Fixed mission choices

- Mission 1: lander1 at wp1, rover1 aboard lander1.
- Mission 2: lander1 and already deployed rover1 at wp2; lander2 at wp1,
  rover2 aboard lander2. All memory/sample/storage slots initially free.
- Figure 2 edges: 1→2, 2→3, 3→5, 5→1, 1→4, 4→3 (six).
- Figure 3 edges: 1→2, 2→1, 2→4, 4→2, 3→5, 5→3, 2→3, 5→6, 6→4 (nine).
- Mission 3 must retain Mission 2's choices, map and six goals.

## Part 2C integration points

Copy the reviewed base implementation into the existing Part C domain file,
then retain its original domain name `lunar-extended`. Base action semantics and
capacity effects must be preserved while adding the astronaut restrictions.

1. `deploy`: require an astronaut in the docking bay of the SAME lander parameter.
2. `store-sample`: require an astronaut in that receiving lander's docking bay.
3. BOTH `transmit-image` and `transmit-scan`: require an astronaut in the receiving
   lander's control room. No physical rover/lander proximity restriction is added.
4. Astronaut movement must stay inside that astronaut's own lander and must remove
   the previous room state. Alice belongs to lander1 and starts in its docking bay;
   Bob belongs to lander2 and starts in its control room.
5. Pinxin Liu chooses and documents the added astronaut/room types and predicates. If
   action signatures change, preserve the existing meanings and record additions.

Do not add astronaut prerequisites to the base domain: Mission 1/2 use the base
rules. The independent base validator is not an astronaut-extension validator;
Part C requires separate tests and Mission 3 planning evidence.

## Reproduction

From the repository root, create an environment and install the pinned planner:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-planning.txt
python tools/validate_base.py
```

To run a single mission:

```sh
pyperplan -s gbf -H hff "PDDL/PartA&B/domain.pddl" "PDDL/PartA&B/mission1.pddl"
pyperplan -s gbf -H hff "PDDL/PartA&B/domain.pddl" "PDDL/PartA&B/mission2.pddl"
```

The planner CLI may create `.soln` files beside the problems; these are output,
not extra PDDL submission files. The full validator also runs a larger generality
check that took about one minute on the recorded machine; other machines or
Python hash orders may take longer. A different valid plan is acceptable.

Saved run: Pyperplan 2.1, greedy best-first with hFF; Mission 1: 10 actions,
Mission 2: 20 actions; renamed three-rover instance: 23 actions. These are not
optimality claims. Semantic checks: 2,496 typed action instances across 16 states,
63 permitted with correct effects and 2,433 forbidden. This is targeted validation,
not exhaustive reachability analysis. All returned plans passed independent replay.

Evidence: `evidence/base-pddl/validation.json`, raw `.plan` and `.log` files,
and per-step `*-trace.json`. The validation JSON seals source files with SHA-256.
`source_base_commit` identifies the pre-change repository commit, not a claim
that the new PDDL already existed at that commit. The handoff manifest records
the final local implementation commit separately.

## Acceptance and future changes

- Pinxin Liu runs Mission 2 and confirms that he understands every action.
- Both confirm the predicate/action table and lander2=wp1 choice.
- Pinxin Liu implements and tests Part C on his own extension branch.
- Gong remains responsible for Part 1A and Parts 2A/2B; allocation is unchanged.
- Do not silently edit the other member's owned files. A later base fix must be
  identified by commit/hash, discussed, and followed by Mission 3 regression checks.
- The handoff archive is not the final submission. Final PDDL content is exactly
  five completed starter files; do not submit empty Part C templates.
