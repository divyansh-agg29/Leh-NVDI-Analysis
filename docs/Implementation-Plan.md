# Leh/Ladakh NVDI Study — Programming Implementation Plan

This plan focuses on how to build the project in Python, using a Stage → Phase → Tasks → Deliverables structure.

The goal is to develop a reproducible system that can:

1. Obtain satellite imagery for Leh/Ladakh.

2. Calculate vegetation indices such as NDVI.

3. Compare vegetation change across years.

4. Separate urban, irrigated, plantation, and natural mountain areas.

5. Integrate rainfall and temperature data.

6. Produce maps, graphs, tables, and a final research report.

# Overall Technical Architecture

```
                ┌──────────────────────┐
                │ Study Configuration  │
                │ AOI, dates, zones    │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Data Acquisition     │
                │ Satellite + Climate  │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Data Preprocessing   │
                │ Cloud, snow, masks   │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Vegetation Indices   │
                │ NDVI, EVI, etc.      │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Spatial Analysis     │
                │ Zones, pixels, bands │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Temporal Analysis   │
                │ Annual trends       │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Climate Integration  │
                │ Rainfall + temp      │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Statistical Analysis │
                │ Trends + correlation │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Visualization        │
                │ Maps, plots, reports  │
                └──────────────────────┘
```

# Stage 0 — Define the Programming Scope

## Objective

Convert the research question into a technically manageable software project.

## Phase 0.1 — Define the Minimum Viable Project

Start with the smallest version that can produce a meaningful result.

### Initial MVP

The first working version should:

* Use one satellite dataset.

* Cover Leh and its surrounding area.

* Calculate annual growing-season NDVI.

* Compare at least three land-use zones:

  * Urban/settlement areas.

  * Irrigated/agricultural areas.

  * Natural mountain/barren areas.

* Produce:

  * One NDVI map.

  * One annual NDVI trend graph.

  * One zone-wise comparison.

  * One CSV file containing results.

### MVP output

```
data/
    annual_ndvi.csv

outputs/
    ndvi_map.png
    annual_ndvi_trend.png
    zone_comparison.png
```

## Phase 0.2 — Fix the Initial Technical Stack

Recommended stack:
| Purpose | Tool |
|---|---|
| Programming | Python |
| Satellite processing | Google Earth Engine |
| Earth Engine Python interface | `earthengine-api` |
| Interactive geospatial work | `geemap` |
| Data manipulation | `pandas`, `numpy` |
| Geospatial vector data | `geopandas`, `shapely` |
| Plotting | `matplotlib` |
| Statistics | `scipy`, optionally `statsmodels` |
| Notebook environment | Jupyter or Google Colab |
| Configuration | YAML or JSON |
| Version control | Git |

## Phase 0.3 — Decide the Execution Environment

### Recommended initial approach

Use Google Colab or Jupyter Notebook first.

Reasons:

* Easier Earth Engine authentication.

* Less local dependency trouble.

* Convenient plotting and experimentation.

* Suitable for early satellite-data exploration.

Later, convert stable code into Python modules.

### Deliverable

A short technical specification containing:

* Research objective.

* Initial study area.

* Initial satellite dataset.

* Initial date range.

* Initial zones.

* Python environment choice.

* MVP outputs.

# Stage 1 — Create the Project Foundation

## Objective

Create a clean Python project structure before writing analysis code.

## Phase 1.1 — Create the Repository

Suggested project name:

```
leh-nvdi-analysis
```

Suggested structure:

```
leh-nvdi-analysis/
│
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   ├── settings.yaml
│   └── zones.geojson
│
├── notebooks/
│   ├── 01_environment_check.ipynb
│   ├── 02_data_exploration.ipynb
│   ├── 03_ndvi_experiment.ipynb
│   └── 04_initial_results.ipynb
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── gee_auth.py
│   ├── areas.py
│   ├── satellite.py
│   ├── preprocessing.py
│   ├── indices.py
│   ├── extraction.py
│   ├── climate.py
│   ├── statistics.py
│   ├── visualization.py
│   └── pipeline.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── outputs/
│   ├── maps/
│   ├── figures/
│   ├── tables/
│   └── exports/
│
└── tests/
    ├── test_config.py
    ├── test_indices.py
    └── test_statistics.py
```

