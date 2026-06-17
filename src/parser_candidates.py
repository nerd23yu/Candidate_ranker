import json
import pandas as pd

def load_candidates(filepath: str) -> pd.DataFrame:
    """
    Reads candidates.jsonl and returns a flat DataFrame.
    Each row = one candidate.
    """
    records = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                candidate = json.loads(line)
                records.append(parse_candidate(candidate))
            except json.JSONDecodeError as e:
                print(f"Skipping malformed line: {e}")

    df = pd.DataFrame(records)
    print(f"✅ Loaded {len(df)} candidates.")
    return df


def parse_candidate(c: dict) -> dict:
    """
    Flattens one candidate JSON into a flat dictionary.
    """
    profile     = c.get("profile", {})
    signals     = c.get("redrob_signals", {})
    salary      = signals.get("expected_salary_range_inr_lpa", {})

    return {
        # --- Identity ---
        "candidate_id":         c.get("candidate_id"),
        "name":                 profile.get("anonymized_name"),
        "headline":             profile.get("headline"),
        "summary":              profile.get("summary"),
        "location":             profile.get("location"),
        "country":              profile.get("country"),
        "years_of_experience":  profile.get("years_of_experience"),
        "current_title":        profile.get("current_title"),
        "current_company":      profile.get("current_company"),
        "current_company_size": profile.get("current_company_size"),
        "current_industry":     profile.get("current_industry"),

        # --- Career history (kept as raw list for later use) ---
        "career_history":       c.get("career_history", []),

        # --- Education (kept as raw list) ---
        "education":            c.get("education", []),

        # --- Skills (kept as raw list) ---
        "skills":               c.get("skills", []),

        # --- Certifications ---
        "certifications":       c.get("certifications", []),

        # --- Redrob behavioral signals ---
        "profile_completeness":     signals.get("profile_completeness_score"),
        "open_to_work":             signals.get("open_to_work_flag"),
        "last_active_date":         signals.get("last_active_date"),
        "recruiter_response_rate":  signals.get("recruiter_response_rate"),
        "avg_response_time_hours":  signals.get("avg_response_time_hours"),
        "github_activity_score":    signals.get("github_activity_score"),
        "interview_completion_rate":signals.get("interview_completion_rate"),
        "offer_acceptance_rate":    signals.get("offer_acceptance_rate"),
        "notice_period_days":       signals.get("notice_period_days"),
        "willing_to_relocate":      signals.get("willing_to_relocate"),
        "preferred_work_mode":      signals.get("preferred_work_mode"),
        "skill_assessment_scores":  signals.get("skill_assessment_scores", {}),
        "salary_min":               salary.get("min"),
        "salary_max":               salary.get("max"),
        "linkedin_connected":       signals.get("linkedin_connected"),
        "verified_email":           signals.get("verified_email"),
        "verified_phone":           signals.get("verified_phone"),
        "connection_count":         signals.get("connection_count"),
        "endorsements_received":    signals.get("endorsements_received"),
        "saved_by_recruiters_30d":  signals.get("saved_by_recruiters_30d"),
        "applications_submitted_30d": signals.get("applications_submitted_30d"),
    }