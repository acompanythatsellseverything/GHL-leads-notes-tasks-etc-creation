from marshmallow import Schema, fields


class AddressSchema(Schema):
    city = fields.Str()
    state = fields.Str()


class EmailSchema(Schema):
    value = fields.Email(required=True)


class PhoneSchema(Schema):
    value = fields.Str(required=True)


class PersonSchema(Schema):
    id = fields.Int()
    firstName = fields.Str(required=True)
    lastName = fields.Str(required=True)
    addresses = fields.List(fields.Nested(AddressSchema))
    customMLSNumber = fields.Str()
    customListingType = fields.Str()
    customAddress = fields.Str()
    customCity = fields.Str()
    customProvince = fields.Str()
    customFB4SLeadID = fields.Str()
    customFB4SRCAURL = fields.Url()
    customListingURL = fields.Url()
    customParentCategory = fields.Str()
    customAbandonedPondReason = fields.Str()
    customChromeExtensionLink = fields.Url()
    customFB4SInquiriesCounter = fields.Int()
    customBuyerProfileFB4S = fields.Url()
    customAssignedNotFromWillowAt = fields.Str()
    emails = fields.List(fields.Nested(EmailSchema), required=True)
    phones = fields.List(fields.Nested(PhoneSchema), required=True)
    tags = fields.List(fields.Str())


class PropertySchema(Schema):
    street = fields.Str()
    city = fields.Str()
    state = fields.Str()
    code = fields.Str()
    mlsNumber = fields.Str()
    url = fields.Url()


class PostLeadSchema(Schema):
    person = fields.Nested(PersonSchema, required=True)
    property = fields.Nested(PropertySchema, required=True)
    type = fields.Str(required=True)
    source = fields.Str()
    system = fields.Str()
    description = fields.Str()
    message = fields.Str()


post_lead_schema = PostLeadSchema()
