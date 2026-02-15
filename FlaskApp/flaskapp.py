from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create DB
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT, password TEXT,
              firstname TEXT, lastname TEXT,
              email TEXT, address TEXT)''')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    data = (
        request.form['username'],
        request.form['password'],
        request.form['firstname'],
        request.form['lastname'],
        request.form['email'],
        request.form['address']
    )

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

    return redirect(url_for('profile', username=data[0]))

@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template('profile.html', user=user)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/relogin', methods=['POST'])
def relogin():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return redirect(url_for('profile', username=username))
    else:
        return "Invalid login"

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    with open(path, 'r') as f:
        word_count = len(f.read().split())

    return render_template('upload.html', count=word_count, filename=file.filename)

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run()
