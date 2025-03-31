from marshmallow import Schema, fields


class TaskSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str()
    dueDate = fields.Str(required=True)


task_validation = TaskSchema()