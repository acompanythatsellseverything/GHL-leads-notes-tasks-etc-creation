from marshmallow import Schema, fields


class AddressSchema(Schema):
    city = fields.Str()
    state = fields.Str()


class EmailSchema(Schema):
    value = fields.Email()


class PhoneSchema(Schema):
    value = fields.Str()


class PersonSchema(Schema):
    id = fields.Int()
    firstName = fields.Str()
    lastName = fields.Str()
    assignedUserId = fields.Str()
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
    customExpectedPriceRange = fields.Str()
    customListingURLPath = fields.Str()
    customAssignedNotFromWillowAt = fields.Str()
    emails = fields.List(fields.Nested(EmailSchema))
    phones = fields.List(fields.Nested(PhoneSchema))
    tags = fields.List(fields.Str())


class UpdateLeadSchema(Schema):
    person = fields.Nested(PersonSchema, required=True)


update_lead_schema = UpdateLeadSchema()
