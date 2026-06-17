import os
import pandas as pd
from src.parser_candidates import load_candidates
from src.parser_jd import parse_jd
from src.scoring_engine import score_all
from src.explainer import explain_all
from config import CANDIDATES_FILE, JD_FILE, OUTPUT_FILE

# Step 1 - Load
df = load_candidates(CANDIDATES_FILE)
jd = parse_jd(JD_FILE)

# Step 2 - Score
df_scored = score_all(df, jd)

# Step 3 - Explain
df_explained = explain_all(df_scored, jd)

# Step 4 - Take top 100 only
top100 = df_explained.head(100).copy()
top100["rank"] = range(1, 101)

# Step 5 - Keep only required columns
submission = top100[["candidate_id", "rank", "score", "reasoning"]]

# Step 6 - Validate
assert len(submission) == 100, "Must have exactly 100 rows!"
assert submission["rank"].tolist() == list(range(1, 101)), "Ranks must be 1-100!"
assert submission["candidate_id"].nunique() == 100, "Duplicate candidate_ids found!"
assert all(submission["score"].diff().dropna() <= 0), "Scores must be non-increasing!"

# Step 7 - Save
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
submission.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
print(f"Submission saved to: {OUTPUT_FILE}")
print(f"Rows: {len(submission)}")
print(f"Score range: {submission['score'].max():.4f} to {submission['score'].min():.4f}")

print("\nTop 10 preview:")
print(submission.head(10).to_string(index=False))
