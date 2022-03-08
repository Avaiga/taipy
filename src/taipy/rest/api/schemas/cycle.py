from marshmallow import Schema, fields


class CycleSchema(Schema):
    name = fields.String()
    frequency = fields.String()
    properties = fields.Dict()
    creation_date = fields.String()
    start_date = fields.String()
    end_date = fields.String()


class CycleResponseSchema(CycleSchema):
    id = fields.String()
