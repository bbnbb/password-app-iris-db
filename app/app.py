from functools import wraps
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import irisnative
from cryptography.fernet import Fernet

app = Flask(__name__)
app.config.update(
    SECRET_KEY='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'.encode('utf-8')
)

ip = "iris"
port = 1972
namespace = "USER"
username = "_SYSTEM"
password = "demopass"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def init():
    connection = irisnative.createConnection(ip, port, namespace, username, password)
    cur = connection.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR(50), crypto_key VARCHAR(256), email VARCHAR(50), password VARCHAR(256))')
    cur.execute(
        'CREATE TABLE IF NOT EXISTS passwords (id SERIAL PRIMARY KEY, user_id INTEGER, title VARCHAR(50), password VARCHAR(256), FOREIGN KEY (user_id) REFERENCES users(id))')
    # when finished, use the line below to close the connection
    connection.close()

    return "<p>init</p>"


@app.route("/")
def hello_world():
    init()
    return redirect(url_for('dashboard'))


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session.get('user_id')
    if user_id:
        connection = irisnative.createConnection(ip, port, namespace, username, password)
        cur = connection.cursor()
        query = f"SELECT * FROM users WHERE id = {user_id}"
        cur.execute(query)
        # Получение результатов запроса
        result = cur.fetchall()
        check_user = result[0]
        # Если пользователь найден, получаем его данные
        if result:
            user = {
                'id': check_user[0],
                'crypto_key': check_user[2],
            }
        else:
            return jsonify({'message': 'User not found'}), 400

        crypto_key = check_user[2]
        cipher_suite = Fernet(crypto_key)
        query = f"SELECT id, title, password FROM passwords WHERE user_id = {user_id}"
        cur.execute(query)
        passwords = []
        for row in cur.fetchall():
            decrypted_password = cipher_suite.decrypt(row[2]).decode('utf-8')
            passwords.append({
                'id': row[0],
                'title': row[1],
                'password': decrypted_password
            })

        connection.close()
        return render_template('dashboard.html', passwords=passwords)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('username')
        user_password = request.form.get('password')

        if not user_name or not user_password:
            return render_template('login.html', error='Invalid credentials'), 401

        connection = irisnative.createConnection(ip, port, namespace, username, password)
        cur = connection.cursor()

        # Получение пользователя по имени пользователя
        query = f"SELECT id,password FROM users WHERE username = '{user_name}'"
        cur.execute(query)
        result = cur.fetchall()
        check_user = result[0]

        if result:
            # Извлечение хэша пароля из базы данных
            stored_password_hash = check_user[1]

            # Хеширование введенного пароля
            password_hash = hashlib.sha256(user_password.encode()).hexdigest()

            if password_hash == stored_password_hash:
                # После успешной аутентификации
                session['logged_in'] = True
                session['user_id'] = check_user[0]
                session['user_name'] = user_name
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid password'), 401
        else:
            return render_template('login.html', error='Invalid credentials'), 401

    # Отображение страницы авторизации
    return render_template('login.html')


# Выход из системы
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_name = request.form.get('username')
        user_password = request.form.get('password')

        if not user_name or not user_password:
            return render_template('register.html', error='not username or password'), 400

        # Проверка, что пользователь с таким именем не существует
        connection = irisnative.createConnection(ip, port, namespace, username, password)
        cur = connection.cursor()
        query = f"SELECT * FROM users WHERE username = '{user_name}'"
        cur.execute(query)
        result = cur.fetchall()
        if result:
            return render_template('register.html', error='Username already exists'), 409

        # Хеширование пароля
        password_hash = hashlib.sha256(user_password.encode()).hexdigest()

        key = Fernet.generate_key()

        # Добавление пользователя в базу данных
        query = "INSERT INTO users (username, crypto_key, password) VALUES (?, ?, ?)"
        values = [user_name, key, password_hash]
        cur.execute(query, values)
        connection.commit()
        connection.close()

        # Перенаправление на страницу успешной регистрации
        return redirect(url_for('login'))

    # Отображение страницы регистрации
    return render_template('register.html')


# Обработчик для удаления пароля по его ID
@app.route('/passwords/<int:password_id>', methods=['DELETE'])
def delete_password(password_id):
    # Проверка, что password_id передан
    if not password_id:
        return "Invalid password ID"

    # Установка соединения с базой данных InterSystems IRIS
    connection = irisnative.createConnection(ip, port, namespace, username, password)
    cur = connection.cursor()

    # Проверка существования пароля по его ID
    sql_select = "SELECT COUNT(*) FROM passwords WHERE id = ?"
    cur.execute(sql_select, (password_id,))
    result = cur.fetchall()
    check_pass_id = result[0]
    if check_pass_id[0] == 0:
        return jsonify({'message': 'Password not found'}), 404

    # Определение SQL-запроса для удаления пароля
    sql_delete = "DELETE FROM passwords WHERE id = ?"

    # Выполнение SQL-запроса с передачей параметров
    cur.execute(sql_delete, (password_id,))

    # Фиксация изменений и закрытие соединения
    connection.commit()
    connection.close()

    return "Password deleted successfully"


@app.route('/add_password', methods=['POST'])
def add_password():
    user_id = session.get('user_id')
    if user_id:
        password_name = request.json.get('passwordName')
        password_value = request.json.get('passwordValue')

        if not password_name or not password_value:
            return jsonify({'message': 'Invalid data provided'}), 400

        connection = irisnative.createConnection(ip, port, namespace, username, password)
        cur = connection.cursor()
        query = f"SELECT id, crypto_key FROM users WHERE id = {user_id}"
        cur.execute(query)
        # Получение результатов запроса
        result = cur.fetchall()
        check_user = result[0]
        # Если пользователь найден, получаем его данные
        if result:
            user = {
                'id': check_user[0],
                'crypto_key': check_user[1],
            }
        else:
            return jsonify({'message': 'User not found'}), 400

        # Получение ключа шифрования из поля crypto_key пользователя
        crypto_key = check_user[1]

        if not crypto_key:
            return jsonify({'message': 'Encryption key not found for user'}), 400

        # Шифрование пароля
        cipher_suite = Fernet(crypto_key)
        encrypted_password = cipher_suite.encrypt(password_value.encode('utf-8'))

        sql = "INSERT INTO passwords (user_id, title, password) VALUES (?, ?, ?)"
        values = [user_id, password_name, encrypted_password]
        # Выполнение SQL-запроса с передачей параметров
        cur.execute(sql, values)
        # Фиксация изменений в базе данных
        connection.commit()
        connection.close()

        # Возвращение успешного ответа
        return jsonify({'message': 'Password added successfully'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8011, debug=True)
