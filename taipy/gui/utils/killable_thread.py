import sys
import threading


class _KillableThread(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup  # pragma: no cover

    def globaltrace(self, frame, why, arg):
        return self.localtrace if why == "call" else None  # pragma: no cover

    def localtrace(self, frame, why, arg):  # pragma: no cover
        if self.killed and why == "line":
            raise SystemExit(0)
        return self.localtrace

    def kill(self):
        self.killed = True
