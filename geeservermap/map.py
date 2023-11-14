"""The Map class used to display in the Flask server."""
from dataclasses import dataclass

import ee
import requests

from . import layers
from .exceptions import ServerNotRunning
from .main import PORT


@dataclass
class Map:
    """The Map class used to display in the Flask server."""

    port: int = PORT
    "The port the server is running on."

    do_async: bool = False
    "Whether to use async jobs or not."

    def addLayer(self, layer, visParams=None, name=None, shown=True, opacity=1):
        """Add a layer to the Map."""
        # exit if layer is not an ee Image
        if not isinstance(layer, ee.Image):
            return None

        vis = layers.VisParams.from_image(layer, visParams)
        layer = layers.Image(layer, vis).layer(opacity, shown)
        data = {**layer.info(), "name": name}
        try:
            requests.get(f"http://localhost:{self.port}/add_layer", params=data)
        except ConnectionError:
            raise ServerNotRunning(self.port)
