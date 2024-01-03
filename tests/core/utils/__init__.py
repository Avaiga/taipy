# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.


def assert_true_after_time(assertion, msg=None, time=120):
    from datetime import datetime
    from time import sleep

    loops = 0
    start = datetime.now()
    while (datetime.now() - start).seconds < time:
        sleep(1)  # Limit CPU usage
        try:
            if assertion():
                return
        except BaseException as e:
            print("Raise : ", e)
            loops += 1
            continue
    if msg:
        print(msg)
    assert assertion()
