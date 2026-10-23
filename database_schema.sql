


-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS LoginActivity CASCADE;
DROP TABLE IF EXISTS TransactionHistory CASCADE;
DROP TABLE IF EXISTS AuditLog CASCADE;
DROP TABLE IF EXISTS Accounts CASCADE;
DROP TABLE IF EXISTS Customers CASCADE;

-- Customers Table 
CREATE TABLE Customers (
    customer_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index 
CREATE INDEX idx_email ON Customers(email);

-- Accounts Table 
CREATE TABLE Accounts (
    account_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    account_type VARCHAR(20) NOT NULL,  
    account_number VARCHAR(20) UNIQUE NOT NULL,
    ifsc_code VARCHAR(11) NOT NULL,
    branch_name VARCHAR(100) NOT NULL,
    balance DECIMAL(15, 2) DEFAULT 0.00 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE
);

-- Index for JOIN and lookup operations
CREATE INDEX idx_customer_id ON Accounts(customer_id);
CREATE INDEX idx_accounts_ifsc ON Accounts(ifsc_code);

-- TransactionHistory Table 
CREATE TABLE TransactionHistory (
    transaction_id SERIAL PRIMARY KEY,
    from_account_id INTEGER,
    to_account_id INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,  
    amount DECIMAL(15, 2) NOT NULL,
    status VARCHAR(20) NOT NULL,  
    transaction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_account_id) REFERENCES Accounts(account_id) ON DELETE SET NULL,
    FOREIGN KEY (to_account_id) REFERENCES Accounts(account_id) ON DELETE CASCADE
);

CREATE INDEX idx_timestamp ON TransactionHistory(transaction_timestamp);
CREATE INDEX idx_to_account ON TransactionHistory(to_account_id);
CREATE INDEX idx_from_account ON TransactionHistory(from_account_id);

-- AuditLog Table 
CREATE TABLE AuditLog (
    log_id SERIAL PRIMARY KEY,
    action_type VARCHAR(50) NOT NULL,
    user_id INTEGER,
    account_id INTEGER,
    details TEXT,
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_log_timestamp ON AuditLog(log_timestamp);

-- LoginActivity Table 
CREATE TABLE LoginActivity (
    activity_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES Customers(customer_id) ON DELETE CASCADE,
    login_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_info TEXT,
    ip_address VARCHAR(45)
);

CREATE INDEX idx_loginactivity_customer ON LoginActivity(customer_id);

-- Insert Sample Data
INSERT INTO Customers (email, password_hash, full_name, phone) VALUES
('john.doe@email.com', 'hashed_password_123', 'John Doe', '+1-555-0100'),
('jane.smith@email.com', 'hashed_password_456', 'Jane Smith', '+44-20-7946-001'),
('bob.wilson@email.com', 'hashed_password_789', 'Bob Wilson', '+91-22-4000-100');



INSERT INTO Accounts (customer_id, account_type, account_number, ifsc_code, branch_name, balance) VALUES
(1, 'Savings', '100000000001', 'HDFC0001001', 'Mumbai Downtown', 5000.00),
(1, 'Checking', '100000000002', 'HDFC0001001', 'Mumbai Downtown', 2500.00),
(2, 'Savings', '100000000003', 'ICIC0002002', 'Bangalore MG Road', 10000.00),
(3, 'Savings', '100000000004', 'SBIN0003003', 'Delhi Connaught Place', 7500.00);

INSERT INTO TransactionHistory (from_account_id, to_account_id, transaction_type, amount, status) VALUES
(1, 2, 'Transfer', 500.00, 'Success'),
(2, 1, 'Transfer', 200.00, 'Success'),
(1, 3, 'Transfer', 1000.00, 'Success'),
(3, 1, 'Transfer', 250.00, 'Success');




