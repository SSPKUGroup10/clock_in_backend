from datetime import date
from marshmallow import Schema, fields, pprint
from marshmallow.exceptions import ValidationError


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
album = dict(artist=bowie, TITLE='Hunky Dory', release_date=date(2019, 12, 2), a=1)

schema = AlbumSchema()
try:
    result = schema.dump(album)
    print(type(result))
    pprint(result, indent=2)
except Exception as e:
    print(e)