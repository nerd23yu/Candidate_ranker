# Candidate Ranking System

An intelligent candidate discovery and ranking engine built for the India Runs Data & AI Challenge.

## What it does
- Parses a Job Description to extract required skills, experience range, and preferences
- Loads and processes 100,000 candidate profiles from a JSONL dataset
- Scores each candidate using a weighted multi-criteria engine
- Generates human-readable explanations for every ranking decision
- Outputs a ranked list of the top 100 best-fit candidates

## How it works
| Component | File | Purpose |
|---|---|---|
| JD Parser | src/parser_jd.py | Extracts skills, requirements from JD |
| Candidate Parser | src/parser_candidates.py | Loads and flattens JSONL profiles |
| Feature Extractor | src/feature_extractor.py | Computes 25+ features per candidate |
| Scoring Engine | src/scoring_engine.py | Weighted scoring with penalty logic |
| Explainer | src/explainer.py | Generates reasoning per candidate |

## Scoring Criteria
- 35% Skills match (must-have + nice-to-have)
- 25% Experience (years, AI role months, product company)
- 15% Education (institution tier + relevant field)
- 15% Behavioral signals (recency, GitHub, response rate)
- 10% Location preference

## How to run
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python main.py

## Output
outputs/team_data_dealers.csv — top 100 candidates with rank, score, and reasoning.
