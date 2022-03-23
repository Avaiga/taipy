from marshmallow import Schema, fields


class ScenarioSchema(Schema):
    pipelines = fields.List(fields.String)
    properties = fields.Dict()
    primary_scenario = fields.Boolean(default=False)
    tags = fields.List(fields.String)


class ScenarioResponseSchema(ScenarioSchema):
    id = fields.String()
    subscribers = fields.List(fields.Dict)
    cycle = fields.String()
    creation_date = fields.String()
