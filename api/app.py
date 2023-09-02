from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

# Preloaded list of movies
preloaded_movies = {
    str(uuid.uuid4()): {'title': 'Interstellar', 'genres': 'Sci-Fi'},
    str(uuid.uuid4()): {'title': 'Spider-Man', 'genres': 'Animation'},
    str(uuid.uuid4()): {'title': 'Oppenheimer', 'genres': 'Biography'},
}

# List to store movies
movies = preloaded_movies.copy()

# Create a new movie
@app.route('/movies', methods=['POST'])
def create_movie():
    data = request.json
    movie_id = str(uuid.uuid4())
    movies[movie_id] = data
    return jsonify({'message': 'Movie created', 'id': movie_id}), 201

# Get all movies
@app.route('/movies', methods=['GET'])
def get_movies():
    return jsonify(movies)

# Get a specific movie
@app.route('/movies/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    if movie_id in movies:
        return jsonify(movies[movie_id])
    return jsonify({'error': 'Movie not found'}), 404

# Update a movie
@app.route('/movies/<string:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    data = request.json
    if movie_id in movies:
        movies[movie_id] = data
        return jsonify({'message': 'Movie updated'})
    return jsonify({'error': 'Movie not found'}), 404

# Partial update of a movie (PATCH)
@app.route('/movies/<string:movie_id>', methods=['PATCH'])
def patch_movie(movie_id):
    data = request.json
    if movie_id in movies:
        movies[movie_id].update(data)
        return jsonify({'message': 'Movie patched'})
    return jsonify({'error': 'Movie not found'}), 404

# Delete a movie
@app.route('/movies/<string:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    if movie_id in movies:
        del movies[movie_id]
        return jsonify({'message': 'Movie deleted'})
    return jsonify({'error': 'Movie not found'}), 404
