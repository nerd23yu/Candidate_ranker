from datetime import date, datetime
































# Proficiency weights for skill scoring
PROFICIENCY_WEIGHTS = {
    "beginner":     0.25,
    "intermediate": 0.55,
    "advanced":     0.80,
    "expert":       1.00,
}

# Consulting-only company disqualifiers (from JD)
DISQUALIFIER_COMPANIES = {
    "tcs", "infosys", "wipro", "accenture",
    "cognizant", "capgemini",
}


def extract_features(row: dict, jd: dict) -> dict:
    """
    Takes one candidate row (as dict) + parsed JD,
    returns a flat dict of numeric features.
    """
    skills          = row.get("skills", [])
    career          = row.get("career_history", [])
    education       = row.get("education", [])
    certifications  = row.get("certifications", [])

    return {
        **_skill_features(skills, jd),
        **_experience_features(row, career, jd),
        **_education_features(education),
        **_certification_features(certifications),
        **_signal_features(row),
        **_location_features(row, jd),
        **_disqualifier_features(row, career, jd),
    }


# ── 1. Skill features ──────────────────────────────────────────────────────

def _skill_features(skills: list, jd: dict) -> dict:
    skill_names_lower = [s["name"].lower() for s in skills]

    must_have    = jd["must_have_skills"]
    nice_to_have = jd["nice_to_have_skills"]

    # Count how many must-have skills the candidate has
    must_matches = sum(
        1 for req in must_have
        if any(req in s for s in skill_names_lower)
    )

    # Weighted score — advanced/expert skills count more
    must_score = 0.0
    for skill in skills:
        name = skill["name"].lower()
        if any(req in name for req in must_have):
            prof   = skill.get("proficiency", "beginner")
            weight = PROFICIENCY_WEIGHTS.get(prof, 0.25)
            must_score += weight

    # Normalize by total must-haves
    must_score_norm = min(must_score / max(len(must_have), 1), 1.0)

    # Nice-to-have count
    nice_matches = sum(
        1 for req in nice_to_have
        if any(req in s for s in skill_names_lower)
    )
    nice_score_norm = min(nice_matches / max(len(nice_to_have), 1), 1.0)

    # Assessment scores (if any) on relevant skills
    assessment_scores = row_assessment_avg(skills)

    return {
        "must_have_count":      must_matches,
        "must_have_score":      must_score_norm,
        "nice_to_have_count":   nice_matches,
        "nice_to_have_score":   nice_score_norm,
    }


def row_assessment_avg(skills: list) -> float:
    """Average endorsements as a proxy quality signal."""
    if not skills:
        return 0.0
    total = sum(s.get("endorsements", 0) for s in skills)
    return total / len(skills)


# ── 2. Experience features ─────────────────────────────────────────────────

def _experience_features(row: dict, career: list, jd: dict) -> dict:
    yoe = row.get("years_of_experience") or 0

    # Score years_of_experience against JD range (5-9 years ideal)
    min_exp = jd["min_experience_years"]
    max_exp = jd["max_experience_years"]

    if yoe < min_exp:
        exp_score = yoe / min_exp          # partial credit below minimum
    elif yoe <= max_exp:
        exp_score = 1.0                    # perfect range
    else:
        exp_score = max(0.6, 1 - (yoe - max_exp) * 0.05)  # slight penalty above

    # Has worked at a product company (not only services)?
    product_company_exp = _has_product_company(career)

    # Total months in AI/ML-related roles
    ai_months = _ai_role_months(career)

    # Consulting-only flag
    only_consulting = _is_consulting_only(career)

    return {
        "years_of_experience":      yoe,
        "experience_score":         exp_score,
        "product_company_exp":      int(product_company_exp),
        "ai_role_months":           ai_months,
        "consulting_only":          int(only_consulting),
    }


def _has_product_company(career: list) -> bool:
    """True if candidate has worked at any non-consulting product company."""
    for role in career:
        company = role.get("company", "").lower()
        if not any(c in company for c in DISQUALIFIER_COMPANIES):
            return True
    return False


def _ai_role_months(career: list) -> int:
    """Count months spent in AI/ML/data-adjacent roles."""
    AI_KEYWORDS = [
        "ml", "machine learning", "ai ", "data science",
        "nlp", "deep learning", "research", "ranking",
        "retrieval", "recommendation", "engineer",
    ]
    total = 0
    for role in career:
        title = role.get("title", "").lower()
        desc  = role.get("description", "").lower()
        if any(kw in title or kw in desc for kw in AI_KEYWORDS):
            total += role.get("duration_months", 0)
    return total


def _is_consulting_only(career: list) -> bool:
    """True if ALL career history is at known consulting firms."""
    if not career:
        return False
    return all(
        any(c in role.get("company", "").lower() for c in DISQUALIFIER_COMPANIES)
        for role in career
    )


