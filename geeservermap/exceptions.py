"""TODO Missing docstring."""


class ServerNotRunning(Exception):
    """TODO Missing docstring."""

    def __init__(self, port):
        """TODO Missing docstring."""
        self.message = f"""The server is not running or it isn't running on port {port}. To run the
server follow instructions on <link>. If the server is running in a
different port, you must specify it when creating the Map instance:
Map = geeservermap.Map(port=xxxx)"""
        super().__init__(self.message)
