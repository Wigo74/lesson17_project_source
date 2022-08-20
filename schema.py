from marshmallow import Schema, fields


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    # genre = fields.Int()
    director_id = fields.Int()
    # director = fields.Str()


class Director(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class Genre(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
