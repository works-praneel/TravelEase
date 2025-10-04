from flask import Flask, request, jsonify # <<< Zaroori imports: request aur jsonify
from flask_cors import CORS
# PrometheusMetrics lines removed for cleanliness

app = Flask(__name__)
# CORS fix for local mode: Allow all origins
CORS(app, resources={r"/*": {"origins": "*"}}) 

# FIX 1: Default route for the browser when you open http://127.0.0.1:5002
@app.route('/')
@app.route('/flight')
def flight_home():
    return "Flight Service is up and running!", 200

@app.route('/ping')
def ping():
    return "OK", 200

# FIX: Yahan 'methods=['GET']' hona chahiye, taaki URL se search query read ho
@app.route('/search', methods=['GET']) 
@app.route('/api/search', methods=['GET'])
def search():
    
    # Parameters from the URL Query String ko read karo (e.g., ?departure=DEL&date=2025-10-23)
    departure = request.args.get('departure', 'Unknown')
    date = request.args.get('date', 'Unknown')
    
    # FIX 2: Dummy data return karo jo frontend ke renderFlights() function ko chahiye.
    # Ismein 'name' aur 'price' keys zaroori hain.
    flights = [
        {"name": "Air India AI-345", "price": 12500, "departure": "09:00", "arrival": "11:00", "duration": "2h 0m"},
        {"name": "IndiGo 6E-789", "price": 10800, "departure": "14:30", "arrival": "16:45", "duration": "2h 15m"},
        {"name": "Vistara UK-901", "price": 14200, "departure": "20:00", "arrival": "22:10", "duration": "2h 10m"},
        {"name": "SpiceJet SG-123", "price": 9500, "departure": "06:00", "arrival": "08:00", "duration": "2h 0m"}
    ]
    
    # Yahan pe aap actual database filter logic laga sakte hain, abhi sirf dummy list return kar rahe hain.
    
    return jsonify(flights), 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)