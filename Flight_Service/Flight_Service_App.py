from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
CORS(app)
metrics = PrometheusMetrics(app)

@app.route('/flight')
def flight_home():
    return "Flight Service is Up!"

@app.route('/search')
@app.route('/api/search')
def search():
    return "Flights Found!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
