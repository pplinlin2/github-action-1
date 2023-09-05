from flask import Flask, request, jsonify, g
from flask_cors import CORS
from pymongo import MongoClient
import uuid
import jwt
import datetime
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'devops_in_a_nutshell'
CORS(app)

# Connect to MongoDB
client = MongoClient('mongodb://mongodb:27017/')
db = client['movie_database']
movies_collection = db['movies']

# Simulated user database
users = {
    'admin': {'password': 'qwerty', 'role': 'admin'},
    'user1': {'password': 'qwerty', 'role': 'user'},
    'user2': {'password': 'qwerty', 'role': 'user'}
}

# Custom wrapper to check user role
def role_check(allowed_roles):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token or not token.startswith('Bearer '):
                return jsonify({'error': 'Bearer token missing'}), 401
            token = token.split('Bearer ')[1]

            try:
                payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                g.user = payload
                role = payload['role']
                if role in allowed_roles:
                    return func(*args, **kwargs)
                else:
                    return jsonify({'error': 'Forbidden'}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
        return wrapper
    return decorator

# Login route to get JWT token
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = users.get(username)
    if user and user['password'] == password:
        token_body = {
            'username': username,
            'role': users[username]['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(token_body, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    
    return jsonify({'error': 'Invalid credentials'}), 401

# Create a new movie
@app.route('/movies', methods=['POST'])
@role_check(allowed_roles=['admin'])
def create_movie():
    data = request.json
    movie_id = str(uuid.uuid4())
    data['_id'] = movie_id  # Adding the ID to the data before insertion
    movies_collection.insert_one(data)
    return jsonify({'message': 'Movie created', 'id': movie_id}), 201

# Get all movies
@app.route('/movies', methods=['GET'])
def get_movies():
    movies = list(movies_collection.find())
    return jsonify(movies)

# Get a specific movie
@app.route('/movies/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = movies_collection.find_one({'_id': movie_id})
    if movie:
        return jsonify(movie)
    return jsonify({'error': 'Movie not found'}), 404

# Update a movie
@app.route('/movies/<string:movie_id>', methods=['PUT'])
@role_check(allowed_roles=['admin'])
def update_movie(movie_id):
    data = request.json
    if movies_collection.find_one({'_id': movie_id}):
        data['_id'] = movie_id  # Ensure the ID is present in the data
        movies_collection.replace_one({'_id': movie_id}, data)
        return jsonify({'message': 'Movie updated'})
    return jsonify({'error': 'Movie not found'}), 404

# Partial update of a movie (PATCH)
@app.route('/movies/<string:movie_id>', methods=['PATCH'])
@role_check(allowed_roles=['admin'])
def patch_movie(movie_id):
    data = request.json
    if movies_collection.find_one({'_id': movie_id}):
        movies_collection.update_one({'_id': movie_id}, {'$set': data})
        return jsonify({'message': 'Movie patched'})
    return jsonify({'error': 'Movie not found'}), 404

# Delete a movie
@app.route('/movies/<string:movie_id>', methods=['DELETE'])
@role_check(allowed_roles=['admin'])
def delete_movie(movie_id):
    if movies_collection.find_one({'_id': movie_id}):
        movies_collection.delete_one({'_id': movie_id})
        return jsonify({'message': 'Movie deleted'})
    return jsonify({'error': 'Movie not found'}), 404
