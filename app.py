"""
SecureBank - Flask Web Application
BCSE302L Database Management Systems Project
Demonstrates: JOIN operations, ACID transactions, Stored Functions, Indexing, Triggers
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash
from functools import wraps
import os
from datetime import datetime, timedelta
import ai_utils

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Allow cross-origin API access (for API clients / future React frontend)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

# Database Configuration (PostgreSQL)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',  # Change as needed (default PostgreSQL user)
    'password': 'Priy@nk1Bh',  # Change as needed
    'database': 'securebank',
    'port': 5432  # Default PostgreSQL port
}


def get_db_connection():
    """Create and return database connection"""
    try:
        # Use connection string format to ensure password is properly included
        conn_string = (
            f"host={DB_CONFIG['host']} "
            f"port={DB_CONFIG['port']} "
            f"dbname={DB_CONFIG['database']} "
            f"user={DB_CONFIG['user']} "
            f"password={DB_CONFIG['password']}"
        )
        conn = psycopg2.connect(conn_string)
        return conn
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print(
            f"Attempted connection to: {DB_CONFIG['host']}:{DB_CONFIG['port']}/"
            f"{DB_CONFIG['database']} as user {DB_CONFIG['user']}"
        )
        return None


def mask_email(email: str):
    """Return a masked version of an email for display (e.g., j***@bank.com)."""
    if not email or '@' not in email:
        return None
    name, domain = email.split('@', 1)
    if len(name) <= 1:
        masked_name = '*'
    else:
        masked_name = name[0] + '***'
    return f"{masked_name}@{domain}"


def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def api_login_required(f):
    """Require login for JSON APIs."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"ok": False, "error": "AUTH_REQUIRED"}), 401
        return f(*args, **kwargs)
    return decorated


def _get_last_login_display(customer_id: int):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT login_timestamp
            FROM LoginActivity
            WHERE customer_id = %s
            ORDER BY login_timestamp DESC
            LIMIT 1
            """,
            (customer_id,),
        )
        row = cursor.fetchone()
        if row and row.get("login_timestamp"):
            return row["login_timestamp"].strftime('%d %b %Y at %I:%M %p')
        return None
    except Error:
        return None
    finally:
        conn.close()


@app.route('/api/me', methods=['GET'])
def api_me():
    if 'user_id' not in session:
        return jsonify({"ok": True, "authenticated": False})
    return jsonify({
        "ok": True,
        "authenticated": True,
        "user": {
            "user_id": session.get("user_id"),
            "name": session.get("user_name"),
            "email": session.get("user_email"),
        }
    })


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"ok": True})


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"ok": False, "error": "MISSING_FIELDS"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"ok": False, "error": "DB_CONNECTION"}), 500

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT customer_id, email, password_hash, full_name FROM Customers WHERE email = %s",
            (email,),
        )
        user = cursor.fetchone()
        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify({"ok": False, "error": "INVALID_CREDENTIALS"}), 401

        # Login activity
        device_info = request.headers.get('User-Agent', 'Unknown device')
        ip_address = request.remote_addr
        try:
            cursor.execute(
                """
                INSERT INTO LoginActivity (customer_id, device_info, ip_address)
                VALUES (%s, %s, %s)
                """,
                (user["customer_id"], device_info, ip_address),
            )
            conn.commit()
        except Error:
            conn.rollback()

        session["user_id"] = user["customer_id"]
        session["user_name"] = user["full_name"]
        session["user_email"] = user["email"]

        resp = jsonify({
            "ok": True,
            "user": {
                "user_id": user["customer_id"],
                "name": user["full_name"],
                "email": user["email"],
            }
        })
        resp.set_cookie('last_email', user['email'], max_age=30 * 24 * 60 * 60)
        return resp
    finally:
        conn.close()


@app.route('/api/dashboard', methods=['GET'])
@api_login_required
def api_dashboard():
    conn = get_db_connection()
    if not conn:
        return jsonify({"ok": False, "error": "DB_CONNECTION"}), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT
                account_id,
                account_type,
                balance,
                account_number,
                ifsc_code,
                branch_name,
                created_at
            FROM Accounts
            WHERE customer_id = %s
            ORDER BY account_id
            """,
            (session["user_id"],),
        )
        accounts = cursor.fetchall()
        last_login = _get_last_login_display(session["user_id"])
        return jsonify({
            "ok": True,
            "user_name": session.get("user_name"),
            "last_login": last_login,
            "accounts": accounts,
        })
    finally:
        conn.close()


