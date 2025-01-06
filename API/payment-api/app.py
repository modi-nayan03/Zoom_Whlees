from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client.authentication_db  # Replace with your MongoDB database name
payments_collection = db.payments  # MongoDB collection for payments

# Endpoint to get all payments
@app.route('/api/payments', methods=['GET'])
def get_payments():
    # Retrieve all payment records from the MongoDB collection
    payments = list(payments_collection.find({}, {'_id': 0}))  # Excluding _id from result
    return jsonify(payments)

# Endpoint to create a payment
@app.route('/api/payment', methods=['POST'])
def create_payment():
    data = request.get_json()
    amount = data.get('amount')
    
    if amount is None:
        return jsonify({"error": "Amount is required"}), 400
    
    # Create a new payment record in MongoDB
    new_payment = {
        "amount": amount,
        "status": "Completed"
    }
    result = payments_collection.insert_one(new_payment)
    
    # Retrieve the newly created payment
    payment = payments_collection.find_one({"_id": result.inserted_id}, {'_id': 0})
    
    return jsonify(payment), 201

# Endpoint to get a specific payment by ID
@app.route('/api/payment/<payment_id>', methods=['GET'])
def get_payment(payment_id):
    try:
        # Retrieve payment by ObjectId
        payment = payments_collection.find_one({"_id": ObjectId(payment_id)}, {'_id': 0})
        
        if payment is None:
            return jsonify({'error': 'Payment not found'}), 404
        return jsonify(payment)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
