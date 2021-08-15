from flask import Blueprint, jsonify, request
from . import db
from .models import Song

main = Blueprint('main', __name__)

@main.route('/add_song', methods=['POST'])
def add_song():
    song_data = request.get_json()
    new_song = Song(title=song_data['title'], rating=song_data['rating'])
    db.session.add(new_song)
    db.session.commit()
    return 'done', 201

@main.route('/songs', methods=['GET'])
def songs():
    song_list = Song.query.all()
    songs = []
    for song in song_list:
        Song.append({'title': song.title, 'rating': song.rating})
    return jsonify({'songs': songs})