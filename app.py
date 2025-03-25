from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Убедимся, что папка uploads существует
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Подключение к БД
DATABASE = "database.db"

def init_db():
    """Создаем таблицу, если ее нет"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            code TEXT NOT NULL,
            number TEXT NOT NULL,
            status TEXT NOT NULL
        )''')
        conn.commit()

# Инициализируем базу данных
init_db()

STATUSES = ["Новый", "В процессе", "Завершен"]
USER_DATA = {"admin": "1234", "user": "password"}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in USER_DATA and USER_DATA[username] == password:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            error = "Неверное имя пользователя или пароль."
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        date = request.form.get('date') or datetime.today().strftime('%Y-%m-%d')
        code = request.form.get('code')
        number = request.form.get('number')
        status = request.form.get('status')

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO records (date, code, number, status) VALUES (?, ?, ?, ?)",
                           (date, code, number, status))
            conn.commit()

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records")
        records = cursor.fetchall()

    return render_template('index.html', user=session.get('user'), records=records, statuses=STATUSES, datetime=datetime)

@app.route('/edit/<int:record_id>', methods=['GET', 'POST'])
def edit(record_id):
    if 'user' not in session:
        return redirect(url_for('login'))

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
        status = request.form.get('status')

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE records SET date=?, code=?, number=?, status=? WHERE id=?",
                           (date, code, number, status, record_id))
            conn.commit()

        return redirect(url_for('index'))

    return render_template('edit.html', record=record, statuses=STATUSES)

if __name__ == '__main__':
    app.run(debug=True)
