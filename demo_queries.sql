-- SecureBank Demo Queries for Viva/Evaluation
-- Use these queries to demonstrate database features during evaluation

-- Show all customers and their accounts 
SELECT 
    c.customer_id,
    c.full_name,
    c.email,
    a.account_id,
    a.account_type,
    a.balance
FROM Customers c
INNER JOIN Accounts a ON c.customer_id = a.customer_id
ORDER BY c.customer_id, a.account_id;

--  Show transaction history with account details)
SELECT 
    th.transaction_id,
    th.transaction_timestamp,
    th.transaction_type,
    th.amount,
    th.status,
    fa.account_id AS from_account,
    ta.account_id AS to_account,
    fc.full_name AS from_customer,
    tc.full_name AS to_customer
FROM TransactionHistory th
LEFT JOIN Accounts fa ON th.from_account_id = fa.account_id
LEFT JOIN Accounts ta ON th.to_account_id = ta.account_id
LEFT JOIN Customers fc ON fa.customer_id = fc.customer_id
LEFT JOIN Customers tc ON ta.customer_id = tc.customer_id
ORDER BY th.transaction_timestamp DESC;

-- Show audit log 
SELECT 
    log_id,
    action_type,
    account_id,
    details,
    log_timestamp
FROM AuditLog
ORDER BY log_timestamp DESC
LIMIT 20;

-- Show account balances
SELECT 
    a.account_id,
    a.account_type,
    a.balance,
    c.full_name AS customer_name
FROM Accounts a
JOIN Customers c ON a.customer_id = c.customer_id
ORDER BY a.account_id;

-- Show index usage (
EXPLAIN SELECT 
    transaction_id,
    transaction_timestamp,
    amount,
    status
FROM TransactionHistory
WHERE transaction_timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
ORDER BY transaction_timestamp DESC;

-- Show stored function definition 
SELECT pg_get_functiondef(oid) AS function_definition
FROM pg_proc
WHERE proname = 'transferfunds';

--  Show trigger definitions 
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public';

--  Show all indexes in the database 
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;



START TRANSACTION;

SELECT balance FROM Accounts WHERE account_id = 1 FOR UPDATE;

-- Try to transfer more than balance (will fail)
UPDATE Accounts SET balance = balance - 10000 WHERE account_id = 1;

-- Check if it worked 
SELECT balance FROM Accounts WHERE account_id = 1;

ROLLBACK;  

-- Verify balance is unchanged
SELECT balance FROM Accounts WHERE account_id = 1;
