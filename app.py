 from flask import Flask, render_template, request, redirect, session, flash
import os

app = Flask(__name__)
app.secret_key = 'mtaani-wifi-secret-2024'

# Vouchers za mfano
vouchers = {
    "MTAANI1": {"time": "1 Hour", "used": False},
    "MTAANI24": {"time": "24 Hours", "used": False},
    "TEST123": {"time": "30 Days", "used": False}
}

users = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code = request.form.get('voucher', '').strip().upper()
        if code in vouchers and not vouchers[code]['used']:
            vouchers[code]['used'] = True
            session['user'] = code
            flash(f"Umeunganishwa! {vouchers[code]['time']} imeanza!", "success")
            return redirect('/success')
        else:
            flash("Voucher si sahihi au imeshatumika!", "error")
    return render_template('login.html')

@app.route('/success')
def success():
    if 'user' not in session:
        return redirect('/login')
    return f"<h1>Karibu Mtaani WiFi!</h1><p>Voucher: {session['user']}</p><p>Umeunganishwa!</p><a href='/'>Rudi Nyumbani</a>"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user == 'admin' and pwd == 'mtaani123':
            session['admin'] = True
            return redirect('/dashboard')
        else:
            flash("Login failed!", "error")
    return render_template('admin.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/admin')
    return render_template('dashboard.html', vouchers=vouchers, users=users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
