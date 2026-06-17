from src.feature_extractor import extract_features

def score_candidate(row: dict, jd: dict) -> float:
    f = extract_features(row, jd)

    # --- Core score components ---
    skill_score = (
        0.70 * f["must_have_score"] +
        0.30 * f["nice_to_have_score"]
    )

    experience_score = (
        0.60 * f["experience_score"] +
        0.25 * min(f["ai_role_months"] / 60.0, 1.0) +
        0.15 * f["product_company_exp"]
    )

    education_score = (
        0.70 * f["education_tier_score"] +
        0.30 * f["relevant_field"]
    )

    signal_score = (
        0.30 * f["recency_score"] +
        0.25 * f["recruiter_response_rate"] +
        0.20 * f["notice_score"] +
        0.15 * f["github_score"] +
        0.10 * f["interview_completion_rate"]
    )

    location_score = f["location_score"]

    # --- Weighted composite ---
    raw_score = (
        0.35 * skill_score +
        0.25 * experience_score +
        0.15 * education_score +
        0.15 * signal_score +
        0.10 * location_score
    )

    # --- Apply penalty for disqualifiers ---
    final_score = raw_score * f["penalty"]

    return round(final_score, 4)


def score_all(df, jd: dict):
    import pandas as pd
    print("Scoring candidates...")
    scores = []
    for i, row in df.iterrows():
        s = score_candidate(row.to_dict(), jd)
        scores.append(s)
        if (i + 1) % 10000 == 0:
            print(f"  Scored {i + 1} candidates...")

    df = df.copy()
    df["score"] = scores
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    print(f"Scoring complete!")
    return df
