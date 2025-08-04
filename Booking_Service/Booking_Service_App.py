from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
CORS(app)
metrics = PrometheusMetrics(app)

@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/book')
def book():
    return "Booking Confirmed!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
