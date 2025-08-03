import time
import sys
import schedule
import logging
from datetime import datetime, timedelta
from etl.extract.freelancer_extractor import extract_freelancer_gigs
from etl.transform.data_transformer import transform_gig_data
from etl.load.db_loader import load_gigs_to_db
from utils.db_utils import get_db_connection, close_db_connection
from notification.notifier import send_notifications
from app import create_app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

FREELANCER_RSS_FEED = "https://www.freelancer.com/rss.xml"
SLEEP_INTERVAL_SECONDS_SCHEDULE_CHECK = 60
ETL_RUN_INTERVAL_HOURS = 1

_flask_app_instance = None

def setup_flask_app():
    """
    Sets up the Flask application instance without pushing context.
    """
    global _flask_app_instance
    if _flask_app_instance is None:
        _flask_app_instance = create_app()
        logger.info("Flask app instance created for orchestrator.")

def run_etl_process():
    logger.info(f"--- Starting ETL Process at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to get database connection. Aborting ETL.")
            return False

        logger.info(f"Extracting gigs from {FREELANCER_RSS_FEED}...")
        raw_gigs = extract_freelancer_gigs(FREELANCER_RSS_FEED)
        logger.info(f"Extracted {len(raw_gigs)} gigs.")

        if not raw_gigs:
            logger.info("No new raw gigs extracted. ETL finished.")
            return True

        logger.info(f"Transforming {len(raw_gigs)} gigs...")
        transformed_gigs = transform_gig_data(raw_gigs)
        logger.info(f"Transformed {len(transformed_gigs)} gigs.")

        if not transformed_gigs:
            logger.info("No gigs remaining after transformation. ETL finished.")
            return True

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
            logger.info("Database connection closed (psycopg2).")
        logger.info("Orchestrator finished ETL run.")

def main():
    logger.info("Orchestrator started. Setting up hourly ETL and Notification schedules...")
    setup_flask_app()
    schedule.every(ETL_RUN_INTERVAL_HOURS).hours.at(":00").do(run_etl_process)
    schedule.every(ETL_RUN_INTERVAL_HOURS).hours.at(":22").do(send_notifications, _flask_app_instance)
    logger.info("Performing initial ETL run...")
    run_etl_process()
    logger.info("Performing initial Notification run...")
    send_notifications(_flask_app_instance)
    logger.info("Initial ETL and Notification runs completed. Entering scheduling loop.")
    while True:
        try:
            schedule.run_pending()
            time.sleep(SLEEP_INTERVAL_SECONDS_SCHEDULE_CHECK)
        except KeyboardInterrupt:
            logger.info("\nOrchestrator stopped by user (Ctrl+C). Exiting.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}", exc_info=True)
            time.sleep(SLEEP_INTERVAL_SECONDS_SCHEDULE_CHECK)

if __name__ == "__main__":
    main()