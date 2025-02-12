-- table contenant les Clients
DROP TABLE IF EXISTS Client;
CREATE TABLE Client (
    account SERIAL PRIMARY KEY,  -- Utilisation de SERIAL pour générer automatiquement l'id
    currency VARCHAR(10) NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0 CHECK (balance >= 0) -- On empêche les soldes négatifs 
);

-- table contenant les transactions
DROP TABLE IF EXISTS Transaction;
CREATE TABLE Transaction (
    id SERIAL PRIMARY KEY,  -- Utilisation de SERIAL pour générer automatiquement l'id
    client_source INTEGER NOT NULL,
    client_dest INTEGER NOT NULL,
    montant FLOAT NOT NULL,
    date_transaction TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,  
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
-- INSERT INTO Transaction(client_source, client_dest, montant)
--     VALUES
--         (1, 2, 10),
--         (2, 3, 10);
