import psycopg2
from psycopg2 import extras  # For execute_values
from datetime import datetime


def load_gigs_to_db(gigs, conn):
    """
    Loads a list of transformed gig dictionaries into the 'gigs' table.
    Handles duplicate links using ON CONFLICT DO NOTHING.
    """
    if not gigs:
        print("No gigs to load.")
        return 0

    cursor = conn.cursor()

    insert_sql = """
                 INSERT INTO gigs (title, link, description, published_at, category,
                                   budget_amount, budget_currency, skills, source_platform)
                 VALUES %s ON CONFLICT (link) DO NOTHING; \
                 """

    values = []
    for gig in gigs:
        values.append((
            gig.get('title'),
            gig.get('link'),
            gig.get('description'),
            gig.get('published_at'),
            gig.get('category'),
            gig.get('budget_amount'),
            gig.get('budget_currency'),
            gig.get('skills'),  # psycopg2 will handle list -> TEXT[]
            gig.get('source_platform')
        ))

    try:
        psycopg2.extras.execute_values(cursor, insert_sql, values, page_size=1000)
        conn.commit()
        print(f"Loaded {cursor.rowcount} new gigs into the database.")
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        print(f"Error loading gigs to database: {e}")
        return 0
    finally:
        cursor.close()