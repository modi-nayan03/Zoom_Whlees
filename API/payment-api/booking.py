from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import json

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'authentication_db'

mysql = MySQL(app)

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
    cur = mysql.connection.cursor()
    cur.execute("SELECT availability FROM cars WHERE id = %s", (car_id,))
    car = cur.fetchone()
    if not car or not car[0]:
        return jsonify({"error": "Selected car is not available"}), 400

    # Insert booking into database
    query = """
        INSERT INTO bookings (
            user_name, contact, license_info, car_id, pickup_date, return_date, pickup_location,
            dropoff_location, addons, driver_option, payment_method, total_cost, deposit_amount, coupon_code
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        data["user_name"],
        data["contact"],
        data["license_info"],
        car_id,
        data["pickup_date"],
        data["return_date"],
        data["pickup_location"],
        data.get("dropoff_location", data["pickup_location"]),
        json.dumps(data.get("addons", [])),
        data.get("driver_option", "self-drive"),
        data.get("payment_method", "unpaid"),
        data.get("total_cost", 0),
        data.get("deposit_amount", 0),
        data.get("coupon_code")
    )
    cur.execute(query, values)

    # Mark car as unavailable
    cur.execute("UPDATE cars SET availability = FALSE WHERE id = %s", (car_id,))
    mysql.connection.commit()
    booking_id = cur.lastrowid
    cur.close()

    return jsonify({"message": "Booking created successfully", "booking_id": booking_id}), 201

@app.route("/bookings", methods=["GET"])
def view_bookings():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bookings")
    bookings = cur.fetchall()
    cur.close()

    result = []
    for booking in bookings:
        result.append({
            "id": booking[0],
            "user_name": booking[1],
            "contact": booking[2],
            "license_info": booking[3],
            "car_id": booking[4],
            "pickup_date": booking[5].isoformat(),
            "return_date": booking[6].isoformat(),
            "pickup_location": booking[7],
            "dropoff_location": booking[8],
            "addons": json.loads(booking[9]) if booking[9] else [],
            "driver_option": booking[10],
            "payment_method": booking[11],
            "total_cost": float(booking[12]),
            "deposit_amount": float(booking[13]),
            "coupon_code": booking[14],
            "status": booking[15],
            "created_at": booking[16].isoformat()
        })
    return jsonify(result), 200

@app.route("/bookings/<int:booking_id>", methods=["GET"])
def view_booking(booking_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
    booking = cur.fetchone()
    cur.close()

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    result = {
        "id": booking[0],
        "user_name": booking[1],
        "contact": booking[2],
        "license_info": booking[3],
        "car_id": booking[4],
        "pickup_date": booking[5].isoformat(),
        "return_date": booking[6].isoformat(),
        "pickup_location": booking[7],
        "dropoff_location": booking[8],
        "addons": json.loads(booking[9]) if booking[9] else [],
        "driver_option": booking[10],
        "payment_method": booking[11],
        "total_cost": float(booking[12]),
        "deposit_amount": float(booking[13]),
        "coupon_code": booking[14],
        "status": booking[15],
        "created_at": booking[16].isoformat()
    }
    return jsonify(result), 200

@app.route("/bookings/<int:booking_id>", methods=["PATCH"])
def update_booking_status(booking_id):
    data = request.get_json()
    new_status = data.get("status")

    if not new_status:
        return jsonify({"error": "Status field is required"}), 400

    cur = mysql.connection.cursor()
    cur.execute("UPDATE bookings SET status = %s WHERE id = %s", (new_status, booking_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Booking status updated successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)
