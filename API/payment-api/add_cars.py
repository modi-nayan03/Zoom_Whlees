from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client.authentication_db  # Replace with your MongoDB database name
cars_collection = db.cars  # MongoDB collection for cars

# Endpoint to add a new car
@app.route("/add-car", methods=["POST"])
def add_car():
    data = request.get_json()

    new_car = {
        "make": data["make"],
        "model": data["model"],
        "year": data["year"],
        "vehicle_type": data["vehicle_type"],
        "fuel_type": data["fuel_type"],
        "transmission_type": data["transmission_type"],
        "car_driven": data["car_driven"],
        "registration_number": data["registration_number"],
        "vin": data["vin"],
        "insurance_details": data.get("insurance_details", ""),
        "pickup_location": data["pickup_location"],
        "daily_rental_price": data["daily_rental_price"]
    }

    # Insert the car document into MongoDB
    result = cars_collection.insert_one(new_car)
    
    return jsonify({"message": "Car added successfully", "car_id": str(result.inserted_id)}), 201

# Endpoint to retrieve all cars
@app.route("/cars", methods=["GET"])
def get_cars():
    cars = list(cars_collection.find({}, {'_id': 0}))  # Excluding _id from the result
    return jsonify(cars), 200

# Endpoint to retrieve a specific car by ID
@app.route("/cars/<car_id>", methods=["GET"])
def get_car(car_id):
    try:
        # Retrieve car by ObjectId
        car = cars_collection.find_one({"_id": ObjectId(car_id)}, {'_id': 0})
        if not car:
            return jsonify({"error": "Car not found"}), 404
        return jsonify(car), 200
    except Exception as e:
        return jsonify({"error": "Invalid car ID format"}), 400

# Endpoint to update car details
@app.route("/cars/<car_id>", methods=["PUT"])
def update_car(car_id):
    data = request.get_json()

    # Update the car document in MongoDB
    updated_car = {key: value for key, value in data.items()}
    result = cars_collection.update_one({"_id": ObjectId(car_id)}, {"$set": updated_car})

    if result.matched_count == 0:
        return jsonify({"error": "Car not found"}), 404
    
    return jsonify({"message": "Car updated successfully"}), 200

# Endpoint to delete a car
@app.route("/cars/<car_id>", methods=["DELETE"])
def delete_car(car_id):
    result = cars_collection.delete_one({"_id": ObjectId(car_id)})

    if result.deleted_count == 0:
        return jsonify({"error": "Car not found"}), 404
    
    return jsonify({"message": "Car deleted successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)
