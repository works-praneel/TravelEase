from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "payment-service"}), 200

@app.route('/pay', methods=['POST'])
def process_payment():
    # Mock payment processing
    # In a real app, this would handle a request body with payment details
    # and interact with a payment gateway.
    return jsonify({"status": "success", "transactionId": "T-987654321", "message": "Payment processed successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)