import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from email_sender_gmail import send_confirmation_email_via_gmail
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import Smart Trip Models
from models import Trip, Recommendation
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv(dotenv_path=".env")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Construct DB URI
DB_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"Connecting to DB: {DB_URI}")

# SQLAlchemy setup
engine = create_engine(DB_URI)
SessionLocal = sessionmaker(bind=engine)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def home():
    return "Booking Service is up and running!", 200


@app.route('/ping')
def ping():
    return "OK", 200


# ---------------------------
# BOOKING ENDPOINT (existing)
# ---------------------------
@app.route('/book', methods=['POST'])
def book():
    data = request.get_json(force=True)
    transaction_id = data.get('transaction_id', 'N/A')
    flight_name = data.get('flight', 'Unknown Flight')
    price = data.get('price', 0)
    recipient_email = data.get('user_email', 'default@example.com')

    if transaction_id != 'N/A' and price > 0 and recipient_email != 'default@example.com':
        booking_reference = "BOOK-" + transaction_id.split('-')[-1]

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
            "email_status": "Real Email Sent" if email_success else "Email Failed"
        }), 200
    else:
        return jsonify({"message": "Booking failed: Invalid data or missing email."}), 400


# ---------------------------
# SMART TRIP BUILDER FEATURE
# ---------------------------
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

    # Simple validation
    if not destination or not email:
        return jsonify({"message": "Missing destination or email"}), 400

    session = SessionLocal()
    try:
        # Step 1: Create the trip
        new_trip = Trip(
            destination=destination,
            user_email=email,
            start_date=start_date,
            end_date=end_date
        )
        session.add(new_trip)
        session.commit()

        # Step 2: Add simple, rule-based recommendations
        example_recs = [
            Recommendation(
                trip_id=new_trip.id,
                suggestion_type="hotel",
                name=f"{destination} Paradise Resort",
                description="Beach-facing resort with breakfast",
                price=4500
            ),
            Recommendation(
                trip_id=new_trip.id,
                suggestion_type="cab",
                name="Airport to Hotel Cab",
                description="Affordable city transport",
                price=600
            )
        ]

        session.add_all(example_recs)
        session.commit()

        return jsonify({
            "message": "Smart Trip created successfully!",
            "trip_id": new_trip.id,
            "destination": destination,
            "recommendations": [r.name for r in example_recs]
        }), 200

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500
    finally:
        session.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
