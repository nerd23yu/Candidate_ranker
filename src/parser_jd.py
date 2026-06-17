from docx import Document

def parse_jd(filepath: str) -> dict:
    MUST_HAVE_SKILLS = [
        "embeddings", "sentence-transformers", "vector database",
        "pinecone", "weaviate", "qdrant", "milvus", "faiss",
        "opensearch", "elasticsearch", "hybrid search",
        "retrieval", "ranking", "re-ranking", "ndcg", "mrr", "map",
        "python", "nlp", "information retrieval",
    ]

    NICE_TO_HAVE_SKILLS = [
        "lora", "qlora", "peft", "fine-tuning", "fine tuning",
        "learning to rank", "xgboost", "distributed systems",
        "large scale inference", "open source", "rag",
        "recommendation system", "search",
    ]

    DISQUALIFIER_COMPANIES = [
        "tcs", "infosys", "wipro", "accenture",
        "cognizant", "capgemini",
    ]

    DISQUALIFIER_TITLES = [
        "marketing manager", "operations manager", "accountant",
        "graphic designer", "civil engineer", "mechanical engineer",
        "sales executive", "customer support", "content writer",
        "hr manager", "business analyst", "project manager",
    ]

    PREFERRED_LOCATIONS = [
        "pune", "noida", "hyderabad", "mumbai", "delhi",
        "bangalore", "bengaluru", "gurugram", "gurgaon",
    ]

    return {
        "must_have_skills":         MUST_HAVE_SKILLS,
        "nice_to_have_skills":      NICE_TO_HAVE_SKILLS,
        "disqualifier_companies":   DISQUALIFIER_COMPANIES,
        "disqualifier_titles":      DISQUALIFIER_TITLES,
        "preferred_locations":      PREFERRED_LOCATIONS,
        "min_experience_years":     5,
        "max_experience_years":     9,
        "notice_period_preferred":  30,
        "preferred_country":        "India",
    }
