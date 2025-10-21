from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecret"

# ---------- DB Helper ----------
def get_db():
    conn = sqlite3.connect("atm.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Dummy sound function ----------
def play_sound(name):
    print(f"🔊 Sound played: {name}")

# ---------- Routes ----------
@app.route("/")
def dashboard():
    # Create dummy session for demo
    if "user" not in session:
        session["user"] = {"id": 1, "name": "Naveen"}

    uid = session["user"]["id"]

    # Ensure table exists
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts(
            id INTEGER PRIMARY KEY,
            name TEXT,
            balance INTEGER DEFAULT 5000
        )
    """)
    cur.execute("INSERT OR IGNORE INTO accounts (id, name, balance) VALUES (?, ?, 5000)", (uid, session["user"]["name"]))
    conn.commit()

    cur.execute("SELECT balance FROM accounts WHERE id=?", (uid,))
    bal = cur.fetchone()["balance"]
    conn.close()

    return render_template(
        "dashboard.html",
        welcome="Welcome",
        user={"name": session["user"]["name"], "balance": bal},
        withdraw="Withdraw",
        deposit="Deposit",
        balance="Check Balance",
        exit="Exit"
    )


@app.route("/withdraw", methods=["POST"])
def withdraw():
    if "user" not in session:
        return redirect(url_for("dashboard"))
    uid = session["user"]["id"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = balance - 1000 WHERE id = ?", (uid,))
    print(f"Updated {cur.rowcount} rows for user {uid}")
    conn.commit()
    conn.close()

    play_sound("success")
    return redirect(url_for("dashboard"))


@app.route("/deposit", methods=["POST"])
def deposit():
    if "user" not in session:
        return redirect(url_for("dashboard"))
    uid = session["user"]["id"]

    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = balance + 1000 WHERE id = ?", (uid,))
    conn.commit(); conn.close()

    play_sound("success")
    return redirect(url_for("dashboard"))


@app.route("/balance", methods=["POST"])
def balance():
    return redirect(url_for("dashboard"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return "<h2>Logged out. <a href='/'>Go back</a></h2>"


if __name__ == "__main__":
    app.run(debug=True)
