"""
Visualization utilities for the Leh NDVI analysis project.

Stage 9.1:
    - Annual NDVI trend plots
    - One line per zone type
    - Export plots as image files
"""

from pathlib import Path

import ee
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from src.areas import load_zones, validate_zones
from src.config import load_config, validate_config
from src.indices import create_annual_ndvi_collection
from src.preprocessing import preprocess_collection
from src.satellite import load_landsat_from_config


# ============================================================
# 1. Constants
# ============================================================

REQUIRED_NDVI_COLUMNS = {
    "year",
    "zone_type",
    "mean",
}


# ============================================================
# 2. Data Loading
# ============================================================

def load_ndvi_results(csv_path: str | Path) -> pd.DataFrame:
    """
    Load annual zone-level NDVI results from a CSV file.

    Parameters
    ----------
    csv_path : str or Path
        Path to annual_zone_ndvi.csv.

    Returns
    -------
    pd.DataFrame
        Loaded NDVI results.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist.

    ValueError
        If required columns are missing.
    """

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"NDVI results file not found: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    missing_columns = REQUIRED_NDVI_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"NDVI results are missing required columns: "
            f"{missing_columns}"
        )

    return df


# ============================================================
# 3. Data Preparation
# ============================================================

def prepare_annual_trend_data(
    ndvi_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare NDVI data for annual trend plotting.

    The result contains one mean NDVI value per year and
    zone type.

    If multiple zones share the same zone_type, their mean
    NDVI values are averaged for that year.

    Parameters
    ----------
    ndvi_df : pd.DataFrame
        Raw annual zone-level NDVI results.

    Returns
    -------
    pd.DataFrame
        Prepared data with columns:

        year
        zone_type
        mean_ndvi
    """

    required_columns = {
        "year",
        "zone_type",
        "mean",
    }

    missing_columns = required_columns - set(ndvi_df.columns)

    if missing_columns:
        raise ValueError(
            f"Input DataFrame is missing columns: "
            f"{missing_columns}"
        )

    # Work on a copy so the original DataFrame is unchanged.
    df = ndvi_df.copy()

    # Ensure year is numeric.
    df["year"] = pd.to_numeric(
        df["year"],
        errors="coerce",
    )

    # Ensure mean NDVI is numeric.
    df["mean"] = pd.to_numeric(
        df["mean"],
        errors="coerce",
    )

    # Remove rows that cannot be plotted.
    df = df.dropna(
        subset=[
            "year",
            "zone_type",
            "mean",
        ]
    )

    # Group by year and zone type.
    trend_df = (
        df.groupby(
            ["year", "zone_type"],
            as_index=False,
        )["mean"]
        .mean()
        .rename(
            columns={
                "mean": "mean_ndvi",
            }
        )
    )

    # Convert year to integer after removing invalid values.
    trend_df["year"] = trend_df["year"].astype(int)

    # Sort chronologically.
    trend_df = trend_df.sort_values(
        by=[
            "year",
            "zone_type",
        ]
    )

    return trend_df


# ============================================================
# 4. Annual Trend Plot
# ============================================================

def plot_annual_ndvi_trends(
    ndvi_df: pd.DataFrame,
    output_path: str | Path,
    title: str = "Annual NDVI Trends by Zone Type",
    figsize: tuple[int, int] = (12, 7),
    show: bool = False,
) -> Path:
    """
    Create and save an annual NDVI trend plot.

    Parameters
    ----------
    ndvi_df : pd.DataFrame
        Raw annual zone-level NDVI results.

    output_path : str or Path
        Destination path for the generated figure.

    title : str, optional
        Plot title.

    figsize : tuple[int, int], optional
        Figure width and height in inches.

    show : bool, optional
        Whether to display the plot interactively.

    Returns
    -------
    Path
        Path to the saved figure.
    """

    output_path = Path(output_path)

    # Create the output directory if necessary.
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    trend_df = prepare_annual_trend_data(ndvi_df)

    if trend_df.empty:
        raise ValueError(
            "No valid NDVI data available for plotting."
        )

    fig, ax = plt.subplots(
        figsize=figsize,
    )

    # Plot one line for each zone type.
    for zone_type, zone_data in trend_df.groupby(
        "zone_type"
    ):
        zone_data = zone_data.sort_values("year")

        ax.plot(
            zone_data["year"],
            zone_data["mean_ndvi"],
            marker="o",
            linewidth=2,
            label=zone_type,
        )

    ax.set_title(
        title,
        fontsize=14,
        fontweight="bold",
    )

    ax.set_xlabel(
        "Year",
        fontsize=11,
    )

    ax.set_ylabel(
        "Mean NDVI",
        fontsize=11,
    )

    ax.set_ylim(-1, 1)

    ax.grid(
        True,
        linestyle="--",
        alpha=0.5,
    )

    ax.legend(
        title="Zone Type",
        loc="best",
    )

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    if show:
        plt.show()

    # Close the figure to avoid memory buildup when generating
    # multiple plots.
    plt.close(fig)

    return output_path


# ============================================================
# 5. Zone Comparison Plots
# ============================================================

def plot_average_ndvi_by_zone(
    ndvi_df: pd.DataFrame,
    output_path: str | Path,
    title: str = "Average NDVI by Zone Type",
    figsize: tuple[int, int] = (10, 6),
    show: bool = False,
) -> Path:
    """
    Create a bar chart showing average NDVI for each zone type.

    Parameters
    ----------
    ndvi_df : pd.DataFrame
        Raw annual zone-level NDVI results.

    output_path : str or Path
        Destination path for the generated figure.

    title : str, optional
        Plot title.

    figsize : tuple[int, int], optional
        Figure width and height in inches.

    show : bool, optional
        Whether to display the plot interactively.

    Returns
    -------
    Path
        Path to the saved figure.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    required_columns = {
        "zone_type",
        "mean",
    }

    missing_columns = required_columns - set(ndvi_df.columns)

    if missing_columns:
        raise ValueError(
            f"Input DataFrame is missing columns: "
            f"{missing_columns}"
        )

    df = ndvi_df.copy()

    df["mean"] = pd.to_numeric(
        df["mean"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "zone_type",
            "mean",
        ]
    )

    if df.empty:
        raise ValueError(
            "No valid NDVI data available for plotting."
        )

    average_ndvi = (
        df.groupby("zone_type")["mean"]
        .mean()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(
        figsize=figsize,
    )

    average_ndvi.plot(
        kind="bar",
        ax=ax,
    )

    ax.set_title(
        title,
        fontsize=14,
        fontweight="bold",
    )

    ax.set_xlabel(
        "Zone Type",
        fontsize=11,
    )

    ax.set_ylabel(
        "Average Mean NDVI",
        fontsize=11,
    )

    ax.set_ylim(-1, 1)

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.5,
    )

    plt.xticks(
        rotation=30,
        ha="right",
    )

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    if show:
        plt.show()

    plt.close(fig)

    return output_path


def plot_ndvi_distribution_by_zone(
    ndvi_df: pd.DataFrame,
    output_path: str | Path,
    title: str = "NDVI Distribution by Zone Type",
    figsize: tuple[int, int] = (10, 6),
    show: bool = False,
) -> Path:
    """
    Create a box plot showing the distribution of annual
    NDVI values for each zone type.

    Parameters
    ----------
    ndvi_df : pd.DataFrame
        Raw annual zone-level NDVI results.

    output_path : str or Path
        Destination path for the generated figure.

    title : str, optional
        Plot title.

    figsize : tuple[int, int], optional
        Figure width and height in inches.

    show : bool, optional
        Whether to display the plot interactively.

    Returns
    -------
    Path
        Path to the saved figure.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    required_columns = {
        "zone_type",
        "mean",
    }

    missing_columns = required_columns - set(ndvi_df.columns)

    if missing_columns:
        raise ValueError(
            f"Input DataFrame is missing columns: "
            f"{missing_columns}"
        )

    df = ndvi_df.copy()

    df["mean"] = pd.to_numeric(
        df["mean"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "zone_type",
            "mean",
        ]
    )

    if df.empty:
        raise ValueError(
            "No valid NDVI data available for plotting."
        )

    fig, ax = plt.subplots(
        figsize=figsize,
    )

    df.boxplot(
        column="mean",
        by="zone_type",
        ax=ax,
    )

    # Pandas creates a separate automatic title.
    # Remove it so our own title is used.
    fig.suptitle("")

    ax.set_title(
        title,
        fontsize=14,
        fontweight="bold",
    )

    ax.set_xlabel(
        "Zone Type",
        fontsize=11,
    )

    ax.set_ylabel(
        "Mean NDVI",
        fontsize=11,
    )

    ax.set_ylim(-1, 1)

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.5,
    )

    plt.xticks(
        rotation=30,
        ha="right",
    )

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    if show:
        plt.show()

    plt.close(fig)

    return output_path




# ============================================================
# 6. Spatial NDVI Map Utilities
# ============================================================

def initialize_earth_engine() -> None:
    """
    Initialize the Earth Engine Python API.

    If Earth Engine has not been authenticated on this machine,
    authentication may be required before initialization.
    """

    try:
        ee.Initialize()
    except Exception as error:
        raise RuntimeError(
            "Could not initialize Google Earth Engine. "
            "Run ee.Authenticate() once if necessary."
        ) from error


def create_ee_study_geometry(
    zones: gpd.GeoDataFrame,
) -> ee.Geometry:
    """
    Convert the study zones into one Earth Engine geometry.

    Parameters
    ----------
    zones : geopandas.GeoDataFrame
        Study zones loaded from zones.geojson.

    Returns
    -------
    ee.Geometry
        Union geometry of all study zones.
    """

    if zones.empty:
        raise ValueError(
            "Cannot create study geometry from empty zones."
        )

    ee_zones = ee.FeatureCollection(
        zones.__geo_interface__
    )

    return ee_zones.geometry()


def get_reliable_years(
    processing_metadata_df: pd.DataFrame,
) -> list[int]:
    """
    Return years having valid annual NDVI composites.

    Parameters
    ----------
    processing_metadata_df : pd.DataFrame
        Contents of annual_processing_metadata.csv.

    Returns
    -------
    list[int]
        Sorted list of reliable years.
    """

    required_columns = {
        "year",
        "valid_composite",
    }

    missing_columns = (
        required_columns
        - set(processing_metadata_df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Processing metadata is missing columns: "
            f"{missing_columns}"
        )

    metadata = processing_metadata_df.copy()

    metadata["year"] = pd.to_numeric(
        metadata["year"],
        errors="coerce",
    )

    # Handle boolean values stored as either True/False
    # or as strings in a CSV.
    metadata["valid_composite"] = (
        metadata["valid_composite"]
        .astype(str)
        .str.lower()
        .eq("true")
    )

    metadata = metadata.dropna(
        subset=["year"]
    )

    reliable_years = (
        metadata.loc[
            metadata["valid_composite"],
            "year",
        ]
        .astype(int)
        .sort_values()
        .tolist()
    )

    if not reliable_years:
        raise ValueError(
            "No reliable annual NDVI composites were found."
        )

    return reliable_years


def select_map_years(
    reliable_years: list[int],
) -> dict[str, int]:
    """
    Select earliest, middle, and latest reliable years.

    Parameters
    ----------
    reliable_years : list[int]
        Sorted reliable years.

    Returns
    -------
    dict[str, int]
        Selected map years.
    """

    if not reliable_years:
        raise ValueError(
            "Cannot select map years from an empty list."
        )

    earliest_year = reliable_years[0]
    recent_year = reliable_years[-1]

    middle_index = len(reliable_years) // 2
    middle_year = reliable_years[middle_index]

    return {
        "early": earliest_year,
        "middle": middle_year,
        "recent": recent_year,
    }


def build_annual_ndvi_composites(
    config: dict,
    study_geometry: ee.Geometry,
    years: list[int],
) -> ee.ImageCollection:
    """
    Build annual NDVI composites for selected years.
    """

    satellite_config = config["satellite"]

    dataset_name = satellite_config["primary_dataset"]

    start_month = (
        satellite_config["growing_season_start_month"]
    )

    end_month = (
        satellite_config["growing_season_end_month"]
    )

    collection = load_landsat_from_config(
        study_geometry=study_geometry,
        config=config,
    )

    collection = preprocess_collection(
        collection=collection,
        dataset_name=dataset_name,
    )

    annual_collection = create_annual_ndvi_collection(
        collection=collection,
        years=years,
        start_month=start_month,
        end_month=end_month,
    )

    return annual_collection


def export_ndvi_map(
    image: ee.Image,
    study_geometry: ee.Geometry,
    output_name: str,
    output_directory: str,
    scale: int = 30,
) -> ee.batch.Task:
    """
    Export an NDVI image from Earth Engine to Google Drive.

    Parameters
    ----------
    image : ee.Image
        NDVI image to export.

    study_geometry : ee.Geometry
        Region to export.

    output_name : str
        Name of the exported file.

    output_directory : str
        Google Drive folder name.

    scale : int, optional
        Export resolution in meters.

    Returns
    -------
    ee.batch.Task
        Started Earth Engine export task.
    """

    task = ee.batch.Export.image.toDrive(
        image=image,
        description=output_name,
        folder=output_directory,
        fileNamePrefix=output_name,
        region=study_geometry,
        scale=scale,
        maxPixels=1e13,
        fileFormat="GeoTIFF",
    )

    task.start()

    print(
        f"Started Earth Engine export task: {output_name}"
    )

    return task


def create_spatial_ndvi_maps(
    config: dict,
    processing_metadata_df: pd.DataFrame,
    output_directory: str = "leh_ndvi_maps",
) -> dict[str, int]:
    """
    Create and export early, middle, recent, and change NDVI maps.

    Parameters
    ----------
    config : dict
        Project configuration.

    processing_metadata_df : pd.DataFrame
        Annual processing metadata.

    output_directory : str, optional
        Google Drive folder for exported GeoTIFF files.

    Returns
    -------
    dict[str, int]
        Selected map years.
    """

    initialize_earth_engine()

    zones = load_zones()

    validate_zones(zones)

    study_geometry = create_ee_study_geometry(
        zones
    )

    reliable_years = get_reliable_years(
        processing_metadata_df
    )

    selected_years = select_map_years(
        reliable_years
    )

    print(
        "Selected map years:"
    )

    print(
        f"  Earliest: {selected_years['early']}"
    )

    print(
        f"  Middle:   {selected_years['middle']}"
    )

    print(
        f"  Recent:   {selected_years['recent']}"
    )

    years_to_process = [
        selected_years["early"],
        selected_years["middle"],
        selected_years["recent"],
    ]

    annual_collection = build_annual_ndvi_composites(
        config=config,
        study_geometry=study_geometry,
        years=years_to_process,
    )

    scale = config["analysis"]["scale_meters"]

    early_image = ee.Image(
        annual_collection
        .filter(
            ee.Filter.eq(
                "year",
                selected_years["early"],
            )
        )
        .first()
    )

    middle_image = ee.Image(
        annual_collection
        .filter(
            ee.Filter.eq(
                "year",
                selected_years["middle"],
            )
        )
        .first()
    )

    recent_image = ee.Image(
        annual_collection
        .filter(
            ee.Filter.eq(
                "year",
                selected_years["recent"],
            )
        )
        .first()
    )

    change_image = (
        recent_image
        .subtract(early_image)
        .rename("NDVI_change")
        .set({
            "early_year": selected_years["early"],
            "recent_year": selected_years["recent"],
        })
    )

    export_ndvi_map(
        image=early_image,
        study_geometry=study_geometry,
        output_name=(
            f"ndvi_early_{selected_years['early']}"
        ),
        output_directory=output_directory,
        scale=scale,
    )

    export_ndvi_map(
        image=middle_image,
        study_geometry=study_geometry,
        output_name=(
            f"ndvi_middle_{selected_years['middle']}"
        ),
        output_directory=output_directory,
        scale=scale,
    )

    export_ndvi_map(
        image=recent_image,
        study_geometry=study_geometry,
        output_name=(
            f"ndvi_recent_{selected_years['recent']}"
        ),
        output_directory=output_directory,
        scale=scale,
    )

    export_ndvi_map(
        image=change_image,
        study_geometry=study_geometry,
        output_name=(
            "ndvi_change_"
            f"{selected_years['early']}_"
            f"{selected_years['recent']}"
        ),
        output_directory=output_directory,
        scale=scale,
    )

    return selected_years




# ------------------------------------------------------------
# 7. Statistical Summary
# ------------------------------------------------------------

def create_ndvi_summary(
    df: pd.DataFrame,
    output_path: str | Path,
) -> pd.DataFrame:
    """
    Create a first-vs-last year NDVI summary for each zone.

    The summary describes observed NDVI change between the
    earliest and latest available years. It does not calculate
    a statistical trend or significance test.

    Parameters
    ----------
    df : pandas.DataFrame
        Annual zone-level NDVI results.

    output_path : str or Path
        Destination CSV path.

    Returns
    -------
    pandas.DataFrame
        Summary table.
    """

    required_columns = {
        "year",
        "zone_id",
        "zone_type",
        "name",
        "mean",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns for summary: {sorted(missing)}"
        )

    data = df.copy()

    # Ensure numeric year and mean values.
    data["year"] = pd.to_numeric(
        data["year"],
        errors="coerce",
    )

    data["mean"] = pd.to_numeric(
        data["mean"],
        errors="coerce",
    )

    # Remove rows that cannot contribute to the summary.
    data = data.dropna(
        subset=[
            "year",
            "mean",
            "zone_id",
        ]
    )

    if data.empty:
        raise ValueError(
            "No valid NDVI observations available for summary."
        )

    data["year"] = data["year"].astype(int)

    summary_rows = []

    for zone_id, zone_df in data.groupby(
        "zone_id",
        sort=True,
    ):

        zone_df = zone_df.sort_values("year")

        first_row = zone_df.iloc[0]
        last_row = zone_df.iloc[-1]

        first_ndvi = float(first_row["mean"])
        last_ndvi = float(last_row["mean"])

        change = last_ndvi - first_ndvi

        if first_ndvi != 0:
            change_percent = (
                change / abs(first_ndvi)
            ) * 100.0
        else:
            change_percent = float("nan")

        summary_rows.append(
            {
                "zone_id": zone_id,
                "zone_type": first_row["zone_type"],
                "zone_name": first_row["name"],
                "first_year": int(first_row["year"]),
                "first_mean_ndvi": first_ndvi,
                "last_year": int(last_row["year"]),
                "last_mean_ndvi": last_ndvi,
                "ndvi_change": change,
                "ndvi_change_percent": change_percent,
            }
        )

    summary = pd.DataFrame(summary_rows)

    summary = summary.sort_values(
        by="zone_id",
        kind="stable",
    ).reset_index(drop=True)

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary.to_csv(
        output_path,
        index=False,
    )

    return summary



# ============================================================
# 8. Script Entry Point
# ============================================================

if __name__ == "__main__":

    print("Loading project configuration...")

    RUN_DIR = Path(
            "data/processed/run_20260915_233901"
        )

    VISUALIZATION_DIR = RUN_DIR / "visualizations"
    VISUALIZATION_DIR.mkdir(parents=True, exist_ok=True)

    ndvi_csv_path = (
        RUN_DIR
        / "annual_zone_ndvi.csv"
    )

    metadata_csv_path = (
        RUN_DIR
        / "annual_processing_metadata.csv"
    )

    ndvi_results = load_ndvi_results(
        ndvi_csv_path
    )

    processing_metadata = pd.read_csv(
        metadata_csv_path
    )

    print(
        f"Loaded {len(ndvi_results)} NDVI records."
    )

    # --------------------------------------------------------
    # Annual Zone-wise NDVI Plot
    # --------------------------------------------------------

    print(
        "Creating annual NDVI trend plot..."
    )

    plot_annual_ndvi_trends(
        ndvi_df=ndvi_results,
        output_path=(
            VISUALIZATION_DIR
            / "annual_ndvi_trends.png"
        ),
        show=False,
    )

    # --------------------------------------------------------
    # Comparison and Distribution Plots
    # --------------------------------------------------------

    print(
        "Creating average NDVI comparison plot..."
    )

    plot_average_ndvi_by_zone(
        ndvi_df=ndvi_results,
        output_path=(
            VISUALIZATION_DIR
            / "average_ndvi_by_zone.png"
        ),
        show=False,
    )

    print(
        "Creating NDVI distribution plot..."
    )

    plot_ndvi_distribution_by_zone(
        ndvi_df=ndvi_results,
        output_path=(
            VISUALIZATION_DIR
            / "ndvi_distribution_by_zone.png"
        ),
        show=False,
    )


    # --------------------------------------------------------
    # Summary Table
    # --------------------------------------------------------

    summary_path = RUN_DIR / "summary_statistics.csv"

    summary = create_ndvi_summary(
        df=ndvi_results,
        output_path=summary_path,
    )

    print(summary)
    print(f"Summary saved to: {summary_path}")



    # --------------------------------------------------------
    # EE NDVI map Export Tasks
    # --------------------------------------------------------

    print(
        "Creating spatial NDVI map export tasks..."
    )

    SETTINGS_PATH = RUN_DIR / "settings_snapshot.yaml"
    
    config = load_config(
            SETTINGS_PATH
        )

    validate_config(
            config
        )

    selected_years = create_spatial_ndvi_maps(
        config=config,
        processing_metadata_df=processing_metadata,
        output_directory="leh_ndvi_maps",
    )

    print(
        "\nSpatial map tasks started successfully."
    )

    print(
        f"Selected years: {selected_years}"
    )