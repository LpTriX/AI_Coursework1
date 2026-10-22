# Task Allocation and Schedule

All dates use Beijing time (UTC+8). Each member leads work worth 20 marks. Review the actual workload once the first versions are complete.

## David Liu

- Part 1B: implement Sudoku search, support at least one required file format, validate results, handle unsatisfiable puzzles, collect measurements on several puzzles, prepare the theoretical A* analysis, and write the corresponding report section independently.
- Part 2C: extend Gong Chengtian's base domain and Mission 2 with the astronaut requirements, complete Mission 3, verify that the requirements actually constrain action applicability, and write the corresponding report section independently.
- Prepare the Sudoku run instructions and combine the video recordings.

## Gong Chengtian

- Part 1A: formulate Sudoku as a CSP, analyse complexity, and write the corresponding report section independently.
- Parts 2A and 2B: implement a reusable base domain, Mission 1 and Mission 2, validate them with a planner, and write the corresponding report section independently.
- Format the combined report, organise references, and assemble the final ZIP.

## Shared responsibilities

- Agree on the PDDL interface at the start and record the actual commit used for the handoff.
- Explain the correctness of each implementation and review the other member's results.
- Each member presents a substantial portion of the video; the total must not exceed 8 minutes.
- Check the final files and video link together before submission.
- Compare the remaining workload after the first versions are ready. Reassign measurement organisation, figures, or packaging if needed.

## Suggested schedule

| Date | David Liu | Gong Chengtian | Milestone check |
| --- | --- | --- | --- |
| Oct 22–23 | Define input and search behaviour; start Sudoku | Agree on the base PDDL interface and begin implementation | Both confirm the interface; learning notes are recorded |
| Oct 24–25 | Complete the first Sudoku version; start Part 2C after receiving the base domain | Provide a working base domain and Mission 2; continue Mission 1 and Part 1A | Mark work complete only after actually running it |
| Oct 26 | Run Sudoku experiments and validate Mission 3 | Review the base planning model and add checks | Review against the specification and balance the remaining work |
| Oct 27 | Independently write assigned report sections | Independently write assigned report sections | Part 1: at most 4 pages total; Part 2: at most 3 pages total |
| Oct 28 | Record and combine the video | Format the report and assemble the ZIP | Check the submission together and aim to submit early |
| Oct 29 | Allow time for corrections and submission | Allow time for corrections and submission | Confirm the actual OUC deadline time |

## File ownership and collaboration

Gong Chengtian maintains the base domain, Mission 1, and Mission 2. David Liu maintains the extended domain and Mission 3. Changes needed in the base files should be coordinated rather than introduced silently. Recheck the extension whenever the base version changes.

Preserve the starter filenames, folder structure, and domain/problem names. The final submission must contain exactly the five required PDDL files.
