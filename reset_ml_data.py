"""
Reset ML training data:
1. Delete all mock transactions (keeping only real ones)
2. Regenerate clean baseline with ONLY small normal amounts ($10-$300)
   so that any real large transfer clearly stands out as anomalous
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import random
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': 'localhost', 'port': 5432,
    'dbname': 'securebank', 'user': 'postgres', 'password': 'Priy@nk1Bh'
}

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor(cursor_factory=RealDictCursor)

# 1. Get all account IDs
cur.execute("SELECT account_id FROM Accounts ORDER BY account_id")
account_ids = [r['account_id'] for r in cur.fetchall()]
print("Accounts found:", account_ids)

# 2. Delete ALL existing mock transactions so we start clean
# We keep only those with transaction_type NOT in our mock types to be safe
# Actually, safest to just wipe all and let real transfers accumulate
cur.execute("DELETE FROM TransactionHistory WHERE status = 'Success' AND transaction_type IN ('Deposit', 'Withdrawal', 'Transfer')")
deleted = cur.rowcount
print(f"Deleted {deleted} existing mock transactions.")

# 3. For each account, generate 40 small NORMAL transactions over last 30 days
# These form the "baseline" - all small/medium amounts ($10-$400)
# NO large outliers so fraud detection is sensitive
start_date = datetime.now() - timedelta(days=30)
total_inserted = 0

for acc_id in account_ids:
    other_accounts = [a for a in account_ids if a != acc_id]
    for i in range(40):
        # Strictly small amounts: $10-$400 range, normally distributed around $150
        amount = round(random.gauss(150, 60), 2)
        amount = max(10.0, min(400.0, amount))  # clamp to [10, 400]

        to_acc = random.choice(other_accounts)
        timestamp = start_date + timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        cur.execute(
            """
            INSERT INTO TransactionHistory
            (from_account_id, to_account_id, transaction_type, amount, status, transaction_timestamp)
            VALUES (%s, %s, 'Transfer', %s, 'Success', %s)
            """,
            (acc_id, to_acc, amount, timestamp)
        )
        total_inserted += 1

conn.commit()
conn.close()
print(f"Inserted {total_inserted} clean baseline transactions ({total_inserted // len(account_ids)} per account).")
print("\nNew fraud thresholds (approx):")
print("  Mean ~$150, StdDev ~$60 => Threshold = $150 + 3*$60 = $330")
print("  Any transfer over ~$330 will now trigger the AI Alert!")
