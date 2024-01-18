from __future__ import absolute_import

from logging import getLogger, StreamHandler, getLoggerClass, Formatter, DEBUG


def create_logger(name, debug=False, format=None):
        Logger = getLoggerClass()

        class DebugLogger(Logger):
            def getEffectiveLevel(x):
                if x.level == 0 and debug:
                    return DEBUG
                else:
                    return Logger.getEffectiveLevel(x)

        class DebugHandler(StreamHandler):
            def emit(x, record):
                StreamHandler.emit(x, record) if debug else None

        handler = DebugHandler()
        handler.setLevel(DEBUG)

        if format:
            handler.setFormatter(Formatter(format))

        logger = getLogger(name)
        del logger.handlers[:]
        logger.__class__ = DebugLogger
        logger.addHandler(handler)

        return logger
