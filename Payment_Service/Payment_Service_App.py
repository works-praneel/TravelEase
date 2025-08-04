from flask import Flask, request
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
CORS(app)
metrics = PrometheusMetrics(app)

@app.route('/pay', methods=['GET'])
def healthcheck():
    return "Payment Service is Running!"

@app.route('/payment', methods=['POST'])
@app.route('/api/payment', methods=['POST'])
def payment():
    data = request.get_json()
    amount = data.get("amount", 0)
    return f"Please Proceed With The Payment!!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
