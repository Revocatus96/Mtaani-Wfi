 from flask import Flask, render_template, request, redirect, session, flash
import sqlite3, os, random, string
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mtaani_wifi_super_secret_2026'

def init_db():
    conn = sqlite3.connect('mtaani.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, jina TEXT, phone TEXT UNIQUE, password TEXT, is_active INTEGER DEFAULT 1, created TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vouchers
                 (code TEXT PRIMARY KEY, hours INTEGER, used INTEGER DEFAULT 0, created_by TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments
                 (id INTEGER PRIMARY KEY, phone TEXT, amount INTEGER, code TEXT, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- PUBLIC PAGES ---
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        jina = request.form['jina']
        phone = request.form['phone']
        password = generate_password_hash(request.form['password'])
        try:
            conn = sqlite3.connect('mtaani.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (jina, phone, password, created) VALUES (?,?,?,?)',
                      (jina, phone, password, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            session['user_phone'] = phone
            session['user_jina'] = jina
            return redirect('/dashboard')
        except:
            return "Namba imeshatumika! <a href='/'>Rudi</a>"
    return render_template('landing.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        pwd = request.form['password']
        conn = sqlite3.connect('mtaani.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE phone=?', (phone,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[3], pwd):
            if user[4] == 0:
                return "Account yako imezuiwa na Admin! <a href='/'>Rudi</a>"
            session['user_phone'] = user[2]
            session['user_jina'] = user[1]
            session['user_id'] = user[0]
            return redirect('/dashboard')
        else:
            return "Namba au password sio sahihi! <a href='/'>Rudi</a>"
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('user_phone'):
        return redirect('/')
    return render_template('dashboard.html', jina=session.get('user_jina'), phone=session.get('user_phone'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# --- ADMIN ---
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username']=='admin' and request.form['password']=='mtaani123':
            session['admin']=True
            return redirect('/admin')
        else:
            return "Login ya admin sio sahihi!"
    return render_template('admin_login.html')

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/admin/login')
    conn = sqlite3.connect('mtaani.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users ORDER BY id DESC')
    users = c.fetchall()
    c.execute('SELECT * FROM vouchers ORDER BY code DESC')
    vouchers = c.fetchall()
    c.execute('SELECT * FROM payments ORDER BY id DESC')
    payments = c.fetchall()
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM vouchers')
    total_vouchers = c.fetchone()[0]
    conn.close()
    return render_template('admin.html', users=users, vouchers=vouchers, payments=payments, total_users=total_users, total_vouchers=total_vouchers)

@app.route('/admin/user/toggle/<int:user_id>')
def toggle_user(user_id):
    if not session.get('admin'): return redirect('/admin/login')
    conn = sqlite3.connect('mtaani.db')
    c = conn.cursor()
    c.execute('UPDATE users SET is_active = CASE WHEN is_active=1 THEN 0 ELSE 1 END WHERE id=?', (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/user/delete/<int:user_id>')
def delete_user(user_id):
    if not session.get('admin'): return redirect('/admin/login')
    conn = sqlite3.connect('mtaani.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/voucher/create', methods=['POST'])
def create_voucher():
    if not session.get('admin'): return redirect('/admin/login')
    hours = request.form['hours']
    code = 'MTAA-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    conn = sqlite3.connect('mtaani.db')
    c = conn.cursor()
    c.execute('INSERT INTO vouchers (code, hours, created_by) VALUES (?,?,?)', (code, hours, 'admin'))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin/login')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)