from flask import Flask, request, jsonify 
from flask_cors import CORS

app = Flask(__name__)
# CORS fix for local mode: Allow all origins
CORS(app, resources={r"/*": {"origins": "*"}}) 

# Default routes to check if the service is running
@app.route('/')
@app.route('/flight')
def flight_home():
    return "Flight Service is up and running!", 200

@app.route('/ping')
def ping():
    return "OK", 200

# 🛑 FINAL FIX 1: Frontend ka zaroori route /api/flights add kar diya
@app.route('/search', methods=['GET']) 
@app.route('/api/search', methods=['GET'])
@app.route('/api/flights', methods=['GET']) 
def search():
    
    # Parameters from the URL Query String ko read karo (e.g., ?departure=DEL&date=2025-10-23)
    departure = request.args.get('departure', 'Unknown')
    date = request.args.get('date', 'Unknown')
    
    # Frontend ke createFlightCard function se match karne ke liye detail mein data
    flights = [
        {"name": "Air India", "flightNumber": "AI-345", "route": "DEL - BOM", "price": 12500, "departure": "09:00", "arrival": "11:00", "duration": "2h 0m"},
        {"name": "IndiGo", "flightNumber": "6E-789", "route": "DEL - BOM", "price": 10800, "departure": "14:30", "arrival": "16:45", "duration": "2h 15m"},
        {"name": "Vistara", "flightNumber": "UK-901", "route": "DEL - BOM", "price": 14200, "departure": "20:00", "arrival": "22:10", "duration": "2h 10m"},
        {"name": "SpiceJet", "flightNumber": "SG-123", "route": "DEL - BOM", "price": 9500, "departure": "06:00", "arrival": "08:00", "duration": "2h 0m"}
    ]
    
    # 🛑 FINAL FIX 2: JSON return structure ko frontend se match kiya.
    # Frontend ko '{ "flights": [...] }' chahiye.
    return jsonify({"flights": flights}), 200
    
# 🛑 Application ko chalane ke liye yeh block zaroori hai 🛑
if __name__ == '__main__':
    # Yeh app ko 0.0.0.0 IP par default port 5002 par chalayega.
    app.run(host='0.0.0.0', port=5002)