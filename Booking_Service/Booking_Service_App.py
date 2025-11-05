# works-praneel/travelease/TravelEase-main/Booking_Service/Booking_Service_App.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Key, Attr  # <-- FIX: Added Attr
from botocore.exceptions import ClientError
import os
import uuid
import json
from decimal import Decimal

# Import your custom email function
# This assumes email_sender_gmail.py is in the same directory
try:
    from email_sender_gmail import send_booking_confirmation, send_cancellation_confirmation
except ImportError:
    print("Warning: email_sender_gmail.py not found. Email notifications will be disabled.")
    # Create dummy functions so the app doesn't crash
    def send_booking_confirmation(email, booking_ref, flight_details, seat, price):
        print(f"DUMMY_EMAIL: Sending booking confirmation to {email} for {booking_ref}")
        return "Email service is not configured."
    
    def send_cancellation_confirmation(email, booking_ref, refund_amount):
        print(f"DUMMY_EMAIL: Sending cancellation confirmation to {email} for {booking_ref}")
        return "Email service is not configured."

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# --- DynamoDB Setup ---
# We use a Boto3 resource which is high-level
try:
    if os.environ.get('AWS_SAM_LOCAL'):
        # For local SAM testing
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://host.docker.internal:8000")
    else:
        # For production (deployed to ECS)
        dynamodb = boto3.resource('dynamodb')
except Exception as e:
    print(f"Error initializing DynamoDB resource: {e}")
    dynamodb = None

# Get table names from Environment Variables set in Terraform
BOOKINGS_TABLE_NAME = os.environ.get('BOOKINGS_TABLE_NAME', 'BookingsDB')
SEAT_TABLE_NAME = os.environ.get('SEAT_TABLE_NAME', 'SeatInventory')
SMART_TRIPS_TABLE_NAME = "SmartTripsDB"  # <-- FIX: Added SmartTripsDB table

try:
    bookings_table = dynamodb.Table(BOOKINGS_TABLE_NAME)
    seat_table = dynamodb.Table(SEAT_TABLE_NAME)
    smart_trips_table = dynamodb.Table(SMART_TRIPS_TABLE_NAME) # <-- FIX: Added table object
except Exception as e:
    print(f"Error connecting to tables: {e}")
    bookings_table = None
    seat_table = None
    smart_trips_table = None

# Helper for JSON encoding Decimals
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)

app.json_encoder = DecimalEncoder

# --- Routes ---

@app.route('/ping', methods=['GET'])
def ping():
    """ A simple health check endpoint. """
    return jsonify({"message": "Booking Service is running!"}), 200

