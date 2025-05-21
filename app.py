import os
import time
from flask import Flask, request

app = Flask(__name__)

hall_state = "closed"
click = 0
click_time = 0


@app.route('/')
def index():
    return open('index.html').read()


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
    response = f"{hall_state}"
    return response

@app.route('/get')
def get_relay_command():
    global click, click_time

    # Sprawdzenie, czy minęło 60 sekund od kliknięcia
    if click == 1 and time.time() - click_time > 60:
        click = 0

    if click == 0:
        response = f"0,{hall_state}"
    else:
        response = f"1,{hall_state}"
        click = 0  # resetujemy po odczycie tylko jeśli było kliknięcie
    return response


@app.route('/click')
def register_click():
    global click, click_time
    click = 1
    click_time = time.time()
    return "Kliknięcie zarejestrowane."


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