## Phase 1.2 — Create the Environment

Install the initial dependencies:

Bash

```
pip install earthengine-api geemap
pip install pandas numpy matplotlib scipy
pip install geopandas shapely pyproj rasterio
pip install pyyaml jupyter
```

Create a `requirements.txt`:

```
earthengine-api
geemap
pandas
numpy
matplotlib
scipy
geopandas
shapely
pyproj
rasterio
pyyaml
jupyter
```

## Phase 1.3 — Verify the Environment

Create a basic environment-check notebook.

Test:

* Python version.

* Imports.

* Earth Engine authentication.

* Earth Engine initialization.

* Map display.

* Basic geometry creation.

Example test:

Python

Run

```
import ee

ee.Authenticate()
ee.Initialize(project="YOUR_GCP_PROJECT")
```

### Deliverable

A notebook proving that:

* Python works.

* Required packages import successfully.

* Earth Engine connects.

* A basic map can be displayed.

# Stage 2 — Build the Configuration System

## Objective

Avoid hardcoding dates, coordinates, datasets, and thresholds inside the analysis code.

## Phase 2.1 — Create `settings.yaml`

Example:

YAML

```
project:
  name: "leh-nvdi-analysis"
  timezone: "Asia/Kolkata"

study:
  name: "Leh and surrounding region"

satellite:
  primary_dataset: "LANDSAT/LC08/C02/T1_L2"
  start_year: 1984
  end_year: 2025
  growing_season_start_month: 5
  growing_season_end_month: 10

analysis:
  cloud_cover_limit: 40
  scale_meters: 30
  ndvi_min: -1
  ndvi_max: 1

outputs:
  export_csv: true
  export_maps: true
  export_figures: true
```

The actual date range should be adjusted after dataset feasibility testing.

## Phase 2.2 — Build `src/config.py`

Responsibilities:

* Load YAML configuration.

* Validate required fields.

* Convert values into convenient Python objects.

* Provide a single configuration interface.

Example interface:

Python

Run

```
from src.config import load_config

config = load_config("config/settings.yaml")

print(config["satellite"]["primary_dataset"])
```

## Phase 2.3 — Add Configuration Validation

Validate:

* Start year is before end year.

* Month values are between 1 and 12.

* Cloud threshold is between 0 and 100.

* Scale is positive.

* Dataset name is not empty.

### Deliverable

All notebooks and modules should obtain settings from one configuration file.

# Stage 3 — Define and Load the Study Areas

## Objective

Create the geographical boundaries required for the analysis.

## Phase 3.1 — Define the Main Area of Interest

Create an initial polygon covering:

* Leh town.

* Nearby settlements.

* Surrounding mountain slopes.

* Nearby valleys and agricultural areas.

Do not make the initial region unnecessarily large.

The first area should be small enough for fast experimentation.

## Phase 3.2 — Create Zone Boundaries

Create separate polygons for:

```
Zone A — Urban/settlement area
Zone B — Irrigated/agricultural area
Zone C — Natural valley vegetation
Zone D — Natural mountain slopes
Zone E — Plantation/restoration area
```

Some zones may initially be unavailable. Start with the three most reliable zones:

1. Urban.

2. Irrigated/agricultural.

3. Natural mountain/barren.

## Phase 3.3 — Store Zones as GeoJSON

Example:

```
config/zones.geojson
```

Each feature should contain properties such as:

JSON

```
{
  "zone_id": "urban_01",
  "zone_type": "urban",
  "name": "Leh urban area"
}
```

## Phase 3.4 — Build `src/areas.py`

Responsibilities:

* Load GeoJSON.

* Convert it to Earth Engine geometries.

* Return zones by type.

* Validate geometry.

* Calculate area.

* Display zones on a map.

Suggested functions:

Python

Run

