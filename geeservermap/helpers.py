"""helper methods used throughout the package."""

import ee

MAX_VALUE = {
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
"Maximum value for each GEE data type."


def visparamsStrToList(viz_params: str) -> list:
    """Transform a string formatted as needed by ee.data.getMapId to a list.

    Args:
        viz_params: a string describing the visualization parameters

    Returns:
        a list of the split parameters from the input string
    """
    return [b.strip() for b in viz_params.split(",")]


def visparamsListToStr(viz_params: list) -> str:
    """Transform a list to a string formatted as needed by ee.data.getMapId.

    Args:
        viz_params: a list of the visualization parameters

    Returns:
        a string formatted as needed by ee.data.getMapId
    """
    return ",".join([f"{b}" for b in viz_params])


def getImageTile(image: ee.Image, viz_params: dict = {}, visible=True) -> dict:
    """Get image's tiles uri.

    Args:
        image: the image to get the tiles from
        viz_params: the visualization parameters to apply to the image
        visible: whether the layer is visible or not

    Returns:
        a dict with the url, attribution, visible and visParams
    """
    # init the options of the Image
    options = {}

    # load the bands from the image and overwrite them with the one
    # from viz_params if passed

    band_names = image.bandNames().getInfo()
    bands = list([band_names[0]] if len(band_names) < 3 else band_names[0:3])
    bands = viz_params.get("bands", bands)

    # parse the bands into a list of value and a string
    band_str = visparamsListToStr(bands) if isinstance(bands, list) else bands
    band_list = visparamsStrToList(bands) if isinstance(bands, str) else bands

    # Set proxy parameters
    options["bands"] = band_str

    # set the min value respecting the format required by GEE
    min_ = viz_params.get("min", "0")
    min_ = visparamsListToStr(min_) if isinstance(min_, list) else str(min_)
    options["min"] = min_

    # set the max value respecting the format required by GEE
    band_types = image.select(band_list).bandTypes().values().getInfo()
    default_max = [MAX_VALUE.get(band_types, 1) for b in band_list]
    max_ = viz_params.get("max", default_max)
    max_ = visparamsListToStr(max_) if isinstance(max_, list) else str(max_)
    options["max"] = max_

    # get the palette if passed and if the image has only one band
    if len(band_list) == 1:
        palette = viz_params.get("palette", None)
        palette = visparamsListToStr(palette) if isinstance(palette, list) else palette
        options["palette"] = palette
    else:
        raise ValueError("Can't use palette parameter with more than one band")

    # Get the MapID and Token after applying parameters
    image_info = image.getMapId(options)
    fetcher = image_info["tile_fetcher"]
    tiles = fetcher.url_format
    attribution = 'Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>'

    return {
        "url": tiles,
        "attribution": attribution,
        "visible": visible,
        "visParams": options,
    }
