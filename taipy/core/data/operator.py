from enum import Enum


class Operator(Enum):
    """
    Enumeration of operators for Data Node filtering. The possible values are `EQUAL`, `NOT_EQUAL`, `LESS_THAN`,
    `LESS_OR_EQUAL`, `GREATER_THAN`, `GREATER_OR_EQUAL`.
    """

    EQUAL = 1
    NOT_EQUAL = 2
    LESS_THAN = 3
    LESS_OR_EQUAL = 4
    GREATER_THAN = 5
    GREATER_OR_EQUAL = 6


class JoinOperator(Enum):
    """
    Enumeration of join operators for Data Node filtering. The possible values are `AND` and `OR`.
    """

    AND = 1
    OR = 2
