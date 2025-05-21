import os
import time
from flask import Flask, request, redirect, session, url_for
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Sekretna wartość do sesji
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Oczekiwany hasz hasła użytkownika
PASSWORD_HASH = os.getenv("PASSWORD_HASH")

hall_state = "closed"
click = 0
click_time = 0


@app.route('/')
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return open('index.html').read()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if check_password_hash(PASSWORD_HASH, password):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return "Błędne hasło", 401
    return open('login.html').read()


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/set_status')
def set_status():
    global hall_state
    state = request.args.get("state")
    if state in ["open", "closed"]:
        hall_state = state
        return f"Status ustawiony na: {state}"
    return "Błąd", 400


@app.route('/get_status')
def get_status():
    if not session.get("logged_in"):
        return "Nieautoryzowany", 401
    response = f"{hall_state}"
    return response


@app.route('/get')
def get_relay_command():
    global click, click_time

    if click == 1 and time.time() - click_time > 60:
        click = 0

    if click == 1:
        response = f"1,{hall_state}"
        click = 0
    else:
        response = f"0,{hall_state}"
    return response


@app.route('/click')
def register_click():
    if not session.get("logged_in"):
        return "Nieautoryzowany", 401

    global click, click_time
    click = 1
    click_time = time.time()
    return "Kliknięcie zarejestrowane."


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