@app.route('/book', methods=['POST'])
def book_flight():
    """
    Handles the booking of a flight.
    This is a 2-step process:
    1. Try to reserve the seat (PutItem with ConditionExpression)
    2. If seat reservation is successful, create the booking.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400

        required_fields = ['flight_id', 'seat_number', 'price', 'transaction_id', 'user_email', 'flight_details']
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Missing required booking information"}), 400

        flight_id = data['flight_id']
        seat_number = data['seat_number']
        user_email = data['user_email']
        price = Decimal(str(data['price']))
        booking_reference = f"BK-{str(uuid.uuid4())[:6].upper()}"

        # Step 1: Try to reserve the seat in the SeatInventory table.
        # This operation is conditional (ConditionExpression) and atomic.
        # It will FAIL if an item with the same flight_id and seat_number already exists.
        seat_reservation = {
            'flight_id': flight_id,
            'seat_number': seat_number,
            'booking_reference': booking_reference,
            'user_email': user_email
        }

        try:
            seat_table.put_item(
                Item=seat_reservation,
                ConditionExpression="attribute_not_exists(flight_id) AND attribute_not_exists(seat_number)"
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(f"SEAT CONFLICT: Seat {seat_number} on flight {flight_id} is already booked.")
                return jsonify({"message": "That seat was just taken. Please select another."}), 409
            else:
                print(f"Error reserving seat in DynamoDB: {e}")
                raise

        # Step 2: If seat reservation was successful, create the booking.
        booking_details = {
            'booking_reference': booking_reference,
            'flight_id': flight_id,
            'seat_number': seat_number,
            'flight_details': data['flight_details'],
            'price': price,
            'transaction_id': data['transaction_id'],
            'user_email': user_email,
            'booking_status': 'CONFIRMED'
        }

        bookings_table.put_item(Item=booking_details)

        # Step 3: Send confirmation email
        email_status = "Skipped"
        try:
            email_status = send_booking_confirmation(
                email=user_email,
                booking_ref=booking_reference,
                flight_details=data['flight_details'],
                seat=seat_number,
                price=str(price)
            )
        except Exception as email_error:
            print(f"CRITICAL: Booking {booking_reference} confirmed but email failed: {email_error}")
            email_status = f"Failed: {email_error}"

        return jsonify({
            "message": "Booking successful!",
            "booking_reference": booking_reference,
            "email_status": email_status
        }), 201

    except Exception as e:
        print(f"Error in /book route: {e}")
        return jsonify({"message": "Booking failed due to an internal error.", "error": str(e)}), 500

@app.route('/cancel', methods=['POST'])
def cancel_booking():
    """
    Cancels a booking.
    1. Fetches the booking to verify email and get seat details.
    2. Deletes the booking from the BookingsDB.
    3. Deletes the seat reservation from the SeatInventoryDB (making it available).
    4. Sends a cancellation email.
    """
    try:
        data = request.get_json()
        if not data or 'booking_reference' not in data or 'user_email' not in data:
            return jsonify({"message": "Booking reference and email are required."}), 400

        booking_ref = data['booking_reference']
        user_email = data['user_email']

        # Step 1: Get the booking
        response = bookings_table.get_item(Key={'booking_reference': booking_ref})
        booking = response.get('Item')

        if not booking:
            return jsonify({"message": "Booking not found."}), 404

        # Step 2: Verify user email
        if booking['user_email'] != user_email:
            return jsonify({"message": "Unauthorized. Email does not match booking."}), 403

        # Step 3: Get details needed for deletion
        flight_id = booking['flight_id']
        seat_number = booking['seat_number']
        price = booking.get('price', 0)
        
        # Step 4: Delete booking and seat reservation in a transaction (or sequentially)
        # We will do it sequentially for simplicity.

        # 4a. Delete seat reservation
        try:
            seat_table.delete_item(
                Key={
                    'flight_id': flight_id,
                    'seat_number': seat_number
                }
            )
        except ClientError as e:
            print(f"Warning: Could not delete seat {seat_number} for flight {flight_id}. It might have been deleted already. {e}")

        # 4b. Delete booking
        bookings_table.delete_item(
            Key={'booking_reference': booking_ref}
        )
        
        # Step 5: Send cancellation email
        # In a real app, you'd trigger a refund via the payment service first.
        refund_amount = price * Decimal('0.9') # Simulate a 10% cancellation fee
        email_status = "Skipped"
        try:
            email_status = send_cancellation_confirmation(
                email=user_email,
                booking_ref=booking_ref,
                refund_amount=str(refund_amount)
            )
        except Exception as email_error:
            print(f"Warning: Cancellation for {booking_ref} processed but email failed: {email_error}")
            email_status = f"Failed: {email_error}"

        return jsonify({
            "message": "Booking successfully cancelled.",
            "booking_reference": booking_ref,
            "refund_amount": float(refund_amount),
            "email_status": email_status
        }), 200

    except Exception as e:
        print(f"Error in /cancel route: {e}")
        return jsonify({"message": "Cancellation failed due to an internal error.", "error": str(e)}), 500

@app.route('/api/get_seats', methods=['GET'])
def get_booked_seats():
    """
    Gets all booked seats for a specific flight_id.
    flight_id is passed as a query parameter (e.g., ?flight_id=AI202_2025-10-20)
    """
    flight_id = request.args.get('flight_id')
    if not flight_id:
        return jsonify({"message": "flight_id query parameter is required."}), 400

    try:
        # We use query() because flight_id is the hash key of the seat_table
        response = seat_table.query(
            KeyConditionExpression=Key('flight_id').eq(flight_id),
            ProjectionExpression='seat_number' # Only get the seat_number
        )
        
        booked_seats = [item['seat_number'] for item in response.get('Items', [])]
        
        return jsonify({
            "flight_id": flight_id,
            "booked_seats": booked_seats
        }), 200

    except Exception as e:
        print(f"Error in /api/get_seats route: {e}")
        return jsonify({"message": "Could not retrieve seat map.", "error": str(e)}), 500

@app.route('/smart-trip', methods=['POST'])
def get_smart_trip_recommendations():
    """
    Scans the SmartTripsDB for recommendations matching a destination.
    This new function handles the "Smart Trip" button presses.
    """
    try:
        data = request.get_json()
        if not data or 'destination' not in data:
            return jsonify({"message": "Destination code is required."}), 400

        destination_code = data.get('destination')

        # We must use a Scan operation because the table's hash key is trip_id,
        # but we are searching by a non-key attribute 'destination_code'.
        # This is not efficient on large tables, but works for this design.
        if not smart_trips_table:
            raise Exception("Smart Trips table is not initialized.")
            
        response = smart_trips_table.scan(
            FilterExpression=Attr('destination_code').eq(destination_code)
        )

        items = response.get('Items', [])
        
        # Convert DynamoDB Decimal types to standard numbers
        recommendations = []
        for item in items:
            recommendations.append({
                "trip_id": item.get('trip_id'),
                "name": item.get('name'),
                "description": item.get('description'),
                "price": int(item.get('price', 0)), # Use int() to convert Decimal
                "suggestion_type": item.get('suggestion_type', 'Activity'),
                "destination_code": item.get('destination_code')
            })

        return jsonify({"recommendations": recommendations}), 200

    except Exception as e:
        print(f"Error in /smart-trip: {e}")
        return jsonify({"message": "Could not retrieve smart trip recommendations.", "error": str(e)}), 500


# --- Main ---
if __name__ == '__main__':
    # Set a default port 5000, which matches your Dockerfile and ALB
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)