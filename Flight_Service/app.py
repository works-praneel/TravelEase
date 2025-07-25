from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.route('/flight')
def home():
    return "Flight Service Root Path Active!"

@app.route('/search')
@app.route('/api/search')
def search():
    return "Flights Found!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
