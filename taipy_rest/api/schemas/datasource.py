from marshmallow import Schema, fields


class DataSourceSchema(Schema):

    config_name = fields.String()
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


class DataSourceConfigSchema(Schema):
    name = fields.String()
    storage_type = fields.String()
    scope = fields.Integer()


class CSVDataSourceConfigSchema(DataSourceConfigSchema):
    path = fields.String()
    has_header = fields.Boolean()


class InMemoryDataSourceConfigSchema(DataSourceConfigSchema):
    default_data = fields.Inferred()


class PickleDataSourceConfigSchema(DataSourceConfigSchema):
    path = fields.String()
    default_data = fields.Inferred()


class SQLDataSourceConfigSchema(DataSourceConfigSchema):
    db_username = fields.String()
    db_password = fields.String()
    db_name = fields.String()
    db_engine = fields.String()
    read_query = fields.String()
    write_table = fields.String()
