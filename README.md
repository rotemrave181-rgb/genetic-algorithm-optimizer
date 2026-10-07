# Genetic Algorithm Optimizer – JIT Job Scheduling

A Python genetic algorithm that schedules jobs Just-In-Time, minimizing total weighted **earliness + tardiness** penalties. It is benchmarked against an exact Linear Programming model (PuLP) that optimizes job timing for a fixed order.

## What this is
In JIT scheduling, finishing a job too early costs inventory/holding, and finishing it too late costs a delay penalty. The problem has two parts:

1. **Sequencing** – in which order should the jobs run? (combinatorial, *n!* options)
2. **Timing** – given an order, when should each job start?

The LP solver handles the timing step optimally for a *given* order. The genetic algorithm searches over orders and uses the LP model to evaluate each one. The question the project answers is how much is gained by searching the sequence, compared with keeping the original order.

## Why
Built as part of an algorithms course project, working independently. I'm generally drawn to algorithms — the challenge of solving puzzles and finding efficient solutions to complex, combinatorial problems is what got me interested in building a genetic algorithm from scratch rather than relying on an off-the-shelf optimizer.

## How it works
- **Chromosome:** a permutation – the order in which jobs are scheduled.
- **Fitness:** the job order is passed to the LP timing model; the resulting total earliness/tardiness penalty is the fitness (lower is better).
- **Selection:** rank-based roulette wheel.
- **Crossover:** order crossover (OX), which preserves relative job order from both parents.
- **Mutation:** swap mutation between two random positions.
- **Elitism:** the best solutions carry over unchanged to the next generation.
- **Stopping rule:** a configurable time limit.

## Results
GA (best order found) vs. the LP solver on the original job order:

| Instance size | LP solver, original order – penalty | GA, best order found – penalty | Improvement | GA runtime |
|---|---|---|---|---|
| 5 jobs | 250 | 207 | ~17% lower | 147 generations / 100.5s |
| 100 jobs | 45,223 | 22,458 | ~50% lower | 47 generations / 150.8s |

The gap widens with problem size: on the small instance the GA trims about a sixth of the penalty, but on the 100-job instance it more than halves it — showing that searching over job sequences, not just optimizing timing for a fixed order, matters a lot as the scheduling problem grows.

## Project structure
| File | Role |
|---|---|
| `Project_Form.py` | tkinter GUI – entry point |
| `GA_Engine.py` | Genetic algorithm (selection, crossover, mutation, elitism) |
| `Solver_Engine.py` | Excel input/output and the PuLP LP timing model |
| `sample_input.xlsx` | Example input with 10 jobs |
| `GA_Picture.png` | GUI background image |

## Input format
One Excel sheet, one column per job (starting at column B):

| Row | Content |
|---|---|
| 1 | Job ID |
| 2 | Processing time |
| 3 | Due date |
| 4 | Earliness penalty per time unit |
| 5 | Tardiness penalty per time unit |

GA parameters sit in column A: population size (`A7`), number of elites (`A9`), mutation probability (`A11`), time limit in seconds (`A13`). See `sample_input.xlsx`.

## How to run
```bash
pip install -r requirements.txt
python Project_Form.py
```
In the window, type `sample_input` as the input file and any name for the output file, choose GA or the exact solver, and click **Solve**. The schedule and total penalty are written to the output Excel file.

## Tech stack
Python · tkinter · openpyxl · PuLP (CBC solver)
