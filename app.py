from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'

DATABASE = "database.db"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

STATUSES = ["Новый", "В процессе", "Завершен"]

# Инициализация базы данных
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Таблица записей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                code TEXT NOT NULL,
                number TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        # Добавление пользователей, если они еще не добавлены
        existing_users = cursor.execute("SELECT username FROM users").fetchall()
        if not existing_users:
            users = [
                ("admin", "1234", "admin"),
                ("user1", "1111", "reader"),
                ("user2", "2222", "writer")
            ]
            cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", users)
        conn.commit()

init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password, role FROM users WHERE username=?", (username,))
            result = cursor.fetchone()

            if not result:
                error = "Пользователь не найден."
                return render_template('login.html', error=error)

            db_password, role = result
            if password == db_password:
                session['user'] = username
                session['role'] = role
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="Неверный пароль.")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST' and session['role'] != 'reader':
        date = request.form.get('date') or datetime.today().strftime('%Y-%m-%d')
        code = request.form.get('code')
        number = request.form.get('number')
        # Только админ может выбирать статус, остальным ставим "Новый"
        status = request.form.get('status') if session['role'] == 'admin' else "Новый"

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO records (date, code, number, status) VALUES (?, ?, ?, ?)",
                           (date, code, number, status))
            conn.commit()

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records")
        records = cursor.fetchall()

    return render_template('index.html',
                           user=session.get('user'),
                           role=session.get('role'),
                           records=records,
                           statuses=STATUSES,
                           datetime=datetime)

@app.route('/edit/<int:record_id>', methods=['GET', 'POST'])
def edit(record_id):
    if 'user' not in session or session['role'] == 'reader':
        return redirect(url_for('index'))

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records WHERE id=?", (record_id,))
        record = cursor.fetchone()

    if not record:
        return "Запись не найдена", 404

    if request.method == 'POST':
        date = request.form.get('date')
        code = request.form.get('code')
        number = request.form.get('number')
        # Только админ может менять статус
        status = request.form.get('status') if session['role'] == 'admin' else record[4]

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE records SET date=?, code=?, number=?, status=? WHERE id=?",
                           (date, code, number, status, record_id))
            conn.commit()

        return redirect(url_for('index'))

    return render_template('edit.html', record=record, statuses=STATUSES)
if __name__ == '__main__':
    app.run(debug=True)
