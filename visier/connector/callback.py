# Copyright 2023 Visier Solutions Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Visier Public Python Connector OAuth2 Callback
"""

import threading
import dataclasses
from urllib.parse import urlparse
from queue import Queue
import logging
from flask import Flask, request
from werkzeug.serving import make_server

# Disable to avoid Flask logging on callbacks
logging.getLogger('werkzeug').disabled = True

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
