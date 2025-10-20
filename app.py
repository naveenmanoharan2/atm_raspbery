from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, bcrypt, os, json, time, pygame

# ---------------- Config ----------------
app = Flask(__name__)
app.secret_key = "supersecurekey"
DB = "atm.db"
pygame.mixer.init()
current_lang = "en"

# ------------- Helpers ------------------
def play_sound(name):
    path = os.path.join("static", "sounds", f"{name}.wav")
    if os.path.exists(path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

def get_text(key):
    with open(f"lang/{current_lang}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(key, key)

def get_db():
    return sqlite3.connect(DB)

# ------------- Routes -------------------
@app.route("/lang/<lang>")
def switch_lang(lang):
    global current_lang
    if lang in ["en", "hi", "ta"]:
        current_lang = lang
    return redirect(url_for("login"))

@app.route("/")
def login():
    play_sound("welcome")
    texts = {k: get_text(k) for k in ["login_title","card","pin","login_btn"]}
    return render_template("login.html", **texts)

@app.route("/login", methods=["POST"])
def do_login():
    card_id = request.form["card_id"]
    pin     = request.form["pin"].encode()

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, pin_hash, name, balance FROM accounts WHERE card_id=?", (card_id,))
    row = cur.fetchone()
    conn.close()

    if row and bcrypt.checkpw(pin, row[1]):
        session["user"] = {"id": row[0], "name": row[2], "balance": row[3]}
        play_sound("success")
        return redirect(url_for("dashboard"))
    else:
        play_sound("error")
        return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    texts = {k: get_text(k) for k in ["welcome","withdraw","deposit","balance","exit"]}
    return render_template("dashboard.html", user=user, **texts)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/withdraw", methods=["POST"])
def withdraw():
    if "user" not in session": 
        return redirect(url_for("login"))
    conn = get_db(); cur = conn.cursor()
    uid = session["user"]["id"]
    cur.execute("UPDATE accounts SET balance=balance-1000 WHERE id=?", (uid,))
    conn.commit(); conn.close()
    play_sound("success")
    return redirect(url_for("dashboard"))

@app.route("/deposit", methods=["POST"])
def deposit():
    if "user" not in session": 
        return redirect(url_for("login"))
    conn = get_db(); cur = conn.cursor()
    uid = session["user"]["id"]
    cur.execute("UPDATE accounts SET balance=balance+1000 WHERE id=?", (uid,))
    conn.commit(); conn.close()
    play_sound("success")
    return redirect(url_for("dashboard"))

@app.route("/balance", methods=["POST"])
def balance():
    if "user" not in session": 
        return redirect(url_for("login"))
    play_sound("pin")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
