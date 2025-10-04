from flask import Flask, request, jsonify 
from flask_cors import CORS

app = Flask(__name__)
# CORS fix for local mode: Allow all origins
CORS(app, resources={r"/*": {"origins": "*"}}) 

# Default route for the browser when you open http://127.0.0.1:5003
@app.route('/')
def payment_home():
    return "Payment Service is up and ready to process payments!", 200

@app.route('/ping')
def ping():
    return "OK", 200

# This is the correct definition of the payment route
@app.route('/payment', methods=['POST']) 
@app.route('/api/payment', methods=['POST'])
def payment():
    # FIX: request.get_json() MUST be called inside the function
    try:
        data = request.get_json() # Frontend payment data is read here
    except Exception:
        data = {} 
        
    # Simulate payment processing logic 
    amount = data.get('amount', 0)

    if amount > 0 and len(data.get('card_number', '')) >= 16:
        # Payment successful
        return jsonify({"message": "Payment successful!", "transaction_id": "TXN" + data['card_number'][-4:]}), 200
    else:
        # Payment failed (e.g., invalid data)
        return jsonify({"message": "Payment failed: Invalid card details or amount."}), 400
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)