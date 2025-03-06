from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Убедитесь, что папка uploads существует
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Простые данные для проверки
USER_DATA = {
    'admin': '1234',
    'user': 'password'
}

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
        else:
            filename = 'Файл не выбран'

        date = request.form.get('date')
        status = request.form.get('status')

        return f"Документ: {filename}, Дата: {date}, Статус: {status}"

    return render_template('index.html', user=session.get('user'))

if __name__ == '__main__':
    app.run(debug=True)
