# This file is part of visier-connector-python.
#
# visier-connector-python is free software: you can redistribute it and/or modify
# it under the terms of the Apache License, Version 2.0 (the "License").
#
# visier-connector-python is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License, Version 2.0 for more details.
#
# You should have received a copy of the Apache License, Version 2.0
# along with visier-connector-python. If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""
Visier Public Python Connector OAuth2 Callback
"""

import threading
from flask import Flask, request
from werkzeug.serving import make_server
from queue import Queue

class CallbackServer:
    """Callback server that listens for the OAuth2 authorization code"""
    def __init__(self):
        self.host = 'localhost'
        self.port = 5000
        self.server = None
        self.flask_thread = None
        self.app = Flask(__name__)
        self.app.route('/oauth2/callback', methods=['GET'])(self.callback)
        self.queue = Queue()

    def callback(self):
        code = request.args.get('code')
        self.queue.put(code)
        return '<p>You can now close this window</p>'
    
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, ex_type, ex_value, trace_back):
        self.stop()
    
    def start(self):
        self.server = make_server(self.host, self.port, self.app)
        self.flask_thread = threading.Thread(target=self.server.serve_forever)
        self.flask_thread.start()

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.flask_thread.join()
            self.server = None
            self.flask_thread = None