# app.py (simplified)
from flask import Flask, render_template, request, jsonify
import sqlite3, bcrypt, time

app = Flask(__name__)
DB='atm.db'

def get_db():
    return sqlite3.connect(DB)

@app.route('/')
def index():
    return render_template('index.html')  # Simple UI page served locally

# Endpoint called when card read
@app.route('/card', methods=['POST'])
def card():
    card_id = request.json.get('card_id')
    # lookup account
    conn = get_db(); cur = conn.cursor()
    cur.execute('SELECT id,name FROM accounts WHERE card_id=?', (card_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({'status':'unknown_card'}), 404
    account_id, name = row
    return jsonify({'status':'ok','account_id':account_id,'name':name})

# Verify PIN
@app.route('/verify_pin', methods=['POST'])
def verify_pin():
    account_id = request.json['account_id']
    pin = request.json['pin'].encode()
    conn = get_db(); cur = conn.cursor()
    cur.execute('SELECT pin_hash FROM accounts WHERE id=?', (account_id,))
    row = cur.fetchone()
    conn.close()
    if not row: return jsonify({'ok':False})
    pin_hash = row[0]
    ok = bcrypt.checkpw(pin, pin_hash)
    return jsonify({'ok': ok})

# perform transaction
@app.route('/transaction', methods=['POST'])
def transaction():
    account_id = request.json['account_id']
    ttype = request.json['type']
    amount = int(request.json.get('amount_cents',0))
    conn = get_db(); cur = conn.cursor()
    if ttype=='withdraw':
        cur.execute('SELECT balance_cents FROM accounts WHERE id=?', (account_id,))
        bal = cur.fetchone()[0]
        if amount > bal:
            conn.close(); return jsonify({'ok':False,'reason':'insufficient'})
        newbal = bal - amount
    elif ttype=='deposit':
        cur.execute('SELECT balance_cents FROM accounts WHERE id=?', (account_id,))
        newbal = cur.fetchone()[0] + amount
    else:
        cur.close(); conn.close()
        return jsonify({'ok':False})
    cur.execute('UPDATE accounts SET balance_cents=? WHERE id=?', (newbal, account_id))
    cur.execute('INSERT INTO transactions(account_id,type,amount_cents) VALUES (?,?,?)',
                (account_id,ttype,amount))
    conn.commit(); conn.close()
    return jsonify({'ok':True,'balance_cents':newbal})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
