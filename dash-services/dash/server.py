"""create a cherrypy server and run in a new thread to serve the the store.json data."""

from os import environ, path

import cherrypy
from loguru import logger

from .config import ROOT_DIR, SERVICES_DEFAULT_PORT, SERVICES_PORT, SERVER_HOST
from .services import JsonPersistenceClient


class DashboardDataServer(object):
    _data_client: JsonPersistenceClient = None

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {"message": "Dash Data Provider Server is running!"}

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


def run_server():
    """
    Subscribes single scheduler/task executor application to cherrypy engine lifecyle.
    Chosen methods are exposed at the base url on port 8080 (default).

    TODO: secure application endpoints with shared app credentials (can be managed through
    env vars). See auth_digest tool authentication
    """
    cherrypy.server.socket_host = SERVER_HOST
    cherrypy.server.socket_port = SERVICES_PORT
    if cherrypy.server.socket_port == SERVICES_DEFAULT_PORT:
        logger.warning(
            f"Dashboard Data Server is running on default port {SERVICES_DEFAULT_PORT}. This may cause conflicts with other applications. Check port in the .env file."
        )

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
            'global': {'server.socket_host': '0.0.0.0', 'server.socket_port': SERVICES_PORT, 'server.socket_timeout': 3},
        },

    )