@app.route('/api/profile', methods=['GET'])
@api_login_required
def api_profile():
    conn = get_db_connection()
    if not conn:
        return jsonify({"ok": False, "error": "DB_CONNECTION"}), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT customer_id, full_name, email, phone, created_at
            FROM Customers
            WHERE customer_id = %s
            """,
            (session["user_id"],),
        )
        customer = cursor.fetchone()
        cursor.execute(
            """
            SELECT account_id, account_type, account_number, ifsc_code, branch_name, balance, created_at
            FROM Accounts
            WHERE customer_id = %s
            ORDER BY account_id
            """,
            (session["user_id"],),
        )
        accounts = cursor.fetchall()
        return jsonify({
            "ok": True,
            "customer": customer,
            "accounts": accounts,
        })
    finally:
        conn.close()


@app.route('/api/history/<int:account_id>', methods=['GET'])
@api_login_required
def api_history(account_id: int):
    conn = get_db_connection()
    if not conn:
        return jsonify({"ok": False, "error": "DB_CONNECTION"}), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT customer_id FROM Accounts WHERE account_id = %s", (account_id,))
        acc = cursor.fetchone()
        if not acc or acc["customer_id"] != session["user_id"]:
            return jsonify({"ok": False, "error": "NOT_FOUND"}), 404

        cursor.execute(
            "SELECT account_id, account_type, balance, account_number, ifsc_code, branch_name FROM Accounts WHERE account_id = %s",
            (account_id,),
        )
        account_info = cursor.fetchone()

        cursor.execute(
            """
            SELECT transaction_id, from_account_id, to_account_id, transaction_type, amount, status, transaction_timestamp
            FROM TransactionHistory
            WHERE from_account_id = %s OR to_account_id = %s
            ORDER BY transaction_timestamp DESC
            LIMIT 50
            """,
            (account_id, account_id),
        )
        transactions = cursor.fetchall()

        return jsonify({"ok": True, "account": account_info, "transactions": transactions})
    finally:
        conn.close()


@app.route('/api/forecast/<int:account_id>', methods=['GET'])
@api_login_required
def api_forecast(account_id: int):
    conn = get_db_connection()
    if not conn:
        return jsonify({"ok": False, "error": "DB_CONNECTION"}), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get current balance
        cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s", (account_id,))
        curr = cursor.fetchone()
        if not curr:
            return jsonify({"ok": False, "error": "ACCOUNT_NOT_FOUND"}), 404
        current_balance = float(curr['balance'])

        # Get daily NET change: money out is negative, money in is positive
        cursor.execute(
            """
            SELECT
                DATE(transaction_timestamp) as date,
                SUM(
                    CASE
                        WHEN from_account_id = %(aid)s THEN -amount
                        ELSE amount
                    END
                ) as net_change
            FROM TransactionHistory
            WHERE (from_account_id = %(aid)s OR to_account_id = %(aid)s)
              AND status = 'Success'
            GROUP BY DATE(transaction_timestamp)
            ORDER BY date DESC
            """,
            {"aid": account_id}
        )
        daily_changes = cursor.fetchall()

        if len(daily_changes) < 2:
            return jsonify({"ok": True, "predictions": [], "message": "Not enough transaction history"})

        # Reconstruct balance timeline walking backwards from current balance
        processed_history = []
        running_bal = current_balance
        for row in daily_changes:
            processed_history.append({"date": row['date'], "balance": running_bal})
            running_bal -= float(row['net_change'])  # undo this day's change

        # Reverse so oldest is first for regression
        processed_history = processed_history[::-1]

        predictions = ai_utils.predict_balance_trend(processed_history)
        return jsonify({"ok": True, "predictions": predictions})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        conn.close()


@app.route('/api/transfer', methods=['POST'])
@api_login_required
def api_transfer():
    data = request.get_json(silent=True) or {}
    from_account_id = data.get("from_account_id")
    to_account_number = (data.get("to_account_number") or "").strip()
    amount = data.get("amount")
    beneficiary_name = (data.get("beneficiary_name") or "").strip()
    bank_name = (data.get("bank_name") or "").strip()
    ifsc = (data.get("ifsc") or "").strip()

    if not all([from_account_id, to_account_number, amount, beneficiary_name, bank_name, ifsc]):
        return jsonify({"ok": False, "error": "MISSING_FIELDS"}), 400

    try:
        from_account_id = int(from_account_id)
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "INVALID_INPUT"}), 400

    if amount <= 0:
        return jsonify({"ok": False, "error": "INVALID_AMOUNT"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"ok": False, "error": "DB_CONNECTION"}), 500

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Ensure from account belongs to user
        cursor.execute("SELECT customer_id FROM Accounts WHERE account_id = %s", (from_account_id,))
        fa = cursor.fetchone()
        if not fa or fa["customer_id"] != session["user_id"]:
            return jsonify({"ok": False, "error": "FORBIDDEN"}), 403

        # Resolve destination by account number
        cursor.execute("SELECT account_id FROM Accounts WHERE account_number = %s", (to_account_number,))
        to_acc = cursor.fetchone()
        if not to_acc:
            return jsonify({"ok": False, "error": "DEST_NOT_FOUND"}), 404
        to_account_id = to_acc["account_id"]

        # AI Fraud Detection Check
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT amount FROM TransactionHistory WHERE from_account_id = %s AND status = 'Success' LIMIT 50",
            (from_account_id,)
        )
        recent_txs = cursor.fetchall()
        is_fraud_risk = ai_utils.analyze_fraud_risk(recent_txs, amount)
        cursor.close()

        # Call stored function
        cur2 = conn.cursor()
        cur2.execute("SELECT * FROM TransferFunds(%s, %s, %s)", (from_account_id, to_account_id, amount))
        res = cur2.fetchone()
        status = res[0]
        message = res[1]
        if status == "Success":
            conn.commit()
            return jsonify({
                "ok": True, 
                "status": status, 
                "message": message,
                "ai_risk_warning": is_fraud_risk
            })
        conn.rollback()
        return jsonify({"ok": False, "status": status, "message": message}), 400
    except Error as e:
        conn.rollback()
        return jsonify({"ok": False, "error": "TRANSFER_FAILED", "details": str(e)}), 500
    finally:
        conn.close()


@app.route('/')
def index():
    """Redirect to login page"""
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Page - Demonstrates: Security & Access (SELECT query)"""
    # Determine returning user info from cookie
    last_email = request.cookies.get('last_email')
    masked_email = mask_email(last_email) if last_email else None
    last_login = None
    last_device = None

    # Fetch last successful login activity for returning user (previous login)
    if last_email:
        conn_activity = get_db_connection()
        if conn_activity:
            try:
                cursor = conn_activity.cursor(cursor_factory=RealDictCursor)
                activity_query = """
                    SELECT la.login_timestamp, la.device_info
                    FROM LoginActivity la
                    JOIN Customers c ON la.customer_id = c.customer_id
                    WHERE c.email = %s
                    ORDER BY la.login_timestamp DESC
                    OFFSET 1 LIMIT 1
                """
                cursor.execute(activity_query, (last_email,))
                activity = cursor.fetchone()
                if activity:
                    last_login = activity["login_timestamp"]
                    last_device = activity["device_info"]
            except Error:
                pass
            finally:
                conn_activity.close()

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again.', 'error')
            return render_template(
                'login.html',
                masked_email=masked_email,
                last_login=last_login,
                last_device=last_device,
            )
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            # SELECT query for authentication
            query = "SELECT customer_id, email, password_hash, full_name FROM Customers WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                # Login successful - record login activity
                device_info = request.headers.get('User-Agent', 'Unknown device')
                ip_address = request.remote_addr

                try:
                    cursor.execute(
                        """
                        INSERT INTO LoginActivity (customer_id, device_info, ip_address)
                        VALUES (%s, %s, %s)
                        """,
                        (user['customer_id'], device_info, ip_address),
                    )
                    conn.commit()
                except Error:
                    conn.rollback()

                # Store user session
                session['user_id'] = user['customer_id']
                session['user_name'] = user['full_name']
                session['user_email'] = user['email']

                cursor.close()
                conn.close()

                # Set masked email cookie for future visits
                response = make_response(redirect(url_for('dashboard')))
                response.set_cookie('last_email', user['email'], max_age=30 * 24 * 60 * 60)
                return response
            else:
                flash('Invalid email or password. Please try again.', 'error')
        except Error as e:
            flash(f'Login error: {str(e)}', 'error')
        finally:
            if conn:
                conn.close()
    
    return render_template(
        'login.html',
        masked_email=masked_email,
        last_login=last_login,
        last_device=last_device,
    )


