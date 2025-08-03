import logging
from datetime import datetime, timedelta
from app.models import User, Gig, SentNotification
from notification.email_sender import send_email, format_gigs_for_email

logger = logging.getLogger(__name__)

def send_notifications(app_instance):
    """
    Sends email notifications to users based on their preferences and new gigs.
    This function expects a Flask application instance to be passed.
    """
    logger.info(f"--- Starting Notification Process ---")

    with app_instance.app_context():  # Ensure context is active
        logger.info("Accessing db attribute")
        db = app_instance.db
        logger.info("db attribute accessed successfully")
        try:
            users = db.session.query(User).filter(User.is_active == True).all()
            for user in users:
                user_preferences = [p.category_name for p in user.preferences]
                user_email = user.email

                if not user_preferences:
                    logger.info(f"User {user.id} ({user_email}) has no preferences set. Skipping notifications.")
                    continue

                notification_window_start = datetime.utcnow() - timedelta(hours=2)
                gigs_to_notify = db.session.query(Gig).outerjoin(
                    SentNotification,
                    (SentNotification.gig_id == Gig.id) & (SentNotification.user_id == user.id)
                ).filter(
                    Gig.category.in_(user_preferences),
                    Gig.published_at >= notification_window_start,
                    SentNotification.id.is_(None)
                ).order_by(Gig.published_at.desc()).all()

                if gigs_to_notify:
                    logger.info(f"Found {len(gigs_to_notify)} new gigs for user {user.id} ({user_email}).")
                    email_body_html = format_gigs_for_email(gigs_to_notify)
                    subject = f"New Gig Alerts from StreamLance ({len(gigs_to_notify)} new matches!)"
                    if send_email(user_email, subject, email_body_html):
                        for gig in gigs_to_notify:
                            try:
                                new_notification = SentNotification(user_id=user.id, gig_id=gig.id)
                                db.session.add(new_notification)
                            except Exception as e:
                                db.session.rollback()
                                logger.warning(
                                    f"Failed to record notification for user {user.id}, gig {gig.id}: {e}. Skipping this record.")
                                continue
                        db.session.commit()
                        logger.info(
                            f"Successfully sent and recorded notifications for {len(gigs_to_notify)} gigs to {user_email}.")
                    else:
                        logger.error(f"Failed to send email to {user_email}. Notifications not recorded for this run.")
                else:
                    logger.info(
                        f"No new matching gigs for user {user.id} ({user_email}) in the last 2 hours that haven't been sent.")

        except Exception as e:
            db.session.rollback()
            logger.error(f"An error occurred during notification process: {e}", exc_info=True)