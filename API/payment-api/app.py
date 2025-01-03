from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# MySQL connection setup
db_config = {
    "host": "localhost",
    "user": "root",  # Replace with your MySQL username
    "password": "",  # Replace with your MySQL password
    "database": "authentication_db"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Endpoint to get all payments
@app.route('/api/payments', methods=['GET'])
def get_payments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Retrieve all payment records
    cursor.execute("SELECT * FROM payments")
    payments = cursor.fetchall()
    
    conn.close()
    return jsonify(payments)

# Endpoint to create a payment
@app.route('/api/payment', methods=['POST'])
def create_payment():
    data = request.get_json()
    amount = data.get('amount')
    
    if amount is None:
        return jsonify({"error": "Amount is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Insert a new payment record
    cursor.execute("INSERT INTO payments (amount, status) VALUES (%s, %s)", (amount, "Completed"))
    conn.commit()
    payment_id = cursor.lastrowid
    
    # Retrieve the newly created payment
    cursor.execute("SELECT * FROM payments WHERE id = %s", (payment_id,))
    new_payment = cursor.fetchone()
    
    conn.close()
    return jsonify(new_payment), 201

# Endpoint to get a specific payment by ID
@app.route('/api/payment/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Retrieve payment by ID
    cursor.execute("SELECT * FROM payments WHERE id = %s", (payment_id,))
    payment = cursor.fetchone()
    
    conn.close()
    if payment is None:
        return jsonify({'error': 'Payment not found'}), 404
    return jsonify(payment)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
