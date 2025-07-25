import time
from etl.extract.freelancer_extractor import extract_freelancer_gigs
from etl.transform.data_transformer import transform_gig_data
from etl.load.db_loader import load_gigs_to_db
from utils.db_utils import get_db_connection, close_db_connection

FREELANCER_RSS_FEED = "https://www.freelancer.com/rss.xml"

def run_etl_process():
    """
    Orchestrates the ETL pipeline for gig data.
    """
    print("--- Starting ETL Process ---")
    conn = None
    try:
        # 1. Get database connection
        conn = get_db_connection()
        if not conn:
            print("Failed to get database connection. Aborting ETL.")
            return False

        # 2. Extract Data
        raw_gigs = extract_freelancer_gigs(FREELANCER_RSS_FEED)
        if not raw_gigs:
            print("No new raw gigs extracted. ETL finished.")
            return True

        # 3. Transform Data
        transformed_gigs = transform_gig_data(raw_gigs)
        if not transformed_gigs:
            print("No gigs remaining after transformation. ETL finished.")
            return True

        # 4. Load Data
        loaded_count = load_gigs_to_db(transformed_gigs, conn)
        print(f"ETL Process completed. Successfully loaded {loaded_count} new gigs.")
        return True

    except Exception as e:
        print(f"An unexpected error occurred during ETL: {e}")
        return False
    finally:
        if conn:
            close_db_connection(conn)

if __name__ == "__main__":
    print("Orchestrator started. Running ETL process once...")
    success = run_etl_process()
    if success:
        print("Orchestrator finished ETL run successfully.")
    else:
        print("Orchestrator finished ETL run with errors.")