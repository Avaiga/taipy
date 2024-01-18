from geventwebsocket.handler import WebSocketHandler
from gunicorn.workers.ggevent import GeventPyWSGIWorker


class GeventWebSocketWorker(GeventPyWSGIWorker):
    wsgi_handler = WebSocketHandler
