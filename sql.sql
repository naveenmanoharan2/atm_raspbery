import sqlite3, bcrypt
conn = sqlite3.connect('atm.db')
cur = conn.cursor()
cur.execute("INSERT INTO accounts (card_id,name,pin_hash,balance_cents) VALUES (?,?,?,?)",
            ('card001','Alice', bcrypt.hashpw(b'1234', bcrypt.gensalt()), 50000))
conn.commit(); conn.close()
