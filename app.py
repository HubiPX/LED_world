from flask import Flask, request

app = Flask(__name__)

hall_state = "closed"
click_count = 0


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
    return f"{click_count},{hall_state}"

@app.route('/click')
def register_click():
    global click_count
    click_count += 1
    return f"Kliknięcie zarejestrowane. Nowa wartość: {click_count}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
