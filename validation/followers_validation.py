from marshmallow import Schema, fields

class FollowersSchema(Schema):
    followers = fields.List(
        fields.Str(),
        required=True,
    )


followers_schema = FollowersSchema()