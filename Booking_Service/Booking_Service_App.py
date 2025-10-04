from flask import Flask, request, jsonify 
from flask_cors import CORS
# Nayi email file se function import kiya. Ensure 'email_sender_gmail.py' is in the same folder.
from email_sender_gmail import send_confirmation_email_via_gmail 

app = Flask(__name__)
# CORS fix for local mode: Allow all origins
CORS(app, resources={r"/*": {"origins": "*"}}) 

# Default routes to check if the service is running
@app.route('/')
def booking_home():
    return "Booking Service is up and running!", 200

@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/book', methods=['POST']) 
def book():
    try:
        # Frontend/Payment service se aaya hua JSON data receive karo
        data = request.get_json() 
    except Exception:
        # Agar JSON nahi mila
        data = {} 
        
    transaction_id = data.get('transaction_id', 'N/A')
    flight_name = data.get('flight', 'Unknown Flight')
    price = data.get('price', 0)
    
    # Email ID ko Payment Service se 'user_email' key ke through receive karo
    recipient_email = data.get('user_email', 'default@example.com') 

    # Simple check for successful booking
    if transaction_id != 'N/A' and price > 0 and recipient_email != 'default@example.com':
        booking_reference = "BOOK-" + transaction_id.split('-')[-1]

        # EMAIL SENDING LOGIC
        email_success = send_confirmation_email_via_gmail(recipient_email, {
            "booking_reference": booking_reference,
            "flight": flight_name,
            "price": price,
            "transaction_id": transaction_id
        })
        
        return jsonify({
            "message": "Booking successfully finalized!",
            "booking_reference": booking_reference,
            "flight": flight_name,
            "email_status": "Real Email Sent" if email_success else "Email Failed (Check terminal for errors)" 
        }), 200
    else:
        return jsonify({"message": "Booking failed: Invalid data or missing email."}), 400

# 🛑 Application ko chalane ke liye yeh block zaroori hai 🛑
if __name__ == '__main__':
    # Yeh app ko 0.0.0.0 IP par default port 5000 par chalayega.
    app.run(host='0.0.0.0', port=5000)