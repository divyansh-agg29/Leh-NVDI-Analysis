from pathlib import Path
import geopandas as gpd

# Project root:
# src/areas.py -> src -> project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

ZONES_PATH = PROJECT_ROOT / "config" / "zones.geojson"


def load_zones(path: Path = ZONES_PATH) -> gpd.GeoDataFrame:
    """
    Load the study-area GeoJSON file.

    Parameters
    ----------
    path : Path
        Path to the zones GeoJSON file.

    Returns
    -------
    geopandas.GeoDataFrame
        Loaded study areas.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Zones file not found: {path}"
        )

    zones = gpd.read_file(path)

    return zones


def plot_zones(
    zones: gpd.GeoDataFrame,
) -> None:
    """
    Display all study zones on a simple map.
    """

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(
        figsize=(10, 8)
    )

    zones.plot(
        ax=ax,
        column="zone_type",
        legend=True,
        edgecolor="black",
        alpha=0.6,
    )

    ax.set_title(
        "Leh Study Area and Analysis Zones"
    )

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    plt.tight_layout()
    plt.show()



def validate_zones(zones: gpd.GeoDataFrame) -> None:
    """
    Validate the basic structure of the study-area GeoDataFrame.
    """

    required_columns = {
        "zone_id",
        "zone_type",
        "name",
        "geometry",
    }

    missing_columns = required_columns - set(zones.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if zones.empty:
        raise ValueError("The zones file contains no features.")

    if zones.geometry.is_empty.any():
        raise ValueError(
            "One or more geometries are empty."
        )

    if zones.geometry.is_valid.all() is False:
        raise ValueError(
            "One or more geometries are invalid."
        )


def get_zone(
    zones: gpd.GeoDataFrame,
    zone_id: str,
) -> gpd.GeoDataFrame:
    """
    Return a zone by its zone_id.
    """

    selected = zones[zones["zone_id"] == zone_id]

    if selected.empty:
        raise KeyError(
            f"Zone not found: {zone_id}"
        )

    return selected



def calculate_areas(
    zones: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Calculate area of each zone in hectares and square kilometers.

    The input GeoDataFrame is expected to use EPSG:4326.
    """

    # Project to a CRS with meter-based units.
    # EPSG:32643 = WGS 84 / UTM zone 43N.
    projected = zones.to_crs(epsg=32643)

    result = zones.copy()

    result["area_m2"] = projected.geometry.area
    result["area_ha"] = result["area_m2"] / 10_000
    result["area_km2"] = result["area_m2"] / 1_000_000

    return result


if __name__ == "__main__":

    print("Loading study areas...")

    zones = load_zones()

    print("Validating study areas...")

    validate_zones(zones)

    print("\nCalculating zone areas...")

    zones = calculate_areas(zones)

    print("\nStudy areas loaded successfully!")
    print(f"Number of features: {len(zones)}")

    print("\nAvailable zones:")

    print(
        zones[
            [
                "zone_id",
                "zone_type",
                "name",
                "area_ha",
                "area_km2",
            ]
        ].to_string(index=False)
    )

    print("\nCRS:")
    print(zones.crs)

    print("\nTesting zone lookup...")

    urban_zone = get_zone(
        zones,
        "urban_01",
    )

    print(
        urban_zone[
            [
                "zone_id",
                "name",
                "area_km2",
            ]
        ].to_string(index=False)
    )

    print("\nDisplaying study area map...")

    plot_zones(zones)