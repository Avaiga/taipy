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
    """Abstract base class for implementing a Core event consumer.

    This class provides a framework for consuming events from a queue in a separate thread.
    It should be subclassed, and the `process_event` method should be implemented to define
    the custom logic for handling incoming events.

    Example usage:

    ```python
    class MyEventConsumer(CoreEventConsumerBase):
        def process_event(self, event: Event):
            # Custom event processing logic here
            print(f"Received event created at : {event.creation_date}")
            pass

    consumer = MyEventConsumer("consumer_1", event_queue)
    consumer.start()
    # ...
    consumer.stop()
    ```

    Subclasses should implement the `process_event` method to define their specific event handling behavior.

    Attributes:
        queue (SimpleQueue): The queue from which events will be consumed.


    """

    def __init__(self, registration_id: str, queue: SimpleQueue):
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

    def start(self):
        """Start the event consumer thread."""
        self.__STOP_FLAG = False
        threading.Thread.start(self)

    def stop(self):
        """Stop the event consumer thread."""
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
        """This method should be overridden in subclasses to define how events are processed."""
        raise NotImplementedError
