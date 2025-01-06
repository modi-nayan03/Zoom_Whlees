from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client.authentication_db  # Replace with your MongoDB database name
users_collection = db.users
cars_collection = db.cars


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    phone_no = data.get("phone_no")
    password = data.get("password")

    if not username or not email or not phone_no or not password:
        return jsonify({"error": "All fields (username, email, phone number, password) are required"}), 400

    # Check if the email already exists
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User with this email already exists"}), 409

    # Insert the new user with default 'renter' role
    new_user = {
        "username": username,
        "email": email,
        "phone_no": phone_no,
        "password": password,  # Store password in plain text (not hashed)
        "role": "renter"
    }
    users_collection.insert_one(new_user)

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = users_collection.find_one({"email": email})

    if not user or user["password"] != password:  # Compare password in plain text
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": f"Welcome, {user['username']}!", "role": user['role']}), 200


@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("new_password")

    if not email or not new_password:
        return jsonify({"error": "Email and new password are required"}), 400

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User with this email not found"}), 404

    # Update the password (plain text)
    users_collection.update_one({"email": email}, {"$set": {"password": new_password}})

    return jsonify({"message": "Password reset successfully"}), 200


@app.route("/switch-role", methods=["POST"])
def switch_role():
    data = request.get_json()
    email = data.get("email")
    new_role = data.get("new_role")  # Should be 'hosted_car' or 'renter'

    if not email or not new_role:
        return jsonify({"error": "Email and new role are required"}), 400

    user = users_collection.find_one({"email": email})

    if not user:
        return jsonify({"error": "User with this email not found"}), 404

    # Update the user's role
    users_collection.update_one({"email": email}, {"$set": {"role": new_role}})

    return jsonify({"message": f"Role switched to {new_role}"}), 200


@app.route("/users", methods=["GET"])
def get_users():
    users = users_collection.find({}, {"_id": 0, "username": 1, "email": 1, "phone_no": 1})
    return jsonify([user for user in users]), 200


@app.route("/list-cars", methods=["GET"])
def list_cars():
    email = request.args.get("email")
    user = users_collection.find_one({"email": email})

    if not user or user["role"] != "hosted_car":
        return jsonify({"error": "You must be a host to list cars"}), 403

    # Proceed with listing cars for hosted users
    cars = cars_collection.find({"user_email": email})
    return jsonify([car for car in cars]), 200


if __name__ == "__main__":
    app.run(debug=True)
