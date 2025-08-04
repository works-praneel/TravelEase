from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "flight-service"}), 200

@app.route('/flights', methods=['GET'])
def get_flights():
    # Mock flight data
    mock_flights = [
        {"flightId": "F-001", "from": "JFK", "to": "LAX", "price": 450, "availableSeats": 50},
        {"flightId": "F-002", "from": "LAX", "to": "JFK", "price": 430, "availableSeats": 30},
        {"flightId": "F-003", "from": "DEL", "to": "LHR", "price": 800, "availableSeats": 150}
    ]
    return jsonify({"flights": mock_flights}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)