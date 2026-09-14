
"""
Vegetation index calculations for the Leh NDVI analysis project.
"""

import ee

from src.satellite import (
    get_server_side_band_mapping,
)


def add_ndvi(image, red_band, nir_band):
    """
    Calculate NDVI and add it as a new band.

    Parameters
    ----------
    image : ee.Image
        Preprocessed satellite image.

    red_band : str
        Name of the red reflectance band.

    nir_band : str
        Name of the near-infrared reflectance band.

    Returns
    -------
    ee.Image
        Original image with an additional NDVI band.
    """

    ndvi = image.normalizedDifference(
        [nir_band, red_band]
    ).rename("NDVI")

    return image.addBands(ndvi)


def add_ndvi_by_sensor(image):
    """
    Calculate NDVI using the appropriate Landsat
    red and NIR bands.

    Parameters
    ----------
    image : ee.Image
        Preprocessed Landsat image.

    Returns
    -------
    ee.Image
        Image with an NDVI band.
    """

    band_mapping = get_server_side_band_mapping(
        image
    )

    red_band = ee.String(
        band_mapping.get("red")
    )

    nir_band = ee.String(
        band_mapping.get("nir")
    )

    return add_ndvi(
        image=image,
        red_band=red_band,
        nir_band=nir_band
    )


def add_time_metadata(image):
    """
    Add acquisition date information to an Earth Engine image.

    Parameters
    ----------
    image : ee.Image
        Satellite image.

    Returns
    -------
    ee.Image
        Image with date metadata added.
    """

    date = ee.Date(image.get("system:time_start"))

    year = date.get("year")
    month = date.get("month")
    day_of_year = date.getRelative(
        "day",
        "year"
    )

    return image.set({
        "year": year,
        "month": month,
        "day_of_year": day_of_year,
        "acquisition_date": date.format("YYYY-MM-dd")
    })



def create_annual_ndvi_composite(
    collection,
    year,
    start_month,
    end_month,
):
    """
    Create an annual median NDVI composite.

    Parameters
    ----------
    collection : ee.ImageCollection
        Preprocessed Landsat image collection.

    year : int
        Year to process.

    start_month : int
        First month of the growing season.

    end_month : int
        Last month of the growing season.
        This month is included.

    Returns
    -------
    ee.Image
        Annual median NDVI composite.
    """

    # --------------------------------------------------------
    # 1. Define the annual date range.
    # --------------------------------------------------------

    start_date = ee.Date.fromYMD(
        year,
        start_month,
        1,
    )

    # Advance one month beyond end_month.
    # This makes end_month inclusive.
    end_date = ee.Date.fromYMD(
        year,
        end_month,
        1,
    ).advance(1, "month")

    # --------------------------------------------------------
    # 2. Filter the collection to the growing season.
    # --------------------------------------------------------

    annual_collection = collection.filterDate(
        start_date,
        end_date,
    )

    # --------------------------------------------------------
    # 3. Calculate NDVI for every image.
    # --------------------------------------------------------

    annual_ndvi = annual_collection.map(
        add_ndvi_by_sensor
    )

    # --------------------------------------------------------
    # 4. Create the median NDVI composite.
    # --------------------------------------------------------

    annual_composite = (
        annual_ndvi
        .select("NDVI")
        .median()
        .rename("NDVI")
    )

    # --------------------------------------------------------
    # 5. Store useful metadata.
    # --------------------------------------------------------

    annual_composite = annual_composite.set({
        "year": year,
        "start_month": start_month,
        "end_month": end_month,
        "image_count": annual_collection.size(),
    })

    return annual_composite



def create_annual_ndvi_collection(
    collection,
    years,
    start_month,
    end_month,
):
    """
    Create annual NDVI composites for multiple years.

    Parameters
    ----------
    collection : ee.ImageCollection
        Preprocessed Landsat image collection.

    years : list[int] or ee.List
        Years to process.

    start_month : int
        First month of the growing season.

    end_month : int
        Last month of the growing season.

    Returns
    -------
    ee.ImageCollection
        Collection containing one annual NDVI composite
        per requested year.
    """

    # Convert Python list to an Earth Engine list.
    years = ee.List(years)

    # Create one annual composite for every year.
    annual_images = years.map(
        lambda year: create_annual_ndvi_composite(
            collection=collection,
            year=ee.Number(year),
            start_month=start_month,
            end_month=end_month,
        )
    )

    # Convert the list of images into an ImageCollection.
    return ee.ImageCollection.fromImages(
        annual_images
    )