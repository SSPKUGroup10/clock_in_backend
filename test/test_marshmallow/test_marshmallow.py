from datetime import date
from marshmallow import Schema, fields, pprint


class ArtistSchema(Schema):
    a = fields.Str()
    b = fields.Str()


class AlbumSchema(Schema):
    titlex = fields.Str(attribute="TITLE")
    release_date = fields.Date()
    artist = fields.Nested(ArtistSchema())
    a = fields.Int()

bowie = dict(name='David Bowie')
# date(1971, 12, 17)
album = dict(artist=bowie, TITLE='Hunky Dory', release_date="1997-12-17", a=1)

schema = AlbumSchema()
result = schema.dump(album)
pprint(result, indent=2)