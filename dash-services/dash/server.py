"""create a cherrypy server and run in a new thread to serve the the store.json data."""

from os import environ, path

import cherrypy

from .config import ROOT_DIR
from .services import JsonPersistenceClient


class DashboardDataServer(object):
    _data_client: JsonPersistenceClient = None

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def summary(self):
        ts, investment_data = self._data_client.get_from_table('investments')
        return {"timestamp": ts, "investments": investment_data}

    def _set_data_client(self, data_client):
        if isinstance(data_client, JsonPersistenceClient):
            self._data_client = data_client
        else:
            raise TypeError(
                f"Dashboard Data Server Error - data_client must be a JsonPersistenceClient. Recieved '{type(data_client)}'"
            )


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

    # Configure and start cherrypy engine
    dashboard_data_server = DashboardDataServer()
    dashboard_data_server._set_data_client(
        JsonPersistenceClient(store_path=path.normpath(path.join(ROOT_DIR, environ.get('JSON_STORE_PATH'))))
    )
    cherrypy.quickstart(
        dashboard_data_server,
        "/api/v1/",
        {
            'global': {'server.socket_host': '0.0.0.0', 'server.socket_port': 8080, 'server.socket_timeout': 3},
            "/api/v1": {},
        },
    )
