
from pathlib import Path

import yaml


def load_config(config_path):
    """
    Load project configuration from a YAML file.

    Parameters
    ----------
    config_path : str or Path
        Path to the YAML configuration file.

    Returns
    -------
    dict
        Configuration loaded from the YAML file.
    """

    config_path = Path(config_path)

    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config



def validate_config(config):
    """
    Validate project configuration.

    Parameters
    ----------
    config : dict
        Configuration loaded from YAML.

    Returns
    -------
    bool
        True if the configuration is valid.

    Raises
    ------
    ValueError
        If any configuration value is invalid.
    """

    # --------------------------------------------------------
    # 1. Validate required top-level sections
    # --------------------------------------------------------

    required_sections = [
        "project",
        "study",
        "satellite",
        "analysis",
        "outputs",
    ]

    for section in required_sections:

        if section not in config:
            raise ValueError(
                f"Missing required configuration section: '{section}'"
            )

    # --------------------------------------------------------
    # 2. Validate satellite configuration
    # --------------------------------------------------------

    satellite = config["satellite"]

    required_satellite_fields = [
        "primary_dataset",
        "start_year",
        "end_year",
        "growing_season_start_month",
        "growing_season_end_month",
    ]

    for field in required_satellite_fields:

        if field not in satellite:
            raise ValueError(
                f"Missing required satellite setting: '{field}'"
            )

    # Dataset name must not be empty
    dataset = satellite["primary_dataset"]

    if not isinstance(dataset, str) or not dataset.strip():
        raise ValueError(
            "Satellite dataset name must not be empty."
        )

    # --------------------------------------------------------
    # 3. Validate years
    # --------------------------------------------------------

    start_year = satellite["start_year"]
    end_year = satellite["end_year"]

    if not isinstance(start_year, int):
        raise ValueError(
            "Start year must be an integer."
        )

    if not isinstance(end_year, int):
        raise ValueError(
            "End year must be an integer."
        )

    if start_year >= end_year:
        raise ValueError(
            "Start year must be before end year."
        )

    # --------------------------------------------------------
    # 4. Validate months
    # --------------------------------------------------------

    start_month = satellite[
        "growing_season_start_month"
    ]

    end_month = satellite[
        "growing_season_end_month"
    ]

    if not isinstance(start_month, int):
        raise ValueError(
            "Growing season start month must be an integer."
        )

    if not isinstance(end_month, int):
        raise ValueError(
            "Growing season end month must be an integer."
        )

    if not 1 <= start_month <= 12:
        raise ValueError(
            "Growing season start month must be between 1 and 12."
        )

    if not 1 <= end_month <= 12:
        raise ValueError(
            "Growing season end month must be between 1 and 12."
        )

    # --------------------------------------------------------
    # 5. Validate analysis configuration
    # --------------------------------------------------------

    analysis = config["analysis"]

    required_analysis_fields = [
        "cloud_cover_limit",
        "scale_meters",
        "ndvi_min",
        "ndvi_max",
    ]

    for field in required_analysis_fields:

        if field not in analysis:
            raise ValueError(
                f"Missing required analysis setting: '{field}'"
            )

    cloud_limit = analysis["cloud_cover_limit"]

    if not isinstance(cloud_limit, (int, float)):
        raise ValueError(
            "Cloud cover limit must be a number."
        )

    if not 0 <= cloud_limit <= 100:
        raise ValueError(
            "Cloud cover limit must be between 0 and 100."
        )

    scale = analysis["scale_meters"]

    if not isinstance(scale, (int, float)):
        raise ValueError(
            "Scale must be a number."
        )

    if scale <= 0:
        raise ValueError(
            "Scale must be positive."
        )

    # --------------------------------------------------------
    # 6. Validate NDVI range
    # --------------------------------------------------------

    ndvi_min = analysis["ndvi_min"]
    ndvi_max = analysis["ndvi_max"]

    if ndvi_min >= ndvi_max:
        raise ValueError(
            "NDVI minimum must be less than NDVI maximum."
        )

    # --------------------------------------------------------
    # 7. If all checks pass
    # --------------------------------------------------------

    return True