"""
Database initialization script.
Run this script to create the database and tables if they don't exist yet.
"""
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path to allow importing app modules
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.database.database import create_db_and_tables
from app.users.models import User  # Import User model to register it with SQLModel

def init_database():
    """Initialize the database and create tables if they don't exist."""
    print("Initializing database...")
    
    # Create database file directory if it doesn't exist
    db_dir = os.path.dirname(os.path.join(project_root, "youkie.db"))
    os.makedirs(db_dir, exist_ok=True)
    
    # Create database and tables
    create_db_and_tables()
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()
