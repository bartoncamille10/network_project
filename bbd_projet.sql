-- table contenant les Clients
DROP TABLE IF EXISTS Client;
CREATE TABLE Client (
    account INTEGER PRIMARY KEY AUTOINCREMENT,
    currency VARCHAR(10) NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0 CHECK (balance >= 0)
);

-- table contenant les transactions
DROP TABLE IF EXISTS Transaction;
CREATE TABLE Transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_source INTEGER NOT NULL,
    client_dest INTEGER NOT NULL,
    montant REAL NOT NULL,
    date_transaction DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_source) REFERENCES Client(account),
    FOREIGN KEY (client_dest) REFERENCES Client(account)
);

-- insert des données dans la table Client
INSERT INTO Client(currency, balance)
    VALUES 
        ('EUR', 50),
        ('EUR', 50),
        ('EUR', 50),
        ('EUR', 50),
        ('EUR', 50);

INSERT INTO Client(account, currency, balance) VALUES (1, 'EUR', 500);
INSERT INTO Client(account, currency, balance) VALUES (2, 'EUR', 300);

-- insert des données dans la table Transaction
INSERT INTO Transaction(client_source, client_dest, montant)
    VALUES
        (1, 2, 10),
        (2, 3, 10);
