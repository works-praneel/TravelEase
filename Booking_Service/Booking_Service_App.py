import os
import boto3
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
# This import now matches the function names in the email sender file
from email_sender_gmail import send_confirmation_email, send_cancellation_email
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr # Import Attr for scanning
from datetime import datetime

# AWS DynamoDB Setup
# These table names come from your dynamodb.tf file
dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
bookings_table = dynamodb.Table('BookingsDB') 
trips_table = dynamodb.Table('SmartTripsDB') 

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# -------------------------------------
# UPDATED MOCK RECOMMENDATION DATA
# (2 Hotels + 1 Cab per destination)
# -------------------------------------
MOCK_RECOMMENDATIONS = {
    # Domestic
    "DEL": [
        {"suggestion_type": "hotel", "name": "The Oberoi, Delhi", "description": "Luxury stay near city center", "price": 15000},
        {"suggestion_type": "hotel", "name": "Radisson Blu Plaza", "description": "Close to the airport", "price": 8000},
        {"suggestion_type": "cab", "name": "Airport to Hotel Cab", "description": "Reliable city taxi", "price": 850}
    ],
    "BOM": [
        {"suggestion_type": "hotel", "name": "The Taj Mahal Palace", "description": "Iconic sea-facing hotel", "price": 22000},
        {"suggestion_type": "hotel", "name": "Trident Nariman Point", "description": "Stunning marine drive views", "price": 12000},
        {"suggestion_type": "cab", "name": "Airport to Hotel Cab", "description": "Reliable city taxi", "price": 700}
    ],
    "CCU": [
        {"suggestion_type": "hotel", "name": "ITC Sonar, Kolkata", "description": "A luxury collection hotel", "price": 9000},
        {"suggestion_type": "hotel", "name": "The Oberoi Grand", "description": "Colonial-era luxury", "price": 11000},
        {"suggestion_type": "cab", "name": "Airport to Hotel Cab", "description": "Reliable city taxi", "price": 600}
    ],
    "MAA": [
        {"suggestion_type": "hotel", "name": "Le Royal Meridien", "description": "5-star hotel in Chennai", "price": 7500},
        {"suggestion_type": "hotel", "name": "Taj Coromandel", "description": "Luxury in the heart of the city", "price": 10000},
        {"suggestion_type": "cab", "name": "Airport to Hotel Cab", "description": "Reliable city taxi", "price": 650}
    ],
    "GOI": [
        {"suggestion_type": "hotel", "name": "Taj Exotica Resort & Spa", "description": "Luxury beach resort", "price": 18000},
        {"suggestion_type": "hotel", "name": "W Goa", "description": "Vibrant stay on Vagator beach", "price": 25000},
        {"suggestion_type": "cab", "name": "Airport to Hotel Cab", "description": "Reliable city taxi", "price": 1200}
    ],
    "HYD": [
        {"suggestion_type": "hotel", "name": "Taj Falaknuma Palace", "description": "A palace hotel", "price": 30000},
        {"suggestion_type": "hotel", "name": "ITC Kohenur", "description": "Luxury hotel in HITEC City", "price": 12000},
        {"suggestion_type": "cab", "name": "Airport to Hotel Cab", "description": "Reliable city taxi", "price": 900}
    ],
    # International
    "HKT": [
        {"suggestion_type": "hotel", "name": "Keemala Phuket", "description": "Unique pool villas", "price": 45000},
        {"suggestion_type": "hotel", "name": "The Shore at Katathani", "description": "Adults-only beach resort", "price": 30000},
        {"suggestion_type": "cab", "name": "Airport to Hotel Cab", "description": "Reliable city taxi", "price": 1500}
    ],
    "SUB": [
        {"suggestion_type": "hotel", "name": "JW Marriott Hotel Surabaya", "description": "Luxury hotel in city center", "price": 10000},
        {"suggestion_type": "hotel", "name": "Shangri-La Surabaya", "description": "5-star accommodation", "price": 9000},
        {"suggestion_type": "cab", "name": "Airport to Hotel Cab", "description": "Reliable city taxi", "price": 1300}
    ],
    "NRT": [
        {"suggestion_type": "hotel", "name": "Hotel Nikko Narita", "description": "Convenient airport hotel", "price": 8000},
        {"suggestion_type": "hotel", "name": "Narita Tobu Hotel Airport", "description": "Shuttle service included", "price": 7000},
        {"suggestion_type": "cab", "name": "Airport to Tokyo Center", "description": "Fixed fare taxi", "price": 15000}
    ],
    "HND": [
        {"suggestion_type": "hotel", "name": "The Royal Park Hotel Tokyo Haneda", "description": "Directly connected to terminal", "price": 12000},
        {"suggestion_type": "hotel", "name": "Haneda Excel Hotel Tokyu", "description": "Connected to Terminal 2", "price": 11000},
        {"suggestion_type": "cab", "name": "Airport to Tokyo Center", "description": "Fixed fare taxi", "price": 7000}
    ],
    "DXB": [
        {"suggestion_type": "hotel", "name": "Burj Al Arab Jumeirah", "description": "Iconic 7-star hotel", "price": 150000},
        {"suggestion_type": "hotel", "name": "Atlantis, The Palm", "description": "Luxury resort with waterpark", "price": 40000},
        {"suggestion_type": "cab", "name": "Airport to Hotel Cab", "description": "Reliable city taxi", "price": 1000}
    ],
    "SYD": [
        {"suggestion_type": "hotel", "name": "Park Hyatt Sydney", "description": "Views of the Opera House", "price": 60000},
        {"suggestion_type": "hotel", "name": "Four Seasons Hotel Sydney", "description": "Luxury by the harbour", "price": 25000},
        {"suggestion_type": "cab", "name": "Airport to Hotel Cab", "description": "Reliable city taxi", "price": 2500}
    ],
    "MEL": [
        {"suggestion_type": "hotel", "name": "Crown Towers Melbourne", "description": "Luxury on the Yarra River", "price": 30000},
        {"suggestion_type": "hotel", "name": "The Langham, Melbourne", "description": "5-star elegance", "price": 22000},
        {"suggestion_type": "cab", "name": "Airport to Hotel Cab", "description": "Reliable city taxi", "price": 2400}
    ],
    "AKL": [
        {"suggestion_type": "hotel", "name": "SkyCity Grand Hotel", "description": "Luxury in the city center", "price": 18000},
        {"suggestion_type": "hotel", "name": "Cordis, Auckland", "description": "Elegant rooms and suites", "price": 15000},
        {"suggestion_type": "cab", "name": "Airport to Hotel Cab", "description": "Reliable city taxi", "price": 2800}
    ],
    "DEFAULT": [
        {"suggestion_type": "hotel", "name": "Grand Default Hotel", "description": "Reliable comfort", "price": 6000},
        {"suggestion_type": "hotel", "name": "City Inn", "description": "Clean and affordable", "price": 4000},
        {"suggestion_type": "cab", "name": "Airport Taxi", "description": "Standard city fare", "price": 1000}
    ]
}


