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
    using a loaded template with modern card design.
    """
    if not gigs:
        return "<p>No new gigs matching your preferences at this time.</p>"

    template_html = _load_email_template()
    if template_html is None:
        return "<p>Error: Email template could not be loaded.</p>"

    gigs_html_items = []
    for gig in gigs:
        title = gig.title if hasattr(gig, 'title') else 'N/A'
        link = gig.link if hasattr(gig, 'link') else '#'
        description = gig.description if hasattr(gig, 'description') else 'No description provided.'
        category = gig.category if hasattr(gig, 'category') else 'Uncategorized'
        published_at = gig.published_at if hasattr(gig, 'published_at') else None
        budget_amount = getattr(gig, 'budget_amount', None)
        budget_currency = getattr(gig, 'budget_currency', None)

        # Format published date
        if isinstance(published_at, datetime):
            published_at_str = published_at.strftime('%Y-%m-%d %H:%M UTC')
        elif isinstance(published_at, str):
            published_at_str = published_at
        else:
            published_at_str = 'N/A'

        # Format budget if available
        budget_html = ""
        if budget_amount and budget_currency:
            budget_html = f"""
                <div class="gig-budget">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <line x1="12" y1="2" x2="12" y2="22"/>
                        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                    </svg>
                    {budget_amount} {budget_currency}
                </div>
            """

        # Format category
        category_html = f"""
            <span class="gig-category">
                {category}
            </span>
        """

        # Format date
        date_html = f"""
            <span class="gig-date">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
                {published_at_str}
            </span>
        """

        # Build the gig card
        gig_html = f"""
        <div class="gig-card">
            <div class="gig-header">
                <h3 class="gig-title">
                    <a href="{link}" target="_blank" rel="noopener noreferrer">
                        {title}
                    </a>
                </h3>
                <div class="gig-meta">
                    {category_html}
                    {date_html}
                    {budget_html}
                </div>
            </div>
            <div class="gig-content">
                <p class="gig-description">
                    {description[:200]}{'...' if len(description) > 200 else ''}
                </p>
                <div class="gig-actions">
                    <a href="{link}" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
                        View Opportunity
                    </a>
                </div>
            </div>
        </div>
        """
        gigs_html_items.append(gig_html)

    # Join all gig cards and replace the placeholder
    return template_html.replace('{{gigs_content}}', '\n'.join(gigs_html_items))