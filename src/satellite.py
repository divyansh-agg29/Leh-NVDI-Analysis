
"""
Satellite data access for the Leh NDVI analysis project.

Stage 4.2:
    - Landsat collection definitions
    - Band mappings
    - Collection loading and filtering
"""

import ee


# ============================================================
# 1. Landsat Collection Definitions
# ============================================================

LANDSAT_COLLECTIONS = {
    "landsat4": "LANDSAT/LT04/C02/T1_L2",
    "landsat5": "LANDSAT/LT05/C02/T1_L2",
    "landsat7": "LANDSAT/LE07/C02/T1_L2",
    "landsat8": "LANDSAT/LC08/C02/T1_L2",
    "landsat9": "LANDSAT/LC09/C02/T1_L2",
}


# ============================================================
# 2. Band Mappings
# ============================================================

# Landsat 4, 5 and 7:
# Red = SR_B3
# NIR = SR_B4

LANDSAT_457_BANDS = {
    "blue": "SR_B1",
    "green": "SR_B2",
    "red": "SR_B3",
    "nir": "SR_B4",
    "swir1": "SR_B5",
    "swir2": "SR_B7",
}


# Landsat 8 and 9:
# Red = SR_B4
# NIR = SR_B5

LANDSAT_89_BANDS = {
    "blue": "SR_B2",
    "green": "SR_B3",
    "red": "SR_B4",
    "nir": "SR_B5",
    "swir1": "SR_B6",
    "swir2": "SR_B7",
}


# ============================================================
# 3. Collection Loader
# ============================================================

def load_landsat_collection(
    study_geometry,
    start_date,
    end_date,
    cloud_cover_limit=40,
):
    """
    Load and filter Landsat imagery.

    Parameters
    ----------
    study_geometry : ee.Geometry
        Region of interest.

    start_date : str
        Start date in YYYY-MM-DD format.

    end_date : str
        End date in YYYY-MM-DD format.

    cloud_cover_limit : int or float
        Maximum scene-level cloud cover percentage.

    Returns
    -------
    ee.ImageCollection
        Filtered Landsat image collection.
    """

    collections = [
        ee.ImageCollection(collection_id)
        for collection_id in LANDSAT_COLLECTIONS.values()
    ]

    landsat = collections[0]

    for collection in collections[1:]:
        landsat = landsat.merge(collection)

    filtered = (
        landsat
        .filterBounds(study_geometry)
        .filterDate(start_date, end_date)
        .filter(
            ee.Filter.lte(
                "CLOUD_COVER",
                cloud_cover_limit,
            )
        )
    )

    return filtered

def load_landsat_from_config(
    study_geometry,
    config,
):
    """
    Load Landsat imagery using project configuration.

    Parameters
    ----------
    study_geometry : ee.Geometry
        Region of interest.

    config : dict
        Project configuration loaded from settings.yaml.

    Returns
    -------
    ee.ImageCollection
        Filtered Landsat image collection.
    """

    satellite_config = config["satellite"]
    analysis_config = config["analysis"]

    start_year = satellite_config["start_year"]
    end_year = satellite_config["end_year"]

    start_date = f"{start_year}-01-01"

    # End date is exclusive in Earth Engine.
    end_date = f"{end_year + 1}-01-01"

    cloud_cover_limit = analysis_config[
        "cloud_cover_limit"
    ]

    return load_landsat_collection(
        study_geometry=study_geometry,
        start_date=start_date,
        end_date=end_date,
        cloud_cover_limit=cloud_cover_limit,
    )


# ============================================================
# 4. Collection Inspection
# ============================================================

def get_collection_size(collection):
    """
    Return the number of images in an Earth Engine collection.

    Parameters
    ----------
    collection : ee.ImageCollection

    Returns
    -------
    int
        Number of images.
    """

    return collection.size().getInfo()


def get_collection_date_range(collection):
    """
    Return the earliest and latest acquisition dates.

    Parameters
    ----------
    collection : ee.ImageCollection

    Returns
    -------
    dict
        Earliest and latest acquisition dates.
    """

    sorted_collection = collection.sort(
        "system:time_start"
    )

    first_image = ee.Image(
        sorted_collection.first()
    )

    last_image = ee.Image(
        sorted_collection.sort(
            "system:time_start",
            opt_ascending=False,
        ).first()
    )

    first_date = ee.Date(
        first_image.get("system:time_start")
    ).format("YYYY-MM-dd").getInfo()

    last_date = ee.Date(
        last_image.get("system:time_start")
    ).format("YYYY-MM-dd").getInfo()

    return {
        "start_date": first_date,
        "end_date": last_date,
    }


def get_first_image(collection):
    """
    Return the first image from a collection.

    Parameters
    ----------
    collection : ee.ImageCollection

    Returns
    -------
    ee.Image
        First image.
    """

    return ee.Image(collection.first())



# ============================================================
# 5. Sensor and Band Utilities
# ============================================================


def get_available_sensors(collection):
    """
    Return unique satellite IDs in a collection.

    Parameters
    ----------
    collection : ee.ImageCollection

    Returns
    -------
    list
        Available satellite IDs.
    """

    sensors = collection.aggregate_array(
        "SPACECRAFT_ID"
    ).distinct()

    return sensors.getInfo()


def get_sensor_type(image):
    """
    Determine the Landsat sensor generation.

    Parameters
    ----------
    image : ee.Image

    Returns
    -------
    str
        "landsat_457" or "landsat_89".
    """

    spacecraft_id = image.get(
        "SPACECRAFT_ID"
    ).getInfo()

    if spacecraft_id in [
        "LANDSAT_4",
        "LANDSAT_5",
        "LANDSAT_7",
    ]:
        return "landsat_457"

    if spacecraft_id in [
        "LANDSAT_8",
        "LANDSAT_9",
    ]:
        return "landsat_89"

    raise ValueError(
        f"Unsupported Landsat sensor: {spacecraft_id}"
    )


def get_band_mapping(image):
    """
    Return the appropriate band mapping for an image.

    Parameters
    ----------
    image : ee.Image

    Returns
    -------
    dict
        Sensor-specific band mapping.
    """

    sensor_type = get_sensor_type(image)

    if sensor_type == "landsat_457":
        return LANDSAT_457_BANDS

    if sensor_type == "landsat_89":
        return LANDSAT_89_BANDS

    raise ValueError(
        f"Unsupported sensor type: {sensor_type}"
    )



# ============================================================
# 6. Collection Validation
# ============================================================

def validate_collection(collection):
    """
    Validate that an Earth Engine collection contains imagery.

    Parameters
    ----------
    collection : ee.ImageCollection

    Returns
    -------
    bool
        True if the collection contains at least one image.

    Raises
    ------
    ValueError
        If the collection is empty.
    """

    image_count = collection.size().getInfo()

    if image_count == 0:
        raise ValueError(
            "The Landsat collection contains no images."
        )

    return True