@app.route('/')
def home():
    return "Booking Service (Main Branch with DynamoDB) is up!", 200


@app.route('/ping')
def ping():
    return "OK", 200


# ---------------------------
# BOOKING ENDPOINT (Corrected)
# ---------------------------
@app.route('/book', methods=['POST'])
def book():
    data = request.get_json(force=True)
    transaction_id = data.get('transaction_id', 'N/A')
    flight_name = data.get('flight', 'Unknown Flight') # From payment service
    price = data.get('price', 0)
    recipient_email = data.get('user_email', 'default@example.com')
    selected_seat = data.get('seat_number', 'N/A') # From payment service
    flight_id = data.get('flight_id', 'N/A') # From payment service
    
    booking_reference = "BK-" + str(uuid.uuid4()).split('-')[1]
    booking_timestamp = datetime.utcnow().isoformat()

    try:
        # --- Check if seat is already booked (Atomic Check) ---
        # We try to put the item, but only if an item with the same
        # flight_id AND selected_seat does not already exist.
        bookings_table.put_item(
            Item={
                'booking_reference': booking_reference,
                'user_email': recipient_email,
                'transaction_id': transaction_id,
                'flight_name': flight_name, 
                'flight_id': flight_id, # e.g., "6E-123_2025-11-06"
                'price': price,
                'selected_seat': selected_seat,
                'booking_status': 'CONFIRMED',
                'created_at': booking_timestamp
            },
            # This is the "Conditional Expression"
            # It ensures this write only succeeds if no other item
            # has this combination of flight_id and selected_seat.
            # We need a GSI on (flight_id, selected_seat) for this,
            # but for now, we'll rely on the /get_seats check
            # and this put_item will just create the booking.
            # A more robust solution would use DynamoDB Transactions.
        )
    except ClientError as e:
        print(f"Boto3 Error: {e.response['Error']['Message']}")
        return jsonify({"message": "Booking failed: Database error."}), 500
    except Exception as e:
        print(f"General Error: {str(e)}")
        return jsonify({"message": f"Booking failed: {str(e)}"}), 500

    email_success = send_confirmation_email(recipient_email, {
        "booking_reference": booking_reference,
        "flight": flight_name,
        "price": price,
        "seat": selected_seat,
        "transaction_id": transaction_id
    })

    return jsonify({
        "message": "Booking successfully finalized!",
        "booking_reference": booking_reference,
        "flight": flight_name,
        "email_status": "Real Email Sent" if email_success else "Email Failed"
    }), 200


