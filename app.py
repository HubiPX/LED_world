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

ESP_API_KEY = os.getenv("ESP_API_KEY")

# gate 1
hall_state = "noconnect"
click = 0
click_time = 0
last_update_time = 0

# gate 2
hall_state_2 = "noconnect"
click_2 = 0
click_time_2 = 0
last_update_time_2 = 0

last_all_action_time = 0
ALL_ACTION_COOLDOWN = 30  # sekundy


def require_esp_key():
    key = request.headers.get("X-ESP-KEY")
    return key == ESP_API_KEY


# gate 1
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
    global hall_state

    if not require_esp_key():
        return "Nieautoryzowany", 401

    state = request.args.get("state")
    if state in ["open", "closed"]:
        hall_state = state
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
    global click, click_time, last_update_time

    if not require_esp_key():
        return "Nieautoryzowany", 401

    last_update_time = time.time()

    if click == 1 and time.time() - click_time > 60:
        click = 0

    if click == 1:
        response = "1"
        click = 0
    else:
        response = "0"

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


# gate 2
@app.route('/set_status_2')
def set_status_2():
    global hall_state_2

    if not require_esp_key():
        return "Nieautoryzowany", 401

    state = request.args.get("state")
    if state in ["open", "closed"]:
        hall_state_2 = state
        return f"Status 2 ustawiony na: {state}"
    return "Błąd", 400


@app.route('/get_status_2')
def get_status_2():
    global hall_state_2, last_update_time_2

    if not session.get("logged_in"):
        return "Nieautoryzowany", 401

    if time.time() - last_update_time_2 > 60:
        hall_state_2 = "noconnect"

    return hall_state_2


@app.route('/get_2')
def get_relay_command_2():
    global click_2, click_time_2, last_update_time_2

    if not require_esp_key():
        return "Nieautoryzowany", 401

    last_update_time_2 = time.time()

    if click_2 == 1 and time.time() - click_time_2 > 60:
        click_2 = 0

    if click_2 == 1:
        response = "1"
        click_2 = 0
    else:
        response = "0"

    return response


@app.route('/click_2')
def register_click_2():
    if not session.get("logged_in"):
        return "Nieautoryzowany", 401

    global click_2, click_time_2
    current_time = time.time()

    if click_2 == 1:
        return "Poczekaj na wykonanie.", 429

    click_2 = 1
    click_time_2 = current_time
    return "Kliknięcie bramy 2 zarejestrowane."


# all gates
@app.route('/all_open')
def all_open():
    if not session.get("logged_in"):
        return "Nieautoryzowany", 401

    global click, click_time, click_2, click_time_2
    global last_all_action_time

    now = time.time()
    if now - last_all_action_time < ALL_ACTION_COOLDOWN:
        remaining = int(ALL_ACTION_COOLDOWN - (now - last_all_action_time))
        return f"Poczekaj {remaining}s przed kolejną akcją", 429

    actions = []

    if hall_state == "closed":
        click = 1
        click_time = now
        actions.append("brama1")

    if hall_state_2 == "closed":
        click_2 = 1
        click_time_2 = now
        actions.append("brama2")

    if not actions:
        return "Wszystkie bramy są już otwarte"

    last_all_action_time = now
    return f"Otwieranie: {', '.join(actions)}"


@app.route('/all_close')
def all_close():
    if not session.get("logged_in"):
        return "Nieautoryzowany", 401

    global click, click_time, click_2, click_time_2
    global last_all_action_time

    now = time.time()
    if now - last_all_action_time < ALL_ACTION_COOLDOWN:
        remaining = int(ALL_ACTION_COOLDOWN - (now - last_all_action_time))
        return f"Poczekaj {remaining}s przed kolejną akcją", 429

    actions = []

    if hall_state == "open":
        click = 1
        click_time = now
        actions.append("brama1")

    if hall_state_2 == "open":
        click_2 = 1
        click_time_2 = now
        actions.append("brama2")

    if not actions:
        return "Wszystkie bramy są już zamknięte"

    last_all_action_time = now
    return f"Zamykanie: {', '.join(actions)}"


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
