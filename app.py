from flask import Flask, render_template, request, redirect, url_for
import sqlite3, bcrypt, os, datetime

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
        cur.execute("""
        CREATE TABLE transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_number TEXT,
            type TEXT,
            amount REAL,
            timestamp TEXT
        );
        """)
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
            return redirect(url_for('dashboard', card=card))
        else:
            return render_template('error.html', message="Invalid card or PIN!")
    return render_template('login.html')

@app.route('/dashboard/<card>')
def dashboard(card):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE card_number=?", (card,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return render_template('error.html', message="Card not found!")
    return render_template('dashboard.html', card=card, balance=row[0])

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
    cur.execute("INSERT INTO transactions(card_number,type,amount,timestamp) VALUES(?,?,?,?)",
                (card, 'Withdraw', amount, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard', card=card))

@app.route('/deposit', methods=['POST'])
def deposit():
    card = request.form['card']
    amount = float(request.form['amount'])
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE card_number=?", (card,))
    row = cur.fetchone()
    if not row:
        return render_template('error.html', message="Card not found!")
    new_balance = row[0] + amount
    cur.execute("UPDATE users SET balance=? WHERE card_number=?", (new_balance, card))
    cur.execute("INSERT INTO transactions(card_number,type,amount,timestamp) VALUES(?,?,?,?)",
                (card, 'Deposit', amount, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard', card=card))

@app.route('/history/<card>')
def history(card):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT type, amount, timestamp FROM transactions WHERE card_number=? ORDER BY id DESC LIMIT 10", (card,))
    rows = cur.fetchall()
    conn.close()
    return render_template('history.html', card=card, transactions=rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
