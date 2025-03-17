from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Убедимся, что папка uploads существует
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Простые данные для проверки
USER_DATA = {
    'admin': '1234',
    'user': 'password'
}

# Пример данных для тестовых записей
DATA = [
    {"id": 1, "date": "2025-03-14", "code": "A123", "number": "001", "status": "Новый"},
    {"id": 2, "date": "2025-03-15", "code": "B456", "number": "002", "status": "В процессе"},
    {"id": 3, "date": "2025-03-16", "code": "C789", "number": "003", "status": "Завершен"}
]

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
        file = request.files.get('document')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        date = request.form.get('date')
        code = request.form.get('code')
        number = request.form.get('number')
        status = request.form.get('status')

        new_id = len(DATA) + 1
        DATA.append({"id": new_id, "date": date, "code": code, "number": number, "status": status})

    return render_template('index.html', user=session.get('user'), records=DATA)

# Обновляем статус записи через AJAX
@app.route('/update_status/<int:record_id>', methods=['POST'])
def update_status(record_id):
    new_status = request.form.get('status')
    for record in DATA:
        if record['id'] == record_id:
            record['status'] = new_status
            break
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
