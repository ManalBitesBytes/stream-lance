import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establishes and returns a database connection using psycopg2."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        print("Successfully connected to the database.")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def close_db_connection(conn):
    """Closes the database connection."""
    if conn:
        conn.close()
        print("Database connection closed.")