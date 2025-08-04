from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/api/book', methods=['GET'])
def book_flight():
    return jsonify({"status": "success", "message": "Booking successful."}), 200

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "booking-service"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8086)