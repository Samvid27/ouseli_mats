from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'Priy@nk1Bh',
    'database': 'securebank',
    'port': 5432
}

passwords = {
    'john.doe@email.com': 'password123',
    'jane.smith@email.com': 'password456',
    'bob.wilson@email.com': 'password789'
}

conn_string = (
    f"host={DB_CONFIG['host']} port={DB_CONFIG['port']} "
    f"dbname={DB_CONFIG['database']} user={DB_CONFIG['user']} "
    f"password={DB_CONFIG['password']}"
)

print("Connecting to database...")
conn = psycopg2.connect(conn_string)
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("Updating password hashes...")
for email, password in passwords.items():
    new_hash = generate_password_hash(password)
    cursor.execute('UPDATE Customers SET password_hash = %s WHERE email = %s', (new_hash, email))
    print(f'  Updated: {email}')

conn.commit()

print("\nVerifying passwords...")
for email, password in passwords.items():
    cursor.execute('SELECT password_hash FROM Customers WHERE email = %s', (email,))
    row = cursor.fetchone()
    ok = check_password_hash(row['password_hash'], password) if row else False
    print(f'  {email}: {"OK" if ok else "FAIL"}')

conn.close()
print("\nDone! You can now log in with:")
print("  john.doe@email.com / password123")
print("  jane.smith@email.com / password456")
print("  bob.wilson@email.com / password789")
