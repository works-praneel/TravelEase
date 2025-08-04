from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "booking-service"}), 200

@app.route('/bookings/<user_id>', methods=['GET'])
def get_bookings(user_id):
    # This is a mock API. In a real application, this would query a database.
    mock_bookings = [
        {"bookingId": "B-12345", "flightId": "F-001", "userId": user_id, "status": "confirmed"},
        {"bookingId": "B-67890", "flightId": "F-002", "userId": user_id, "status": "pending"}
    ]
    return jsonify({"bookings": mock_bookings}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)