@app.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard Page - Demonstrates: JOIN operation (Customer + Accounts)
    Shows all accounts for the logged-in user
    """
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('login'))
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # JOIN query: Customer + Accounts with account numbers
        query = """
            SELECT 
                a.account_id,
                a.account_type,
                a.balance,
                a.account_number,
                a.ifsc_code,
                a.branch_name,
                a.created_at,
                c.full_name,
                c.email
            FROM Accounts a
            INNER JOIN Customers c ON a.customer_id = c.customer_id
            WHERE c.customer_id = %s
            ORDER BY a.account_id
        """
        cursor.execute(query, (session['user_id'],))
        accounts = cursor.fetchall()
        
        # Get last login time
        last_login_query = """
            SELECT login_timestamp, device_info
            FROM LoginActivity
            WHERE customer_id = %s
            ORDER BY login_timestamp DESC
            LIMIT 1
        """
        cursor.execute(last_login_query, (session['user_id'],))
        last_login_data = cursor.fetchone()
        
        last_login = None
        if last_login_data and last_login_data['login_timestamp']:
            last_login = last_login_data['login_timestamp'].strftime('%d %b %Y at %I:%M %p')
        
        cursor.close()
        conn.close()
        
        return render_template('dashboard.html', 
                             user_name=session['user_name'],
                             accounts=accounts,
                             last_login=last_login)
    except Error as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        if conn:
            conn.close()
        return redirect(url_for('login'))


@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    """
    Transfer Funds Page - Demonstrates: ACID Transaction, Stored Function, Concurrency Control
    This is the most important page for demonstrating database concepts
    """
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Get user's accounts for dropdown (with account numbers)
        query = """
            SELECT account_id, account_type, balance, account_number, ifsc_code, branch_name
            FROM Accounts
            WHERE customer_id = %s
            ORDER BY account_id
        """
        cursor.execute(query, (session['user_id'],))
        user_accounts = cursor.fetchall()
        
        # Get list of other accounts for reference (to show available accounts to transfer to)
        other_accounts_query = """
            SELECT a.account_id, a.account_number, a.ifsc_code, a.branch_name, c.full_name
            FROM Accounts a
            JOIN Customers c ON a.customer_id = c.customer_id
            WHERE a.customer_id != %s
            ORDER BY c.full_name, a.account_id
        """
        cursor.execute(other_accounts_query, (session['user_id'],))
        other_accounts = cursor.fetchall()
        
        if request.method == 'POST':
            from_account_id = request.form.get('from_account')
            to_account_number = request.form.get('to_account')  # Now expects 12-digit account number
            amount = request.form.get('amount')
            beneficiary_name = request.form.get('beneficiary_name')
            bank_name = request.form.get('bank_name')
            ifsc = request.form.get('ifsc')
            
            # Validation
            if not all([from_account_id, to_account_number, amount, beneficiary_name, bank_name, ifsc]):
                flash('All fields are required.', 'error')
                return render_template('transfer.html', accounts=user_accounts, other_accounts=other_accounts)
            
            try:
                amount = float(amount)
                from_account_id = int(from_account_id)
                
                if amount <= 0:
                    flash('Amount must be greater than zero.', 'error')
                    return render_template('transfer.html', accounts=user_accounts, other_accounts=other_accounts)
                
                # Look up destination account by account_number
                to_account_query = "SELECT account_id FROM Accounts WHERE account_number = %s"
                cursor.execute(to_account_query, (to_account_number,))
                to_account = cursor.fetchone()
                
                if not to_account:
                    flash(f'Account number {to_account_number} not found. Please check and try again.', 'error')
                    cursor.close()
                    conn.close()
                    return render_template('transfer.html', accounts=user_accounts, other_accounts=other_accounts)
                
                to_account_id = to_account['account_id']
                
                if from_account_id == to_account_id:
                    flash('Source and destination accounts cannot be the same.', 'error')
                    cursor.close()
                    conn.close()
                    return render_template('transfer.html', accounts=user_accounts, other_accounts=other_accounts)
                
            except ValueError:
                flash('Invalid input. Please check account number (12 digits) and amount.', 'error')
                return render_template('transfer.html', accounts=user_accounts, other_accounts=other_accounts)
            
            # Call Stored Function for ACID Transaction
            try:
                # AI Fraud Detection Check
                cursor.execute(
                    "SELECT amount FROM TransactionHistory WHERE from_account_id = %s AND status = 'Success' LIMIT 50",
                    (from_account_id,)
                )
                recent_txs = cursor.fetchall()
                is_fraud_risk = ai_utils.analyze_fraud_risk(recent_txs, amount)
                
                # Close previous cursor and create new one for stored function
                cursor.close()
                cursor = conn.cursor()
                # Call stored function (PostgreSQL functions return records)
                cursor.execute(
                    "SELECT * FROM TransferFunds(%s, %s, %s)",
                    (from_account_id, to_account_id, amount)
                )
                result = cursor.fetchone()
                
                # Get output parameters
                status = result[0]  # p_status
                message = result[1]  # p_message
                
                if status == 'Success':
                    conn.commit()  # Commit the transaction
                    if is_fraud_risk:
                        flash(f'{message} (⚠️ AI Alert: This amount is unusually high for your pattern)', 'success')
                    else:
                        flash(message, 'success')
                else:
                    conn.rollback()  # Rollback on failure
                    flash(message, 'error')
                
                cursor.close()
                conn.close()
                
                return redirect(url_for('dashboard'))
                
            except Error as e:
                if conn:
                    conn.rollback()
                    conn.close()
                flash(f'Transfer failed: {str(e)}. Transaction rolled back.', 'error')
                return render_template('transfer.html', accounts=user_accounts, other_accounts=other_accounts)
        
        # Close cursor and connection before returning template
        cursor.close()
        conn.close()
        return render_template('transfer.html', accounts=user_accounts, other_accounts=other_accounts)
        
    except Error as e:
        flash(f'Error: {str(e)}', 'error')
        if conn:
            conn.close()
        return redirect(url_for('dashboard'))


@app.route('/history/<int:account_id>')
@login_required
def history(account_id):
    """
    Transaction History Page - Demonstrates: Indexing (B-tree on timestamp)
    Fast retrieval using indexed timestamp column
    """
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Verify account belongs to user
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        verify_query = "SELECT customer_id FROM Accounts WHERE account_id = %s"
        cursor.execute(verify_query, (account_id,))
        account = cursor.fetchone()
        
        if not account or account['customer_id'] != session['user_id']:
            flash('Access denied. Account not found.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('dashboard'))
        
        # Get account details
        account_query = """
            SELECT account_id, account_type, balance
            FROM Accounts
            WHERE account_id = %s
        """
        cursor.execute(account_query, (account_id,))
        account_info = cursor.fetchone()
        
        # Get transaction history (uses indexed timestamp for fast retrieval)
        history_query = """
            SELECT 
                transaction_id,
                from_account_id,
                to_account_id,
                transaction_type,
                amount,
                status,
                transaction_timestamp
            FROM TransactionHistory
            WHERE from_account_id = %s OR to_account_id = %s
            ORDER BY transaction_timestamp DESC
            LIMIT 50
        """
        cursor.execute(history_query, (account_id, account_id))
        transactions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('history.html', 
                             account=account_info,
                             transactions=transactions)
    except Error as e:
        flash(f'Error loading history: {str(e)}', 'error')
        if conn:
            conn.close()
        return redirect(url_for('dashboard'))


@app.route('/profile')
@login_required
def profile():
    """
    Profile Page - Shows personal info and secure banking details for the logged-in user.
    """
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Fetch customer record
        cursor.execute(
            """
            SELECT customer_id, full_name, email, phone, created_at
            FROM Customers
            WHERE customer_id = %s
            """,
            (session['user_id'],),
        )
        customer = cursor.fetchone()

        # Fetch all accounts for this customer, including sensitive fields
        cursor.execute(
            """
            SELECT
                account_id,
                account_type,
                account_number,
                ifsc_code,
                branch_name,
                balance,
                created_at
            FROM Accounts
            WHERE customer_id = %s
            ORDER BY account_id
            """,
            (session['user_id'],),
        )
        accounts = cursor.fetchall()

        cursor.close()
        conn.close()

        if not customer:
            flash('Profile not found.', 'error')
            return redirect(url_for('dashboard'))

        primary_account = accounts[0] if accounts else None

        return render_template(
            'profile.html',
            customer=customer,
            accounts=accounts,
            primary_account=primary_account,
        )
    except Error as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        if conn:
            conn.close()
        return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
