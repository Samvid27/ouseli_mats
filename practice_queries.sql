-- =====================================================
-- SecureBank — Practice Queries for Viva
-- Run these in psql or pgAdmin connected to 'securebank'
-- =====================================================


-- =====================================================
-- SECTION 1: BASIC SELECT QUERIES
-- =====================================================

-- Q1. Show all customers
SELECT * FROM Customers;

-- Q2. Show all accounts
SELECT * FROM Accounts;

-- Q3. Show only Savings accounts
SELECT account_id, account_number, balance
FROM Accounts
WHERE account_type = 'Savings';

-- Q4. Show customers created after a certain date
SELECT full_name, email, created_at
FROM Customers
WHERE created_at >= '2025-01-01';

-- Q5. Show accounts with balance greater than 5000
SELECT account_number, account_type, balance
FROM Accounts
WHERE balance > 5000;


-- =====================================================
-- SECTION 2: AGGREGATE FUNCTIONS (MAX, MIN, AVG, SUM, COUNT)
-- =====================================================

-- Q6. Total number of customers
SELECT COUNT(*) AS total_customers FROM Customers;

-- Q7. Total number of accounts
SELECT COUNT(*) AS total_accounts FROM Accounts;

-- Q8. Maximum balance across all accounts
SELECT MAX(balance) AS highest_balance FROM Accounts;

-- Q9. Minimum balance across all accounts
SELECT MIN(balance) AS lowest_balance FROM Accounts;

-- Q10. Average balance across all accounts
SELECT ROUND(AVG(balance), 2) AS average_balance FROM Accounts;

-- Q11. Total money in the bank (sum of all balances)
SELECT SUM(balance) AS total_deposits FROM Accounts;

-- Q12. Count of accounts per account type
SELECT account_type, COUNT(*) AS num_accounts
FROM Accounts
GROUP BY account_type;

-- Q13. Average balance per account type
SELECT account_type, ROUND(AVG(balance), 2) AS avg_balance
FROM Accounts
GROUP BY account_type;

-- Q14. Total balance per customer
SELECT c.full_name, SUM(a.balance) AS total_balance
FROM Customers c
JOIN Accounts a ON c.customer_id = a.customer_id
GROUP BY c.full_name
ORDER BY total_balance DESC;

-- Q15. Maximum single transaction amount
SELECT MAX(amount) AS largest_transaction FROM TransactionHistory;

-- Q16. Average transaction amount
SELECT ROUND(AVG(amount), 2) AS avg_transaction FROM TransactionHistory;

-- Q17. Total amount transferred (sum of all successful transfers)
SELECT SUM(amount) AS total_transferred
FROM TransactionHistory
WHERE status = 'Success';

-- Q18. Number of transactions per status
SELECT status, COUNT(*) AS num_transactions
FROM TransactionHistory
GROUP BY status;


-- =====================================================
-- SECTION 3: GROUP BY + HAVING
-- =====================================================

-- Q19. Customers with total balance > 5000
SELECT c.full_name, SUM(a.balance) AS total_balance
FROM Customers c
JOIN Accounts a ON c.customer_id = a.customer_id
GROUP BY c.full_name
HAVING SUM(a.balance) > 5000;

-- Q20. Account types with average balance > 3000
SELECT account_type, ROUND(AVG(balance), 2) AS avg_balance
FROM Accounts
GROUP BY account_type
HAVING AVG(balance) > 3000;

-- Q21. Accounts that have more than 2 transactions
SELECT from_account_id, COUNT(*) AS txn_count
FROM TransactionHistory
WHERE from_account_id IS NOT NULL
GROUP BY from_account_id
HAVING COUNT(*) > 2;


-- =====================================================
-- SECTION 4: JOIN QUERIES
-- =====================================================

-- Q22. INNER JOIN — Customer names with their account details
SELECT c.full_name, c.email, a.account_type, a.account_number, a.balance
FROM Customers c
INNER JOIN Accounts a ON c.customer_id = a.customer_id
ORDER BY c.full_name;

-- Q23. LEFT JOIN — All customers even if they have no accounts
SELECT c.full_name, a.account_type, a.balance
FROM Customers c
LEFT JOIN Accounts a ON c.customer_id = a.customer_id;

-- Q24. JOIN with multiple tables — Full transaction details
SELECT
    th.transaction_id,
    th.amount,
    th.status,
    th.transaction_timestamp,
    fc.full_name AS sender,
    tc.full_name AS receiver
FROM TransactionHistory th
LEFT JOIN Accounts fa ON th.from_account_id = fa.account_id
LEFT JOIN Accounts ta ON th.to_account_id = ta.account_id
LEFT JOIN Customers fc ON fa.customer_id = fc.customer_id
LEFT JOIN Customers tc ON ta.customer_id = tc.customer_id
ORDER BY th.transaction_timestamp DESC;

-- Q25. Self-referencing query — Accounts at the same branch
SELECT a1.account_number AS acc1, a2.account_number AS acc2, a1.branch_name
FROM Accounts a1
JOIN Accounts a2 ON a1.branch_name = a2.branch_name
  AND a1.account_id < a2.account_id;


-- =====================================================
-- SECTION 5: SUBQUERIES
-- =====================================================

