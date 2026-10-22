import sqlite3
from Encryption import Encryption

def init_db():
    crypto = Encryption()  # same key as the app will use
    
    conn = sqlite3.connect('contest.db')
    cur = conn.cursor()

    # start fresh every time
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("DROP TABLE IF EXISTS entries")

    # users table - name, phone, password are encrypted in the db
    cur.execute('''
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            phone TEXT NOT NULL,
            security_level INTEGER NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # entries table - one user can have many baking items
    cur.execute('''
        CREATE TABLE entries (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            baking_item TEXT NOT NULL,
            excellent_votes INTEGER DEFAULT 0,
            ok_votes INTEGER DEFAULT 0,
            bad_votes INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # sample users - one of each security level
    users_data = [
        # Level 1 User
        ('Grace', 21, '555-0123', 1, 'Ilovecoding1!'),
        # Level 2 User
        ('Kim', 64, '555-0420', 2, 'Ilovecoding1!'),
        # Level 3 User (Admin)
        ('David', 65, '555-0789', 3, 'Ilovecoding1!')
    ]

    print("Inserting Users...")
    for name, age, phone, sec, pwd in users_data:
        # encrypt the sensitive fields before storing
        enc_name = crypto.encrypt(name)
        enc_phone = crypto.encrypt(phone)
        enc_pwd = crypto.encrypt(pwd)
        
        cur.execute("INSERT INTO users (name, age, phone, security_level, password) VALUES (?, ?, ?, ?, ?)",
                    (enc_name, age, enc_phone, sec, enc_pwd))

    # one entry for each starter user
    cur.execute("INSERT INTO entries (user_id, baking_item, excellent_votes, ok_votes, bad_votes) VALUES (1, 'Whoot Whoot Brownies', 1, 2, 4)")
    cur.execute("INSERT INTO entries (user_id, baking_item, excellent_votes, ok_votes, bad_votes) VALUES (2, 'Sugar Cookies', 2, 2, 1)")
    cur.execute("INSERT INTO entries (user_id, baking_item, excellent_votes, ok_votes, bad_votes) VALUES (3, 'Perfect Pie', 5, 0, 0)")

    conn.commit()
    
    # show the raw encrypted data so we know it worked
    print("\n--- Verifying Database Content (Raw/Encrypted) ---")
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    for row in rows:
        print(row)
        
    conn.close()
    print("\nDatabase initialized successfully.")

if __name__ == '__main__':
    init_db()