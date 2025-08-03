import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime

# Ensure .env is loaded
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Path to the HTML email template file
EMAIL_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'email_template.html')

def _load_email_template():
    """
    Loads the HTML email template from a file.
    """
    try:
        with open(EMAIL_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Email template file not found: {EMAIL_TEMPLATE_PATH}")
        return None
    except Exception as e:
        logger.error(f"Error loading email template: {e}", exc_info=True)
        return None

def send_email(recipient_email, subject, body_html):
    """
    Sends an email notification using Gmail SMTP with an App Password.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([sender_email, smtp_server, smtp_port, smtp_username, smtp_password]):
        logger.error("Gmail SMTP configuration is incomplete. Check .env variables: SENDER_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD")
        return False

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.ehlo()  # Identify with the SMTP server
            server.starttls()  # Secure the connection
            server.ehlo()  # Re-identify after STARTTLS
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        logger.info(f"Email sent successfully to {recipient_email} for subject: '{subject}'")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Authentication failed for {recipient_email}: Check SMTP_USERNAME and SMTP_PASSWORD (ensure App Password is used). Error: {e}", exc_info=True)
        return False
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"Recipient email {recipient_email} refused: {e}. Ensure the email address is valid.", exc_info=True)
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error while sending email to {recipient_email}: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email to {recipient_email}: {e}", exc_info=True)
        return False

def format_gigs_for_email(gigs):
    """
    Formats a list of gig dictionaries into an HTML string suitable for an email,
    using a loaded template.
    """
    if not gigs:
        return "<p>No new gigs matching your preferences at this time.</p>"

    template_html = _load_email_template()
    if template_html is None:
        return "<p>Error: Email template could not be loaded.</p>"

    gigs_html_items = ""
    for gig in gigs:
        title = gig.title if hasattr(gig, 'title') else 'N/A'
        link = gig.link if hasattr(gig, 'link') else '#'
        description = gig.description if hasattr(gig, 'description') else 'No description provided.'
        category = gig.category if hasattr(gig, 'category') else 'Uncategorized'
        published_at = gig.published_at if hasattr(gig, 'published_at') else None

        if isinstance(published_at, datetime):
            published_at_str = published_at.strftime('%Y-%m-%d %H:%M UTC')
        elif isinstance(published_at, str):
            published_at_str = published_at
        else:
            published_at_str = 'N/A'

        safe_description = description.replace('<', '&lt;').replace('>', '&gt;')

        gigs_html_items += f"""
            <div class="gig-item">
                <div class="gig-title"><a href="{link}" target="_blank">{title}</a></div>
                <div class="gig-category">Category: {category} | Published: {published_at_str}</div>
                <div class="gig-description">{safe_description[:200]}...</div>
                <div class="gig-link"><a href="{link}" target="_blank">View Gig</a></div>
            </div>
        """

    return template_html.format(gigs_content=gigs_html_items)