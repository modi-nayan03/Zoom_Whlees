from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import json
from bson import ObjectId

app = Flask(__name__)

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client.authentication_db  # MongoDB database name
bookings_collection = db.bookings  # MongoDB collection for bookings
cars_collection = db.cars  # MongoDB collection for cars

# Booking API Endpoints

@app.route("/bookings", methods=["POST"])
def create_booking():
    data = request.get_json()
    required_fields = ["user_name", "contact", "license_info", "car_id", "pickup_date", "return_date", "pickup_location"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    car_id = data["car_id"]

    # Check car availability
    car = cars_collection.find_one({"_id": ObjectId(car_id)})

    if not car:
        return jsonify({"error": "Car not found"}), 404
    if car.get("availability") == 0:  # availability is 0 means unavailable
        return jsonify({"error": "Selected car is not available"}), 400

    # Prepare booking data
    booking_data = {
        "user_name": data["user_name"],
        "contact": data["contact"],
        "license_info": data["license_info"],
        "car_id": car_id,
        "pickup_date": data["pickup_date"],
        "return_date": data["return_date"],
        "pickup_location": data["pickup_location"],
        "dropoff_location": data.get("dropoff_location", data["pickup_location"]),
        "addons": data.get("addons", []),
        "driver_option": data.get("driver_option", "self-drive"),
        "payment_method": data.get("payment_method", "unpaid"),
        "total_cost": data.get("total_cost", 0),
        "deposit_amount": data.get("deposit_amount", 0),
        "coupon_code": data.get("coupon_code"),
        "status": "pending",  # Initially set status to 'pending'
        "created_at": datetime.utcnow()
    }

    # Insert booking into MongoDB
    result = bookings_collection.insert_one(booking_data)

    # Mark car as unavailable
    cars_collection.update_one({"_id": ObjectId(car_id)}, {"$set": {"availability": 0}})

    return jsonify({"message": "Booking created successfully", "booking_id": str(result.inserted_id)}), 201

@app.route("/bookings", methods=["GET"])
def view_bookings():
    bookings = list(bookings_collection.find({}, {'_id': 0}))  # Excluding _id from result
    return jsonify(bookings), 200

@app.route("/bookings/<booking_id>", methods=["GET"])
def view_booking(booking_id):
    try:
        # Retrieve booking by ObjectId
        booking = bookings_collection.find_one({"_id": ObjectId(booking_id)}, {'_id': 0})
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        return jsonify(booking), 200
    except Exception as e:
        return jsonify({"error": "Invalid booking ID format"}), 400

@app.route("/bookings/<booking_id>", methods=["PATCH"])
def update_booking_status(booking_id):
    data = request.get_json()
    new_status = data.get("status")

    if not new_status:
        return jsonify({"error": "Status field is required"}), 400

    result = bookings_collection.update_one({"_id": ObjectId(booking_id)}, {"$set": {"status": new_status}})

    if result.matched_count == 0:
        return jsonify({"error": "Booking not found"}), 404

    return jsonify({"message": "Booking status updated successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)
