"""
End-to-end pipeline for the Leh NDVI analysis project.

Run from the project root with:

    python -m src.pipeline

Optional:

    python -m src.pipeline --config config/settings.yaml
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import ee
import geopandas as gpd
import pandas as pd
import yaml

import ee
import geopandas as gpd

from src.areas import load_zones, validate_zones
from src.config import load_config, validate_config
from src.extraction import (
    create_ndvi_reducer,
    extract_collection_statistics,
    results_to_dataframe,
)
from src.indices import create_annual_ndvi_collection
from src.preprocessing import preprocess_collection
from src.satellite import (
    get_available_sensors,
    get_collection_date_range,
    get_collection_size,
    load_landsat_from_config,
    validate_collection,
)


LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "settings.yaml"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

def configure_logging() -> None:
    """Configure application-wide logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def create_run_directory() -> tuple[Path, str]:
    """
    Create a unique timestamped directory for the current run.

    Returns
    -------
    tuple[Path, str]
        The run directory and its run ID.
    """
    timezone = ZoneInfo("Asia/Kolkata")

    run_timestamp = datetime.now(timezone)

    run_id = run_timestamp.strftime(
        "run_%Y%m%d_%H%M%S"
    )

    run_directory = PROCESSED_DIR / run_id

    # Avoid accidental collision if two runs start within
    # the same second.
    counter = 1

    while run_directory.exists():
        run_directory = PROCESSED_DIR / (
            f"{run_id}_{counter}"
        )
        counter += 1

    run_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    return run_directory, run_directory.name


def initialize_earth_engine() -> None:
    """
    Initialize the Earth Engine client.

    Authentication should be completed once beforehand if required,
    for example from a notebook using ee.Authenticate().
    """
    try:
        ee.Initialize()
        LOGGER.info("Earth Engine initialized successfully.")
    except Exception as exc:
        raise RuntimeError(
            "Earth Engine initialization failed. "
            "Authenticate Earth Engine first, then try again."
        ) from exc


def create_study_geometry(zones: gpd.GeoDataFrame) -> ee.Geometry:
    """
    Convert all study zones into one Earth Engine geometry.
    """
    if zones.crs is None:
        raise ValueError(
            "The zones GeoDataFrame has no CRS. "
            "Expected geographic coordinates, preferably EPSG:4326."
        )

    if zones.crs.to_epsg() != 4326:
        LOGGER.info("Converting zones from %s to EPSG:4326.", zones.crs)
        zones = zones.to_crs(epsg=4326)

    union_geometry = zones.geometry.unary_union

    if union_geometry.is_empty:
        raise ValueError("The combined study geometry is empty.")

    return ee.Geometry(union_geometry.__geo_interface__)


def get_available_years(collection) -> list[int]:
    """
    Extract distinct acquisition years represented in an EE collection.
    """
    timestamps = collection.aggregate_array("system:time_start")

    years = (
        timestamps
        .map(lambda timestamp: ee.Date(timestamp).get("year"))
        .distinct()
        .sort()
        .getInfo()
    )

    return [int(year) for year in years]


def get_run_output_paths(
    run_directory: Path,
) -> dict[str, Path]:
    """
    Return all output paths for a single pipeline run.
    """
    return {
        "ndvi_csv": (
            run_directory / "annual_zone_ndvi.csv"
        ),
        "processing_metadata_csv": (
            run_directory
            / "annual_processing_metadata.csv"
        ),
        "run_metadata_json": (
            run_directory / "run_metadata.json"
        ),
        "config_snapshot": (
            run_directory / "settings_snapshot.yaml"
        ),
    }


