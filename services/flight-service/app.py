from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "flight-service"}), 200

@app.route('/flights', methods=['GET'])
def get_flights():
    mock_flights = [
        {"flightId": "F-001", "from": "JFK", "to": "LAX", "price": 450, "availableSeats": 50},
    ]
    return jsonify({"flights": mock_flights}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8086)