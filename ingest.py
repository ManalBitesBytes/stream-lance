# ingest.py (TEMPORARY VERSION FOR EXTRACTION TESTING - CATEGORIZATION WITH DESCRIPTION)

import feedparser
import re
import json
from datetime import datetime

def extract_skills_from_entry(entry_tags):
    """
    Extracts skills from the 'tags' list within the feedparser entry
    for Freelancer.com.
    """
    if entry_tags:
        return [tag['term'] for tag in entry_tags if 'term' in tag]
    return []


def parse_budget_from_summary(summary_text):
    """
    Extracts budget amount and currency from the 'summary' field
    of a Freelancer.com RSS entry.
    """
    amount = None
    currency = None

    match = re.search(
        r"Budget:\s*(?:([\$€£¥₹])\s*)?([\d,\.]+)(?:\s*-\s*(?:[\$€£¥₹])?\s*([\d,\.]+))?\s*(USD|CAD|INR|AUD|NZD|EUR|GBP|HKD)?",
        summary_text,
        re.IGNORECASE
    )

    if match:
        try:
            budget_start_str = match.group(2).replace(',', '')
            budget_start = float(budget_start_str)

            if match.group(3):
                budget_end_str = match.group(3).replace(',', '')
                budget_end = float(budget_end_str)
                amount = (budget_start + budget_end) / 2
            else:
                amount = budget_start

            if match.group(4):
                currency = match.group(4).upper()
            elif match.group(1):
                symbol = match.group(1)
                if symbol == '$':
                    currency = 'USD'
                elif symbol == '€':
                    currency = 'EUR'
                elif symbol == '£':
                    currency = 'GBP'
                elif symbol == '¥':
                    currency = 'JPY'
                elif symbol == '₹':
                    currency = 'INR'
            else:
                currency = 'UNKNOWN'
        except ValueError:
            print(f"Warning: Could not parse budget numbers from summary: {summary_text}")
            amount = None
            currency = None

    return amount, currency


# --- CATEGORIZATION FUNCTION (UPDATED) ---

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


# --- Main Ingestion Logic (Modified for Printing Results) ---

def ingest_gigs_from_feed_and_print(feed_url, source_platform="Freelancer"):
    """
    Fetches, parses, and prints extracted gig data without db interaction.
    """
    print(f"--- Starting temporary ingestion and printing from {feed_url} ---")
    feed = feedparser.parse(feed_url)

    if not feed.entries:
        print(f"No entries found in feed {feed_url}.")
        return

    raw_data_filename = f"raw_gigs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    raw_entries_list = [entry for entry in feed.entries]
    with open(raw_data_filename, 'w', encoding='utf-8') as f:
        json.dump(raw_entries_list, f, ensure_ascii=False, indent=4)
    print(f"Raw feed data for {source_platform} saved to {raw_data_filename}")
    print(f"Found {len(feed.entries)} entries to process.")
    print("-" * 50)

    for i, entry in enumerate(feed.entries):
        print(f"\n--- Processing Entry {i + 1} ---")

        # --- Extraction Logic ---
        title = entry.get('title')
        link = entry.get('link')
        description = entry.get('summary') or entry.get('description') or entry.get('content', [{}])[0].get('value')

        published = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'published'):
            try:
                # Attempt to parse your example format first
                published = datetime.strptime(entry.published, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:  # Fallback to common feedparser format
                    published = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
                except ValueError:
                    try:  # Fallback without timezone offset
                        published = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
                    except ValueError:
                        print(f"Warning: Could not parse date string for '{title}': {entry.published}")
                        published = None

        skills = extract_skills_from_entry(entry.get('tags'))
        budget_amount, budget_currency = parse_budget_from_summary(description or "")

        # --- IMPORTANT: Pass description to categorize_gig ---
        category = categorize_gig(title or "", skills, description or "")

        # --- Prepare extracted data for printing ---
        extracted_data = {
            "title": title,
            "link": link,
            "description": description,
            "published": str(published) if published else None,
            "category": category,
            "budget_amount": budget_amount,
            "budget_currency": budget_currency,
            "skills": skills,
            "source_platform": source_platform,
        }

        # --- Print the extracted data ---
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        print("-" * 50)

    print(f"\n--- Temporary ingestion and printing from {feed_url} complete. ---")


if __name__ == "__main__":
    freelancer_rss_feed = "https://www.freelancer.com/rss.xml"
    ingest_gigs_from_feed_and_print(freelancer_rss_feed, "Freelancer")