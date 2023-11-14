"""Custom exceptions for geeservermap."""


class ServerNotRunning(Exception):
    """Exception raised when the server is not running."""

    def __init__(self, port: int):
        """Initialize the exception.

        Args:
            port: The port the server is not running on.
        """
        self.message = f"""
            The server is not running or it isn't running on port {port}.
            To run the server follow instructions on <link>.
            If the server is running in a different port, you must specify it when creating the Map instance:
            Map = geeservermap.Map(port=xxxx)
        """
        super().__init__(self.message)
