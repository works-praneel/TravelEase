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
    try:
        data = request.get_json() 
    except Exception:
        data = {} 
        
    # Simulate payment processing logic 
    amount = data.get('amount', 0)
    card_number = data.get('card_number', '')
    
    # Email ID ko frontend se receive karo
    user_email = data.get('email', 'email_missing@example.com') 

    if amount > 0 and len(card_number) >= 16:
        # Payment successful
        return jsonify({
            "message": "Payment successful!", 
            "transaction_id": "TXN" + card_number[-4:],
            "user_email": user_email # Email ID ko Booking Service ke liye forward karo
        }), 200
    else:
        # Payment failed (e.g., invalid data)
        return jsonify({"message": "Payment failed: Invalid card details or amount."}), 400
    
# 🛑🛑🛑 YAHI PART MISSING THA! 🛑🛑🛑
if __name__ == '__main__':
    # Yeh app ko 0.0.0.0 IP par port 5003 par chalayega.
    app.run(host='0.0.0.0', port=5003)