from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.route('/pay')
def home():
    return "Payment Service Active"

@app.route('/payment')
@app.route('/api/payment')
def pay():
    return "Payment Processed!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
