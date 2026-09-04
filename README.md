# genetic-algorithm-optimizer
Genetic algorithm-based optimizer, benchmarked against a heuristic solver.
# Genetic Algorithm Optimizer

## What this is
A Python implementation of a genetic algorithm for a Just-In-Time job scheduling problem — minimizing total weighted earliness and tardiness penalties across a sequence of jobs. Includes a comparison mode that solves the same problem exactly using Linear Programming (PuLP), so the GA's solutions can be benchmarked against a mathematically optimal (or near-optimal) baseline.

## Why
Built as part of an algorithms course project, working independently. I'm generally drawn to algorithms — the challenge of solving puzzles and finding efficient solutions to complex, combinatorial problems is what got me interested in building a genetic algorithm from scratch rather than relying on an off-the-shelf optimizer.

## How it works
- Each candidate solution (chromosome) is a permutation — the order in which jobs are scheduled.
- Fitness is computed by scheduling the jobs in that order and summing the earliness/tardiness penalties.
- Selection: rank-based roulette wheel selection.
- Crossover: order crossover (preserves relative job order from both parents).
- Mutation: swap mutation between two random positions.
- Elitism: the best solutions carry over unchanged to the next generation.
- The algorithm runs until a configurable time limit is reached.

## Results
Compared the GA against solving directly with the exact LP solver — which finds the optimal timing for a *given* job order but does not search across different orderings — on two problem instances:

| Instance size | Solver (default order) penalty | GA (best order found) penalty | Improvement | GA runtime |
|---|---|---|---|---|
| 5 jobs | 250 | 207 | ~17% lower | 147 generations / 100.5s |
| 100 jobs | 45,223 | 22,458 | ~50% lower | 47 generations / 150.8s |

The gap widens with problem size: on the small instance the GA trims about a sixth of the penalty, but on the 100-job instance it more than halves it — showing that searching over job sequences, not just optimizing timing for a fixed order, matters a lot as the scheduling problem grows.

## Tech stack
Python, tkinter (GUI), openpyxl (Excel I/O), PuLP (Linear Programming solver)

## How to run
python Project_Form.py

Then enter an input Excel file name (with job data) and an output file name, choose whether to run the GA or the exact solver, and click Solve.
