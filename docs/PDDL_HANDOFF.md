# PDDL Handoff Checklist

Use this checklist to agree on the interface with Gong Chengtian and avoid incompatible models. Record confirmed decisions here; do not treat pending items as implemented agreements.

Current status: Gong Chengtian's implemented base domain and Mission 2 have not yet been received. Part 2C has not been implemented.

## Materials to request from Gong Chengtian

- Working versions of `domain.pddl` and `mission2.pddl`, with the corresponding Git commit.
- The planner and its version or service name, run instructions, and the actual plan found.
- Object types and hierarchy, plus the parameter order and meaning of important predicates.
- Explanations of deployment, movement, imaging, scanning, transmission, sample collection, and sample storage actions.
- Representations of undeployed rovers, free data memory, rover sample capacity, and lander sample capacity.
- The representation and enforcement of rover/lander ownership.
- The chosen landing waypoint for Lander 2 in Mission 2 and its rationale; Mission 3 must retain that choice.
- A check of every connection against the arrow directions in Figure 3.

## Decisions to confirm together

| Item | Confirmed agreement |
| --- | --- |
| Base version commit | Awaiting handoff |
| Object types and parameter order | Awaiting handoff |
| Rover/lander ownership representation | Awaiting handoff |
| Deployment state representation | Awaiting handoff |
| Data types, possession, and transmission state | Awaiting handoff |
| Memory, rover sample capacity, and lander storage capacity | Awaiting handoff |
| Transmission, deployment, and storage action names | Awaiting handoff |
| Lander 2 location | Awaiting handoff |
| Test planner and run instructions | Awaiting handoff |
| Process for synchronising later base-model changes | To be agreed by both members |

## Starter files and names

| Component | File | Internal names |
| --- | --- | --- |
| Base domain | `PDDL/PartA&B/domain.pddl` | domain `lunar` |
| Mission 1 | `PDDL/PartA&B/mission1.pddl` | problem `lunar-mission-1`, domain `lunar` |
| Mission 2 | `PDDL/PartA&B/mission2.pddl` | problem `lunar-mission-2`, domain `lunar` |
| Extended domain | `PDDL/PartC/domain-ext.pddl` | domain `lunar-extended` |
| Mission 3 | `PDDL/PartC/mission3.pddl` | problem `lunar-mission-3`, domain `lunar-extended` |

These names have been checked against the original starter package. This table documents the interface; it does not mean the files have been completed or uploaded.

## Handoff acceptance checks

- The base model runs Mission 2 with an allowed planner.
- The plan respects data, sample, ownership, and direction restrictions, beyond merely returning a successful planner status.
- Parameterised actions do not hard-code specific waypoints, rovers, or landers.
- Base-model validation evidence corresponds to the recorded commit.
- Understand the base actions before independently implementing Part 2C. Do not combine an unexplained base version with the final extension.
