"""
Database Setup Script for SecureBank (PostgreSQL)
This script initializes the database with proper password hashing
"""

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from werkzeug.security import generate_password_hash
import os

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',  # Change as needed (default PostgreSQL user)
    'password': 'Priy@nk1Bh',  # Change as needed
    'port': 5432  # Default PostgreSQL port
}

def setup_database():
    """Set up the database with schema and sample data"""
    
    # First, create database if it doesn't exist
    # Connect to default 'postgres' database to create our database
    config_postgres = DB_CONFIG.copy()
    config_postgres['database'] = 'postgres'  # Connect to default postgres database
    
    try:
        conn = psycopg2.connect(**config_postgres)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'securebank'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE securebank")
            print("[OK] Database 'securebank' created")
        else:
            print("[OK] Database 'securebank' already exists")
        
        cursor.close()
        conn.close()
    except Error as e:
        print(f"[ERROR] Error creating database: {e}")
        print(f"  Make sure PostgreSQL is running and password is correct.")
        print(f"  Try connecting manually: psql -U postgres -h localhost")
        return False
    
    # Now connect to the securebank database
    db_config = DB_CONFIG.copy()
    db_config['database'] = 'securebank'
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Read and execute schema file
        print("Reading database schema...")
        with open('database_schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
            # Execute the entire schema (PostgreSQL handles multiple statements)
            try:
                cursor.execute(schema)
                conn.commit()
                print("[OK] Database schema created")
            except Error as e:
                # Some errors are expected (like table already exists)
                if "already exists" not in str(e).lower() and "does not exist" not in str(e).lower():
                    print(f"Warning: {e}")
                conn.rollback()
                # Try to continue anyway
        
        # Update passwords with proper hashing
        print("Setting up user passwords...")
        passwords = {
            'john.doe@email.com': 'password123',
            'jane.smith@email.com': 'password456',
            'bob.wilson@email.com': 'password789'
        }
        
        for email, password in passwords.items():
            password_hash = generate_password_hash(password)
            update_query = "UPDATE Customers SET password_hash = %s WHERE email = %s"
            cursor.execute(update_query, (password_hash, email))
        
        conn.commit()
        print("[OK] User passwords updated with proper hashing")
        
        # Read and execute stored functions
        print("Creating stored functions...")
        with open('stored_procedures.sql', 'r', encoding='utf-8') as f:
            functions = f.read()
            try:
                cursor.execute(functions)
                conn.commit()
                print("[OK] Stored functions created")
            except Error as e:
                if "already exists" not in str(e).lower():
                    print(f"Warning: {e}")
                conn.rollback()
        
        # Read and execute triggers
        print("Creating triggers...")
        with open('triggers.sql', 'r', encoding='utf-8') as f:
            triggers = f.read()
            try:
                cursor.execute(triggers)
                conn.commit()
                print("[OK] Triggers created")
            except Error as e:
                if "already exists" not in str(e).lower() and "does not exist" not in str(e).lower():
                    print(f"Warning: {e}")
                conn.rollback()
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*50)
        print("Database setup completed successfully!")
        print("="*50)
        print("\nDemo Credentials:")
        print("  Email: john.doe@email.com")
        print("  Password: password123")
        print("\nYou can now run: python app.py")
        
        return True
        
    except Error as e:
        print(f"[ERROR] Error setting up database: {e}")
        return False

if __name__ == '__main__':
    print("SecureBank Database Setup (PostgreSQL)")
    print("="*50)
    print("\nMake sure PostgreSQL is running and update DB_CONFIG in this file if needed.")
    input("\nPress Enter to continue...")
    setup_database()
