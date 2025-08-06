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

./
├── .env                      # Environment variables (e.g., database credentials)
├── .gitignore                # Git ignore file
├── docker-compose.yml        # Docker Compose configuration for all services
├── Dockerfile.app            # Dockerfile for the Flask web application
├── Dockerfile.orchestrator   # Dockerfile for the orchestrator background worker
├── orchestrator.py           # Script for orchestrating background tasks
├── venv/                     # Virtual environment (ignored by Git)
├── app/                      # Flask application code
│   ├── init.py           # Initialization file for the Flask app
│   ├── frontend_routes.py    # Routes for the frontend
│   ├── main.py               # Entry point for the Flask web application
│   ├── models.py             # Database models
│   ├── routes.py             # Additional API or app routes
│   ├── static/               # Static files (e.g., CSS, JS, images)
│   └── templates/            # HTML templates for the web interface
├── db/                       # Database initialization scripts
│   └── init_db.sql           # SQL script to initialize the PostgreSQL database
├── etl/                      # ETL (Extract, Transform, Load) pipeline
│   ├── extract/              # Directory for extract scripts
│   ├── transform/            # Directory for transform scripts
│   └── load/                 # Directory for load scripts
├── notification/             # Notification-related code
│   ├── init.py           # Initialization file for the notification module
│   ├── email_sender.py       # Logic for sending email notifications
│   ├── email_template.html   # HTML template for email notifications
│   └── notifier.py           # Notification logic (e.g., scheduling emails)
├── utils/                    # Utility modules (e.g., database utilities)
│   └── (utility files)

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


From your terminal, navigate to the project's root directory and execute the following command:

```docker-compose up --build

