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
    if "user" not in session:
        return redirect(url_for("login"))

    uid = session["user"]["id"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts(
            id INTEGER PRIMARY KEY,
            name TEXT,
            balance INTEGER DEFAULT 5000
        )
    """)
    cur.execute("INSERT OR IGNORE INTO accounts (id, name, balance) VALUES (?, ?, 5000)",
                (uid, session["user"]["name"]))
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


@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if "user" not in session:
        return redirect(url_for("login"))
    uid = session["user"]["id"]

    if request.method == "POST":
        amount = request.form.get("amount")
        if not amount:
            return redirect(url_for("withdraw"))

        try:
            amount = int(amount)
        except ValueError:
            return "Invalid amount", 400

        # Update DB balance
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, uid))
        conn.commit()
        conn.close()

        play_sound("success")

        return f"""
        <body style='font-family:Inter,system-ui;background:#0a0f24;color:white;text-align:center;padding-top:20%;'>
          <h2>✅ Withdrawal of ₹{amount} successful!</h2>
          <a href='{url_for('dashboard')}' style='color:#00aaff;font-size:22px;'>Back to Dashboard</a>
        </body>
        """

    # GET → show predefined options
    return render_template("withdraw.html")


@app.route("/withdraw_other", methods=["GET", "POST"])
def withdraw_other():
    if "user" not in session:
        return redirect(url_for("login"))
    uid = session["user"]["id"]

    if request.method == "POST":
        amount = request.form.get("amount")
        if not amount:
            return redirect(url_for("withdraw_other"))

        try:
            amount = int(amount)
        except ValueError:
            return "Invalid amount", 400

        # Deduct entered amount from balance
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, uid))
        conn.commit()
        conn.close()

        play_sound("success")

        return f"""
        <body style='font-family:Inter,system-ui;background:#0a0f24;color:white;text-align:center;padding-top:20%;'>
          <h2>✅ Withdrawal of ₹{amount} successful!</h2>
          <a href='{url_for('dashboard')}' style='color:#00aaff;font-size:22px;'>Back to Dashboard</a>
        </body>
        """

    # GET → show form to input custom amount
    return render_template("withdraw_other.html")


@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    if "user" not in session:
        return redirect(url_for("login"))
    uid = session["user"]["id"]

    if request.method == "POST":
        amount = request.form.get("amount")
        if not amount:
            return redirect(url_for("deposit"))

        try:
            amount = int(amount)
        except ValueError:
            return "Invalid amount", 400

        # --- Update balance (add instead of subtract) ---
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, uid))
        conn.commit()
        conn.close()

        play_sound("success")

        return f"""
        <body style='font-family:Inter,system-ui;background:#0a0f24;color:white;text-align:center;padding-top:20%;'>
          <h2>✅ ₹{amount} deposited successfully!</h2>
          <a href='{url_for('dashboard')}' style='color:#00ff88;font-size:22px;'>Back to Dashboard</a>
        </body>
        """

    # GET → show deposit options
    return render_template("deposit.html")


@app.route("/deposit_other", methods=["GET", "POST"])
def deposit_other():
    if "user" not in session:
        return redirect(url_for("login"))
    uid = session["user"]["id"]

    if request.method == "POST":
        amount = request.form.get("amount")
        if not amount:
            return redirect(url_for("deposit_other"))

        try:
            amount = int(amount)
        except ValueError:
            return "Invalid amount", 400

        # --- Add custom amount ---
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, uid))
        conn.commit()
        conn.close()

        play_sound("success")

        return f"""
        <body style='font-family:Inter,system-ui;background:#0a0f24;color:white;text-align:center;padding-top:20%;'>
          <h2>✅ ₹{amount} deposited successfully!</h2>
          <a href='{url_for('dashboard')}' style='color:#00ff88;font-size:22px;'>Back to Dashboard</a>
        </body>
        """

    # GET → show form for entering custom amount
    return render_template("deposit_other.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Simple authentication (you can later replace with real DB check)
        if username == "admin" and password == "1234":
            session["user"] = {"id": 1, "name": username}
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")

    # GET → show login form
    return render_template("login.html")

@app.route("/balance", methods=["GET", "POST"])
def balance():
    if "user" not in session:
        return redirect(url_for("login"))
    uid = session["user"]["id"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM accounts WHERE id = ?", (uid,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return "Account not found", 404

    current_balance = row["balance"] if isinstance(row, dict) else row[0]

    return f"""
    <body style='font-family:Inter,system-ui;background:#0a0f24;color:white;text-align:center;padding-top:20%;'>
      <h2>💰 Current Balance: ₹{current_balance}</h2>
      <a href='{url_for('dashboard')}' style='color:#00aaff;font-size:22px;'>Back to Dashboard</a>
    </body>
    """
@app.route("/logout", methods=["POST"])
def logout():
    # End the session and go back to login
    session.clear()
    play_sound("logout")  # optional if you have that sound
    return redirect(url_for("login"))



if __name__ == "__main__":
    app.run(debug=True)