def get_annual_processing_metadata(
    annual_collection,
) -> pd.DataFrame:
    """
    Extract year-wise annual composite metadata.

    Returns
    -------
    pandas.DataFrame
        One row per requested year.
    """
    years = annual_collection.aggregate_array(
        "year"
    ).getInfo()

    image_counts = annual_collection.aggregate_array(
        "image_count"
    ).getInfo()

    rows = []

    for year, image_count in zip(years, image_counts):
        rows.append(
            {
                "year": int(year),
                "image_count": int(image_count),
                "valid_composite": int(image_count) > 0,
            }
        )

    metadata = pd.DataFrame(rows)

    if not metadata.empty:
        metadata = metadata.sort_values(
            by="year"
        ).reset_index(drop=True)

    return metadata


def save_json_metadata(
    metadata: dict,
    output_path: Path,
) -> None:
    """
    Save run metadata as formatted JSON.
    """
    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=4,
            ensure_ascii=False,
        )

    LOGGER.info(
        "Run metadata saved to: %s",
        output_path,
    )


def save_config_snapshot(
    config_path: Path,
    output_path: Path,
) -> None:
    """
    Copy the exact YAML configuration used for the run.
    """
    config_text = config_path.read_text(
        encoding="utf-8"
    )

    output_path.write_text(
        config_text,
        encoding="utf-8",
    )

    LOGGER.info(
        "Configuration snapshot saved to: %s",
        output_path,
    )


