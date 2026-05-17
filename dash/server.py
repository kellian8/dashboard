"""create a cherrypy server and run in a new thread to serve the the store.json data."""

import cherrypy


class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        return "Hello World!"


def run_server():
    cherrypy.quickstart(HelloWorld(), "/")
