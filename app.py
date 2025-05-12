from flask import Flask, request

app = Flask(__name__)

led_state = "OFF"  # Stan diody
short_count = 0  # Licznik zwarć


@app.route('/set')
def set_led():
    global led_state
    state = request.args.get('led')
    if state in ["ON", "OFF"]:
        led_state = state
        return f"LED ustawiono na: {led_state}"
    return "Nieprawidłowa wartość"


@app.route('/get')
def get_led():
    return led_state


@app.route('/set_count')
def set_count():
    global short_count
    count = request.args.get('count')

    if count is not None and count.isdigit():
        short_count = int(count)  # Zapisz liczbę zwarć
        return f"Zliczono {short_count} zwarć."
    return "Nieprawidłowa wartość"


@app.route('/get_count')
def get_count():
    return str(short_count)


@app.route('/')
def index():
    return open('index.html').read()  # Ładuje stronę HTML


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # Gunicorn uruchomi aplikację, więc ta linia jest niekonieczna