# ── 3. Education features ──────────────────────────────────────────────────

def _education_features(education: list) -> dict:
    TIER_SCORES = {
        "tier_1": 1.0,
        "tier_2": 0.75,
        "tier_3": 0.50,
        "tier_4": 0.25,
        "unknown": 0.30,
    }
    RELEVANT_FIELDS = [
        "computer science", "information technology", "electronics",
        "electrical", "mathematics", "statistics", "data", "ai", "ml",
    ]

    if not education:
        return {"education_tier_score": 0.2, "relevant_field": 0}

    best = max(
        education,
        key=lambda e: TIER_SCORES.get(e.get("tier", "unknown"), 0.3)
    )

    tier_score = TIER_SCORES.get(best.get("tier", "unknown"), 0.3)

    field = best.get("field_of_study", "").lower()
    relevant = int(any(f in field for f in RELEVANT_FIELDS))

    return {
        "education_tier_score": tier_score,
        "relevant_field":       relevant,
    }


# ── 4. Certification features ──────────────────────────────────────────────

def _certification_features(certifications: list) -> dict:
    AI_CERT_KEYWORDS = [
        "machine learning", "deep learning", "nlp", "ai",
        "tensorflow", "pytorch", "aws", "gcp", "azure",
        "data science", "mlops",
    ]
    count = len(certifications)
    ai_count = sum(
        1 for cert in certifications
        if any(kw in cert.get("name", "").lower() for kw in AI_CERT_KEYWORDS)
    )
    return {
        "cert_count":    count,
        "ai_cert_count": ai_count,
    }


# ── 5. Behavioral signal features ─────────────────────────────────────────

def _signal_features(row: dict) -> dict:
    # Days since last active
    last_active = row.get("last_active_date")
    if last_active:
        try:
            last_dt  = datetime.strptime(last_active, "%Y-%m-%d").date()
            days_inactive = (date.today() - last_dt).days
        except ValueError:
            days_inactive = 999
    else:
        days_inactive = 999

    # Recency score — penalize candidates inactive > 90 days
    if days_inactive <= 30:
        recency_score = 1.0
    elif days_inactive <= 90:
        recency_score = 0.75
    elif days_inactive <= 180:
        recency_score = 0.50
    else:
        recency_score = 0.20

    # GitHub score (-1 means not linked → treat as 0)
    github = row.get("github_activity_score", -1)
    github_score = max(github, 0) / 100.0

    # Response rate
    response_rate = row.get("recruiter_response_rate") or 0.0

    # Notice period score — prefer < 30 days
    notice = row.get("notice_period_days") or 90
    if notice <= 30:
        notice_score = 1.0
    elif notice <= 60:
        notice_score = 0.70
    elif notice <= 90:
        notice_score = 0.40
    else:
        notice_score = 0.10

    # Open to work bonus
    open_to_work = int(row.get("open_to_work", False) or False)

    return {
        "days_inactive":            days_inactive,
        "recency_score":            recency_score,
        "github_score":             github_score,
        "recruiter_response_rate":  response_rate,
        "notice_score":             notice_score,
        "open_to_work":             open_to_work,
        "interview_completion_rate": row.get("interview_completion_rate") or 0.0,
        "profile_completeness":     (row.get("profile_completeness") or 0) / 100.0,
    }


# ── 6. Location features ───────────────────────────────────────────────────

def _location_features(row: dict, jd: dict) -> dict:
    location = (row.get("location") or "").lower()
    country  = (row.get("country") or "").lower()

    preferred = jd["preferred_locations"]
    in_preferred = int(any(loc in location for loc in preferred))
    in_india     = int("india" in country)
    willing_to_relocate = int(row.get("willing_to_relocate") or False)

    location_score = 1.0 if in_preferred else (0.7 if in_india else (0.5 if willing_to_relocate else 0.2))

    return {
        "in_preferred_location": in_preferred,
        "in_india":              in_india,
        "willing_to_relocate":   willing_to_relocate,
        "location_score":        location_score,
    }


# ── 7. Disqualifier features ───────────────────────────────────────────────

def _disqualifier_features(row: dict, career: list, jd: dict) -> dict:
    title = (row.get("current_title") or "").lower()

    # Title mismatch — non-technical roles are a red flag
    disq_titles = jd["disqualifier_titles"]
    title_mismatch = int(any(t in title for t in disq_titles))

    # Consulting-only career
    consulting_only = _is_consulting_only(career)

    # Penalty multiplier — reduces final score
    penalty = 1.0
    if title_mismatch:
        penalty -= 0.30
    if consulting_only:
        penalty -= 0.20

    return {
        "title_mismatch":   title_mismatch,
        "penalty":          max(penalty, 0.1),   # floor at 0.1
    }