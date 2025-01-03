from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="authentication_db"
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS cars (
    car_id INT PRIMARY KEY AUTO_INCREMENT,
    make VARCHAR(50),
    model VARCHAR(50),
    year INT,
    vehicle_type VARCHAR(50),
    fuel_type VARCHAR(50),
    transmission_type VARCHAR(50),
    car_driven INT,
    registration_number VARCHAR(50),
    vin VARCHAR(50),
    insurance_details TEXT,
    pickup_location VARCHAR(100),
    daily_rental_price DECIMAL(10,2)
)
''')
conn.commit()

# Endpoint to add a new car
@app.route("/add-car", methods=["POST"])
def add_car():
    data = request.get_json()
    cursor.execute(
        '''INSERT INTO cars (make, model, year, vehicle_type, fuel_type, transmission_type, car_driven, 
        registration_number, vin, insurance_details, pickup_location, daily_rental_price) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
        (
            data["make"], data["model"], data["year"], data["vehicle_type"], data["fuel_type"],
            data["transmission_type"], data["car_driven"], data["registration_number"],
            data["vin"], data.get("insurance_details"), data["pickup_location"], data["daily_rental_price"]
        )
    )
    conn.commit()
    return jsonify({"message": "Car added successfully"}), 201

# Endpoint to retrieve all cars
@app.route("/cars", methods=["GET"])
def get_cars():
    cursor.execute("SELECT * FROM cars")
    cars = cursor.fetchall()
    car_list = [dict(zip([key[0] for key in cursor.description], car)) for car in cars]
    return jsonify(car_list), 200

# Endpoint to retrieve a specific car by ID
@app.route("/cars/<int:car_id>", methods=["GET"])
def get_car(car_id):
    cursor.execute("SELECT * FROM cars WHERE car_id = %s", (car_id,))
    car = cursor.fetchone()
    if not car:
        return jsonify({"error": "Car not found"}), 404
    car_data = dict(zip([key[0] for key in cursor.description], car))
    return jsonify(car_data), 200

# Endpoint to update car details
@app.route("/cars/<int:car_id>", methods=["PUT"])
def update_car(car_id):
    data = request.get_json()
    update_query = "UPDATE cars SET {} WHERE car_id = %s"
    update_data = [f"{key} = %s" for key in data.keys()]
    values = list(data.values()) + [car_id]
    cursor.execute(update_query.format(", ".join(update_data)), values)
    conn.commit()
    return jsonify({"message": "Car updated successfully"}), 200

# Endpoint to delete a car
@app.route("/cars/<int:car_id>", methods=["DELETE"])
def delete_car(car_id):
    cursor.execute("DELETE FROM cars WHERE car_id = %s", (car_id,))
    conn.commit()
    return jsonify({"message": "Car deleted successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)
