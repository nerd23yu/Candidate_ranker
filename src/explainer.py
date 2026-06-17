from src.feature_extractor import extract_features

def explain_candidate(row: dict, jd: dict) -> str:
    f = extract_features(row, jd)

    parts = []

    # --- Title & Experience ---
    title = row.get("current_title", "Unknown")
    yoe   = row.get("years_of_experience", 0)
    parts.append(f"{title} with {yoe} yrs experience")

    # --- Must-have skills ---
    skills         = row.get("skills", [])
    must_have      = jd["must_have_skills"]
    matched_skills = [
        s["name"] for s in skills
        if any(req in s["name"].lower() for req in must_have)
    ]
    if matched_skills:
        parts.append(f"matched JD skills: {', '.join(matched_skills[:4])}")
    else:
        parts.append("no direct JD skill matches")

    # --- Experience quality ---
    if f["product_company_exp"]:
        parts.append("has product company experience")
    if f["consulting_only"]:
        parts.append("consulting-only background (penalized)")

    ai_months = f["ai_role_months"]
    if ai_months >= 36:
        parts.append(f"{ai_months} months in AI/ML roles")

    # --- Education ---
    education = row.get("education", [])
    if education:
        best = education[0]
        tier = best.get("tier", "unknown")
        inst = best.get("institution", "")
        parts.append(f"{tier} institution ({inst})")

    # --- Location ---
    location = row.get("location", "")
    if f["in_preferred_location"]:
        parts.append(f"based in preferred location ({location})")
    elif f["in_india"]:
        parts.append(f"based in India ({location})")
    elif f["willing_to_relocate"]:
        parts.append("willing to relocate")
    else:
        parts.append(f"outside preferred region ({location})")

    # --- Behavioral signals ---
    days = f["days_inactive"]
    if days <= 30:
        parts.append("active in last 30 days")
    elif days <= 90:
        parts.append(f"active {days} days ago")
    else:
        parts.append(f"inactive for {days} days (penalized)")

    rr = f["recruiter_response_rate"]
    if rr >= 0.6:
        parts.append(f"high recruiter response rate ({rr:.0%})")
    elif rr <= 0.2:
        parts.append(f"low recruiter response rate ({rr:.0%})")

    notice = row.get("notice_period_days", 90)
    if notice <= 30:
        parts.append(f"notice period {notice} days (ideal)")
    elif notice > 60:
        parts.append(f"notice period {notice} days (long)")

    github = row.get("github_activity_score", -1)
    if github > 50:
        parts.append(f"strong GitHub activity ({github:.0f}/100)")
    elif github == -1:
        parts.append("no GitHub linked")

    # --- Disqualifiers ---
    if f["title_mismatch"]:
        parts.append("current title is non-technical (penalized)")

    # --- Certifications ---
    certs = row.get("certifications", [])
    if certs:
        cert_names = ", ".join(c.get("name", "") for c in certs[:2])
        parts.append(f"certifications: {cert_names}")

    return "; ".join(parts) + "."


def explain_all(df, jd: dict):
    print("Generating explanations...")
    reasonings = []
    for i, row in df.iterrows():
        r = explain_candidate(row.to_dict(), jd)
        reasonings.append(r)
    df = df.copy()
    df["reasoning"] = reasonings
    print("Explanations done!")
    return df
