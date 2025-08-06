# stream-lance

## Overview

StreamLance Analytics is a robust, multi-service application designed to help freelancers and job seekers find relevant gigs that match their skills and interests. It features an automated ETL (Extract, Transform, Load) pipeline that scrapes gig data from online sources and a sophisticated notification system that delivers personalized job alerts directly to users' inboxes. The project is built using Python, Flask, Docker, and PostgreSQL, ensuring a scalable and maintainable architecture.

## Key Features

* **Automated Data Extraction:** Regularly pulls gig data from the Freelancer.com RSS feed.
* **Intelligent Transformation:** Standardizes and categorizes raw gig data, making it easier to filter and search.
* **Robust Data Storage:** Persistently stores all gig and user data in a PostgreSQL database.
* **Personalized Notifications:** Sends scheduled email alerts to users with a curated list of new gigs that match their saved preferences.
* **Dockerized Architecture:** The application is broken down into three main services (`app`, `orchestrator`, `db`) that run in isolated containers, simplifying deployment and management.

## Architecture

The project is structured into three main services, orchestrated by Docker Compose:

1.  **`app`:** A Flask web application that serves as the user-facing interface. It handles user authentication, preference management, and a dashboard view of the gigs.
2.  **`orchestrator`:** A background Python service that runs the scheduled tasks. It's responsible for the ETL process to keep the database up-to-date and the notification process to alert users.
3.  **`db`:** A PostgreSQL database instance that serves as the single source of truth for all application data.

## Getting Started

Follow these steps to get a local instance of the application up and running.

### Prerequisites

* **Docker and Docker Compose:** Ensure you have them installed on your machine.
* **Python:** The core logic is in Python 3.10+.
* **Email Account:** You'll need a Gmail account with an [App Password](https://support.google.com/accounts/answer/185833?hl=en) enabled for sending notification emails.

### 1. Project Structure


### Components

- **.env**: Stores environment variables such as `DATABASE_URL`, `POSTGRES_USER`, and `FLASK_SECRET_KEY`.
- **.gitignore**: Specifies files and directories to ignore in Git (e.g., `venv/`).
- **docker-compose.yml**: Orchestrates the PostgreSQL database, Flask app, and orchestrator services.
- **Dockerfile.app**: Defines the Docker image for the Flask app, running with Gunicorn.
- **Dockerfile.orchestrator**: Defines the Docker image for the orchestrator, running background tasks.
- **orchestrator.py**: The main script for running background tasks, such as triggering the ETL pipeline and notifications.
- **app/**:
  - `__init__.py`: Initializes the Flask application.
  - `frontend_routes.py`: Defines routes for the web frontend.
  - `main.py`: The entry point for the Flask app.
  - `models.py`: Defines database models (e.g., `User`, `Gig`).
  - `routes.py`: Additional API or app routes.
  - `static/`: Contains static assets (e.g., CSS, JavaScript, images).
  - `templates/`: Contains HTML templates for rendering web pages.
- **db/**: Holds `init_db.sql` for setting up the PostgreSQL database schema.
- **etl/**: Contains the ETL pipeline with subdirectories:
  - `extract/`: Scripts for extracting gig data from sources.
  - `transform/`: Scripts for transforming extracted data.
  - `load/`: Scripts for loading transformed data into the database.
- **notification/**:
  - `__init__.py`: Initializes the notification module.
  - `email_sender.py`: Handles sending email notifications.
  - `email_template.html`: The HTML template for formatting gig emails.
  - `notifier.py`: Manages notification scheduling or logic.
- **utils/**: Houses utility modules shared across the application.


### 2. Configuration

Create a `.env` file in the root directory and configure your environment variables.

```ini
# Database configuration
POSTGRES_DB=streamlance_db
POSTGRES_USER=streamlance_user
POSTGRES_PASSWORD=your_secure_db_password
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

# Flask application configuration
FLASK_SECRET_KEY=a_super_secret_key_for_flask

# Email notification configuration
SENDER_EMAIL=your_email_address@gmail.com
SMTP_USERNAME=your_email_address@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

### 3. Running the Application

### Getting Started

Clone the repository:
 ```bash
 git clone https://github.com/yourusername/stream-lance.git
 cd stream-lance

Build and start the services:
bashdocker-compose up --build
ذذ

