#
# THIS IS THE CORRECTED Payment_Service/Payment_Service_App.py
#
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from decimal import Decimal

# Import Prometheus metrics if you use them (from your requirements.txt)
try:
    from prometheus_flask_exporter import PrometheusMetrics
    metrics = PrometheusMetrics(app)
except ImportError:
    print("PrometheusMetrics not found. /metrics endpoint will be basic.")
    # Define a dummy metrics object if not found
    class DummyMetrics:
        def init_app(self, app): pass
    metrics = DummyMetrics()

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)
# Initialize metrics
metrics.init_app(app)

@app.route('/')
def payment_home():
    return "Payment Service is up and ready to process payments!", 200

@app.route('/ping', methods=['GET'])
def ping():
    """ A simple health check endpoint for the ALB. """
    return jsonify({"message": "Payment Service is running!"}), 200

@app.route('/api/payment', methods=['POST'])
def payment():
    """
    Processes a payment.
    This is a MOCK service. It approves cards starting with "4242".
    It receives all data from the frontend and must pass it back.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400

        # --- Get data from frontend (index.html) ---
        card_number = data.get('card_number', '')
        amount = Decimal(str(data.get('amount', 0)))
        
        # --- 
        # --- FIX: Receive the CORRECT variable names from index.html
        # ---
        flight_id = data.get('flight_id')
        flight_details = data.get('flight_details')
        seat_number = data.get('seat_number')
        user_email = data.get('email') # index.html sends 'email'

        # Simple validation
        if not all([flight_id, flight_details, seat_number, user_email, amount > 0, len(card_number) >= 16]):
             return jsonify({"message": "Payment failed: Invalid or missing data from frontend."}), 400

        # Generate a mock transaction ID
        transaction_id = f"TXN-{str(uuid.uuid4())[:8].upper()}"

        # --- Mock Bank Logic ---
        if card_number.startswith("4242"):
            # Approved - Pass all the data back to the frontend
            return jsonify({
                "message": "Payment Successful",
                "transaction_id": transaction_id,
                
                # ---
                # --- FIX: Forward the CORRECT variable names
                # --- These match what index.html and Booking_Service expect
                #
                "flight_id": flight_id,
                "flight_details": flight_details,
                "seat_number": seat_number,
                "user_email": user_email, 
                "amount_paid": amount
                # --- End Fix ---
                
            }), 200
        else:
            # Declined
            return jsonify({
                "message": "Payment Failed. Your bank declined the transaction."
            }), 402 # 402 Payment Required (but failed)

    except Exception as e:
        print(f"Error in /api/payment: {e}")
        return jsonify({"message": "Payment failed due to an internal error.", "error": str(e)}), 500

if __name__ == '__main__':
    # Set a default port 5003, which matches your Dockerfile and ALB
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=True, host='0.0.0.0', port=port)