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

import abc
import threading
from queue import Empty, SimpleQueue

from .event import Event


class CoreEventConsumerBase(threading.Thread):
    """Abstract base class for implementing a Core event consumer.

    This class provides a framework for consuming events from a queue in a separate thread.
    It should be subclassed, and the `process_event` method should be implemented to define
    the custom logic for handling incoming events.

    ??? example "Basic usage"

        ```python
        class MyEventConsumer(CoreEventConsumerBase):
            def process_event(self, event: Event):
                # Custom event processing logic here
                print(f"Received event created at : {event.creation_date}")
                pass

        if __name__ == "__main__":
            registration_id, registered_queue = Notifier.register(
                entity_type=EventEntityType.SCENARIO,
                operation=EventOperation.CREATION
            )

            consumer = MyEventConsumer(registration_id, registered_queue)
            consumer.start()
            # ...
            consumer.stop()

            Notifier.unregister(registration_id)
        ```

        Firstly, we would create a consumer class extending from CoreEventConsumerBase
        and decide how to process the incoming events by defining the process_event.
        Then, we would specify the type of event we want to receive by registering with the Notifier.
        After that, we create an object of the consumer class by providing
        the registration_id and registered_queue and start consuming the event.
    """

    def __init__(self, registration_id: str, queue: SimpleQueue) -> None:
        """Initialize a CoreEventConsumerBase instance.

        Parameters:
            registration_id (str): A unique identifier of the registration. You can get a
                registration id invoking `Notifier.register()^` method.
            queue (SimpleQueue): The queue from which events will be consumed. You can get a
                queue invoking `Notifier.register()^` method.
        """
        threading.Thread.__init__(self, name=f"Thread-Taipy-Core-Consumer-{registration_id}")
        self.daemon = True
        self.queue = queue
        self.__STOP_FLAG = False
        self._TIMEOUT = 0.1

    def start(self) -> None:
        """Start the event consumer thread."""
        self.__STOP_FLAG = False
        threading.Thread.start(self)

    def stop(self) -> None:
        """Stop the event consumer thread."""
        self.__STOP_FLAG = True

    def run(self) -> None:
        while not self.__STOP_FLAG:
            try:
                event: Event = self.queue.get(block=True, timeout=self._TIMEOUT)
                self.process_event(event)
            except Empty:
                pass

    @abc.abstractmethod
    def process_event(self, event: Event) -> None:
        """This method should be overridden in subclasses to define how events are processed."""
        raise NotImplementedError
