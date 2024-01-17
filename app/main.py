from uvicorn import Config, Server as UvicornServer
from app.server import Server


def start():
    print("Running Server")
    app = Server().app
    return app