```
def load_zones(path):
    pass

def get_zone(zones, zone_id):
    pass

def zones_to_ee(zones):
    pass

def calculate_zone_area(zone):
    pass

def plot_zones(zones):
    pass
```

### Deliverable

A map showing the complete study area and each analysis zone in different colors.

# Stage 4 — Build the Satellite Data Layer

## Objective

Create reusable functions for retrieving satellite imagery.

## Phase 4.1 — Select the First Satellite Dataset

Start with one dataset.

Possible strategy:

* Use Landsat for long-term historical analysis.

* Use Sentinel-2 for higher-resolution recent analysis.

* Use MODIS for long, consistent vegetation-index time series.

For the first implementation, choose the dataset that best balances:

* Historical coverage.

* Spatial resolution.

* Processing complexity.

* Availability of cloud and snow masks.

Do not implement all datasets simultaneously.

## Phase 4.2 — Build the Image Collection Loader

Create `src/satellite.py`.

Suggested interface:

Python

Run

```
def get_image_collection(
    dataset_name,
    geometry,
    start_date,
    end_date,
    cloud_limit=None
):
    pass
```

Responsibilities:

* Load the Earth Engine image collection.

* Filter by date.

* Filter by geometry.

* Filter by cloud cover.

* Return the filtered collection.

## Phase 4.3 — Add Dataset-Specific Band Mapping

Different satellite datasets use different band names.

Create a mapping:

Python

Run

```
BAND_MAP = {
    "landsat_8": {
        "red": "SR_B4",
        "nir": "SR_B5",
        "qa": "QA_PIXEL"
    },
    "sentinel_2": {
        "red": "B4",
        "nir": "B8",
        "qa": "QA60"
    }
}
```

The exact bands should be verified for the selected collection.

## Phase 4.4 — Inspect the Collection

Before calculating NDVI, inspect:

* Number of images.

* Date range.

* Cloud percentage.

* Available bands.

* Image footprints.

* Seasonal availability.

Suggested exploratory outputs:

```
Total images: ...
Images per year: ...
Images during growing season: ...
```

### Deliverable

A reusable function that returns a filtered satellite collection for any specified period and geometry.

# Stage 5 — Build the Preprocessing Pipeline

## Objective

Clean satellite imagery before calculating vegetation indices.

This stage is critical because Leh/Ladakh contains:

* Snow.

* Bare rock.

* Bright soil.

* Clouds.

* Shadows.

* Sparse vegetation.

* Strong seasonal variation.

## Phase 5.1 — Cloud and Shadow Masking

Create `src/preprocessing.py`.

Suggested function:

Python

Run

```
def mask_clouds(image, dataset_name):
    pass
```

Tasks:

* Identify cloud pixels.

* Identify cloud-shadow pixels where supported.

* Mask invalid pixels.

* Preserve image metadata.

## Phase 5.2 — Snow and Seasonal Masking

Snow can create misleading vegetation signals.

Implement:

* Snow masking if a reliable snow band or classification is available.

* Seasonal filtering.

* Optional exclusion of winter months.

* Minimum valid-pixel requirements.

Suggested function:

Python

Run

```
def mask_snow(image, dataset_name):
    pass
```

## Phase 5.3 — Surface Reflectance Scaling

Some datasets store reflectance as scaled integers.

Implement a dataset-specific scaling function:

Python

Run

```
def apply_reflectance_scaling(image, dataset_name):
    pass
```

## Phase 5.4 — Create a Clean Collection

Build a pipeline:

Python

Run

```
def preprocess_collection(collection, dataset_name):
    collection = collection.map(
        lambda image: mask_clouds(image, dataset_name)
    )

    collection = collection.map(
        lambda image: mask_snow(image, dataset_name)
    )

    collection = collection.map(
        lambda image: apply_reflectance_scaling(image, dataset_name)
    )

    return collection
```

## Phase 5.5 — Validate the Masks

Compare imagery:

```
Before masking
        ↓
After cloud masking
        ↓
After snow masking
        ↓
Final usable imagery
```

### Deliverable

A clean image collection and visual comparison showing that clouds, shadows, and snow are being handled reasonably.

