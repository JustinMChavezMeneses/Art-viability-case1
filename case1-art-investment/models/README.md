# How to run the four model agents

Four independent agents, one per Conductor workspace, run in parallel. Priority order if usage
is tight: **M1 → M2 → M3**, then **R1**.

## For EACH agent workspace
1. Make sure these two files exist in the workspace (copy from the main workspace if Conductor
   didn't carry `.context/`):
   - `.context/data/artk_quarterly.csv`  ← the data spine (all four need it)
   - `.context/data/japan_bubble_facts.md`  ← M3 only
2. Give the agent this exact instruction:
   > Read `.context/agent_prompts/00_shared_context.md`, then `.context/agent_prompts/<FILE>`,
   > and execute that model. Write output to `.context/outputs/<M#>/`.

   | Agent | FILE | Output |
   |-------|------|--------|
   | M1 | `M1_correlation.md` | `.context/outputs/M1/` |
   | M2 | `M2_inflation.md` | `.context/outputs/M2/` |
   | M3 | `M3_event_study.md` | `.context/outputs/M3/` |
   | R1 | `R1_desmoothing.md` | `.context/outputs/R1/` |

3. Each agent sets up its own venv and pulls its own FRED/yfinance data (keyless). No secrets needed.

## Collecting results (MD, at rejoin)
Each agent produces `results.json` + `*.png` + `findings.md`. Copy the four `outputs/<M#>/` folders
back into the main workspace, then we:
- read the four `findings.md` for the support/weaken/kill verdicts,
- run the **portfolio overlay** (60/40 vs 58/38/4-art: Δ drawdown in each crisis, Δ real return in
  inflation regimes, return give-up) — this is the opportunity-cost answer (Q5), done at rejoin,
- decide the paper's verdict (YES-caveats / NO), pick exhibits, then draft the LaTeX memo.

## Guardrails baked into every prompt
Real vs nominal labeled; HAC/Newey-West SEs (art returns are autocorrelated from smoothing);
correlations on returns not levels; no fabricating/padding missing data; state sample period + n
for every stat; flag when smoothing or thin-market noise could be driving a result.
