"""TODO Missing docstring."""


def visparamsStrToList(params):
    """Transform a string formatted as needed by ee.data.getMapId to a list.

    Args:
        params: to convert

    Returns:
        a list with the params
    """
    proxy_bands = []
    bands = params.split(",")
    for band in bands:
        proxy_bands.append(band.strip())
    return proxy_bands


def visparamsListToStr(params):
    """Transform a list to a string formatted as needed by ee.data.getMapId.

    Args:
        params: params to convert

    Returns:
        a string formatted as needed by ee.data.getMapId
    """
    if not params:
        return params
    n = len(params)
    if n == 1:
        newbands = "{}".format(params[0])
    elif n == 3:
        newbands = "{},{},{}".format(params[0], params[1], params[2])
    else:
        newbands = "{}".format(params[0])
    return newbands


def getImageTile(image, visParams, visible=True):
    """Get image's tiles uri."""
    proxy = {}
    params = visParams or {}

    # BANDS #############
    def default_bands(image):
        bandnames = image.bandNames().getInfo()
        if len(bandnames) < 3:
            bands = [bandnames[0]]
        else:
            bands = [bandnames[0], bandnames[1], bandnames[2]]
        return bands

    bands = params.get("bands", default_bands(image))

    # if the passed bands is a string formatted like required by GEE, get the
    # list out of it
    if isinstance(bands, str):
        bands_list = visparamsStrToList(bands)
        bands_str = visparamsListToStr(bands_list)

    # Transform list to getMapId format
    # ['b1', 'b2', 'b3'] == 'b1, b2, b3'
    if isinstance(bands, list):
        bands_list = bands
        bands_str = visparamsListToStr(bands)

    # Set proxy parameters
    proxy["bands"] = bands_str

    # MIN #################
    themin = params.get("min") if "min" in params else "0"

    # if the passed min is a list, convert to the format required by GEE
    if isinstance(themin, list):
        themin = visparamsListToStr(themin)

    proxy["min"] = themin

    # MAX #################
    def default_max(image, bands):
        proxy_maxs = []
        maxs = {
            "float": 1,
            "double": 1,
            "int8": ((2**8) - 1) / 2,
            "uint8": (2**8) - 1,
            "int16": ((2**16) - 1) / 2,
            "uint16": (2**16) - 1,
            "int32": ((2**32) - 1) / 2,
            "uint32": (2**32) - 1,
            "int64": ((2**64) - 1) / 2,
        }
        for band in bands:
            ty = image.select([band]).getInfo()["bands"][0]["data_type"]
            try:
                themax = maxs[ty]
            except Exception:
                themax = 1
            proxy_maxs.append(themax)
        return proxy_maxs

    themax = params.get("max") if "max" in params else default_max(image, bands_list)

    # if the passed max is a list or the max is computed by the default function
    # convert to the format required by GEE
    if isinstance(themax, list):
        themax = visparamsListToStr(themax)

    proxy["max"] = themax

    # PALETTE
    if "palette" in params:
        if len(bands_list) == 1:
            palette = params.get("palette")
            if isinstance(palette, str):
                palette = visparamsStrToList(palette)
            toformat = "{}," * len(palette)
            palette = toformat[:-1].format(*palette)
            proxy["palette"] = palette
        else:
            print("Can't use palette parameter with more than one band")

    # Get the MapID and Token after applying parameters
    image_info = image.getMapId(proxy)
    fetcher = image_info["tile_fetcher"]
    tiles = fetcher.url_format
    attribution = (
        'Map Data &copy; <a href="https://earthengine.google.com/">'
        "Google Earth Engine</a> "
    )

    return {
        "url": tiles,
        "attribution": attribution,
        "visible": visible,
        "visParams": proxy,
    }
