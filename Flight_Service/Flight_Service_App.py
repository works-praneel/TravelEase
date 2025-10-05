from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# CORS fix for local mode: Allow all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Comprehensive Database of All Flights ---
ALL_FLIGHTS = [
    # --- Domestic Flights (India) ---
    # Delhi <=> Mumbai
    {"type": "domestic", "name": "IndiGo", "flightNumber": "6E-2021", "route": "DEL - BOM", "price": 4800, "duration": "2h 5m"},
    {"type": "domestic", "name": "Vistara", "flightNumber": "UK-990", "route": "DEL - BOM", "price": 5200, "duration": "2h 10m"},
    {"type": "domestic", "name": "Air India", "flightNumber": "AI-805", "route": "DEL - BOM", "price": 5000, "duration": "2h 15m"},
    {"type": "domestic", "name": "SpiceJet", "flightNumber": "SG-871", "route": "DEL - BOM", "price": 4600, "duration": "2h 20m"},
    {"type": "domestic", "name": "Akasa Air", "flightNumber": "QP-1101", "route": "DEL - BOM", "price": 4750, "duration": "2h 5m"},
    {"type": "domestic", "name": "Air India", "flightNumber": "AI-809", "route": "BOM - DEL", "price": 4950, "duration": "2h 5m"},
    {"type": "domestic", "name": "SpiceJet", "flightNumber": "SG-817", "route": "BOM - DEL", "price": 4700, "duration": "2h 15m"},
    {"type": "domestic", "name": "IndiGo", "flightNumber": "6E-2022", "route": "BOM - DEL", "price": 4850, "duration": "2h 10m"},
    {"type": "domestic", "name": "Vistara", "flightNumber": "UK-991", "route": "BOM - DEL", "price": 5300, "duration": "2h 5m"},
    {"type": "domestic", "name": "Akasa Air", "flightNumber": "QP-1102", "route": "BOM - DEL", "price": 4800, "duration": "2h 10m"},

    # Delhi <=> Kolkata
    {"type": "domestic", "name": "IndiGo", "flightNumber": "6E-632", "route": "DEL - CCU", "price": 5500, "duration": "2h 20m"},
    {"type": "domestic", "name": "Vistara", "flightNumber": "UK-774", "route": "DEL - CCU", "price": 5600, "duration": "2h 15m"},
    {"type": "domestic", "name": "Air India", "flightNumber": "AI-763", "route": "DEL - CCU", "price": 5400, "duration": "2h 25m"},
    {"type": "domestic", "name": "SpiceJet", "flightNumber": "SG-451", "route": "DEL - CCU", "price": 5300, "duration": "2h 30m"},
    {"type": "domestic", "name": "IndiGo", "flightNumber": "6E-633", "route": "CCU - DEL", "price": 5550, "duration": "2h 20m"},
    {"type": "domestic", "name": "Vistara", "flightNumber": "UK-775", "route": "CCU - DEL", "price": 5650, "duration": "2h 15m"},

    # Mumbai <=> Chennai
    {"type": "domestic", "name": "Air India", "flightNumber": "AI-765", "route": "BOM - MAA", "price": 3800, "duration": "1h 50m"},
    {"type": "domestic", "name": "IndiGo", "flightNumber": "6E-555", "route": "BOM - MAA", "price": 3900, "duration": "1h 55m"},
    {"type": "domestic", "name": "Vistara", "flightNumber": "UK-821", "route": "BOM - MAA", "price": 4100, "duration": "1h 45m"},
    {"type": "domestic", "name": "SpiceJet", "flightNumber": "SG-331", "route": "BOM - MAA", "price": 3700, "duration": "2h 0m"},
    {"type": "domestic", "name": "IndiGo", "flightNumber": "6E-556", "route": "MAA - BOM", "price": 3950, "duration": "1h 55m"},
    {"type": "domestic", "name": "Air India", "flightNumber": "AI-766", "route": "MAA - BOM", "price": 3850, "duration": "1h 50m"},

    # Delhi <=> Goa
    {"type": "domestic", "name": "SpiceJet", "flightNumber": "SG-301", "route": "DEL - GOI", "price": 6200, "duration": "2h 35m"},
    {"type": "domestic", "name": "IndiGo", "flightNumber": "6E-123", "route": "DEL - GOI", "price": 6300, "duration": "2h 40m"},
    {"type": "domestic", "name": "Vistara", "flightNumber": "UK-847", "route": "DEL - GOI", "price": 6500, "duration": "2h 30m"},
    {"type": "domestic", "name": "Air India", "flightNumber": "AI-887", "route": "DEL - GOI", "price": 6400, "duration": "2h 45m"},
    {"type": "domestic", "name": "IndiGo", "flightNumber": "6E-124", "route": "GOI - DEL", "price": 6350, "duration": "2h 40m"},
    {"type": "domestic", "name": "Vistara", "flightNumber": "UK-848", "route": "GOI - DEL", "price": 6550, "duration": "2h 30m"},
    
    # Hyderabad <=> Mumbai
    {"type": "domestic", "name": "Vistara", "flightNumber": "UK-850", "route": "HYD - BOM", "price": 3100, "duration": "1h 25m"},
    {"type": "domestic", "name": "Air India", "flightNumber": "AI-560", "route": "HYD - BOM", "price": 3200, "duration": "1h 30m"},
    {"type": "domestic", "name": "IndiGo", "flightNumber": "6E-876", "route": "HYD - BOM", "price": 3000, "duration": "1h 20m"},
    {"type": "domestic", "name": "IndiGo", "flightNumber": "6E-877", "route": "BOM - HYD", "price": 3050, "duration": "1h 20m"},
    {"type": "domestic", "name": "Air India", "flightNumber": "AI-561", "route": "BOM - HYD", "price": 3250, "duration": "1h 30m"},

    # --- International Flights ---
    # India <=> Thailand (Phuket - HKT)
    {"type": "international", "name": "Thai Airways", "flightNumber": "TG-316", "route": "DEL - HKT", "price": 22000, "duration": "4h 15m"},
    {"type": "international", "name": "IndiGo", "flightNumber": "6E-1051", "route": "DEL - HKT", "price": 21000, "duration": "4h 25m"},
    {"type": "international", "name": "Vistara", "flightNumber": "UK-121", "route": "BOM - HKT", "price": 23000, "duration": "4h 40m"},
    {"type": "international", "name": "SpiceJet", "flightNumber": "SG-88", "route": "BOM - HKT", "price": 20500, "duration": "4h 45m"},
    {"type": "international", "name": "Go First", "flightNumber": "G8-31", "route": "CCU - HKT", "price": 19800, "duration": "3h 50m"},
    {"type": "international", "name": "Thai Smile", "flightNumber": "WE-334", "route": "CCU - HKT", "price": 21200, "duration": "3h 55m"},

    # India <=> Indonesia (Juanda - SUB)
    {"type": "international", "name": "Garuda Indonesia", "flightNumber": "GA-841", "route": "BOM - SUB", "price": 28000, "duration": "7h 10m"},
    {"type": "international", "name": "Singapore Airlines", "flightNumber": "SQ-529", "route": "MAA - SUB", "price": 27500, "duration": "6h 55m"},
    {"type": "international", "name": "Batik Air", "flightNumber": "ID-6014", "route": "DEL - SUB", "price": 26000, "duration": "8h 20m"},
    {"type": "international", "name": "Malaysia Airlines", "flightNumber": "MH-191", "route": "DEL - SUB", "price": 29000, "duration": "8h 5m"},
    {"type": "international", "name": "Thai Airways", "flightNumber": "TG-413", "route": "CCU - SUB", "price": 28500, "duration": "7h 40m"},

    # India <=> Japan (Tokyo - NRT/HND)
    {"type": "international", "name": "Japan Airlines", "flightNumber": "JL-740", "route": "DEL - NRT", "price": 45000, "duration": "7h 45m"},
    {"type": "international", "name": "ANA", "flightNumber": "NH-838", "route": "DEL - HND", "price": 46000, "duration": "7h 30m"},
    {"type": "international", "name": "Air India", "flightNumber": "AI-306", "route": "DEL - NRT", "price": 44000, "duration": "7h 50m"},
    {"type": "international", "name": "Vistara", "flightNumber": "UK-78", "route": "BOM - HND", "price": 47000, "duration": "8h 15m"},
    {"type": "international", "name": "Singapore Airlines", "flightNumber": "SQ-615", "route": "CCU - NRT", "price": 48000, "duration": "9h 20m"},
    
    # India <=> Dubai (DXB)
    {"type": "international", "name": "Emirates", "flightNumber": "EK-511", "route": "DEL - DXB", "price": 18500, "duration": "3h 45m"},
    {"type": "international", "name": "Vistara", "flightNumber": "UK-201", "route": "BOM - DXB", "price": 17500, "duration": "4h 0m"},
    {"type": "international", "name": "IndiGo", "flightNumber": "6E-1461", "route": "HYD - DXB", "price": 16900, "duration": "4h 10m"},
    {"type": "international", "name": "Flydubai", "flightNumber": "FZ-436", "route": "MAA - DXB", "price": 17800, "duration": "4h 25m"},
    {"type": "international", "name": "Air India Express", "flightNumber": "IX-194", "route": "GOI - DXB", "price": 16500, "duration": "4h 5m"},
    {"type": "international", "name": "Emirates", "flightNumber": "EK-571", "route": "CCU - DXB", "price": 19000, "duration": "4h 30m"},

    # India <=> Australia (SYD/MEL)
    {"type": "international", "name": "Qantas", "flightNumber": "QF-68", "route": "DEL - SYD", "price": 55000, "duration": "12h 30m"},
    {"type": "international", "name": "Air India", "flightNumber": "AI-302", "route": "DEL - MEL", "price": 54000, "duration": "12h 15m"},
    {"type": "international", "name": "Singapore Airlines", "flightNumber": "SQ-423", "route": "BOM - SYD", "price": 58000, "duration": "14h 5m"},
    {"type": "international", "name": "Malaysia Airlines", "flightNumber": "MH-174", "route": "BOM - MEL", "price": 57000, "duration": "13h 45m"},
    {"type": "international", "name": "Thai Airways", "flightNumber": "TG-335", "route": "CCU - SYD", "price": 56500, "duration": "13h 10m"},
    {"type": "international", "name": "Cathay Pacific", "flightNumber": "CX-618", "route": "CCU - MEL", "price": 59000, "duration": "14h 20m"},

    # India <=> New Zealand (AKL)
    {"type": "international", "name": "Air New Zealand", "flightNumber": "NZ-283", "route": "BOM - AKL", "price": 62000, "duration": "15h 45m"},
    {"type": "international", "name": "Singapore Airlines", "flightNumber": "SQ-401", "route": "DEL - AKL", "price": 63000, "duration": "16h 10m"},
    {"type": "international", "name": "Qantas", "flightNumber": "QF-122", "route": "DEL - AKL", "price": 65000, "duration": "17h 5m"},
    {"type": "international", "name": "Emirates", "flightNumber": "EK-570", "route": "HYD - AKL", "price": 68000, "duration": "18h 30m"},
    {"type": "international", "name": "Malaysia Airlines", "flightNumber": "MH-150", "route": "CCU - AKL", "price": 66000, "duration": "17h 50m"},
]

# Default routes
@app.route('/')
def home():
    return "Flight Service is running."

@app.route('/ping')
def ping():
    return "OK", 200

# API endpoint for searching flights
@app.route('/api/flights', methods=['GET'])
def search_flights():
    flight_type = request.args.get('type')
    from_dest = request.args.get('from')
    to_dest = request.args.get('to')

    if not all([flight_type, from_dest, to_dest]):
        return jsonify({"error": "Missing required query parameters: type, from, to"}), 400

    route_str = f"{from_dest} - {to_dest}"
    
    # Filter flights based on type and route
    results = [
        flight for flight in ALL_FLIGHTS
        if flight['type'] == flight_type and flight['route'] == route_str
    ]
    
    return jsonify({"flights": results})

# Application entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)