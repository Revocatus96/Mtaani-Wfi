from flask import Flask, render_template, request
import os

app = Flask(__name__)
app.secret_key = 'mtaani-2024'

vouchers = {
"MTAANI1": {"time": "1 Hour", "used": False},
"MTAANI24": {"time": "24 Hours", "used": False},
"TEST123": {"time": "30 Days", "used": False}
}

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html', vouchers=vouchers)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        code = request.form.get('voucher','').strip().upper()
        if code in vouchers and not vouchers[code]['used']:
            vouchers[code]['used'] = True
            return "<h1>Karibu! Voucher " + code + " imekubaliwa</h1><a href='/'>Home</a>"
        else:
            return "<h1>Voucher Si Sahihi! Jaribu MTAANI1</h1><a href='/'>Rudi</a>"
    return render_template('landing.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
