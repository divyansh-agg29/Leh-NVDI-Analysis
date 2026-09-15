"""
Annual NDVI data-coverage analysis.

This module calculates the percentage of valid NDVI pixels
inside each study zone for every available year.
"""

from __future__ import annotations

from pathlib import Path

import ee
import geopandas as gpd
import pandas as pd

from src.areas import load_zones, validate_zones
from src.config import load_config, validate_config
from src.indices import create_annual_ndvi_composite
from src.pipeline import (
    create_study_geometry,
    get_available_years,
    initialize_earth_engine,
)
from src.preprocessing import preprocess_collection
from src.satellite import (
    load_landsat_from_config,
    validate_collection,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_CONFIG_PATH = (
    PROJECT_ROOT / "config" / "settings.yaml"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "annual_zone_coverage.csv"
)


def calculate_zone_coverage(
    image: ee.Image,
    zones: gpd.GeoDataFrame,
    scale: int,
) -> list[dict]:
    """
    Calculate valid-pixel coverage for each zone.

    Parameters
    ----------
    image:
        Annual NDVI image containing an NDVI band.

    zones:
        Study zones as a GeoDataFrame.

    scale:
        Pixel scale in metres.

    Returns
    -------
    list[dict]
        Coverage results for each zone.
    """

    if zones.crs is None:
        raise ValueError(
            "Study zones must have a coordinate reference system."
        )

    # Earth Engine geometries should use geographic coordinates.
    zones_4326 = zones.to_crs(epsg=4326)

    zone_features = ee.FeatureCollection(
        zones_4326.__geo_interface__
    )

    ndvi = image.select("NDVI")

    # 1 where NDVI is valid, masked where NDVI is invalid.
    valid_pixels = (
        ndvi.mask()
        .rename("valid_pixel_count")
    )

    # A constant image used to count all pixels in each zone.
    total_pixels = (
        ee.Image.constant(1)
        .rename("total_pixel_count")
    )

    combined_image = valid_pixels.addBands(
        total_pixels
    )

    coverage_features = combined_image.reduceRegions(
        collection=zone_features,
        reducer=ee.Reducer.sum(),
        scale=scale,
        tileScale=4,
    )

    coverage_features = coverage_features.map(
        lambda feature: feature.set(
            "valid_coverage_percent",
            ee.Number(
                feature.get("valid_pixel_count")
            )
            .divide(
                ee.Number(
                    feature.get("total_pixel_count")
                )
            )
            .multiply(100),
        )
    )

    return coverage_features.getInfo()["features"]


def calculate_annual_coverage(
    annual_images: list[ee.Image],
    zones: gpd.GeoDataFrame,
    scale: int,
) -> pd.DataFrame:
    """
    Calculate zone coverage for every annual NDVI image.
    """

    rows = []

    for image in annual_images:
        year = int(image.get("year").getInfo())
        image_count = int(
            image.get("image_count").getInfo()
        )

        print(f"Checking coverage for {year}...")

        # No images means there is no usable annual composite.
        if image_count == 0:
            for _, zone in zones.iterrows():
                rows.append(
                    {
                        "year": year,
                        "zone_id": zone["zone_id"],
                        "zone_type": zone["zone_type"],
                        "name": zone["name"],
                        "image_count": image_count,
                        "valid_pixel_count": 0,
                        "total_pixel_count": 0,
                        "valid_coverage_percent": 0.0,
                    }
                )

            continue

        feature_results = calculate_zone_coverage(
            image=image,
            zones=zones,
            scale=scale,
        )

        for feature in feature_results:
            properties = feature["properties"]

            rows.append(
                {
                    "year": year,
                    "zone_id": properties.get("zone_id"),
                    "zone_type": properties.get("zone_type"),
                    "name": properties.get("name"),
                    "image_count": image_count,
                    "valid_pixel_count": properties.get(
                        "valid_pixel_count"
                    ),
                    "total_pixel_count": properties.get(
                        "total_pixel_count"
                    ),
                    "valid_coverage_percent": properties.get(
                        "valid_coverage_percent"
                    ),
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    """
    Run annual coverage analysis.
    """

    print("Loading configuration...")

    config = load_config(DEFAULT_CONFIG_PATH)
    validate_config(config)

    print("Initializing Earth Engine...")
    initialize_earth_engine()

    print("Loading study zones...")
    zones = load_zones()
    validate_zones(zones)

    print("Creating study geometry...")
    study_geometry = create_study_geometry(zones)

    print("Loading Landsat collection...")
    landsat_collection = load_landsat_from_config(
        study_geometry=study_geometry,
        config=config,
    )
    validate_collection(landsat_collection)

    print("Preprocessing collection...")
    preprocessed_collection = preprocess_collection(
        collection=landsat_collection,
        dataset_name=config["satellite"]["primary_dataset"],
    )

    available_years = get_available_years(
        preprocessed_collection
    )

    print(
        f"Available years: {available_years}"
    )

    satellite_config = config["satellite"]
    analysis_config = config["analysis"]

    print("Creating annual NDVI images...")

    annual_images = []

    for year in available_years:
        image = create_annual_ndvi_composite(
            collection=preprocessed_collection,
            year=year,
            start_month=(
                satellite_config[
                    "growing_season_start_month"
                ]
            ),
            end_month=(
                satellite_config[
                    "growing_season_end_month"
                ]
            ),
        )

        annual_images.append(image)

    print("Calculating annual zone coverage...")

    coverage_df = calculate_annual_coverage(
        annual_images=annual_images,
        zones=zones,
        scale=analysis_config["scale_meters"],
    )

    coverage_df = coverage_df.sort_values(
        by=["year", "zone_id"]
    ).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    coverage_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print("Coverage analysis completed.")
    print(f"Saved to: {OUTPUT_PATH}")

    print()
    print("Coverage summary:")
    print(
        coverage_df[
            [
                "year",
                "zone_id",
                "valid_coverage_percent",
                "image_count",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()