# Stage 6 — Implement Vegetation Indices

## Objective

Calculate vegetation indices from satellite bands.

## Phase 6.1 — Implement NDVI

Formula:

NDVI=NIR−RedNIR+RedNDVI = \frac{NIR - Red}{NIR + Red}NDVI=NIR+RedNIR−Red

Create `src/indices.py`.

Suggested function:

Python

Run

```
def add_ndvi(image, red_band, nir_band):
    ndvi = image.normalizedDifference(
        [nir_band, red_band]
    ).rename("NDVI")

    return image.addBands(ndvi)
```

## Phase 6.2 — Implement EVI Later

Enhanced Vegetation Index can be useful in areas with:

* Dense vegetation.

* Soil background effects.

* Atmospheric influence.

But do not make EVI part of the first MVP.

Suggested future interface:

Python

Run

```
def add_evi(image, red_band, nir_band, blue_band):
    pass
```

## Phase 6.3 — Add Metadata

Every image should retain:

* Acquisition date.

* Year.

* Month.

* Day of year.

* Image ID.

* Cloud percentage.

Suggested function:

Python

Run

```
def add_time_metadata(image):
    pass
```

## Phase 6.4 — Create Seasonal Composites

For each year:

1. Filter images to the growing season.

2. Calculate NDVI.

3. Create a median or percentile composite.

4. Store the year as metadata.

Suggested interface:

Python

Run

```
def create_annual_ndvi_composite(
    collection,
    year,
    start_month,
    end_month
):
    pass
```

Possible composite methods:

| Composite | Use |
|---|---|
| Median | General robust annual estimate |
| Maximum NDVI | Peak vegetation signal |
| 90th percentile | Peak but less sensitive to outliers |
| Mean | Average seasonal condition |

Start with median NDVI and later compare it with maximum NDVI.

### Deliverable

A collection of annual NDVI images:

```
1984 NDVI
1985 NDVI
1986 NDVI
...
2025 NDVI
```

# Stage 7 — Build the Spatial Extraction System

## Objective

Convert satellite images into numerical data for each zone.

## Phase 7.1 — Calculate Zone Statistics

For every year and zone, calculate:

* Mean NDVI.

* Median NDVI.

* Standard deviation.

* Minimum NDVI.

* Maximum NDVI.

* Valid pixel count.

* Percentage of valid pixels.

Suggested function:

Python

Run

```
def calculate_zone_statistics(
    image,
    zones,
    scale,
    reducer
):
    pass
```

## Phase 7.2 — Use Multiple Reducers

Start with:

Python

Run

```
ee.Reducer.mean()
```

Later combine reducers:

Python

Run

```
ee.Reducer.mean().combine(
    reducer2=ee.Reducer.median(),
    sharedInputs=True
)
```

Additional reducers can be added later.

## Phase 7.3 — Convert Earth Engine Results to Pandas

Create `src/extraction.py`.

Suggested functions:

Python

Run

```
def extract_image_statistics(image, zones, scale):
    pass

def extract_collection_statistics(collection, zones, scale):
    pass

def results_to_dataframe(results):
    pass
```

Expected dataframe structure:

| Year | Zone ID | Zone Type | Mean NDVI | Median NDVI | Pixel Count |
|---|---|---|---|---|---|
| 2000 | urban_01 | urban | 0.31 | 0.29 | 120 |
| 2000 | natural_01 | natural | 0.08 | 0.07 | 240 |
| 2001 | urban_01 | urban | 0.34 | 0.32 | 120 |

## Phase 7.4 — Export Intermediate Results

Save:

```
data/processed/annual_zone_ndvi.csv
```

Also export:

```
data/processed/annual_zone_ndvi.parquet
```

Parquet is useful for preserving data types and handling larger datasets.

### Deliverable

A clean tabular dataset containing annual NDVI statistics for every zone.

# Stage 8 — Build the First End-to-End MVP Pipeline

## Objective

Connect the individual modules into one complete workflow.

## Phase 8.1 — Create `src/pipeline.py`

The pipeline should execute:

