from sqlalchemy.exc import IntegrityError
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc
from aes import aes_decrypt, aes_encrypt
from my_jwt import decode_token_jwt, generate_token_jwt
import re


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456789@localhost/db_users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db) 


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    job = db.Column(db.String(25), nullable=False)
    

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        # Validate email format using a regular expression
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'status': 'error', 'code': 400, 'message': 'Invalid email format'}), 400
        
        user = Users.query.filter_by(email=email).first()
        print(aes_decrypt(user.password))
        
        if user:
            if aes_decrypt(user.password) == password:
                token = generate_token_jwt(user.id)
                
                return jsonify({'status': 'success','code': 200, "id": user.id, 'message': 'Login successful, you have entered', 'token': token}), 200
            else:
                 return jsonify({'status': 'error','code': 401, 'message': 'Password incorect'}), 401
        else:
            return jsonify({'status': 'error','code': 401, 'message': 'Email incorect'}), 401

    except SQLAlchemyError as e:
        print(f"error at login: {str(e)}")
        return jsonify({'status': 'error', 'code': 500, 'message': 'Login failed'}), 500


@app.route('/api/createUser', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        email = data['email']
        
        # Validate email format using a regular expression
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'status': 'error', 'code': 400, 'message': 'Invalid email format'}), 400
        
        user = Users(
            email=data['email'],
            password=aes_encrypt(data['password']),
            full_name=data['full_name'],
            job=data['job'],
         
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'status': 'success', 'code': 201, 'message': 'User has been created'}), 201

    except IntegrityError as e:
        db.session.rollback()
        print(f"error at create_user: {str(e)}")
        return jsonify({'status': 'error','code': 400, 'message': 'Email already exists'}), 400


@app.route('/api/getAllUsers', methods=['GET'])
def get_all_users():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'status': 'error', 'code': 401, 'message': 'Authorization token is required'}), 401

        payload = decode_token_jwt(token)
        if not payload:
            return jsonify({'status': 'error', 'code': 401, 'message': 'Authorization token incorect or expired'}), 401
        
        
        users = Users.query.order_by(asc(Users.id)).all()
        user_list = []

        for user in users:
            user_data = {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'job': user.job
            }
            user_list.append(user_data)

        return jsonify({'status': 'success', 'code': 200, 'data': user_list}), 200

    except SQLAlchemyError as e:
        print(f"error at get_all_users: {str(e)}")
        return jsonify({'status': 'error', 'code': 500, 'message': 'Failed to get all users'}), 500


@app.route('/api/getUser', methods=['GET'])
def get_user_by_id():
    try:
        user_id = request.args.get('id', type=int)
        
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'status': 'error', 'code': 401, 'message': 'Authorization token is required'}), 401

        payload = decode_token_jwt(token)
        if not payload:
            return jsonify({'status': 'error', 'code': 401, 'message': 'Authorization token incorect or expired'}), 401
        
        user = Users.query.get(user_id)

        if user:
            user_data = {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'job': user.job
            }
            return jsonify({'status': 'success', 'code': 200, 'data': user_data}), 200
        else:
            return jsonify({'status': 'error', 'code': 404, 'message': 'User not exist'}), 404

    except SQLAlchemyError as e:
        print(f"error at get_user_by_id: {str(e)}")
        return jsonify({'status': 'error', 'code': 500, 'message': 'Failed to retrieve user'}), 500


@app.route('/api/updateUser', methods=['PUT'])
def update_user():
    try:
        user_id = request.args.get('id', type=int)
        
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'status': 'error', 'code': 401, 'message': 'Authorization token is required'}), 401

        payload = decode_token_jwt(token)
        if not payload:
            return jsonify({'status': 'error', 'code': 401, 'message': 'Authorization token incorect or expired'}), 401

        # Proceed with updating the user (modify as needed)
        user = Users.query.get(user_id)
        if user:
            data = request.get_json()
            user.full_name = data.get('full_name', user.full_name)
            user.job = data.get('job', user.job)
            new_password = data['password']

            # Use a secure password hashing function (replace with your preferred method)
            new_password_encrypt = aes_encrypt(new_password)
            user.password = new_password_encrypt
        
            db.session.commit()
            return jsonify({'status': 'success', 'code': 200, 'message': 'User has updated'}), 200
        else:
            return jsonify({'status': 'error', 'code': 404, 'message': 'User not found'}), 404


    except SQLAlchemyError as e:
        print(f"error at update_user: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'code': 500, 'message': 'Failed to update user'}), 500


@app.route('/api/deleteUser', methods=['DELETE'])
def delete_user():
    try:
        user_id = request.args.get('id', type=int)
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'status': 'error', 'code': 401, 'message': 'Authorization token is required'}), 401

        # Decode and verify the token
        payload = decode_token_jwt(token)
        if not payload:
            return jsonify({'status': 'error', 'code': 401, 'message': 'Authorization token incorect or expired'}), 401

        # Proceed with deleting the user (modify as needed)
        user = Users.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'status': 'success', 'code': 200,  'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'status': 'error', 'code': 404, 'message': 'User not found'}), 404

    except SQLAlchemyError as e:
        # Log the detailed error for debugging purposes
        print(f"error at delete_user: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'code': 500, 'message': 'Failed to delete user'}), 500
    
    
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)