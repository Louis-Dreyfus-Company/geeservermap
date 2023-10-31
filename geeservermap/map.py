# coding=utf-8
"""TODO Missing docstring."""

import ee
import requests

from .elements import layers
from .exceptions import ServerNotRunning
from .main import PORT


class Map:
    """TODO Missing docstring."""

    def __init__(self, port=PORT, do_async=False):
        """TODO Missing docstring."""
        self.port = port
        self.do_async = do_async

    def _addImage(self, image, visParams=None, name=None, shown=True, opacity=1):
        """Add Image Layer to map."""
        vis = layers.VisParams.from_image(image, visParams)
        image = layers.Image(image, vis)
        layer = image.layer(opacity, shown)
        data = layer.info()
        data["name"] = name
        try:
            requests.get(f"http://localhost:{self.port}/add_layer", params=data)
        except ConnectionError:
            raise ServerNotRunning(self.port)

    def addLayer(self, layer, visParas=None, name=None, shown=True, opacity=1):
        """Add a layer to the Map."""
        if isinstance(layer, ee.Image):
            self._addImage(layer, visParas, name, shown, opacity)
