"""create a cherrypy server and run in a new thread to serve the the store.json data."""

import json
from os import environ, path

import cherrypy

from .config import FILES


class DashboardDataServer(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def investments(self):
        with open(path.join(FILES.temp_dir, 'store.json'), 'r') as sf:
            data: str = json.load(sf)
        return data


# Subscribes single scheduler/task executor application to cherrypy engine lifecyle.
# Chosen methods are exposed at the base url on port 8080 (default).
# TODO: secure application endpoints with shared app credentials (can be managed through
# env vars). See auth_digest tool authentication
def run_server():
    # explicit socket timeout definition to skirt windows specific TIME_WAIT on wanted
    # port after server exits before daemon thread exits.
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 8080
    cherrypy.server.socket_timeout = 3

    cherrypy.engine.autoreload.unsubscribe()

    # Starts cherrypy engine and server with minor configuration
    # (purposefully resets socket_timeout in the global config)
    cherrypy.quickstart(
        DashboardDataServer(),
        "/api/v1/",
        {
            'global': {'server.socket_host': '0.0.0.0', 'server.socket_port': 8080, 'server.socket_timeout': 3},
            "/api/v1": {},
        },
    )