```
Load config
    ↓
Load study area
    ↓
Load zones
    ↓
Load satellite collection
    ↓
Preprocess imagery
    ↓
Add NDVI
    ↓
Create annual composites
    ↓
Extract zone statistics
    ↓
Export CSV
```

Suggested interface:

Python

Run

```
def run_ndvi_pipeline(config_path):
    pass
```

## Phase 8.2 — Add a Command-Line Entry Point

Example:

Bash

```
python -m src.pipeline
```

Optional arguments:

Bash

```
python -m src.pipeline \
    --config config/settings.yaml \
    --start-year 2000 \
    --end-year 2025
```

## Phase 8.3 — Add Logging

Use Python's `logging` module.

Log:

* Configuration loaded.

* Earth Engine initialized.

* Number of images found.

* Number of images per year.

* Processing year.

* Export status.

* Errors and warnings.

Example:

```
INFO - Loaded configuration
INFO - Study area loaded
INFO - Found 428 satellite images
INFO - Processing year 2001
INFO - Extracted statistics for 5 zones
INFO - Export completed
```

### Deliverable

One command that runs the initial NDVI analysis and produces a CSV file.

# Stage 9 — Create the Visualization Layer

## Objective

Turn numerical results into understandable visual outputs.

Create `src/visualization.py`.

## Phase 9.1 — Annual Trend Graph

Plot:

* Year on the x-axis.

* Mean NDVI on the y-axis.

* One line per zone type.

Required graph:

```
Annual NDVI trend:
    Urban
    Irrigated
    Natural valley
    Natural mountain
```

## Phase 9.2 — Compare Zones

Create:

* Box plots.

* Violin plots if enough data exists.

* Bar charts of average NDVI.

* Difference plots.

Examples:

```
Urban NDVI - Natural NDVI
Irrigated NDVI - Natural NDVI
Mountain NDVI trend
```

## Phase 9.3 — Create Spatial NDVI Maps

For selected years, export maps for:

* Earliest reliable year.

* Middle year.

* Most recent year.

Also create a change map:

ΔNDVI=NDVIrecent−NDVIearly\Delta NDVI = NDVI_{recent} - NDVI_{early}ΔNDVI=NDVIrecent−NDVIearly

## Phase 9.4 — Create Statistical Summary Tables

Example:

| Zone | First-year NDVI | Last-year NDVI | Difference | Trend |
|---|---|---|---|---|
| Urban | ... | ... | ... | ... |
| Irrigated | ... | ... | ... | ... |
| Natural mountain | ... | ... | ... | ... |

### Deliverable

A complete first visual report containing:

* Annual trend plot.

* Zone comparison plot.

* NDVI change map.

* Summary CSV.

# Stage 10 — Implement Climate Data Integration

## Objective

Determine whether vegetation changes are associated with rainfall, temperature, or both.

## Phase 10.1 — Create the Climate Data Module

Create:

```
src/climate.py
```

Suggested responsibilities:

* Load rainfall data.

* Load temperature data.

* Filter to study area.

* Aggregate by year and season.

* Export climate statistics.

Suggested interface:

Python

Run

```
def load_rainfall_data(dataset_name, geometry, start_date, end_date):
    pass

def load_temperature_data(dataset_name, geometry, start_date, end_date):
    pass

def aggregate_climate_by_year(collection):
    pass
```

## Phase 10.2 — Calculate Annual Climate Variables

For each year, calculate:

* Annual rainfall.

* Growing-season rainfall.

* Mean annual temperature.

* Growing-season temperature.

* Number of wet days if available.

* Extreme rainfall indicators if available.

Expected dataframe:
| Year | Rainfall (mm) | Mean Temperature (°C) | Growing Season Rainfall |
|---|---|---|---|
| 2000 | ... | ... | ... |
| 2001 | ... | ... | ... |

## Phase 10.3 — Merge Climate and NDVI Data

Merge on:

Python

Run

```
merged = ndvi_df.merge(
    climate_df,
    on="year",
    how="inner"
)
```

For zone-specific analysis:

Python

