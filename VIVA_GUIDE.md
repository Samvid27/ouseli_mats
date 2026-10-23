# SecureBank — Viva Preparation Guide

All database concepts used in this project, where they appear, and how to explain them.

---

## 1. Relational Schema Design & Normalization

**Files:** [database_schema.sql](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/database_schema.sql)

| Table | Purpose |
|---|---|
| `Customers` | Stores user info (email, hashed password, name, phone) |
| `Accounts` | Bank accounts linked to a customer via FK |
| `TransactionHistory` | Records every transfer between accounts |
| `AuditLog` | Auto-populated by triggers for audit trail |
| `LoginActivity` | Tracks login timestamps, device, IP |

**Key points for viva:**
- Tables are in **3NF** — no transitive dependencies, each non-key column depends only on the primary key.
- `SERIAL PRIMARY KEY` is used for auto-incrementing IDs.
- `DECIMAL(15, 2)` for monetary values to avoid floating-point errors.

---

## 2. Primary Keys & Foreign Keys (Referential Integrity)

**File:** [database_schema.sql](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/database_schema.sql)

```sql
-- Primary Key
customer_id SERIAL PRIMARY KEY

-- Foreign Key with CASCADE
FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE

-- Foreign Key with SET NULL
FOREIGN KEY (from_account_id) REFERENCES Accounts(account_id) ON DELETE SET NULL
```

**Key points:**
- **`ON DELETE CASCADE`** — deleting a customer automatically deletes their accounts.
- **`ON DELETE SET NULL`** — deleting an account sets `from_account_id` to NULL in transaction history (preserves the record).
- **`UNIQUE` constraint** on `email` and `account_number` prevents duplicates.

---

## 3. Indexing (B-Tree Index)

**File:** [database_schema.sql](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/database_schema.sql)

```sql
CREATE INDEX idx_email ON Customers(email);               -- Fast login lookup
CREATE INDEX idx_customer_id ON Accounts(customer_id);     -- Fast JOIN
CREATE INDEX idx_timestamp ON TransactionHistory(transaction_timestamp); -- Fast history query
CREATE INDEX idx_from_account ON TransactionHistory(from_account_id);
CREATE INDEX idx_to_account ON TransactionHistory(to_account_id);
CREATE INDEX idx_log_timestamp ON AuditLog(log_timestamp);
```

**Key points:**
- PostgreSQL uses **B+ Tree** indexes by default.
- `idx_timestamp` speeds up `ORDER BY transaction_timestamp DESC` in the history page.
- `idx_email` speeds up the login `SELECT ... WHERE email = %s` query.
- Use `EXPLAIN` to prove index usage:
  ```sql
  EXPLAIN SELECT * FROM TransactionHistory
  WHERE transaction_timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days';
  ```

---

## 4. JOIN Operations

**File:** [app.py](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/app.py) — Dashboard route (line ~552)

```sql
SELECT a.account_id, a.account_type, a.balance, c.full_name, c.email
FROM Accounts a
INNER JOIN Customers c ON a.customer_id = c.customer_id
WHERE c.customer_id = %s
```

**All JOIN types used in the project:**

| Type | Where Used | Purpose |
|---|---|---|
| **INNER JOIN** | Dashboard page | Combine `Customers` + `Accounts` |
| **LEFT JOIN** | `demo_queries.sql` | Transaction history with account/customer names (handles NULLs) |
| **JOIN** | Transfer page | Get other accounts with customer names |

**Key points:**
- INNER JOIN returns only matching rows from both tables.
- LEFT JOIN keeps all rows from the left table even if there's no match.

---

## 5. ACID Transactions

**File:** [stored_procedures.sql](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/stored_procedures.sql)

This is the **most important concept** in the project. The `TransferFunds` function demonstrates all four ACID properties:

| Property | How It's Implemented |
|---|---|
| **Atomicity** | Both `UPDATE` statements (debit + credit) either both succeed or both fail. If any error occurs, `EXCEPTION WHEN OTHERS` triggers a rollback. |
| **Consistency** | Validation checks (sufficient balance, valid accounts, positive amount) run *before* any modification. |
| **Isolation** | `SELECT ... FOR UPDATE` locks the rows so no other transaction can modify them simultaneously. |
| **Durability** | After `COMMIT` in `app.py`, the changes are permanently saved to disk by PostgreSQL. |

**How to demonstrate:**
1. Make a successful transfer → show balances changed.
2. Try to transfer more than the balance → show "Insufficient balance" and balances unchanged (ROLLBACK).

---

## 6. Stored Functions (Stored Procedures)

**File:** [stored_procedures.sql](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/stored_procedures.sql)

```sql
CREATE OR REPLACE FUNCTION TransferFunds(
    p_from_account_id INTEGER,
    p_to_account_id INTEGER,
    p_amount DECIMAL(15, 2),
    OUT p_status VARCHAR(50),
    OUT p_message VARCHAR(255)
) RETURNS RECORD LANGUAGE plpgsql AS $$ ...
```

