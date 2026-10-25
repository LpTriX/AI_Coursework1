# Actual base-model validation evidence

See `validation.json` for environment, source SHA-256 hashes and the saved run.
The implementation uses Pyperplan 2.1 with greedy best-first search and hFF.

| Instance | Plan actions | All goals and each action independently checked |
| --- | ---: | --- |
| Mission 1 | 10 | Yes |
| Mission 2 | 20 | Yes |
| Renamed Mission 2 with a third rover/lander and seventh goal | 23 | Yes |

The independent replay implements the specification's rules separately from the
PDDL parser and compares expected effects with the actual PDDL action schema.
It also checks location, ownership and capacity invariants after each plan step.
Targeted applicability checks examined 2,496 action instances across 16 coherent
states: 63 applicable instances had correct effects; 2,433 forbidden instances
were inapplicable. These counts are not 2,496 different missions or an exhaustive
proof over all reachable states.

Raw plans and planner logs are retained. Traces show dynamic states after every
step. Timings describe one local run (parse, grounding and search, excluding
subsequent replay), not a repeated benchmark. No optimality or cross-planner
performance comparison is claimed. The generality instance is embedded as text
in the JSON and was generated in a temporary directory; no extra `.pddl` files
were added to the five-file submission tree.

Figures 2/3 were visually inspected in the supplied coursework PDF; their six and
nine directed edges were checked separately against the problem files. The Part C
starter files remain empty and untested pending the partner's implementation.
