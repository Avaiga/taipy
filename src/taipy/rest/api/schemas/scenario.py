from marshmallow import Schema, fields


class ScenarioSchema(Schema):
    name = fields.String()
    pipeline_ids = fields.List(fields.String)
    properties = fields.Dict()
    master_scenario = fields.Boolean(default=False)


class ScenarioResponseSchema(ScenarioSchema):
    id = fields.String()
    subscribers = fields.List(fields.Dict)
    cycle = fields.String()
