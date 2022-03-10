import sys
import threading


class _KillableThread(threading.Thread):  # pragma: no cover
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
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        return self.localtrace if why == "call" else None

    def localtrace(self, frame, why, arg):
        if self.killed and why == "line":
            raise SystemExit(0)
        return self.localtrace

    def kill(self):
        self.killed = True
