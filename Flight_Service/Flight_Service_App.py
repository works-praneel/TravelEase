from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from itertools import permutations
import datetime

app = Flask(__name__)
# CORS fix for local mode: Allow all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Data for Flight Generation ---
DOMESTIC_AIRLINES = ["IndiGo", "Vistara", "Air India", "SpiceJet", "Akasa Air", "AirAsia India"]
INTERNATIONAL_AIRLINES = {
    "HKT": ["Thai Airways", "IndiGo", "SpiceJet", "Go First"],
    "SUB": ["Garuda Indonesia", "Batik Air", "Singapore Airlines", "Malaysia Airlines"],
    "NRT": ["Japan Airlines", "ANA", "Air India", "Vistara", "Singapore Airlines"],
    "HND": ["Japan Airlines", "ANA", "Vistara"],
    "DXB": ["Emirates", "Flydubai", "Air India Express", "IndiGo", "Vistara", "SpiceJet"],
    "SYD": ["Qantas", "Air India", "Singapore Airlines", "Thai Airways"],
    "MEL": ["Qantas", "Air India", "Malaysia Airlines", "Cathay Pacific"],
    "AKL": ["Air New Zealand", "Singapore Airlines", "Qantas", "Emirates", "Malaysia Airlines"]
}
DOMESTIC_HUBS = ["DEL", "BOM", "CCU", "MAA", "HYD", "GOI"]
INTERNATIONAL_HUBS = ["HKT", "SUB", "NRT", "HND", "DXB", "SYD", "MEL", "AKL"]

# (price, duration_in_minutes)
GENERIC_ROUTE_PROFILES = {
    "domestic_short": (4000, 100),
    "domestic_medium": (6000, 140),
    "international_short": (18000, 240),
    "international_medium": (25000, 420),
    "international_long": (45000, 750),
    "international_xl": (65000, 950)
}

# --- Flight Generation Function ---
def generate_flights(flight_type, route_key, num_flights=10):
    flights = []
    origin, dest = route_key.split('-')
    
    profile_key = "domestic_medium"
    if flight_type == "domestic":
        if {origin, dest} in [{"BOM", "HYD"}, {"BOM", "GOI"}, {"MAA", "HYD"}]:
            profile_key = "domestic_short"
    else:
        intl_hub = dest if dest in INTERNATIONAL_HUBS else origin
        if intl_hub in ["DXB"]: profile_key = "international_short"
        elif intl_hub in ["HKT", "SUB"]: profile_key = "international_medium"
        elif intl_hub in ["SYD", "MEL", "NRT", "HND"]: profile_key = "international_long"
        elif intl_hub in ["AKL"]: profile_key = "international_xl"

    base_price, base_duration = GENERIC_ROUTE_PROFILES[profile_key]

    for _ in range(num_flights):
        if flight_type == "domestic":
            airline = random.choice(DOMESTIC_AIRLINES)
        else:
            intl_hub = dest if dest in INTERNATIONAL_HUBS else origin
            airline = random.choice(INTERNATIONAL_AIRLINES.get(intl_hub, ["Intl. Airline"]))
        
        flight_prefix = airline.split(' ')[0][:2].upper()

        price_variation = random.randint(-2000, 2000)
        duration_variation = random.randint(-30, 30)
        
        final_price = base_price + price_variation
        final_duration_min = base_duration + duration_variation
        hours, minutes = divmod(final_duration_min, 60)

        # --- NEW: Generate Timings ---
        departure_hour = random.randint(0, 23)
        departure_minute = random.choice([0, 15, 30, 45])
        departure_time = datetime.datetime(2025, 1, 1, departure_hour, departure_minute)
        arrival_time = departure_time + datetime.timedelta(minutes=final_duration_min)
        
        flight = {
            "type": flight_type,
            "name": airline,
            "flightNumber": f"{flight_prefix}-{random.randint(100, 9999)}",
            "route": f"{origin}-{dest}",
            "price": final_price,
            "duration": f"{hours}h {minutes}m",
            "departureTime": departure_time.strftime("%H:%M"),
            "arrivalTime": arrival_time.strftime("%H:%M")
        }
        flights.append(flight)
    return flights

# --- Generate the Full Flight List ---
ALL_FLIGHTS = []
# 1. Domestic
for origin, dest in permutations(DOMESTIC_HUBS, 2):
    ALL_FLIGHTS.extend(generate_flights("domestic", f"{origin}-{dest}", 10))
# 2. International (To)
for origin in DOMESTIC_HUBS:
    for dest in INTERNATIONAL_HUBS:
        ALL_FLIGHTS.extend(generate_flights("international", f"{origin}-{dest}", 10))
# 3. International (From)
for origin in INTERNATIONAL_HUBS:
    for dest in DOMESTIC_HUBS:
        ALL_FLIGHTS.extend(generate_flights("international", f"{origin}-{dest}", 10))


# --- API Endpoints ---
@app.route('/')
def home(): return "Flight Service is running."
@app.route('/ping')
def ping(): return "OK", 200

@app.route('/api/flights', methods=['GET'])
def search_flights():
    flight_type = request.args.get('type')
    from_dest = request.args.get('from')
    to_dest = request.args.get('to')

    if not all([flight_type, from_dest, to_dest]):
        return jsonify({"error": "Missing required query parameters"}), 400

    route_str = f"{from_dest}-{to_dest}"
    results = [f for f in ALL_FLIGHTS if f['type'] == flight_type and f['route'] == route_str]
    
    if not results: print(f"No flights found for route: {route_str}")
    return jsonify({"flights": results})

# --- Main Execution ---
if __name__ == '__main__':
    print(f"Generated a total of {len(ALL_FLIGHTS)} flights.")
    app.run(host='0.0.0.0', port=5002)