-- Q26. Customer with the highest total balance
SELECT full_name, email
FROM Customers
WHERE customer_id = (
    SELECT customer_id FROM Accounts
    GROUP BY customer_id
    ORDER BY SUM(balance) DESC
    LIMIT 1
);

-- Q27. Accounts with balance above average
SELECT account_number, account_type, balance
FROM Accounts
WHERE balance > (SELECT AVG(balance) FROM Accounts);

-- Q28. Customers who have made at least one transaction
SELECT full_name, email
FROM Customers
WHERE customer_id IN (
    SELECT DISTINCT a.customer_id
    FROM Accounts a
    JOIN TransactionHistory th ON a.account_id = th.from_account_id
);

-- Q29. Accounts that have never sent a transaction
SELECT account_number, account_type
FROM Accounts
WHERE account_id NOT IN (
    SELECT DISTINCT from_account_id
    FROM TransactionHistory
    WHERE from_account_id IS NOT NULL
);


-- =====================================================
-- SECTION 6: ORDER BY, LIMIT, DISTINCT
-- =====================================================

-- Q30. Top 3 accounts by balance
SELECT account_number, account_type, balance
FROM Accounts
ORDER BY balance DESC
LIMIT 3;

-- Q31. Last 5 transactions
SELECT transaction_id, amount, status, transaction_timestamp
FROM TransactionHistory
ORDER BY transaction_timestamp DESC
LIMIT 5;

-- Q32. Distinct branches in the system
SELECT DISTINCT branch_name FROM Accounts;

-- Q33. Distinct transaction statuses
SELECT DISTINCT status FROM TransactionHistory;


-- =====================================================
-- SECTION 7: DATE FUNCTIONS
-- =====================================================

-- Q34. Transactions from the last 7 days
SELECT * FROM TransactionHistory
WHERE transaction_timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days';

-- Q35. Transactions grouped by date
SELECT DATE(transaction_timestamp) AS txn_date, COUNT(*) AS num_txns, SUM(amount) AS total
FROM TransactionHistory
GROUP BY DATE(transaction_timestamp)
ORDER BY txn_date DESC;

-- Q36. Login activity in the last 24 hours
SELECT c.full_name, la.login_timestamp, la.device_info
FROM LoginActivity la
JOIN Customers c ON la.customer_id = c.customer_id
WHERE la.login_timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY la.login_timestamp DESC;


-- =====================================================
-- SECTION 8: VIEWS (if professor asks)
-- =====================================================

-- Q37. Create a view for customer account summary
CREATE OR REPLACE VIEW CustomerAccountSummary AS
SELECT
    c.customer_id,
    c.full_name,
    c.email,
    COUNT(a.account_id) AS num_accounts,
    SUM(a.balance) AS total_balance,
    MAX(a.balance) AS max_balance,
    MIN(a.balance) AS min_balance
FROM Customers c
LEFT JOIN Accounts a ON c.customer_id = a.customer_id
GROUP BY c.customer_id, c.full_name, c.email;

-- Use the view
SELECT * FROM CustomerAccountSummary;


-- =====================================================
-- SECTION 9: INDEX USAGE (EXPLAIN)
-- =====================================================

-- Q38. Show that the timestamp index is being used
EXPLAIN SELECT * FROM TransactionHistory
WHERE transaction_timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
ORDER BY transaction_timestamp DESC;

-- Q39. Show that the email index is being used
EXPLAIN SELECT * FROM Customers WHERE email = 'john.doe@email.com';

-- Q40. Show all indexes in the database
SELECT tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;


-- =====================================================
-- SECTION 10: STORED FUNCTION & TRIGGERS (show these exist)
-- =====================================================

-- Q41. Show the TransferFunds function definition
SELECT pg_get_functiondef(oid) AS function_definition
FROM pg_proc
WHERE proname = 'transferfunds';

-- Q42. Show all triggers
SELECT trigger_name, event_manipulation, event_object_table, action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public';

-- Q43. Show audit log entries (proof triggers work)
SELECT * FROM AuditLog ORDER BY log_timestamp DESC LIMIT 10;


-- =====================================================
-- SECTION 11: UPDATE & DELETE
-- =====================================================

-- Q44. Update a customer's phone number
-- UPDATE Customers SET phone = '+91-99-1234-5678' WHERE email = 'john.doe@email.com';

-- Q45. Delete a specific transaction (careful!)
-- DELETE FROM TransactionHistory WHERE transaction_id = 99;

-- NOTE: Uncomment the above only if you want to actually run them.
-- They modify data!


-- =====================================================
-- SECTION 12: TRANSACTION CONTROL (demo in psql)
-- =====================================================

-- Q46. Manual transaction with ROLLBACK demo
-- Run these one-by-one in psql:

-- START TRANSACTION;
-- SELECT balance FROM Accounts WHERE account_id = 1;  -- Note the balance
-- UPDATE Accounts SET balance = balance - 99999 WHERE account_id = 1;
-- SELECT balance FROM Accounts WHERE account_id = 1;  -- Balance changed!
-- ROLLBACK;
-- SELECT balance FROM Accounts WHERE account_id = 1;  -- Balance restored!
