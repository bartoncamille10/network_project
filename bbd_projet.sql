-- table contenant les Clients
DROP TABLE IF EXISTS Client;
CREATE TABLE Client (
    id SERIAL PRIMARY KEY,  -- Utilisation de SERIAL pour générer automatiquement l'id
    prenom VARCHAR(30),
    nom VARCHAR(30),
    solde FLOAT DEFAULT 0
);

-- table contenant les transactions
DROP TABLE IF EXISTS Transaction;
CREATE TABLE Transaction (
    id SERIAL PRIMARY KEY,  -- Utilisation de SERIAL pour générer automatiquement l'id
    client_source INTEGER NOT NULL,
    client_dest INTEGER NOT NULL,
    montant FLOAT NOT NULL,
    date_transaction TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,  -- Utilisation de TIMESTAMPTZ
    FOREIGN KEY (client_source) REFERENCES Client(id),
    FOREIGN KEY (client_dest) REFERENCES Client(id)
);

-- insert des données dans la table Client
INSERT INTO Client(prenom, nom, solde)
    VALUES 
        ('Barton', 'Camille', 50),
        ('Mlika', 'Imen', 50),
        ('Mazeau', 'Clément', 50),
        ('Lecouffe', 'Eric', 50),
        ('Lucas', 'Joshua', 50);

-- insert des données dans la table Transaction
INSERT INTO Transaction(client_source, client_dest, montant)
    VALUES
        (1, 2, 10),
        (2, 3, 10);
