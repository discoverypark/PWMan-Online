from flask import Flask, render_template, request, session, redirect, url_for, abort
import sqlite3, hashlib

app = Flask(__name__)

app.secret_key = 'iNfvK773__jyBgho1vOH7jVV-__gTO4rZgLJFetDSkdGpTrVILjNZ0orR_h61ZY0YaI1NeZ7wGGIzBw03PMIjxb-AdhtSlfUl9WhewZQSjQbhVfr3ElRZceXZni5B5nbpgB3_glcJiZW5jLNyJqzEU9a1sk6SbpKdsV1zf86Xz6tMUKscWxmQU_CHXjAQC6ks2h-yKuoX_oJfu1i2N8cFQmNU-mpvKVro4By94R1bsaRzoCvFCMq-zmSGYrG8HNNxaRm35eztatSJ0WlBz1Eupmtku4APjnsbd9qjcIwbtOfdo51v0bw18VZECTXGVBqVGhsvSIhlcOxSEzgaZV9yZ55EO__yjrbC3QGCeH-42FRuPi3RqLXxSCbMmGwO5Mz457AvrYK9ojvD6COvURfHLyZBHU8kK1ev1220WkcxvX1fVLB1KwG8Bb5aOZdYTN1Rj1AWBtiZQ-vOceUleOLOHtFeC20ObBaIhkJo-YPS7bUiRMJtjwLEX7EOOxAfXF_QBaS29eDxany5cfgWJFZJc9zyM2JYf5vJuY1bQ6rJmGgUQtx64JijERNELLGzT4V8Ie3OKXUc81NB0MzkLM4znBP66Ft97X5IWz7hyqgUxD872UYC6lbE5zM1E95Lp0HyXedaOw_k-RNZ4kZjeJXB6NQ9pvscJjkePrTm-6FihaQN8lhXBMMnYVJvmPgyo9wjTByn0BmwH5D_4rlfk2Al1z2tIVum8zpbHFByNXFKsg-O622u8ZTSmUh38vi-pfLPI-Np5B2sHUms2YwhT_LT-SATT5p7q6bPPUh0IaEgrUjaUWTu8crGe_ZaiuycXfKFmDwvv0WhMIpCH1lvveOzvJWezVrJoKjuVKI9rt-_7b2QMvR9fIebll6lZjt3CQG5xWsP_rGQEDN857TjLFrtW6ZOEwqdkJ9Vuz5UQ_an_9K4LHHX44qLA0CznB_0BVHcfTWEGS3AY_utLJbfUV-4PMDI_pzo7bl0ZCdJgsowiQ15MugBTBElXE-PC2iuiakSVn9l6hEHi8odzvbENpywoZ7y4m598E43ZLelbyzT0hrtSJb__wnNoqlXYwofd6EtefS33vzLOBIrMZmjP6ejPp_CqGCDWn-zfjl96dzvizjZHOb3NsdX2jfMt2sLH7CkOCkbeTwkIjZI9xWbXe5DQsf-k8bB5JG6nNZ4LImAFc8N3z_nQ-VhPAzthPr-DstAZsG-TdkonzuAmVK951TjzVwhdpFkdw6Ki4Y__99Mq4fb0Qm2r-eJLgMRaPua76NuLmHknDcD4YgrFji2wM-auaPSfzeevCiTwDeBktBv9CsOsqd2Dm6eg9K8QYo-NPrj0odB0o9cY8lDZerNAE-Kg'

def sql_query(sql, parameters, save=False):
    conn = sqlite3.connect('PWMan.db')
    conn.row_factory = sqlite3.Row
    query = conn.cursor().execute(sql, parameters).fetchall()
    if save:
        conn.commit()
    conn.close()
    return query

def create_user(uname, pwd):
    sql_query('INSERT INTO users (uname, pwd) VALUES (?, ?)', (uname, pwd), save=True)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        udata = sql_query('SELECT * FROM users WHERE uname=?', (username,))
        if udata:
            udata = udata[0]
            hash = hashlib.sha3_512(
                (udata['salt'] + password).encode()).hexdigest()
            print(hash)
            if udata['hash'] == hash:
                session['uid'] = udata['uid']
                session.permanent = True
                return redirect(url_for('manager'))
        return render_template('login.html', login_fail=True)
    return render_template('login.html', login_fail=False)

@app.route('/logout')
def logout():
    session['uid'] = None
    return redirect(url_for('index'))

def loggedIn():
    return session and session['uid']

@app.route('/manager')
def manager():
    if loggedIn():
        pwdata = sql_query('SELECT * FROM passwords WHERE uid=?',
                           (session['uid'], ))
        return render_template('passwords.html', pwdata=pwdata)

    abort(403)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if loggedIn():
        if request.method == 'POST':
            conn = sqlite3.connect('PWMan.db')
            cur = conn.cursor()
            cur.execute(
                '''INSERT INTO passwords (uid, name, uname, pwd, url)
                VALUES (?,?,?,?,?);''',
                (session['uid'], request.form['name'], request.form['uname'],
                 request.form['pwd'], request.form['url']))
            conn.commit()
            return redirect(url_for('manager'))
        elif request.method == 'GET':
            return render_template('add.html')

    else:
        abort(403)

@app.route('/dev')
def dev():
    if loggedIn() and session['uid'] == 1:
        return render_template('dev/dev.html')
    else:
        abort(403)

@app.route('/dev/user')
def user():
    pass

@app.route('/dev/user/add', methods=['GET', 'POST'])
def user_add():
    pass

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

app.run(host='0.0.0.0', port=8080)