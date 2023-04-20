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

import abc
import threading
from queue import Empty, SimpleQueue

from .event import Event


class CoreEventConsumerBase(threading.Thread):
    """
    Abstract class showing an example on how to implement a Core event consumer.

    It can be used as a parent class so only the business logic has to be implemented in process_event method.

    """

    def __init__(self, registration_id: str, queue: SimpleQueue):
        threading.Thread.__init__(self, name=f"Thread-Taipy-Core-Consumer-{registration_id}")
        self.daemon = True
        self.queue = queue
        self.__STOP_FLAG = False

    def start(self):
        self.__STOP_FLAG = False
        threading.Thread.start(self)

    def stop(self):
        self.__STOP_FLAG = True

    def run(self):
        while not self.__STOP_FLAG:
            try:
                event: Event = self.queue.get(block=True, timeout=1)
                self.process_event(event)
            except Empty:
                pass

    @abc.abstractmethod
    def process_event(self, event: Event):
        raise NotImplementedError
