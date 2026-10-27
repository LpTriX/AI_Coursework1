# Part 2C: Astronaut Extension Learning and Validation Roadmap

This is an understanding and validation checklist, not submission PDDL or report text. The extension is now implemented and validated. See the [implementation details](../docs/PART2C_IMPLEMENTATION.md) and [saved evidence](../evidence/part2c/README.md).

## 1. Confirm the base version

Complete the [PDDL handoff checklist](../docs/PDDL_HANDOFF.md) and record the actual commit. Run Mission 2, understand its plan, and verify the base behaviour first.

Retain Mission 2's map, initial rover/lander setup, and six goals. Lander 2's location must match the base version; do not silently replace it with a more convenient choice.

## 2. Identify the new facts and restrictions

Alice belongs to Lander 1 and Bob to Lander 2. Each lander has a docking bay and a control room. Astronauts can move only within their own lander. Initially, Alice is in the docking bay and Bob is in the control room.

Work through these questions:

- How are an astronaut's lander association and current internal location represented?
- How is an astronaut prevented from being in two areas simultaneously?
- How is movement restricted to the astronaut's own lander?
- Which existing actions need extra location conditions, and which should remain unaffected?
- Do the conditions actually control action applicability, rather than merely recording unused facts?

## 3. Match the required action restrictions

| Behaviour | Required condition inside the relevant lander |
| --- | --- |
| Deploy a rover | An astronaut is in the docking bay |
| Store a sample | An astronaut is in the docking bay |
| Receive data transmitted by a rover | An astronaut is in the control room |

The base requirements for memory, sample capacity, rover ownership, acquired data, and physical sample return must still hold. The extension must not relax them.

## 4. Verify that the restrictions have an effect

Check individual action applicability in a given state before checking complete plans. Temporary local problem instances can test forbidden cases; the final submission must still contain only the five required PDDL files.

| Scenario | Expected behaviour | Actual result / evidence |
| --- | --- | --- |
| Deploy while the relevant astronaut is in the control room | Deployment is inapplicable | Passed in typed action checks |
| Transmit while the relevant astronaut is in the docking bay | Transmission is inapplicable | Passed for images and scans |
| Store a sample while the relevant astronaut is in the control room | Storage is inapplicable | Passed in typed action checks |
| Move the astronaut to the required area while all other conditions hold | The dependent action becomes applicable | Passed in checks and plan replay |
| Use another lander's astronaut to meet a local condition | Forbidden | Passed, including co-located landers |
| Move an astronaut between landers | Forbidden | Passed, including a cross-lander adjacency |
| Achieve every Mission 3 goal | The plan achieves all six goals and obeys all restrictions | Passed by independent replay |

## 5. Retain real validation evidence

For each run, record the commit, domain/problem files, planner, execution method, whether a plan was found, the raw plan, and the checks performed. Different planners may return different valid plans; action-by-action equality is not required.

The video should show an astronaut moving to the required area before a dependent action, with an explanation of why the movement is necessary. A successful planner message alone is insufficient evidence of this behaviour.

## Current status

- Interface: based on the handoff; additions are documented in `docs/PART2C_IMPLEMENTATION.md`.
- Extended PDDL: both Part C files are complete.
- Planner execution: all three missions run locally with Pyperplan 2.1.
- Plan validity: checked against an independent rule model; all six Mission 3 goals achieved.
- Report and video: still outstanding.
