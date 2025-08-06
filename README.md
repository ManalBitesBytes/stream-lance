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

Your project should have the following file structure:
