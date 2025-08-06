import time
import sys
import schedule
import logging
from datetime import datetime, timedelta

# Assuming these functions are in the specified paths
from etl.extract.freelancer_extractor import extract_freelancer_gigs
from etl.transform.data_transformer import transform_gig_data
from etl.load.db_loader import load_gigs_to_db
from utils.db_utils import get_db_connection, close_db_connection

# NEW: Import the send_notifications function from the new notifier module
from notification.notifier import send_notifications

# NEW: Import create_app from your Flask application for context management
from app import create_app

# Removed: from app.models import db as flask_db_instance - no longer needed here


# Configure logging for orchestrator.py
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

FREELANCER_RSS_FEED = "https://www.freelancer.com/rss.xml"
SLEEP_INTERVAL_SECONDS_SCHEDULE_CHECK = 60  # How often the scheduler checks for pending tasks (every minute)
ETL_RUN_INTERVAL_HOURS = 1  # How often the ETL process should run

# Global variable to hold the Flask app instance and its context
_flask_app_instance = None
_flask_app_context = None


def setup_flask_app_context():
    """
    Sets up a Flask application context for SQLAlchemy operations.
    This is needed for the orchestrator to interact with app.models.
    """
    global _flask_app_instance, _flask_app_context
    if _flask_app_instance is None:
        _flask_app_instance = create_app()  # Create the Flask app instance
        # IMPORTANT: create_app() (from app/__init__.py) already calls db.init_app(_flask_app_instance).
        # We do NOT need to call db.init_app() again here.

        _flask_app_context = _flask_app_instance.app_context()
        _flask_app_context.push()
        logger.info("Flask app context pushed for orchestrator.")
        logger.info("SQLAlchemy instance is now linked via app context.")


def teardown_flask_app_context():
    """
    Tears down the Flask application context.
    """
    global _flask_app_context, _flask_app_instance
    if _flask_app_context:
        _flask_app_context.pop()
        _flask_app_context = None
        _flask_app_instance = None  # Reset app instance as well
        logger.info("Flask app context popped.")


def run_etl_process():
    """
    Orchestrates the ETL pipeline for gig data.
    This function will be called by the scheduler.
    """
    logger.info(f"--- Starting ETL Process at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    conn = None
    try:
        # 1. Get database connection (for psycopg2 loader)
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
            logger.info("Database connection closed (psycopg2).")
        logger.info("Orchestrator finished ETL run.")


# Wrapper function for scheduled notifications to manage Flask context
def scheduled_send_notifications_wrapper():
    """
    Wrapper to ensure Flask app context is managed for scheduled notification runs.
    """
    setup_flask_app_context()
    try:
        send_notifications(_flask_app_instance)  # Pass the app instance
    finally:
        teardown_flask_app_context()


def main():
    """
    Main function to set up and run the scheduled ETL and Notification processes.
    """
    logger.info("Orchestrator started. Setting up hourly ETL and Notification schedules...")

    # Schedule the ETL process to run every hour
    schedule.every(ETL_RUN_INTERVAL_HOURS).hours.at(":00").do(run_etl_process)

    # Schedule the Notification process to run every hour, at :10 past the hour
    # The wrapper ensures the Flask context is handled correctly for the scheduled call
    schedule.every(ETL_RUN_INTERVAL_HOURS).hours.at(":22").do(scheduled_send_notifications_wrapper)

    # Perform initial ETL run immediately on start
    logger.info("Performing initial ETL run...")
    run_etl_process()

    # Perform initial Notification run immediately on start (after initial ETL)
    logger.info("Performing initial Notification run...")
    # For the initial run, we manage context directly as it's not a scheduled call
    setup_flask_app_context()
    try:
        send_notifications(_flask_app_instance)  # Pass the app instance for initial run too
    finally:
        teardown_flask_app_context()

    logger.info("Initial ETL and Notification runs completed. Entering scheduling loop.")

    # Keep the script running to check the schedule
    while True:
        try:
            schedule.run_pending()  # Run any jobs that are due
            time.sleep(SLEEP_INTERVAL_SECONDS_SCHEDULE_CHECK)  # Wait for a minute before checking again
        except KeyboardInterrupt:
            logger.info("\nOrchestrator stopped by user (Ctrl+C). Exiting.")
            sys.exit(0)  # Exit cleanly
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}", exc_info=True)
            time.sleep(SLEEP_INTERVAL_SECONDS_SCHEDULE_CHECK)  # Prevent rapid error looping


if __name__ == "__main__":
    main()
