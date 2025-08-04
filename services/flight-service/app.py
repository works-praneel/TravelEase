from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/api/search', methods=['GET'])
def search_flights():
    return jsonify({"status": "success", "message": "Flights fetched successfully."}), 200

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "flight-service"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8086)