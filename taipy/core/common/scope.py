from taipy.common._repr_enum import _OrderedEnum


class Scope(_OrderedEnum):
    """Scope of a `DataNodeConfig^` or a `DataNode^`.

    This enumeration can have the following values:

    - `GLOBAL`: Global scope, the data node is shared by all the scenarios.
    - `CYCLE`: Cycle scope, the data node is shared by all the scenarios of the same cycle.
    - `SCENARIO` (Default value): Scenario scope, the data node is unique to a scenario.

    Each data node config has a scope. It is an attribute propagated to the `DataNode^`
    when instantiated from a `DataNodeConfig^`. The scope is used to determine the
    _visibility_ of the data node, and which scenarios can access it.

    In other words :

    - There can be only one data node instantiated from a `DataNodeConfig^` with a `GLOBAL`
        scope. All the scenarios share the unique data node. When a new scenario is created,
        the data node is also created if and only if it does not exist yet.
    - Only one data node instantiated from a `DataNodeConfig^` with a `CYCLE` scope is
        created for each cycle. All the scenarios of the same cycle share the same data node.
        When a new scenario is created within a cycle, Taipy instantiates a new data node if
        and only if there is no data node for the cycle yet.
    - A data node that has the scope set to `SCENARIO` belongs to a unique scenario and cannot
        be used by others. When creating a new scenario, data nodes with a `SCENARIO` scope
        are systematically created along with the new scenario.

    !!! example

        Let's consider a simple example where a company wants to predict its sales for the next
        month. The company has a trained model that predicts the sales based on the current month
        and the historical sales. Based on the sales forecasts the company wants to plan its
        production orders. The company wants to simulate two scenarios every month: one with
        low capacity and one with high capacity.

        We can create the `DataNodeConfig^`s with the following scopes:

        - One data node for the historical sales with a `GLOBAL` scope.
        - Three data nodes with a `CYCLE` scope, for the trained model, the current month,
            and the sales predictions.
        - Two data nodes with a `SCENARIO` scope, for the capacity and the production orders.

        The code snippet below shows how to configure the data nodes with the different scopes:

        ```python
        from taipy import Config, Scope

        hist_cfg = Config.configure_csv_data_node("sales_history", scope=Scope.GLOBAL)
        model_cfg = Config.configure_data_node("trained_model", scope=Scope.CYCLE)
        month_cfg = Config.configure_data_node("current_month", scope=Scope.CYCLE)
        predictions_cfg = Config.configure_data_node("sales_predictions", scope=Scope.CYCLE)
        capacity_cfg = Config.configure_data_node("capacity", scope=Scope.SCENARIO)
        orders_cfg = Config.configure_sql_data_node("production_orders",
                                                    scope=Scope.SCENARIO,
                                                    db_name="taipy",
                                                    db_engine="sqlite",
                                                    table_name="sales")
        ```
    """

    GLOBAL = 3
    CYCLE = 2
    SCENARIO = 1

    @staticmethod
    def _type_identifier() -> str:
        """Return a string to identify the object type.

        The type identifier is used to identify the type of the value when serializing
        and deserializing the configuration. As a consequence, the identifier must be
        a unique string and must not change over time to ensure backward compatibility.
        """
        return "SCOPE"

    def _stringify(self) -> str:
        """Return a string representation of the object.

        The string representation is used to serialize the object. It must be a unique string
        that can be used to deserialize the object. The string representation must not change
        over time to ensure backward compatibility.
        """
        return f"{self.name}:{self._type_identifier()}"

    @classmethod
    def _pythonify(cls, value: str):
        return Scope[str.upper(value)]
