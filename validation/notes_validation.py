from marshmallow import Schema, fields


class PropertySchema(Schema):
    street = fields.Str()
    city = fields.Str()
    state = fields.Str()
    code = fields.Str()
    mlsNumber = fields.Str()
    url = fields.Url()
    price = fields.Int()


class NotesSchema(Schema):
    property = fields.Nested(PropertySchema)
    type = fields.Str()
    source = fields.Str()
    system = fields.Str()
    description = fields.Str()
    message = fields.Str()


notes_validation = NotesSchema()