
import ee


import pandas as pd


def results_to_dataframe(results):
    """
    Convert an Earth Engine FeatureCollection
    into a Pandas DataFrame.

    Parameters
    ----------
    results : ee.FeatureCollection
        FeatureCollection containing zone statistics.

    Returns
    -------
    pd.DataFrame
        One row per zone.
    """

    # Request the results from Earth Engine.
    results_info = results.getInfo()

    # Extract feature properties.
    features = results_info["features"]

    rows = [
        feature["properties"]
        for feature in features
    ]

    # Convert to DataFrame.
    df = pd.DataFrame(rows)

    return df


def calculate_zone_statistics(
    image,
    zones,
    scale,
    reducer,
):
    """
    Calculate statistics for each zone in an Earth Engine image.

    Parameters
    ----------
    image : ee.Image
        Image containing the NDVI band.

    zones : geopandas.GeoDataFrame
        Study zones with geometry and zone properties.

    scale : int
        Resolution in meters.

    reducer : ee.Reducer
        Earth Engine reducer to apply.

    Returns
    -------
    ee.FeatureCollection
        One feature per zone containing the statistics.
    """

    # Convert GeoDataFrame to Earth Engine FeatureCollection.
    ee_zones = ee.FeatureCollection(
        zones.__geo_interface__
    )

    # Extract statistics for every zone.
    results = image.reduceRegions(
        collection=ee_zones,
        reducer=reducer,
        scale=scale,
        tileScale=2,
    )

    return results


def create_ndvi_reducer():
    """
    Create a combined reducer for NDVI statistics.
    """

    reducer = (
        ee.Reducer.mean()
        .combine(
            reducer2=ee.Reducer.median(),
            sharedInputs=True,
        )
        .combine(
            reducer2=ee.Reducer.stdDev(),
            sharedInputs=True,
        )
        .combine(
            reducer2=ee.Reducer.minMax(),
            sharedInputs=True,
        )
        .combine(
            reducer2=ee.Reducer.count(),
            sharedInputs=True,
        )
    )

    return reducer



def extract_image_statistics(
    image,
    zones,
    scale,
    reducer,
):
    """
    Extract statistics for all zones from one
    annual NDVI image.

    Parameters
    ----------
    image : ee.Image
        Annual NDVI composite.

    zones : geopandas.GeoDataFrame
        Study zones.

    scale : int
        Pixel scale in meters.

    reducer : ee.Reducer
        Statistics reducer.

    Returns
    -------
    ee.FeatureCollection
        Statistics for all zones for one year.
    """

    # Calculate statistics for all zones.
    results = calculate_zone_statistics(
        image=image,
        zones=zones,
        scale=scale,
        reducer=reducer,
    )

    # Get the year from image metadata.
    year = image.get("year")

    # Add year to every zone feature.
    results = results.map(
        lambda feature: feature.set(
            "year",
            year
        )
    )

    return results



def extract_collection_statistics(
    collection,
    zones,
    scale,
    reducer,
):
    """
    Extract statistics for every image in an
    annual NDVI collection.

    Returns
    -------
    ee.FeatureCollection
        Flattened zone statistics for all years.
    """

    def extract_for_image(image):
        return extract_image_statistics(
            image=image,
            zones=zones,
            scale=scale,
            reducer=reducer,
        )

    # Map extraction over every annual image.
    yearly_results = collection.map(
        extract_for_image
    )

    # Convert collection of FeatureCollections
    # into one flattened FeatureCollection.
    all_results = yearly_results.flatten()

    return all_results