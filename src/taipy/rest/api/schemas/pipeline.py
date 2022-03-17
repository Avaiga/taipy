from marshmallow import Schema, fields


class PipelineSchema(Schema):
    config_id = fields.String()
    parent_id = fields.String()
    tasks = fields.List(fields.String)
    properties = fields.Dict()


class PipelineResponseSchema(PipelineSchema):
    id = fields.String()
    subscribers = fields.List(fields.Dict)