def save_results(df, output_path: Path) -> None:
    """Create the output directory and save the result DataFrame."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    LOGGER.info("Results saved to: %s", output_path)


def run_ndvi_pipeline(config_path: str | Path = DEFAULT_CONFIG_PATH):
    """
    Run the complete annual zone-level NDVI analysis.

    Parameters
    ----------
    config_path:
        Path to settings.yaml.

    Returns
    -------
    pandas.DataFrame
        Extracted annual NDVI statistics for all zones.
    """
    config_path = Path(config_path)

    LOGGER.info("Loading configuration: %s", config_path)
    config = load_config(config_path)
    validate_config(config)
    LOGGER.info("Configuration validated successfully.")

    run_directory, run_id = create_run_directory()

    output_paths = get_run_output_paths(
        run_directory
    )

    LOGGER.info(
        "Run ID: %s",
        run_id,
    )

    LOGGER.info(
        "Run output directory: %s",
        run_directory,
    )

    initialize_earth_engine()

    LOGGER.info("Loading study zones.")
    zones = load_zones()
    validate_zones(zones)
    LOGGER.info("Loaded %d study zones.", len(zones))

    study_geometry = create_study_geometry(zones)

    LOGGER.info("Loading Landsat collection.")
    landsat_collection = load_landsat_from_config(
        study_geometry=study_geometry,
        config=config,
    )
    validate_collection(landsat_collection)

    image_count = get_collection_size(landsat_collection)
    date_range = get_collection_date_range(landsat_collection)
    sensors = get_available_sensors(landsat_collection)

    LOGGER.info("Landsat image count: %d", image_count)
    LOGGER.info("Collection date range: %s", date_range)
    LOGGER.info("Available sensors: %s", sensors)

    LOGGER.info("Preprocessing satellite imagery.")
    preprocessed_collection = preprocess_collection(
        collection=landsat_collection,
        dataset_name=config["satellite"]["primary_dataset"],
    )

    available_years = get_available_years(preprocessed_collection)

    if not available_years:
        raise ValueError(
            "No acquisition years were found after preprocessing."
        )

    LOGGER.info("Available acquisition years: %s", available_years)

    satellite_config = config["satellite"]
    analysis_config = config["analysis"]

    LOGGER.info("Creating annual NDVI composites.")
    annual_ndvi_collection = create_annual_ndvi_collection(
        collection=preprocessed_collection,
        years=available_years,
        start_month=satellite_config["growing_season_start_month"],
        end_month=satellite_config["growing_season_end_month"],
    )
    annual_processing_metadata = (
        get_annual_processing_metadata(
            annual_ndvi_collection
        )
    )

    annual_processing_metadata.to_csv(
        output_paths["processing_metadata_csv"],
        index=False,
    )

    LOGGER.info(
        "Annual processing metadata saved to: %s",
        output_paths["processing_metadata_csv"],
    )

    LOGGER.info("Filtering out annual composites with no images.")
    valid_annual_ndvi = annual_ndvi_collection.filter(
        ee.Filter.gt("image_count", 0)
    )

    valid_years = (
        valid_annual_ndvi
        .aggregate_array("year")
        .getInfo()
    )

    LOGGER.info("Valid annual composite years: %s", valid_years)

    reducer = create_ndvi_reducer()

    LOGGER.info("Extracting zone-level NDVI statistics.")
    results = extract_collection_statistics(
        collection=valid_annual_ndvi,
        zones=zones,
        scale=analysis_config["scale_meters"],
        reducer=reducer,
    )
    LOGGER.info("Extracted zone-level NDVI statistics.")

    df = results_to_dataframe(results)

    if df.empty:
        raise ValueError(
            "The extraction returned no rows. "
            "Check the study zones, date range and imagery filters."
        )

    if "year" in df.columns:
        df = df.sort_values(
            by=["year", "zone_id"],
            kind="stable",
        ).reset_index(drop=True)

    if config.get("outputs", {}).get("export_csv",True):
        save_results(df,output_paths["ndvi_csv"],)
    else:
        LOGGER.info("CSV export disabled in configuration.")


    valid_years = (
        annual_processing_metadata.loc[
            annual_processing_metadata[
                "valid_composite"
            ],
            "year",
        ]
        .astype(int)
        .tolist()
    )

    missing_years = (
        annual_processing_metadata.loc[
            ~annual_processing_metadata[
                "valid_composite"
            ],
            "year",
        ]
        .astype(int)
        .tolist()
    )

    run_metadata = {
        "run_id": run_id,
        "run_timestamp": datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).isoformat(),

        "project": config["project"],
        "study": config["study"],

        "configuration": {
            "config_file": str(config_path),
            "satellite": config["satellite"],
            "analysis": config["analysis"],
        },

        "earth_engine": {
            "dataset_type": (
                config["satellite"]["primary_dataset"]
            ),
            "image_count": int(image_count),
            "available_sensors": sensors,
            "collection_date_range": date_range,
        },

        "zones": {
            "zone_count": int(len(zones)),
            "zone_ids": zones["zone_id"].tolist(),
            "zone_types": zones["zone_type"].tolist(),
        },

        "annual_processing": {
            "requested_start_year": (
                config["satellite"]["start_year"]
            ),
            "requested_end_year": (
                config["satellite"]["end_year"]
            ),
            "available_years": available_years,
            "valid_years": valid_years,
            "missing_years": missing_years,
            "valid_year_count": len(valid_years),
            "missing_year_count": len(missing_years),
        },

        "results": {
            "row_count": int(len(df)),
            "column_names": df.columns.tolist(),
        },

        "outputs": {
            "run_directory": str(run_directory),
            "ndvi_csv": str(
                output_paths["ndvi_csv"]
            ),
            "processing_metadata_csv": str(
                output_paths[
                    "processing_metadata_csv"
                ]
            ),
            "run_metadata_json": str(
                output_paths["run_metadata_json"]
            ),
            "config_snapshot": str(
                output_paths["config_snapshot"]
            ),
        },
    }

    save_json_metadata(
        metadata=run_metadata,
        output_path=output_paths[
            "run_metadata_json"
        ],
    )

    save_config_snapshot(
        config_path=config_path,
        output_path=output_paths[
            "config_snapshot"
        ],
    )

    LOGGER.info(
        "Pipeline completed successfully."
    )

    LOGGER.info(
        "Run directory: %s",
        run_directory,
    )

    LOGGER.info(
        "Rows extracted: %d",
        len(df),
    )

    return df


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the Leh annual NDVI analysis pipeline."
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the YAML configuration file.",
    )

    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    configure_logging()
    args = parse_args()
    run_ndvi_pipeline(config_path=args.config)


if __name__ == "__main__":
    main()
