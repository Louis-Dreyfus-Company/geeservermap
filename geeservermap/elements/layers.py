from .. import helpers
import ee
from typing import Union


class VisParams:
    """ Visualization parameters to apply in a layer """
    def __init__(self, bands: list, min: Union[int, list],
                 max: Union[int, list], palette=None,
                 gain=None, bias=None, gamma=None):
        # Bands
        self.bands = self.__format_bands(bands)
        self._bands_len = len(self.bands)
        self.min = self.__format_param(min, 'min')
        self.max = self.__format_param(max, 'max')
        self.gain = self.__format_param(gain, 'gain')
        self.bias = self.__format_param(bias, 'bias')
        self.gamma = self.__format_param(gamma, 'gamma')

        # Palette
        if palette:
            if len(self.bands) > 1:
                print("Can't use palette parameter with more than one band")
                palette = None
        self.palette = palette

    @staticmethod
    def __format_bands(bands):
        if isinstance(bands, str):
            bands = [bands]
        if len(bands) < 3:
            bands = bands[0:1]
        elif len(bands) > 3:
            bands = bands[0:3]
        return bands

    def __format_param(self, value, param):
        if isinstance(value, (int, float)):
            return [value] * self._bands_len
        elif isinstance(value, str):
            return [float(value)] * self._bands_len
        elif isinstance(value, (list, tuple)):
            return [value[0]] * self._bands_len
        elif value is None:
            return value
        else:
            raise ValueError(f"Can't use {value} as {param} value")

    @staticmethod
    def __format_palette(palette):
        """ Format palette list """
        return ','.join(palette) if palette else None

    @classmethod
    def from_image(cls, image, visParams=None):
        visParams = visParams or {}
        if not 'bands' in visParams:
            bands = image.bandNames().getInfo()
        else:
            bands = visParams['bands']
        bands = cls.__format_bands(bands)
        visParams['bands'] = bands

        # Min and max
        btypes = None
        if not 'min' in visParams:
            image = image.select(visParams['bands'])
            btypes = image.bandTypes().getInfo()
            mins = [btype.get('min') for bname, btype in btypes.items()]
            mins = [m or 0 for m in mins]
            visParams['min'] = mins
        if not 'max' in visParams:
            image = image.select(visParams['bands'])
            if not btypes:
                btypes = image.bandTypes().getInfo()
            maxs = [btype.get('max') for bname, btype in btypes.items()]
            maxs = [m or 1 for m in maxs]
            visParams['max'] = maxs

        return cls(**visParams)

    def for_mapid(self):
        """ Return params for using in Image.MapId """
        return {
            'bands': helpers.visparamsListToStr(self.bands),
            'min': helpers.visparamsListToStr(self.min),
            'max': helpers.visparamsListToStr(self.max),
            'palette': self.__format_palette(self.palette),
            'bias': helpers.visparamsListToStr(self.bias),
            'gain': helpers.visparamsListToStr(self.gain),
            'gamma': helpers.visparamsListToStr(self.gamma)
        }


class MapLayer:
    ATTR = 'Map Data &copy; <a href="https://earthengine.google.com/">' \
           'Google Earth Engine</a>'
    def __init__(self, url, opacity, visible, attribution=ATTR):
        self.url = url
        if opacity > 1:
            print('opacity cannot be greater than 1, setting to 1')
            opacity = 1
        elif opacity < 0:
            print('opacity cannot be less than 0, setting to 0')
            opacity = 0
        self.opacity = opacity
        self.visible = visible
        self.attribution = attribution

    def info(self):
        """ Get the message to send to the backend """
        return {
            'url': self.url,
            'attribution': self.attribution,
            'visible': self.visible,
            'opacity': self.opacity
        }


class Image:
    def __init__(self, image: ee.Image, visParams: VisParams):
        self.image = image
        self.visParams = visParams

    def bands(self):
        """ Get bands from visParams or from the image directly """
        if self.visParams.bands:
            return self.visParams.bands
        else:
            bandnames = self.image.bandNames().getInfo()
            if len(bandnames) < 3:
                bands = bandnames[0:1]
            else:
                bands = bandnames[0:3]
            return bands

    @property
    def url(self):
        """ Image Tiles URL """
        params = self.visParams.for_mapid()
        # params.setdefault('bands', self.bands()) # set bands if not passed in visparams
        image_info = self.image.getMapId(params)
        fetcher = image_info['tile_fetcher']
        tiles = fetcher.url_format
        return tiles

    def layer(self, opacity=1, visible=True):
        """ Layer for adding to map """
        return MapLayer(self.url, opacity, visible)


class Geometry:
    def __init__(self, geometry: ee.Geometry):
        self.geometry = geometry

    def layer(self, opacity=1, visible=True):
        pass