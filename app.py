# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

import schema
from schema import MovieSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('director')
genre_ns = api.namespace('genre')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()

directors_schema = schema.Director(many=True)
director_schema = schema.Director()

genres_schema = schema.Genre(many=True)
genre_schema = schema.Genre()


@movie_ns.route("/")
class MoviesView(Resource):
    @movie_ns.response(201, description='Возвращает все фильмы или по ID режиссера или по ID жанра или по обоим ID')
    def get(self):
        movies_query = db.session.query(Movie)
        args = request.args
        director_id = args.get('director_id')
        if director_id is not None:
            movies_query = movies_query.filter(Movie.director_id == director_id)
        genre_id = args.get('genre_id')
        if genre_id is not None:
            movies_query = movies_query.filter(Movie.genre_id == genre_id)
        movies = movies_query.all()
        return movies_schema.dumps(movies)

    @movie_ns.response(201, description='Добавляет кино в фильмотеку')
    def post(self):
        movie = movie_schema.load(request.json)
        db.session.add(Movie(**movie))
        db.session.commit()
        return None, 201


@movie_ns.route("/<int:bid>")
class MovieView(Resource):
    @movie_ns.response(200, description='Возвращает фильм по его ID')
    @movie_ns.response(404, description='Фильм не найден')
    def get(self, bid: int):
        movie = db.session.query(Movie).get(bid)
        if not movie:
            return "", 400

        return movie_schema.dump(movie), 200

    @movie_ns.response(204, description='Перезаписывает значения по ID фильма')
    def put(self, bid: int):
        db.session.query(Movie).filter(Movie.id == bid).update(request.json)
        db.session.commit()
        return None, 204

    @movie_ns.response(204, description='Удаляет по ID фильма')
    def delete (self, bid: int):
        db.session.query(Movie).filter(Movie.id == bid).delete()
        db.session.commit()
        return None, 204



@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(Director).all()
        return directors_schema.dump(directors)


@director_ns.route("/<int:director_id>")
class DirectorView(Resource):
    def get(self, director_id):
        director = db.session.query(Director).filter(Director.id == director_id).first()
        if not director:
            return "", 400

        return director_schema.dump(director), 200


@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        genres = db.session.query(Genre).all()
        return genres_schema.dump(genres)


@genre_ns.route("/<int:genre_id>")
class GenreView(Resource):
    def get(self, genre_id):
        genre = db.session.query(Genre).filter(Genre.id == genre_id).first()
        if not genre:
            return "", 400

        return genre_schema.dump(genre), 200


if __name__ == '__main__':
    app.run(debug=True)
