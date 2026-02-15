from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = '/var/www/flaskapp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_PATH = '/var/www/flaskapp/users.db'


# ---------- DATABASE INIT ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            firstname TEXT,
            lastname TEXT,
            email TEXT,
            address TEXT,
            filename TEXT,
            wordcount INTEGER
        )
    ''')

    conn.commit()
    conn.close()


init_db()


# ---------- HOME ----------
@app.route('/')
def index():
    return render_template('register.html')


# ---------- REGISTER ----------
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    address = request.form['address']

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        INSERT OR REPLACE INTO users 
        (username, password, firstname, lastname, email, address)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, password, firstname, lastname, email, address))

    conn.commit()
    conn.close()

    return redirect(url_for('profile', username=username))


# ---------- LOGIN / RELOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
@app.route('/relogin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            return redirect(url_for('profile', username=username))
        else:
            return "Invalid credentials"

    return render_template('login.html')


# ---------- PROFILE ----------
@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template('profile.html', user=user)


# ---------- FILE UPLOAD ----------
@app.route('/upload/<username>', methods=['POST'])
def upload(username):
    file = request.files['file']

    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # count words
        with open(filepath, 'r') as f:
            wordcount = len(f.read().split())

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute('''
            UPDATE users
            SET filename=?, wordcount=?
            WHERE username=?
        ''', (file.filename, wordcount, username))

        conn.commit()
        conn.close()

    return redirect(url_for('profile', username=username))


# ---------- DOWNLOAD ----------
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
