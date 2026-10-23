import psycopg2
from psycopg2 import Error
import random
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash

# Database Configuration (matches app.py)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': '1234',
    'database': 'securebank',
    'port': 5432
}

def generate_mock_data():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            dbname=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()

        print("Generating mock transactions for ML analysis...")

        # Get all account IDs
        cursor.execute("SELECT account_id FROM Accounts")
        account_ids = [row[0] for row in cursor.fetchall()]

        if not account_ids:
            print("No accounts found. Please run setup_database.py first.")
            return

        # Transaction types
        types = ['Deposit', 'Transfer', 'Withdrawal']
        
        # Start date: 30 days ago
        start_date = datetime.now() - timedelta(days=30)

        # Insert 100 transactions
        for i in range(100):
            # Pick two different accounts
            acc1 = random.choice(account_ids)
            acc2 = random.choice([a for a in account_ids if a != acc1])
            
            t_type = random.choice(types)
            amount = round(random.uniform(10.0, 500.0), 2) # Normal spending
            
            # Occasionally generate a "suspicious" high amount for ML training
            if i % 20 == 0:
                amount = round(random.uniform(5000.0, 10000.0), 2)
                
            timestamp = start_date + timedelta(
                days=random.randint(0, 29),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            status = 'Success'
            
            cursor.execute(
                """
                INSERT INTO TransactionHistory 
                (from_account_id, to_account_id, transaction_type, amount, status, transaction_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (acc1, acc2, t_type, amount, status, timestamp)
            )

        conn.commit()
        print(f"Successfully generated 100 mock transactions.")
        
        cursor.close()
        conn.close()

    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_mock_data()
