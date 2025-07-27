import re
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


def _normalize_text(text):
    """
    Normalizes text by converting to lowercase and replacing common delimiters
    (hyphens, underscores, slashes) with spaces for consistent keyword matching.
    Also handles special cases like 'UI/UX' and 'AI/ML'.
    """
    if text is None:
        return ""

    # Special handling for common compound terms
    text = text.replace("UI/UX", "ui ux").replace("AI/ML", "ai ml")

    # Convert to lowercase and replace hyphens, underscores, and slashes with spaces
    normalized = re.sub(r'[_\-/]', ' ', text.lower())

    # Remove multiple spaces and strip
    return ' '.join(normalized.split()).strip()


def categorize_gig(title, skills, description):
    """
    Categorize a gig based on title, skills, and description using a weighted
    keyword matching system with improved keyword selection and scoring.
    """
    # Normalize all input text first
    normalized_title = _normalize_text(title)
    normalized_skills = [_normalize_text(s) for s in skills if s]
    normalized_description = _normalize_text(description)

    # Combine all normalized text for searching
    combined_text = f"{normalized_title} {' '.join(normalized_skills)} {normalized_description}"

    # --- Non-gig filters ---
    if re.search(r"\b(for sale|selling account|account for sale|offer my|transfer my)\b", combined_text):
        return "Other"

    # --- Define categories and their keywords ---
    # Structure: Each category has:
    # - primary_keywords (highly specific, score +3)
    # - secondary_keywords (related terms, score +2)
    # - skill_keywords (specific skills/tools, score +4)
    # - exclude_keywords (terms that disqualify the category if present)
    categories_data = [
        {
            "name": "AI/ML & Data Science",
            "primary_keywords": [
                "llm", "genai", "generative ai", "computer vision", "nlp",
                "neural network", "predictive modeling", "data mining",
                "transformer model", "deep learning", "machine learning",
                "data science", "data analysis", "ai model", "mlops"
            ],
            "secondary_keywords": [
                "tensorflow", "pytorch", "chatgpt", "openai", "bard", "gemini",
                "ai", "ml", "artificial intelligence", "data visualization",
                "big data", "data pipeline", "feature engineering"
            ],
            "skill_keywords": [
                "tensorflow", "pytorch", "keras", "scikit learn", "spark",
                "hadoop", "numpy", "pandas", "matplotlib", "seaborn",
                "opencv", "nltk", "spacy", "huggingface", "langchain"
            ],
            "exclude_keywords": ["web design", "mobile app", "game"]  # Avoid overlap with other categories
        },
        {
            "name": "Web Development",
            "primary_keywords": [
                "web development", "frontend development", "backend development",
                "fullstack development", "web application", "website development",
                "ecommerce development", "web service", "web portal"
            ],
            "secondary_keywords": [
                "react", "angular", "vue", "django", "flask", "laravel",
                "wordpress", "shopify", "magento", "php", "javascript",
                "typescript", "html", "css", "web design", "responsive design",
                "node", "graphql", "rest api", "web app", "mern", "mean", "mevn"
            ],
            "skill_keywords": [
                "react.js", "angular.js", "vue.js", "next.js", "nuxt.js",
                "express.js", "django", "flask", "laravel", "spring boot",
                "ruby on rails", "wordpress", "shopify", "webpack", "babel"
            ],
            "exclude_keywords": ["mobile app", "game dev", "desktop application"]
        },
        {
            "name": "Mobile Development",
            "primary_keywords": [
                "mobile app development", "ios app", "android app",
                "cross platform app", "mobile application", "app store",
                "play store", "hybrid app"
            ],
            "secondary_keywords": [
                "flutter", "react native", "xamarin", "swift", "kotlin",
                "mobile ui", "app development", "mobile design", "ios",
                "android", "mobile game"
            ],
            "skill_keywords": [
                "flutter", "react native", "xamarin", "swiftui", "jetpack compose",
                "kotlin", "objective c", "firebase", "appium", "fastlane"
            ],
            "exclude_keywords": ["web development", "desktop application"]
        },
        {
            "name": "Software Engineering",
            "primary_keywords": [
                "software engineering", "software development", "api development",
                "system design", "software architecture", "code review",
                "refactoring", "software design", "clean code"
            ],
            "secondary_keywords": [
                "algorithm", "data structure", "microservice", "desktop application",
                "c++", "java", "golang", "c#", ".net", "developer", "programming",
                "coding", "backend", "server side"
            ],
            "skill_keywords": [
                "java", "python", "c++", "c#", ".net core", "spring framework",
                "hibernate", "jpa", "design patterns", "oop", "functional programming",
                "multithreading", "concurrency"
            ],
            "exclude_keywords": ["web design", "mobile app", "data science"]
        },
        {
            "name": "Game Development",
            "primary_keywords": [
                "game development", "game design", "game programming",
                "game mechanics", "indie game", "video game", "game engine",
                "game physics", "character design", "level design"
            ],
            "secondary_keywords": [
                "unity", "unreal engine", "vr game", "ar game", "2d game",
                "3d game", "game art", "game assets", "game scripting", "shader"
            ],
            "skill_keywords": [
                "unity", "unreal engine", "godot", "cryengine", "blender",
                "maya", "3ds max", "substance painter", "shader programming",
                "hlsl", "glsl"
            ],
            "exclude_keywords": ["web development", "mobile app"]
        },
        {
            "name": "Design & Creative",
            "primary_keywords": [
                "graphic design", "logo design", "ui ux design", "illustration",
                "brand identity", "motion graphics", "video editing",
                "3d modeling", "animation", "print design", "vector art",
                "user interface design", "user experience design", "typography"
            ],
            "secondary_keywords": [
                "photoshop", "illustrator", "figma", "adobe xd", "sketch",
                "after effects", "premiere pro", "blender", "maya", "cinema 4d",
                "visual design", "creative", "art", "drawing"
            ],
            "skill_keywords": [
                "adobe photoshop", "adobe illustrator", "figma", "sketch",
                "adobe after effects", "adobe premiere", "adobe indesign",
                "coreldraw", "affinity designer", "procreate", "zbrush"
            ],
            "exclude_keywords": ["web development", "coding", "programming"]
        },
        {
            "name": "Digital Marketing",
            "primary_keywords": [
                "seo", "search engine optimization", "google ads", "facebook ads",
                "ppc", "social media marketing", "email marketing",
                "affiliate marketing", "content marketing", "digital marketing",
                "marketing strategy", "influencer marketing", "brand marketing"
            ],
            "secondary_keywords": [
                "smm", "sem", "google analytics", "google tag manager",
                "marketing campaign", "market research", "lead generation",
                "conversion optimization", "advertising", "b2b marketing"
            ],
            "skill_keywords": [
                "google ads", "facebook ads manager", "google analytics",
                "google search console", "google data studio", "hubspot",
                "mailchimp", "hootsuite", "buffer", "ahrefs", "semrush",
                "moz"
            ],
            "exclude_keywords": ["web development", "graphic design"]
        },
        {
            "name": "Content & Writing",
            "primary_keywords": [
                "content writing", "copywriting", "blog writing", "technical writing",
                "ghostwriting", "creative writing", "article writing",
                "ebook writing", "script writing", "academic writing",
                "business writing", "proofreading", "editing"
            ],
            "secondary_keywords": [
                "transcription", "resume writing", "translation", "journalism",
                "press release", "content strategy", "seo writing",
                "content marketing", "storytelling", "white paper"
            ],
            "skill_keywords": [
                "grammarly", "hemingway editor", "scrivener", "latex",
                "markdown", "seo tools", "cms", "wordpress editor"
            ],
            "exclude_keywords": ["data entry", "programming"]
        },
        {
            "name": "System Admin & DevOps",
            "primary_keywords": [
                "devops", "cloud computing", "kubernetes", "docker",
                "ci cd", "infrastructure as code", "server management",
                "cloud architecture", "site reliability", "system administration"
            ],
            "secondary_keywords": [
                "aws", "azure", "gcp", "jenkins", "terraform", "ansible",
                "linux", "cloud", "serverless", "microservices", "scaling"
            ],
            "skill_keywords": [
                "kubernetes", "docker", "terraform", "ansible", "prometheus",
                "grafana", "jenkins", "gitlab ci", "github actions", "aws",
                "azure", "gcp", "linux", "bash", "powershell"
            ],
            "exclude_keywords": ["web development", "mobile app"]
        },
        {
            "name": "IT & Support",
            "primary_keywords": [
                "it support", "helpdesk", "technical support", "network administration",
                "system administration", "it infrastructure", "it consulting",
                "cybersecurity", "information security", "network security"
            ],
            "secondary_keywords": [
                "troubleshooting", "hardware", "software installation", "active directory",
                "windows server", "linux server", "database administration", "sql",
                "oracle", "backup recovery", "disaster recovery"
            ],
            "skill_keywords": [
                "windows server", "active directory", "linux", "vmware", "hyperv",
                "office 365", "microsoft exchange", "cisco", "jira", "servicenow",
                "splunk", "wireshark"
            ],
            "exclude_keywords": ["web development", "software development"]
        },
        {
            "name": "Business & Consulting",
            "primary_keywords": [
                "business consulting", "management consulting", "strategy consulting",
                "business analysis", "project management", "financial consulting",
                "hr consulting", "legal consulting", "startup consulting"
            ],
            "secondary_keywords": [
                "scrum", "agile", "finance", "bookkeeping", "human resources",
                "virtual assistant", "customer service", "sales", "business plan",
                "market research", "feasibility study"
            ],
            "skill_keywords": [
                "scrum", "agile", "pmp", "prince2", "six sigma", "lean",
                "business model canvas", "swot analysis", "quickbooks",
                "xero", "salesforce", "sap"
            ],
            "exclude_keywords": ["web development", "graphic design"]
        },
        {
            "name": "Engineering & Architecture",
            "primary_keywords": [
                "civil engineering", "mechanical engineering", "electrical engineering",
                "architecture", "architectural design", "structural engineering",
                "cad design", "3d modeling", "product design", "industrial design"
            ],
            "secondary_keywords": [
                "revit", "autocad", "solidworks", "cad", "drafting", "bim",
                "fea", "cfd", "prototyping", "construction", "mep"
            ],
            "skill_keywords": [
                "autocad", "revit", "solidworks", "catia", "fusion 360",
                "inventor", "sketchup", "ansys", "matlab", "staad pro",
                "etabs"
            ],
            "exclude_keywords": ["web development", "software development"]
        },
        {
            "name": "Admin & Data Entry",
            "primary_keywords": [
                "data entry", "copy typing", "manual entry", "excel work",
                "form filling", "spreadsheet", "typing job", "virtual assistant",
                "administrative support", "office assistant"
            ],
            "secondary_keywords": [
                "word processing", "data processing", "transcription",
                "bookkeeping", "customer support", "email management",
                "calendar management", "research assistant"
            ],
            "skill_keywords": [
                "microsoft excel", "google sheets", "microsoft word",
                "google docs", "quickbooks", "data cleaning", "type 60 wpm",
                "zapier", "airtable"
            ],
            "exclude_keywords": ["web development", "graphic design"]
        }
    ]

    # Score calculation with exclusion handling
    category_scores = defaultdict(int)

    for category_data in categories_data:
        category_name = category_data["name"]

        # Check for exclusion keywords first
        if any(re.search(r'\b' + re.escape(kw) + r'\b', combined_text)
               for kw in category_data.get("exclude_keywords", [])):
            continue

        # Score primary keywords (+3)
        for kw in category_data["primary_keywords"]:
            if re.search(r'\b' + re.escape(kw) + r'\b', combined_text):
                category_scores[category_name] += 3

        # Score secondary keywords (+2)
        for kw in category_data["secondary_keywords"]:
            if re.search(r'\b' + re.escape(kw) + r'\b', combined_text):
                category_scores[category_name] += 2

        # Score skill keywords (+4)
        for kw in category_data["skill_keywords"]:
            if re.search(r'\b' + re.escape(kw) + r'\b', combined_text):
                category_scores[category_name] += 4

    # Get the best category
    if category_scores:
        best_category = max(category_scores.items(), key=lambda x: x[1])[0]
        # Only return if score is above threshold (helps filter weak matches)
        if category_scores[best_category] >= 5:
            return best_category

    return "Other"


def transform_gig_data(raw_gigs):
    """
    Applies transformation (e.g., categorization) to a list of raw gig dictionaries.
    Returns a list of transformed gig dictionaries.
    """
    print(f"Transforming {len(raw_gigs)} gigs...")
    transformed_gigs = []

    # Track category distribution for debugging
    category_counts = defaultdict(int)

    for gig in raw_gigs:
        transformed_gig = gig.copy()
        category = categorize_gig(
            transformed_gig.get("title"),
            transformed_gig.get("skills", []),
            transformed_gig.get("description")
        )
        transformed_gig["category"] = category
        transformed_gigs.append(transformed_gig)
        category_counts[category] += 1

    print(f"Transformed {len(transformed_gigs)} gigs.")
    print("Category distribution:")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{cat}: {count}")

    return transformed_gigs