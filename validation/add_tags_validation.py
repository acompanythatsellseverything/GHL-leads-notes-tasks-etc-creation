from marshmallow import Schema, fields

class AddTagsSchema(Schema):
    tags = fields.List(fields.Str())


tags_validation = AddTagsSchema()
