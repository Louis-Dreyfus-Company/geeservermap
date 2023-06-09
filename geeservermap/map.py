# coding=utf-8
import ee

from .main import PORT
import requests
from . import helpers
from .exceptions import *
from .elements import layers


class Map:
    def __init__(self, port=PORT, do_async=False):
        self.port = port
        self.do_async = do_async

    def _addImage(self, image, visParams=None, name=None, shown=True,
                  opacity=1):
        """ Add Image Layer to map """
        vis = layers.VisParams.from_image(image, visParams)
        image = layers.Image(image, vis)
        layer = image.layer(opacity, shown)
        data = layer.info()
        data['name'] = name
        try:
            requests.get(
                f'http://localhost:{self.port}/add_layer',
                params=data
            )
        except ConnectionError:
            raise ServerNotRunning(self.port)

    def addLayer(self, layer, visParas=None, name=None, shown=True, opacity=1):
        """ Add a layer to the Map """
        if isinstance(layer, ee.Image):
            self._addImage(layer, visParas, name, shown, opacity)
