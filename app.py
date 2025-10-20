from flask import Flask, render_template, request, redirect, url_for
import sqlite3, bcrypt, os

app = Flask(__name__)

DB_FILE = "atm.db"

# ---------- DB setup ----------
def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE users(
            card_number TEXT PRIMARY KEY,
            pin_hash BLOB NOT NULL,
            balance REAL DEFAULT 1000.0
        );
        """)
        # Add one demo user: card 123456, PIN 1234
        pin = b"1234"
        hashed = bcrypt.hashpw(pin, bcrypt.gensalt())
        cur.execute("INSERT INTO users VALUES (?, ?, ?)", ("123456", hashed, 1000.0))
        conn.commit()
        conn.close()

init_db()

# ---------- Routes ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        card = request.form['card']
        pin = request.form['pin'].encode('utf-8')
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT pin_hash,balance FROM users WHERE card_number=?", (card,))
        row = cur.fetchone()
        conn.close()

        if row and bcrypt.checkpw(pin, row[0]):
            return render_template('dashboard.html', card=card, balance=row[1])
        else:
            return render_template('error.html', message="Invalid card or PIN!")
    return render_template('login.html')

@app.route('/withdraw', methods=['POST'])
def withdraw():
    card = request.form['card']
    amount = float(request.form['amount'])
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE card_number=?", (card,))
    row = cur.fetchone()
    if not row:
        return render_template('error.html', message="Card not found!")
    balance = row[0]
    if amount > balance:
        return render_template('error.html', message="Insufficient balance!")
    new_balance = balance - amount
    cur.execute("UPDATE users SET balance=? WHERE card_number=?", (new_balance, card))
    conn.commit()
    conn.close()
    return render_template('dashboard.html', card=card, balance=new_balance)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