Run

```
merged = ndvi_df.merge(
    climate_df,
    on=["year"],
    how="left"
)
```

## Phase 10.4 — Add Lagged Climate Variables

Vegetation may respond to previous-season conditions.

Create:

```
rainfall_current_year
rainfall_previous_year
temperature_current_year
temperature_previous_year
```

Example:

Python

Run

```
df["rainfall_lag_1"] = df["rainfall_mm"].shift(1)
```

### Deliverable

A combined dataset containing:

* Annual NDVI.

* Rainfall.

* Temperature.

* Optional lagged climate variables.

# Stage 11 — Implement Statistical Analysis

## Objective

Estimate whether the observed changes are meaningful and whether climate variables explain them.

Create `src/statistics.py`.

## Phase 11.1 — Calculate Linear Trends

For each zone:

NDVIt=a+btNDVI_t = a + btNDVIt=a+bt

Where:

* ttt = year.

* bbb = annual NDVI trend.

* aaa = intercept.

Calculate:

* Slope.

* Intercept.

* Correlation coefficient.

* p-value.

* Number of observations.

Suggested interface:

Python

Run

```
def calculate_linear_trend(years, values):
    pass
```

## Phase 11.2 — Calculate Climate Correlations

Calculate:

* NDVI vs rainfall.

* NDVI vs temperature.

* NDVI vs previous-year rainfall.

* NDVI vs growing-season rainfall.

Use:

* Pearson correlation for linear association.

* Spearman correlation for monotonic association.

## Phase 11.3 — Compare Different Zone Types

Questions to test:

* Is urban NDVI increasing faster than natural mountain NDVI?

* Is irrigated NDVI consistently higher than natural NDVI?

* Are natural areas showing a statistically meaningful trend?

* Does the trend remain after excluding settlement zones?

## Phase 11.4 — Add Robustness Tests

Repeat the analysis using:

* Different growing-season definitions.

* Median vs maximum NDVI.

* Different cloud thresholds.

* Different spatial scales.

* Different start and end years.

* Different zone boundaries.

### Deliverable

A statistical summary table:
| Zone             | Trend slope | p-value | Rainfall correlation | Temperature correlation |
|------------------|-------------|---------|----------------------|-------------------------|
| Urban            | ...         | ...     | ...                  | ...                     |
| Irrigated        | ...         | ...     | ...                  | ...                     |
| Natural valley   | ...         | ...     | ...                  | ...                     |
| Natural mountain | ...         | ...     | ...                  | ...                     |

# Stage 12 — Separate Natural and Human-Managed Greening

## Objective

Avoid treating every increase in NDVI as natural ecological recovery.

## Phase 12.1 — Add Land-Cover Data

Potential categories:

```
Built-up
Agriculture
Natural barren land
Natural grass/shrub
Water
Snow/ice
Plantation
```

Use land-cover information to mask or classify zones.

## Phase 12.2 — Add Distance-Based Analysis

Calculate vegetation change as a function of distance from settlements.

Example distance bands:

```
0–500 m from settlement
500–1000 m
1000–2000 m
2000–5000 m
More than 5000 m
```

This can reveal whether greening is concentrated around human settlements.

## Phase 12.3 — Add Elevation-Based Analysis

Use a DEM to divide the area into elevation bands:

```
Lower valley
Middle slopes
Upper slopes
High mountain terrain
```

Then compare NDVI trends by elevation.

## Phase 12.4 — Add Irrigation/Water Proximity

If reliable waterway or irrigation data is available, calculate:

* Distance from rivers.

* Distance from canals.

* Distance from lakes/wetlands.

* Distance from known irrigated areas.

### Deliverable

A more defensible classification:

```
Likely human-managed greening
Likely natural vegetation change
Uncertain/mixed signal
```

# Stage 13 — Add Validation and Quality Control

## Objective

Check whether the results are physically and scientifically believable.

## Phase 13.1 — Visual Validation

Inspect selected locations manually.

For each location, compare:

* Satellite image.

* NDVI image.

* Land-cover classification.

* Historical imagery if available.

