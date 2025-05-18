import os
from flask import Flask, request

app = Flask(__name__)

hall_state = "closed"
click_count = None  # Flaga jednorazowa


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


@app.route('/get')
def get_relay_command():
    global click_count
    # Pobieramy aktualny stan
    response = f"{click_count if click_count is not None else 0},{hall_state}"
    # Zerujemy po odczycie
    click_count = None
    return response


@app.route('/click')
def register_click():
    global click_count
    click_count = 1
    return "Kliknięcie zarejestrowane."


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
