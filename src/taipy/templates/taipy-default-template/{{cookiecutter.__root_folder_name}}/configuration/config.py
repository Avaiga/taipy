"""
Contain the configuration of the application.

The configuration is run by the Core service.
"""

from taipy import Config

from ..algorithms import *

scenario_config = Config.configure_scenario("placeholder_scenario", [])
