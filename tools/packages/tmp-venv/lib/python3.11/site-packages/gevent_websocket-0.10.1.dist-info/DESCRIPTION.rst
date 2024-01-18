   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Download-URL: https://www.gitlab.com/noppo/gevent-websocket
Description: ================
        gevent-websocket
        ================
        
        `gevent-websocket`_ is a WebSocket library for the gevent_ networking library.
        
        Features include:
        
        - Integration on both socket level or using an abstract interface.
        - RPC and PubSub framework using `WAMP`_ (WebSocket Application
          Messaging Protocol).
        - Easily extendible using a simple WebSocket protocol plugin API
        
        
        ::
        
            from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
        
            class EchoApplication(WebSocketApplication):
                def on_open(self):
                    print "Connection opened"
        
                def on_message(self, message):
                    self.ws.send(message)
        
                def on_close(self, reason):
                    print reason
        
            WebSocketServer(
                ('', 8000),
                Resource({'/': EchoApplication})
            ).serve_forever()
        
        or a low level implementation::
        
            from gevent import pywsgi
            from geventwebsocket.handler import WebSocketHandler
        
            def websocket_app(environ, start_response):
                if environ["PATH_INFO"] == '/echo':
                    ws = environ["wsgi.websocket"]
                    message = ws.receive()
                    ws.send(message)
        
            server = pywsgi.WSGIServer(("", 8000), websocket_app,
                handler_class=WebSocketHandler)
            server.serve_forever()
        
        More examples can be found in the ``examples`` directory. Hopefully more
        documentation will be available soon.
        
        Installation
        ------------
        
        The easiest way to install gevent-websocket is directly from PyPi_ using pip or
        setuptools by running the commands below::
        
            $ pip install gevent-websocket
        
        
        Gunicorn Worker
        ^^^^^^^^^^^^^^^
        
        Using Gunicorn it is even more easy to start a server. Only the
        `websocket_app` from the previous example is required to start the server.
        Start Gunicorn using the following command and worker class to enable WebSocket
        funtionality for the application.
        
        ::
        
            gunicorn -k "geventwebsocket.gunicorn.workers.GeventWebSocketWorker" wsgi:websocket_app
        
        Performance
        ^^^^^^^^^^^
        
        `gevent-websocket`_ is pretty fast, but can be accelerated further by
        installing `wsaccel <https://github.com/methane/wsaccel>`_ and `ujson` or `simplejson`::
        
            $ pip install wsaccel ujson
        
        `gevent-websocket`_ automatically detects ``wsaccell`` and uses the Cython
        implementation for UTF8 validation and later also frame masking and
        demasking.
        
        Get in touch
        ^^^^^^^^^^^^
        
        Get in touch on IRC #gevent on Freenode or on the Gevent `mailinglist
        <https://groups.google.com/forum/#!forum/gevent>`_. Issues can be created
        on `Bitbucket <https://bitbucket.org/Jeffrey/gevent-websocket/issues?status=new&status=open>`_.
        
        .. _WAMP: http://www.wamp.ws
        .. _gevent-websocket: http://www.bitbucket.org/Jeffrey/gevent-websocket/
        .. _gevent: http://www.gevent.org/
        .. _Jeffrey Gelens: http://www.gelens.org/
        .. _PyPi: http://pypi.python.org/pypi/gevent-websocket/
        .. _repository: http://www.bitbucket.org/Jeffrey/gevent-websocket/
        .. _RFC6455: http://datatracker.ietf.org/doc/rfc6455/?include_text=1
        
Platform: UNKNOWN
Classifier: Environment :: Web Environment
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: Apache Software License
Classifier: Operating System :: MacOS :: MacOS X
Classifier: Operating System :: POSIX
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.5
Classifier: Topic :: Internet
Classifier: Topic :: Software Development :: Libraries :: Python Modules
