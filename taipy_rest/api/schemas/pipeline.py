from marshmallow import Schema, fields


class PipelineSchema(Schema):
    name = fields.String()
    parent_id = fields.String()
    task_ids = fields.List(fields.String)
    properties = fields.Dict()


class PipelineResponseSchema(PipelineSchema):
    id = fields.String()
    source_task_edges = fields.Dict()
    task_source_edges = fields.Dict()
    subscribers = fields.List(fields.Dict)
