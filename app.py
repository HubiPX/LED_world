import os
from flask import Flask, request

app = Flask(__name__)

hall_state = "closed"
click_count = 0  # Flaga jednorazowa


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
    return hall_state

@app.route('/get')
def get_relay_command():
    global click_count
    if click_count is 0:
        response = f"0,{hall_state}"
    else:
        response = f"1,{hall_state}"
        click_count = 0  # resetujemy po odczycie tylko jeśli było kliknięcie
    return response


@app.route('/click')
def register_click():
    global click_count
    click_count = 1
    return "Kliknięcie zarejestrowane."


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