## Phase 13.2 — Compare Multiple Satellite Sources

For recent years, compare:

* Landsat NDVI.

* Sentinel-2 NDVI.

* MODIS NDVI.

The goal is not to force identical values, but to check whether the spatial and temporal patterns are consistent.

## Phase 13.3 — Check Seasonal Bias

Run the analysis with:

```
May–September
June–August
May–October
June–September
```

If the trend changes significantly, document it.

## Phase 13.4 — Check Missing Data

Identify years with:

* Too few images.

* Excessive cloud cover.

* Excessive snow.

* Low valid-pixel coverage.

Create a quality table:



| Year | Image count | Valid pixel percentage | Quality |
| ---  | --- | --- | --- |
| 2000 | ... | ... | Good|
| 2001 | ... | ... | Poor|
| 2002 | ... | ... | Good|

## Phase 13.5 — Add Automated Tests

Test pure Python functions such as:

* NDVI calculation logic.

* Configuration validation.

* Year generation.

* Dataframe merging.

* Trend calculations.

* Missing-data handling.

Do not attempt to unit-test every Earth Engine server-side operation initially.

### Deliverable

A quality-control report documenting:

* Missing years.

* Data limitations.

* Cross-dataset consistency.

* Sensitivity to analysis choices.

# Stage 14 — Optimize the Pipeline

## Objective

Make the project faster, cheaper, and easier to rerun.

## Phase 14.1 — Reduce Repeated Earth Engine Requests

Avoid repeatedly calling `.getInfo()` inside loops.

Prefer:

* Batch extraction.

* Server-side operations.

* Export tasks.

* One request per collection where possible.

## Phase 14.2 — Cache Intermediate Data

Save:

```
annual_zone_ndvi.csv
annual_climate.csv
merged_analysis_data.csv
```

Before recomputing, check whether the file already exists.

## Phase 14.3 — Add Pipeline Flags

Example:

Bash

```
python -m src.pipeline --stage satellite
python -m src.pipeline --stage ndvi
python -m src.pipeline --stage climate
python -m src.pipeline --stage statistics
python -m src.pipeline --stage all
```

## Phase 14.4 — Add Dry-Run Mode

A dry run should:

* Load configuration.

* Validate zones.

* Check date range.

* Count available images.

* Avoid expensive exports.

Example:

Bash

```
python -m src.pipeline --dry-run
```

### Deliverable

A reproducible pipeline that can be rerun without manually editing notebooks.

# Stage 15 — Produce the Final Research Outputs

## Objective

Convert the programming outputs into a research-ready package.

## Phase 15.1 — Final Data Products

Create:

```
outputs/exports/
    annual_ndvi_by_zone.csv
    annual_climate.csv
    merged_ndvi_climate.csv
    trend_statistics.csv
    data_quality.csv
```

## Phase 15.2 — Final Figures

Create:

```
outputs/figures/
    study_area_map.png
    zone_map.png
    annual_ndvi_trends.png
    rainfall_trend.png
    temperature_trend.png
    ndvi_vs_rainfall.png
    ndvi_vs_temperature.png
    natural_vs_managed_comparison.png
    ndvi_change_map.png
```

## Phase 15.3 — Final Report Structure

```
1. Introduction
2. Research Questions
3. Study Area
4. Data Sources
5. Programming Methodology
6. Satellite Preprocessing
7. NDVI Calculation
8. Spatial Analysis
9. Temporal Analysis
10. Climate Integration
11. Statistical Results
12. Natural vs Human-Managed Greening
13. Limitations
14. Conclusions
15. Reproducibility Instructions
```

## Phase 15.4 — Reproducibility Documentation

The README should explain:

* How to install dependencies.

* How to authenticate Earth Engine.

* Where to configure the project.

* How to run the pipeline.

* How to reproduce the figures.

* Which datasets were used.

* Which years were excluded.

* What assumptions were made.

### Final deliverable

A repository where another person can:

Bash

```
git clone <repository>
pip install -r requirements.txt
python -m src.pipeline
```

and reproduce the main analysis.

