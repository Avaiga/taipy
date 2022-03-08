from marshmallow import Schema, fields


class CallableSchema(Schema):
    name = fields.String()
    module = fields.String()


class JobSchema(Schema):
    task_name = fields.String()
    callables = fields.Nested(CallableSchema)


class JobResponseSchema(JobSchema):
    id = fields.String()
