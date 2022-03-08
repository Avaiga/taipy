from marshmallow import Schema, fields, pre_dump


class DataNodeSchema(Schema):

    config_id = fields.String()
    scope = fields.String()
    id = fields.String()
    name = fields.String()
    parent_id = fields.String()
    last_edition_date = fields.String()
    job_ids = fields.List(fields.String)
    validity_days = fields.Integer()
    validity_hours = fields.Integer()
    validity_minutes = fields.Integer()
    edition_in_progress = fields.Boolean()
    properties = fields.Dict()


class DataNodeConfigSchema(Schema):
    name = fields.String()
    storage_type = fields.String()
    scope = fields.Integer()

    @pre_dump
    def serialize_scope(self, obj, **kwargs):
        obj.scope = obj.scope.value
        return obj


class CSVDataNodeConfigSchema(DataNodeConfigSchema):
    path = fields.String()
    has_header = fields.Boolean()


class InMemoryDataNodeConfigSchema(DataNodeConfigSchema):
    default_data = fields.Inferred()


class PickleDataNodeConfigSchema(DataNodeConfigSchema):
    path = fields.String()
    default_data = fields.Inferred()


class SQLDataNodeConfigSchema(DataNodeConfigSchema):
    db_username = fields.String()
    db_password = fields.String()
    db_name = fields.String()
    db_engine = fields.String()
    read_query = fields.String()
    write_table = fields.String()


class OperatorSchema(Schema):
    key = fields.String()
    value = fields.Inferred()
    operator = fields.String()


class DataNodeFilterSchema(DataNodeConfigSchema):
    operators = fields.List(fields.Nested(OperatorSchema))
    join_operator = fields.String(default="AND")
