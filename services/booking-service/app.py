from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "booking-service"}), 200

@app.route('/bookings/<user_id>', methods=['GET'])
def get_bookings(user_id):
    mock_bookings = [
        {"bookingId": "B-12345", "flightId": "F-001", "userId": user_id, "status": "confirmed"},
    ]
    return jsonify({"bookings": mock_bookings}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8086)