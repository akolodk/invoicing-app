#!/usr/bin/env python3
"""
Invoice Generator Startup Script
Creates necessary directories and initializes the application.
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'data',
        'uploads', 
        'generated',
        'templates',
        'config'
    ]
    
    print("Creating necessary directories...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ {directory}/")

def check_requirements():
    """Check if required packages are installed"""
    try:
        import streamlit
        import pandas
        import sqlalchemy
        import reportlab
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements with: pip install -r requirements.txt")
        return False

def initialize_database():
    """Initialize the database"""
    try:
        from models.database import init_db
        init_db()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def main():
    """Main startup function"""
    print("🚀 Starting Invoice Generator...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup failed. Please install requirements first.")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("\n⚠️  Database initialization failed, but continuing...")
    
    print("\n✅ Setup complete!")
    print("=" * 50)
    print("Starting Streamlit application...")
    print("Access the app at: http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    print("=" * 50)
    
    # Start Streamlit
    os.system("streamlit run app.py")

if __name__ == "__main__":
    main() 