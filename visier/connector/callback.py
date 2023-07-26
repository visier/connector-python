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
import dataclasses
from urllib.parse import urlparse
from queue import Queue
from flask import Flask, request
from werkzeug.serving import make_server

@dataclasses.dataclass
class CallbackBinding:
    """Callback binding definition"""
    def __init__(self, provided_url: str) -> None:
        result = urlparse(provided_url)
        self.host = result.hostname or "localhost"
        self.port = result.port or 5000
        self.path = result.path or "/oauth2/callback"

class CallbackServer:
    """Callback server that listens for the OAuth2 authorization code"""
    def __init__(self, binding: CallbackBinding):
        self.host = binding.host
        self.port = binding.port
        self.server = None
        self.flask_thread = None
        self.app = Flask(__name__)
        self.app.route(binding.path, methods=["GET"])(self.callback)
        self.queue = Queue()

    def callback(self):
        """The handler for the OAuth2 callback providing the auth code"""
        code = request.args.get("code")
        self.queue.put(code)
        return "<p>You can now close this window</p>"

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, ex_type, ex_value, trace_back):
        self.stop()

    def start(self):
        """Starts the callback server"""
        self.server = make_server(self.host, self.port, self.app)
        self.flask_thread = threading.Thread(target=self.server.serve_forever)
        self.flask_thread.start()

    def stop(self):
        """Stops the callback server"""
        if self.server:
            self.server.shutdown()
            self.flask_thread.join()
            self.server = None
            self.flask_thread = None
