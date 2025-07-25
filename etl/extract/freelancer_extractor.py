import feedparser
import re
from datetime import datetime


def _extract_skills_from_entry(entry_tags):
    """
    Extracts skills from the 'tags' list within the feedparser entry
    for Freelancer.com.
    """
    if entry_tags:
        return [tag['term'] for tag in entry_tags if 'term' in tag]
    return []


def _parse_budget_from_summary(summary_text):
    """
    Extracts budget amount and currency from the 'summary' field
    of a Freelancer.com RSS entry.
    """
    amount = None
    currency = None

    match = re.search(
        r"Budget:\s*(?:([\$€£¥₹])\s*)?([\d,\.]+)(?:\s*-\s*(?:[\$€£¥₹])?\s*([\d,\.]+))?\s*(USD|CAD|INR|AUD|NZD|EUR|GBP|HKD|JPY)?",
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
            elif match.group(1):  # Fallback to symbol
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
                currency = 'UNKNOWN'  # Or set to None if you prefer no currency
        except ValueError:
            print(f"Warning: Could not parse budget numbers from summary: {summary_text}")
            amount = None
            currency = None

    return amount, currency


def extract_freelancer_gigs(feed_url):
    """
    Fetches and parses gig data from a Freelancer.com RSS feed.
    Returns a list of dictionaries with extracted raw data.
    """
    print(f"Extracting gigs from {feed_url}...")
    feed = feedparser.parse(feed_url)

    if not feed.entries:
        print(f"No entries found in feed {feed_url}.")
        return []

    extracted_gigs = []
    for i, entry in enumerate(feed.entries):
        title = entry.get('title')
        link = entry.get('link')
        description = entry.get('summary') or entry.get('description') or entry.get('content', [{}])[0].get('value')

        published = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'published'):
            try:
                published = datetime.strptime(entry.published, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    published = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
                except ValueError:
                    try:
                        published = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
                    except ValueError:
                        # print(f"Warning: Could not parse date string for '{title}': {entry.published}")
                        published = None

        skills = _extract_skills_from_entry(entry.get('tags'))
        budget_amount, budget_currency = _parse_budget_from_summary(description or "")

        extracted_gigs.append({
            "title": title,
            "link": link,
            "description": description,
            "published_at": published,  # Changed key to match DB schema
            "budget_amount": budget_amount,
            "budget_currency": budget_currency,
            "skills": skills,
            "source_platform": "Freelancer",  # Hardcoded for now
        })

    print(f"Extracted {len(extracted_gigs)} gigs.")
    return extracted_gigs