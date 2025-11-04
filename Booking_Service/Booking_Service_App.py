from flask import Flask, request, jsonify 
from flask_cors import CORS
from email_sender_gmail import send_confirmation_email_via_gmail, send_cancellation_email_via_gmail
import boto3
import os
from botocore.exceptions import ClientError

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 

# ==========================================================
# 🛑 NAYA: AWS DYNAMODB SETUP 🛑
# ==========================================================
# Environment variables se table ke naam lein (Terraform mein set kiye gaye)
BOOKINGS_TABLE_NAME = os.environ.get("BOOKINGS_TABLE_NAME", "TravelEase-Bookings")
SEAT_TABLE_NAME = os.environ.get("SEAT_TABLE_NAME", "TravelEase-SeatInventory")

# DynamoDB client initialize karein
# Container ke andar yeh automatically IAM role se credentials le lega
dynamodb = boto3.resource('dynamodb')
bookings_table = dynamodb.Table(BOOKINGS_TABLE_NAME)
seat_table = dynamodb.Table(SEAT_TABLE_NAME)

# Helper function
def get_flight_id(flight_name, date):
    # Yeh unique key banata hai
    return f"{flight_name}_{date}"

# ==========================================================

@app.route('/')
def booking_home():
    return "Booking Service (AWS) is up and running!", 200

@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/book', methods=['POST']) 
def book():
    try:
        data = request.get_json() 
    except Exception:
        data = {} 
        
    transaction_id = data.get('transaction_id', 'N/A')
    flight_name = data.get('flight', 'Unknown Flight')
    price = data.get('price', 0)
    recipient_email = data.get('user_email', 'default@example.com')
    seat_number = data.get('seat_number', 'N/A')
    flight_date = data.get('flight_date', 'N/A')
    
    flight_id = get_flight_id(flight_name, flight_date) # e.g., "IndiGo-6E-202_2025-12-30"

    if any(v == 'N/A' for v in [transaction_id, flight_name, seat_number, flight_date, recipient_email]) or price <= 0:
        return jsonify({"message": "Booking failed: Invalid data, missing email, seat, or date."}), 400

    # 1. SEAT AVAILABILITY CHECK (ATOMIC OPERATION)
    # Hum DynamoDB ko bolenge: "Yeh seat tabhi book karo jab yeh pehle se मौजूद na ho"
    try:
        seat_table.put_item(
           Item={
               'flight_id': flight_id,  # Partition Key
               'seat_number': seat_number # Sort Key
           },
           # Yeh line race condition ko rokti hai:
           ConditionExpression='attribute_not_exists(flight_id) AND attribute_not_exists(seat_number)'
        )
        print(f"SUCCESS: Seat {seat_number} for {flight_id} atomically booked.")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # Iska matlab seat pehle se book hai
            print(f"FAILURE: Seat {seat_number} for {flight_id} is already taken.")
            return jsonify({"message": f"Booking failed: Seat {seat_number} is already taken."}), 409 # 409 Conflict
        else:
            # Koi aur DynamoDB error
            print(f"DYNAMODB ERROR: {e}")
            return jsonify({"message": "Booking failed: Could not process seat."}), 500

    # 2. BOOKING KO DATABASE MEIN SAVE KAREIN
    booking_reference = "BOOK-" + transaction_id.split('-')[-1]
    booking_details = {
        "booking_reference": booking_reference, # Partition Key
        "flight": flight_name,
        "price": price,
        "transaction_id": transaction_id,
        "user_email": recipient_email,
        "flight_id": flight_id,
        "flight_date": flight_date,
        "seat": seat_number,
        "status": "CONFIRMED"
    }

    try:
        bookings_table.put_item(Item=booking_details)
        print(f"SUCCESS: Booking {booking_reference} saved to DynamoDB.")
    except ClientError as e:
        print(f"DYNAMODB ERROR saving booking: {e}")
        # Yahan par seat booking ko rollback (delete) karne ka logic add karna chahiye
        # Abhi ke liye, hum error return karte hain
        return jsonify({"message": "Booking failed: Could not save booking details."}), 500

    # 3. EMAIL BHEJEIN
    email_success = send_confirmation_email_via_gmail(recipient_email, booking_details)
    
    return jsonify({
        "message": "Booking successfully finalized!",
        "booking_reference": booking_reference,
        "flight": flight_name,
        "seat_booked": seat_number,
        "email_status": "Real Email Sent" if email_success else "Email Failed" 
    }), 200

# ==========================================================
# 🛑 NAYA ENDPOINT: CANCELLATION (DYNAMODB KE SAATH) 🛑
# ==========================================================
@app.route('/cancel', methods=['POST'])
def cancel_booking():
    data = request.get_json()
    booking_ref = data.get('booking_reference')
    user_email = data.get('user_email')

    if not booking_ref or not user_email:
        return jsonify({"message": "Cancellation failed: Missing booking reference or email."}), 400

    # 1. Booking dhoondein
    try:
        response = bookings_table.get_item(Key={'booking_reference': booking_ref})
        booking = response.get('Item')
        if not booking:
            return jsonify({"message": "Cancellation failed: Booking not found."}), 404
            
    except ClientError as e:
        print(f"DYNAMODB ERROR fetching booking: {e}")
        return jsonify({"message": "Error finding booking."}), 500

    # 2. Verify email and status
    if booking['user_email'] != user_email:
        return jsonify({"message": "Cancellation failed: Unauthorized."}), 401
    if booking['status'] == 'CANCELLED':
        return jsonify({"message": "This booking is already cancelled."}), 400

    # 3. Cancellation process karein
    original_price = int(booking['price']) # DynamoDB se 'Decimal' type aa sakta hai
    refund_amount = round(original_price * 0.55, 2)
    flight_id = booking['flight_id']
    seat_number = booking['seat']

    try:
        # 4. Booking status update karein (status='CANCELLED')
        bookings_table.update_item(
            Key={'booking_reference': booking_ref},
            UpdateExpression='SET #status = :val',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':val': 'CANCELLED'}
        )
        
        # 5. Seat ko vaapis "available" karein (inventory se delete karke)
        seat_table.delete_item(
            Key={
                'flight_id': flight_id,
                'seat_number': seat_number
            }
        )
        print(f"SUCCESS: Seat {seat_number} for {flight_id} is now available.")
        
    except ClientError as e:
        print(f"DYNAMODB ERROR during cancellation: {e}")
        return jsonify({"message": "Cancellation failed during update."}), 500
    
    # 6. Cancellation email bhejien
    email_success = send_cancellation_email_via_gmail(user_email, booking, refund_amount)

    return jsonify({
        "message": "Booking successfully cancelled.",
        "booking_reference": booking_ref,
        "refund_amount": refund_amount,
        "email_status": "Cancellation Email Sent" if email_success else "Email Failed"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