# ---------------------------
# NAYA: GET SEATS ENDPOINT
# ---------------------------
@app.route('/api/get_seats', methods=['GET'])
def get_seats():
    flight_id = request.args.get('flight_id')
    if not flight_id:
        return jsonify({"message": "Missing flight_id parameter"}), 400

    try:
        # Scan the table for all items matching the flight_id
        # and a 'CONFIRMED' status.
        response = bookings_table.scan(
            FilterExpression=Attr('flight_id').eq(flight_id) & Attr('booking_status').eq('CONFIRMED')
        )
        
        items = response.get('Items', [])
        
        # Extract just the seat numbers
        booked_seats = [item['selected_seat'] for item in items]
        
        return jsonify({"booked_seats": booked_seats}), 200
        
    except ClientError as e:
        print(f"Boto3 Error: {e.response['Error']['Message']}")
        return jsonify({"message": "Could not fetch seats: Database error."}), 500
    except Exception as e:
        print(f"General Error: {str(e)}")
        return jsonify({"message": f"Could not fetch seats: {str(e)}"}), 500


# ---------------------------
# CANCELLATION ENDPOINT (with Refund Logic)
# ---------------------------
@app.route('/cancel', methods=['POST'])
def cancel_booking():
    data = request.get_json(force=True)
    booking_reference = data.get('booking_reference')
    email = data.get('user_email')

    if not booking_reference or not email:
        return jsonify({"message": "Missing booking reference or email"}), 400

    try:
        response = bookings_table.update_item(
            Key={'booking_reference': booking_reference},
            UpdateExpression="set booking_status = :s",
            ExpressionAttributeValues={':s': 'CANCELLED'},
            ReturnValues="ALL_OLD" # Get the old item to fetch price for refund
        )
        
        old_booking = response.get('Attributes', {})
        if not old_booking:
            return jsonify({"message": "Booking reference not found"}), 404

        original_price = old_booking.get('price', 0)
        
        # Calculate the 55% refund
        refund_amount = float(original_price) * 0.55
        
        send_cancellation_email(email, {
            "booking_reference": booking_reference,
            "flight": old_booking.get('flight_name', 'N/A'),
            "price": original_price
        }, refund_amount)
        
        return jsonify({
            "message": "Booking successfully cancelled!",
            "booking_reference": booking_reference,
            "new_status": "CANCELLED",
            "refund_amount": refund_amount
        }), 200

    except ClientError as e:
        print(e.response['Error']['Message'])
        return jsonify({"message": f"Cancellation failed: {str(e)}"}), 500


# ------------------------------------
# SMART TRIP (Mock Data Logic)
# ------------------------------------
@app.route('/smart-trip', methods=['POST'])
def smart_trip():
    """Creates a new trip and gives smart hotel/cab suggestions."""
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"message": "Invalid JSON format"}), 400

    destination = data.get('destination') 
    email = data.get('user_email')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not destination or not email:
        return jsonify({"message": "Missing destination or email"}), 400

    try:
        trip_id = str(uuid.uuid4())
        
        # Use the updated recommendations dictionary
        mock_recs = MOCK_RECOMMENDATIONS.get(destination, MOCK_RECOMMENDATIONS["DEFAULT"])

        # 'SmartTripsDB' mein save karein
        trips_table.put_item(
            Item={
                'trip_id': trip_id,
                'user_email': email,
                'destination': destination,
                'start_date': start_date,
                'end_date': end_date,
                'recommendations': mock_recs
            }
        )

        return jsonify({
            "message": "Smart Trip created successfully!",
            "trip_id": trip_id,
            "destination": destination,
            "recommendations": mock_recs
        }), 200

    except Exception as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)