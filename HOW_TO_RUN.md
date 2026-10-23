# How to Run SecureBank Application

## Step-by-Step Instructions

### Prerequisites Check

1. **Python** - Make sure Python 3.8+ is installed
   ```bash
   python --version
   ```

2. **PostgreSQL** - Make sure PostgreSQL is installed and running
   - Windows: Check if PostgreSQL service is running in Services
   - Or test connection: `psql -U postgres`

---

### Step 1: Install Python Dependencies

Open terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- psycopg2-binary (PostgreSQL database connector)
- Werkzeug (password hashing)

---

### Step 2: Configure Database Connection

Edit **two files** to set your PostgreSQL credentials:

#### File 1: `app.py` (around line 20)
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',    # ← Change if your PostgreSQL user is different
    'password': '',         # ← Enter your PostgreSQL password here
    'database': 'securebank',
    'port': 5432            # Default PostgreSQL port
}
```

#### File 2: `setup_database.py` (around line 10)
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',    # ← Change if your PostgreSQL user is different
    'password': '',         # ← Enter your PostgreSQL password here
    'port': 5432            # Default PostgreSQL port
}
```

**If you don't have a PostgreSQL password**, leave it as empty string `''`.

---

### Step 3: Initialize Database

Run the setup script to create database, tables, and sample data:

```bash
python setup_database.py
```

**What this does:**
- Creates `securebank` database
- Creates all tables (Customers, Accounts, TransactionHistory, AuditLog)
- Inserts sample data
- Creates stored procedures
- Creates triggers
- Sets up demo user accounts

**Expected output:**
```
[OK] Database 'securebank' created/verified
[OK] Database schema created
[OK] User passwords updated with proper hashing
[OK] Stored procedures created
[OK] Triggers created

Database setup completed successfully!
```

---

### Step 4: Run the Application

Start the Flask server:

```bash
python app.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Running on http://0.0.0.0:5000
```

The application is now running!

---

### Step 5: Access the Application

Open your web browser and go to:

```
http://localhost:5000
```

or

```
http://127.0.0.1:5000
```

You should see the **Login Page**.

---

### Step 6: Login

Use these demo credentials:

- **Email:** `john.doe@email.com`
- **Password:** `password123`

Click **Login** button.

---

## You're In!

After login, you'll see the **Dashboard** with your accounts.

### Try These:

1. **View Accounts** - See your account cards on dashboard
2. **Transfer Funds** - Click "Transfer Money" to test ACID transaction
3. **View History** - Click "View History" to see transaction records
4. **Logout** - Click logout button in navbar

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'flask'"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Problem: "Error connecting to PostgreSQL"
**Solutions:**
1. Make sure PostgreSQL is running
2. Check credentials in `app.py` and `setup_database.py`
3. Test PostgreSQL connection: `psql -U postgres`

### Problem: "Access denied for user"
**Solution:** 
- Check PostgreSQL username and password
- Make sure PostgreSQL user has CREATE DATABASE privileges

### Problem: "Port 5000 already in use"
**Solution:** Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5001 to any free port
```

### Problem: "Database 'securebank' doesn't exist"
**Solution:** Run setup script again:
```bash
python setup_database.py
```

### Problem: "Stored function not found"
**Solution:** 
1. Run `setup_database.py` again
2. Or manually execute `stored_procedures.sql` in PostgreSQL:
   ```bash
   psql -U postgres -d securebank -f stored_procedures.sql
   ```

---

## To Stop the Application

Press `Ctrl + C` in the terminal where the app is running.

---

## Quick Command Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database (first time only)
python setup_database.py

# Run application
python app.py

# Access in browser
# http://localhost:5000
```

---

## Verification Checklist

Before running, make sure:
- [ ] Python 3.8+ installed
- [ ] PostgreSQL installed and running
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database credentials configured in `app.py` and `setup_database.py`
- [ ] Database initialized (`python setup_database.py`)

---

**That's it! Your SecureBank application should now be running!**
