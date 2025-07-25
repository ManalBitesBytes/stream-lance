import re


def categorize_gig(title, skills, description):
    """
    Categorize a gig based on title, skills, and description using a weighted
    keyword matching system, with added category for admin/data entry, and
    filtering for non-gig posts (e.g., account for sale).
    """
    title_lower = (title or "").lower()
    skills_lower = [s.lower() for s in skills if s]
    description_lower = (description or "").lower()

    combined_text = f"{title_lower} {' '.join(skills_lower)} {description_lower}"

    # --- Non-gig filters ---
    if re.search(r"\b(for sale|selling account|account for sale|offer my|transfer my)\b", combined_text):
        return "Other"

    # --- Define categories ---
    categories_data = [
        {
            "name": "AI/ML & Data Science",
            "keywords": [
                "machine learning", "deep learning", "computer vision", "llm", "genai",
                "generative ai", "data science", "data analysis", "nlp", "neural network",
                "tensorflow", "pytorch", "mlops", "ai model", "predictive modeling",
                "data mining", "chatgpt", "openai", "bard", "gemini", "transformer model"
            ],
            "skill_keywords": ["ai", "ml", "data-science", "tensorflow", "pytorch"]
        },
        {
            "name": "Web Development",
            "keywords": [
                "web development", "frontend", "backend", "fullstack", "react.js",
                "angular", "vue.js", "django", "flask", "laravel", "wordpress",
                "e-commerce", "shopify", "magento", "php", "javascript", "html",
                "css", "web design", "responsive", "node.js", "graphql", "rest api"
            ],
            "skill_keywords": ["web", "frontend", "backend", "fullstack", "react", "node"]
        },
        {
            "name": "Mobile Development",
            "keywords": [
                "mobile app", "ios", "android", "flutter", "react native", "xamarin",
                "swift", "kotlin", "cross-platform", "mobile ui"
            ],
            "skill_keywords": ["mobile", "flutter", "react-native", "ios", "android"]
        },
        {
            "name": "Software Engineering",
            "keywords": [
                "software engineer", "software developer", "api development",
                "algorithm", "data structure", "microservice", "desktop app",
                "c++", "java", "golang", "c#", ".net", "system design", "developer"
            ],
            "skill_keywords": ["software", "system-design", "java", "python", "c++", "c#"]
        },
        {
            "name": "Game Development",
            "keywords": [
                "game development", "unity", "unreal", "game design", "vr game",
                "ar game", "game mechanics", "indie game", "character design"
            ],
            "skill_keywords": ["unity", "unreal", "gamedev", "game-dev"]
        },
        {
            "name": "Design & Creative",
            "keywords": [
                "graphic design", "logo design", "ui/ux", "illustration", "adobe xd",
                "figma", "sketch", "photoshop", "motion graphics", "video editing",
                "branding", "3d modeling", "animation", "creative"
            ],
            "skill_keywords": ["design", "ui", "ux", "graphic-design", "photoshop", "illustrator"]
        },
        {
            "name": "Digital Marketing",
            "keywords": [
                "seo", "google ads", "facebook ads", "ppc", "social media",
                "email marketing", "affiliate marketing", "content marketing",
                "smm", "sem", "analytics", "marketing campaign"
            ],
            "skill_keywords": ["marketing", "seo", "smm", "digital-marketing"]
        },
        {
            "name": "Content & Writing",
            "keywords": [
                "content writing", "copywriting", "blog writing", "technical writing",
                "proofreading", "ghostwriting", "editing", "creative writing",
                "transcription", "resume writing", "translation"
            ],
            "skill_keywords": ["writing", "copywriting", "content"]
        },
        {
            "name": "System Admin & DevOps",
            "keywords": [
                "devops", "aws", "azure", "gcp", "cloud computing", "kubernetes",
                "docker", "ci/cd", "jenkins", "terraform", "ansible", "linux",
                "system administration", "networking"
            ],
            "skill_keywords": ["devops", "aws", "azure", "gcp", "linux", "docker"]
        },
        {
            "name": "IT & Support",
            "keywords": [
                "it support", "helpdesk", "cyber security", "network admin",
                "sql server", "oracle", "troubleshooting", "system support"
            ],
            "skill_keywords": ["it", "support", "networking", "security"]
        },
        {
            "name": "Business & Consulting",
            "keywords": [
                "consulting", "strategy", "business analysis", "project management",
                "scrum", "agile", "finance", "bookkeeping", "hr", "legal",
                "virtual assistant", "market research", "customer service"
            ],
            "skill_keywords": ["business", "consulting", "project-management", "finance", "hr"]
        },
        {
            "name": "Engineering & Architecture",
            "keywords": [
                "civil engineering", "mechanical engineering", "electrical engineering",
                "architecture", "revit", "autocad", "solidworks", "cad", "drafting"
            ],
            "skill_keywords": ["engineering", "cad", "architecture"]
        },
        {
            "name": "Admin & Data Entry",  # ✅ NEW CATEGORY
            "keywords": [
                "data entry", "copy typing", "manual entry", "excel work", "form filling",
                "spreadsheet", "typing job", "office assistant", "admin work"
            ],
            "skill_keywords": ["data-entry", "typing", "excel", "copy-typing", "transcription"]
        }
    ]

    best_category = "Other"
    max_score = 0

    for category_data in categories_data:
        score = 0
        # Skill keyword weight: 3
        for kw in category_data["skill_keywords"]:
            if re.search(r'\b' + re.escape(kw) + r'\b', combined_text):
                score += 3

        # General keyword weight: 1
        for kw in category_data["keywords"]:
            if re.search(r'\b' + re.escape(kw) + r'\b', combined_text):
                score += 1

        if score > max_score:
            max_score = score
            best_category = category_data["name"]

    return best_category


def transform_gig_data(raw_gigs):
    """
    Applies transformation (e.g., categorization) to a list of raw gig dictionaries.
    Returns a list of transformed gig dictionaries.
    """
    print(f"Transforming {len(raw_gigs)} gigs...")
    transformed_gigs = []
    for gig in raw_gigs:
        # Create a copy to avoid modifying the original raw data dict
        transformed_gig = gig.copy()

        # Apply categorization
        transformed_gig["category"] = categorize_gig(
            transformed_gig.get("title"),
            transformed_gig.get("skills", []),
            transformed_gig.get("description")
        )
        transformed_gigs.append(transformed_gig)

    print(f"Transformed {len(transformed_gigs)} gigs.")
    return transformed_gigs