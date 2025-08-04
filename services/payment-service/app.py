from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/api/payment', methods=['POST'])
def process_payment():
    data = request.json
    return jsonify({"status": "success", "transactionId": "T-987654321", "message": "Payment processed successfully."}), 200

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "payment-service"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8086)