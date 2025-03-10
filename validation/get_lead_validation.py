from marshmallow import Schema, fields


class GetLeadByEmailSchema(Schema):
    email = fields.Email(required=True)


get_lead_by_email_schema = GetLeadByEmailSchema()
