import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

CANDIDATES_FILE = os.path.join(DATA_DIR, "candidates.jsonl")
JD_FILE = os.path.join(DATA_DIR, "job_description.docx")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ranked_candidates.csv")

# Scoring weights (must sum to 1.0)
WEIGHTS = {
    "skills_match":     0.40,
    "experience":       0.30,
    "education":        0.20,
    "certifications":   0.10,
}