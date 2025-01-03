# Authentication API with MySQL Integration

from flask import Flask, request, jsonify
from bcrypt import hashpw, gensalt, checkpw
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

# Helper functions for password hashing
def hash_password(password):
    return hashpw(password.encode(), gensalt()).decode()

def verify_password(stored_password, provided_password):
    return checkpw(provided_password.encode(), stored_password.encode())

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    phone_no = data.get("phone_no")
    password = data.get("password")
    
    if not username or not email or not phone_no or not password:
        return jsonify({"error": "All fields (username, email, phone number, password) are required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if the email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "User with this email already exists"}), 409
    
    # Insert the new user
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO users (username, email, phone_no, password) VALUES (%s, %s, %s, %s)",
                   (username, email, phone_no, hashed_password))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Retrieve user data
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401
    
    return jsonify({"message": f"Welcome, {user['username']}!"}), 200

@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("new_password")
    
    if not email or not new_password:
        return jsonify({"error": "Email and new password are required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if the user exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "User with this email not found"}), 404
    
    # Update the password
    hashed_password = hash_password(new_password)
    cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Password reset successfully"}), 200

@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all users
    cursor.execute("SELECT username, email, phone_no FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return jsonify(users), 200

if __name__ == "__main__":
    app.run(debug=True)
