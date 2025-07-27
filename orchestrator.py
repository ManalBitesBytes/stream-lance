import time
import sys
import schedule
import logging

from etl.extract.freelancer_extractor import extract_freelancer_gigs
from etl.transform.data_transformer import transform_gig_data
from etl.load.db_loader import load_gigs_to_db

from utils.db_utils import get_db_connection, close_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



FREELANCER_RSS_FEED = "https://www.freelancer.com/rss.xml"
SLEEP_INTERVAL_SECONDS_SCHEDULE_CHECK = 60
ETL_RUN_INTERVAL_HOURS = 1


def run_etl_process():
    """
    Orchestrates the ETL pipeline for gig data.
    This function will be called by the scheduler.
    """
    logger.info(f"--- Starting ETL Process at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    conn = None
    try:
        # 1. Get database connection
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to get database connection. Aborting ETL.")
            return False

        # 2. Extract Data
        logger.info(f"Extracting gigs from {FREELANCER_RSS_FEED}...")
        raw_gigs = extract_freelancer_gigs(FREELANCER_RSS_FEED)
        logger.info(f"Extracted {len(raw_gigs)} gigs.")

        if not raw_gigs:
            logger.info("No new raw gigs extracted. ETL finished.")
            return True

        # 3. Transform Data
        # This function is imported from etl.transform.data_transformer
        logger.info(f"Transforming {len(raw_gigs)} gigs...")
        transformed_gigs = transform_gig_data(raw_gigs)
        logger.info(f"Transformed {len(transformed_gigs)} gigs.")

        if not transformed_gigs:
            logger.info("No gigs remaining after transformation. ETL finished.")
            return True

        # 4. Load Data
        logger.info(f"Loading {len(transformed_gigs)} gigs into the database...")
        loaded_count = load_gigs_to_db(transformed_gigs, conn)
        logger.info(f"ETL Process completed. Successfully loaded {loaded_count} new gigs.")
        return True

    except Exception as e:
        logger.error(f"An unexpected error occurred during ETL: {e}", exc_info=True)
        return False
    finally:
        if conn:
            close_db_connection(conn)
            logger.info("Database connection closed.")
        logger.info("Orchestrator finished ETL run.")


def main():
    """
    Main function to set up and run the scheduled ETL process.
    """
    logger.info("Orchestrator started. Setting up hourly ETL schedule...")

    schedule.every(ETL_RUN_INTERVAL_HOURS).hours.do(run_etl_process)

    logger.info("Performing initial ETL run...")
    success = run_etl_process()
    if success:
        logger.info("Initial ETL run completed successfully.")
    else:
        logger.error("Initial ETL run completed with errors.")

    while True:
        try:
            schedule.run_pending()
            time.sleep(SLEEP_INTERVAL_SECONDS_SCHEDULE_CHECK)
        except KeyboardInterrupt:
            logger.info("\nOrchestrator stopped by user (Ctrl+C). Exiting.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}", exc_info=True)
            time.sleep(SLEEP_INTERVAL_SECONDS_SCHEDULE_CHECK)  # Prevent rapid error looping


if __name__ == "__main__":
    main()