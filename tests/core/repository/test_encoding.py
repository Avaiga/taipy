# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import taipy.core.taipy as tp
from taipy.core.config import Config


def test_no_special_characters():
    scenario_config = Config.configure_scenario("scenario_1")

    scenario = tp.create_scenario(scenario_config, name="martin")
    assert scenario.name == "martin"
    scenarios = tp.get_scenarios()
    assert len(scenarios) == 1
    assert scenarios[0].name == "martin"


def test_many_special_characters():
    scenario_config = Config.configure_scenario("scenario_1")

    special_characters = (
        "!#$%&'()*+,-./:;<=>?@[]^_`\\{"
        "|}~¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º"
        "»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ"
        "×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñò"
        "óôõö÷øùúûüýþÿĀāĂăĄąĆćĈĉĊċČčĎ"
        "ďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪ"
        "īĬĭĮįİĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇ"
        "ňŉŊŋŌōŎŏŐőŒœŔŕŖŗŘřŚśŜŝŞşŠšŢţ"
        "ŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽžſ"
    )

    scenario = tp.create_scenario(scenario_config, name=special_characters)
    assert scenario.name == special_characters
    scenarios = tp.get_scenarios()
    assert len(scenarios) == 1
    assert scenarios[0].name == special_characters
