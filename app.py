import os
import time
from flask import Flask, request, redirect, session, url_for
from werkzeug.security import check_password_hash
from datetime import timedelta

app = Flask(__name__)

# v1.0
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=365*10)

PASSWORD_HASH = os.getenv("PASSWORD_HASH")

hall_state = "noconnect"
click = 0
click_time = 0
last_update_time = 0


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
            session.permanent = True
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return open('login.html').read()
    return open('login.html').read()


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/set_status')
def set_status():
    global hall_state, last_update_time
    state = request.args.get("state")
    if state in ["open", "closed"]:
        hall_state = state
        last_update_time = time.time()
        return f"Status ustawiony na: {state}"
    return "Błąd", 400


@app.route('/get_status')
def get_status():
    global hall_state, last_update_time

    if not session.get("logged_in"):
        return "Nieautoryzowany", 401

    if time.time() - last_update_time > 60:
        hall_state = "noconnect"

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

    current_time = time.time()

    if click == 1:
        return "Poczekaj na wykonanie.", 429

    click = 1
    click_time = current_time
    return "Kliknięcie zarejestrowane."


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
