import sys
import uuid
from itertools import count
from typing import List

from taipy.data.data_source import CSVDataSource, DataSource, EmbeddedDataSource
from taipy.data.data_source.models import DataSourceModel, Scope

"""
A Data Manager is entity responsible for keeping track and retrieving Taipy DataSources. The Data Manager will
facilitate data access between Taipy Modules.
"""


class DataManager:
    # This represents a database table that maintains our DataSource References.
    __DATA_SOURCE_DB: List[DataSourceModel] = []

    def create_data_source(
        self, id: str, name: str, data_source_class: str, properties: dict
    ):
        self.__DATA_SOURCE_DB.append(
            DataSourceModel(
                id,
                name,
                Scope.SCENARIO,
                data_source_class,
                properties,
            )
        )

    def fetch_data_source(self, id):
        data_source = None

        for ds in self.__DATA_SOURCE_DB:
            # Not sure if we need to handle missing DataSource here or in the function that
            # calls fetch_data_source. Something to consider in the near future.
            if ds.id == id:
                data_source_class = getattr(
                    sys.modules[__name__], ds.implementation_class_name
                )
                data_source = data_source_class(
                    ds.id, ds.name, ds.scope, ds.data_source_properties
                )
                break

        return data_source