**Called from Python in** [app.py](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/app.py):
```python
cursor.execute("SELECT * FROM TransferFunds(%s, %s, %s)", (from_id, to_id, amount))
```

**Key points:**
- Written in **PL/pgSQL** (PostgreSQL's procedural language).
- Uses `OUT` parameters to return status and message.
- Business logic lives in the database, not in application code — ensures consistency even if called from different apps.

---

## 7. Concurrency Control (Row-Level Locking)

**File:** [stored_procedures.sql](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/stored_procedures.sql) — lines 29-37

```sql
SELECT balance INTO v_from_balance
FROM Accounts WHERE account_id = p_from_account_id
FOR UPDATE;  -- Row-level lock
```

**Key points:**
- `SELECT ... FOR UPDATE` acquires an **exclusive row-level lock**.
- Prevents **lost update** problem: if two users transfer from the same account simultaneously, one waits until the other commits.
- This is **pessimistic concurrency control** (lock first, then operate).

---

## 8. Triggers & Audit Logging

**File:** [triggers.sql](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/triggers.sql)

### Trigger 1: Transfer Audit
```sql
CREATE TRIGGER audit_transfer_access
AFTER INSERT ON TransactionHistory
FOR EACH ROW
EXECUTE FUNCTION audit_transfer_access_func();
```
→ Automatically logs every new transaction into `AuditLog`.

### Trigger 2: Balance Change Audit
```sql
CREATE TRIGGER audit_balance_update
AFTER UPDATE ON Accounts
FOR EACH ROW
EXECUTE FUNCTION audit_balance_update_func();
```
→ Logs whenever a balance changes, recording old and new values.

**Key points:**
- Triggers are **AFTER** triggers (fire after the DML operation).
- **FOR EACH ROW** — fires once per affected row.
- Uses `NEW` (new row values) and `OLD` (previous row values) to access data.
- **How to demonstrate:** Transfer funds, then run:
  ```sql
  SELECT * FROM AuditLog ORDER BY log_timestamp DESC LIMIT 5;
  ```

---

## 9. Data Manipulation (DML Operations)

| Operation | Where Used |
|---|---|
| `SELECT` | Login authentication, dashboard, history, profile |
| `INSERT` | New transactions, login activity logging, audit log entries |
| `UPDATE` | Balance changes during transfer, password hash updates |
| `DELETE` | Cascading deletes via foreign keys |

---

## 10. Security — Password Hashing

**File:** [setup_database.py](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/setup_database.py)

```python
from werkzeug.security import generate_password_hash
password_hash = generate_password_hash(password)
```

**File:** [app.py](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/app.py)
```python
from werkzeug.security import check_password_hash
if user and check_password_hash(user['password_hash'], password):
```

- Passwords are **never stored in plaintext**.
- Uses Werkzeug's PBKDF2 hashing (salted).

---

## 11. Parameterized Queries (SQL Injection Prevention)

**File:** [app.py](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/app.py)

```python
# SAFE — parameterized
cursor.execute("SELECT ... WHERE email = %s", (email,))

# UNSAFE — string interpolation (NOT used in this project)
# cursor.execute(f"SELECT ... WHERE email = '{email}'")
```

All queries use `%s` placeholders with psycopg2, preventing SQL injection attacks.

---

## 12. AI/ML Integration (Statistical Analysis)

**File:** [ai_utils.py](file:///c:/Users/Samvid/Downloads/web_project/dbms_project/ai_utils.py)

| Feature | Method | Formula |
|---|---|---|
| **Fraud Detection** | Statistical anomaly detection | Flag if `amount > mean + 3 × stdev` |
| **Balance Forecast** | Simple linear regression | `y = mx + c` computed from daily balance history |

---

## Quick Viva Cheat Sheet

| If asked about... | Say this & show this |
|---|---|
| **JOINs** | "Dashboard uses INNER JOIN to combine Customers and Accounts tables" → show dashboard page |
| **ACID** | "Transfer uses a stored function with BEGIN/COMMIT/ROLLBACK. `FOR UPDATE` provides isolation" → do a transfer, then try one that fails |
| **Indexing** | "B+ Tree indexes on email, timestamp, and account IDs for fast lookups" → run `EXPLAIN` query |
| **Triggers** | "Two AFTER triggers auto-log to AuditLog on every transfer and balance change" → show AuditLog after a transfer |
| **Stored Procedures** | "TransferFunds is a PL/pgSQL function with OUT parameters" → show `stored_procedures.sql` |
| **Concurrency** | "`SELECT ... FOR UPDATE` locks rows to prevent lost updates" → show line 29-37 in stored_procedures.sql |
| **Normalization** | "Tables are in 3NF — each non-key attribute depends only on the primary key" |
| **Security** | "Passwords are hashed with PBKDF2, queries are parameterized to prevent SQL injection" |
