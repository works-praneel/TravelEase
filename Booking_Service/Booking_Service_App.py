from flask import Flask, request, jsonify 
from flask_cors import CORS

app = Flask(__name__)
# CORS fix for local mode: Allow all origins
CORS(app, resources={r"/*": {"origins": "*"}}) 

# Default route for the browser when you open http://127.0.0.1:5000
@app.route('/')
def booking_home():
    return "Booking Service is up and ready for confirmation!", 200

@app.route('/ping')
def ping():
    return "OK", 200

# FIX: This route now correctly handles the POST request and processes JSON data.
@app.route('/book', methods=['POST']) 
def book():
    try:
        # Frontend se aaya hua JSON data receive karo
        data = request.get_json() 
    except Exception:
        # Agar JSON nahi mila
        data = {} 
        
    transaction_id = data.get('transaction_id', 'N/A')
    flight_name = data.get('flight', 'Unknown Flight')
    price = data.get('price', 0)
    
    # Simple check for successful booking
    if transaction_id != 'N/A' and price > 0:
        return jsonify({
            "message": "Booking successfully finalized!",
            "booking_reference": "BOOK-" + transaction_id.split('-')[-1],
            "flight": flight_name
        }), 200 # <-- Yahi status aapko Network tab mein dikhna chahiye
    else:
        return jsonify({"message": "Booking failed: Invalid transaction ID or price."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)