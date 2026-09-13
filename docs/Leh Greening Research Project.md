# Leh Greening Research Project

## Satellite-Based Analysis of Vegetation Change, Climate and Human Land Use

**Project type:** Independent environmental research / Python data science project  
**Study region:** Leh, Ladakh, India  
**Primary tools:** Python, Google Earth Engine, satellite remote sensing, climate datasets  
**Historical study period:** Flexible — longest reliable data period available  
**Initial approach:** Start with a small working analysis, then expand into a scientifically defensible research study.

---

# 1. Project Aim

## 1.1 Primary Aim

To investigate how vegetation in and around Leh, Ladakh has changed over the longest reliable historical period available, using satellite vegetation data, rainfall records, temperature records and land-use information.

The study will distinguish between:

1. Greening within Leh town and other human-managed areas.
2. Vegetation changes on surrounding natural mountain slopes.
3. Vegetation changes in irrigated agricultural and river-valley areas.
4. Changes associated with government plantations and other human interventions.
5. Natural vegetation recovery or degradation.
6. Climate-related influences, particularly rainfall and temperature.

The ultimate objective is to understand whether observed greening represents ecological recovery, human-managed vegetation expansion, climate-driven change, or a combination of these processes.

## 1.2 Broader Research Question

> Has Leh and its surrounding natural landscape become greener over time, and what are the likely causes and ecological implications of that change?

## 1.3 Environmental Context

Leh is located in a high-altitude cold-desert environment. Its landscape includes natural barren terrain, alpine vegetation, shrubs, grasslands, riverine vegetation, irrigated agriculture and human-created tree cover.

The project will avoid assuming that:

- More trees always mean a healthier ecosystem.
- More rainfall is always beneficial.
- More NDVI automatically means ecological recovery.
- A barren landscape is necessarily degraded.
- A successful plantation is necessarily a successful restoration project.

The study will treat vegetation change as an ecological phenomenon that must be interpreted in its local environmental context.

---

# 2. Project Overview

## 2.1 Background

The project originates from personal observations of increasing greenery in Leh and nearby mountain areas over approximately the last 15 years.

Observed changes include:

- Greater tree cover within Leh town.
- More visible greenery during summer.
- Apparent increases in shrubs and small grass on some mountain slopes.
- Perceived increases in rainfall frequency and abundance.
- Government-led plantation and greening efforts.

These observations raise several questions:

- Is the region actually becoming greener?
- Did greening begin recently, or has it been occurring for decades?
- Is the trend limited to irrigated settlements?
- Are natural mountain slopes also showing a measurable increase in vegetation?
- Is climate change contributing to the trend?
- Are human interventions helping or damaging native ecosystems?
- Can we identify areas where vegetation has declined?

## 2.2 Core Approach

The project will combine four main data sources.

| Data source | Purpose |
|---|---|
| Satellite imagery | Measure historical vegetation change. |
| Rainfall data | Investigate precipitation trends and relationships with vegetation. |
| Temperature data | Investigate warming and growing-season changes. |
| Land-use and ecological information | Separate natural vegetation from irrigation, agriculture, plantations and development. |

The study will be performed primarily through Google Earth Engine and Python.

## 2.3 Why a Flexible Historical Period?

The initial 15-year period is useful because it matches personal observations, but it should not be treated as a fixed scientific boundary.

Different datasets have different historical availability:

- MODIS provides a long vegetation record.
- Landsat provides detailed spatial imagery over several decades.
- Sentinel-2 provides higher-resolution imagery from 2015 onward.
- Climate datasets may extend much further back.
- Historical land-use records may be more limited.

The project will therefore define the study period based on data availability and quality.

### Proposed historical coverage

| Period | Role |
|---|---|
| Longest available satellite record | Main long-term vegetation context. |
| 2000 onward, if supported by selected datasets | Useful comparison period for long-term trends. |
| Approximately 2011 onward | Detailed comparison aligned with personal observations. |
| Most recent complete growing season | Latest comparable observations, subject to data availability. |

The final dates will be selected after examining the datasets.

---

# 3. Research Questions

## 3.1 Primary Questions

### RQ1 — Has Leh become greener?

Has average vegetation cover or vegetation productivity increased within the Leh urban area over the available historical period?

### RQ2 — Have natural mountain slopes become greener?

Have surrounding natural mountain slopes experienced measurable increases or decreases in vegetation?

### RQ3 — Is greening different between land-use types?

How do vegetation trends compare between:

- Urban areas.
- Irrigated agricultural land.
- River valleys.
- Natural mountain slopes.
- Government plantation areas.
- Other relevant land-use categories.

### RQ4 — What role has rainfall played?

Has precipitation changed over time, and is it associated with vegetation trends?

### RQ5 — What role has temperature played?

Have temperature changes affected vegetation productivity, growing-season length or the distribution of vegetation?

### RQ6 — Is the observed greening ecological recovery?

Does increased satellite vegetation correspond to:

- Native vegetation recovery?
- Increased tree plantations?
- Irrigated agriculture?
- Changes in grazing pressure?
- Changes in soil moisture?
- Other land-use changes?

### RQ7 — Are there areas where vegetation has declined?

Is greening uniform, or are some parts of the landscape becoming less vegetated?

### RQ8 — What are the ecological implications?

Can the observed changes be interpreted as beneficial, harmful or mixed from the perspective of Ladakh's natural ecosystems?

---

# 4. Project Scope

## 4.1 Included

- Historical satellite vegetation analysis.
- NDVI-based vegetation trend analysis.
- Optional EVI and other indices where justified.
- Rainfall and temperature analysis.
- Urban versus natural landscape comparison.
- Irrigated versus non-irrigated vegetation comparison.
- Land-use classification and masking.
- Spatial vegetation trend maps.
- Seasonal and annual comparisons.
- Basic statistical analysis.
- Literature review.
- Reproducible Python code.
- Research report with limitations.

## 4.2 Optional Extensions

- Historical land-use change mapping.
- Snow cover and snow persistence.
- Soil moisture analysis.
- Elevation-based vegetation analysis.
- Grazing pressure investigation.
- River and wetland vegetation analysis.
- Field photographs and GPS observations.
- Local interviews with residents or farmers.
- Comparison with other Ladakh valleys.
- Comparison with another cold-desert region.

## 4.3 Excluded from the Initial Version

- Building a production web application.
- Advanced machine learning classification.
- Full ecological field surveys.
- Detailed species-level biodiversity assessment.
- Proving causality between climate change and individual plant species.
- Making policy recommendations before the evidence is sufficient.

---

# 5. Data Sources to Investigate

## 8.1 Satellite Data

### Primary Candidates

- Landsat Collection 2.
- MODIS vegetation products.
- Sentinel-2 Surface Reflectance.

### Selection Criteria

- Long historical coverage.
- Suitable spatial resolution.
- Seasonal coverage.
- Cloud and snow handling.
- Consistency across years.

## 8.2 Climate Data

### Candidate Sources

- India Meteorological Department station data.
- ERA5-Land reanalysis.
- CHIRPS precipitation data.
- NASA POWER.
- Other suitable precipitation and temperature datasets.

### Selection Criteria

- Historical coverage.
- Spatial relevance to Leh.
- Temporal resolution.
- Reliability.
- Availability and licensing.

## 8.3 Land-Use Data

### Candidate Sources

- Existing land-cover datasets.
- Satellite-derived classification.
- OpenStreetMap.
- Government land-use records.
- Local field observations.

## 8.4 Ecological Literature

Research should focus on:

- Ladakh cold-desert vegetation.
- Alpine plant ecology.
- Vegetation response to warming.
- Rainfall and vegetation trends.
- Afforestation and restoration.
- Water use and irrigation.
- Grazing and land degradation.

---


# 6. Minimum Viable Research Project

To avoid getting overwhelmed, the first complete version should answer only:

> Did vegetation increase in Leh urban areas and selected natural mountain slopes over a historically available period?

## Minimum Components

- Earth Engine setup.
- One suitable satellite dataset.
- Three study zones.
- Growing-season NDVI.
- Historical annual or seasonal statistics.
- Basic trend charts.
- One rainfall dataset.
- One temperature dataset.
- Preliminary interpretation.

## Minimum Deliverables

1. One study area map.
2. One NDVI map.
3. One historical NDVI trend chart.
4. One rainfall chart.
5. One temperature chart.
6. One comparison of urban vs natural vegetation.
7. A short research note.

This should be the first major target.

---

# 7. Advanced Extensions

Once the minimum project works, the following can be added.

## 11.1 Multi-Sensor Comparison

Compare Landsat, MODIS and Sentinel-2 trends.

Goal: Check whether the observed trend is robust across datasets.

## 11.2 Seasonal Dynamics

Analyze:

- Spring green-up.
- Summer peak.
- Autumn decline.
- Growing-season length.

## 11.3 Elevation Gradient

Compare vegetation trends across elevation bands.

Goal: Investigate whether vegetation is shifting upward or changing differently at different elevations.

## 11.4 Grazing and Land Use

Investigate whether changes in grazing pressure or agricultural activity correspond to vegetation trends.

## 11.5 Water and Irrigation

Analyze vegetation near:

- Irrigation channels.
- Streams.
- Springs.
- Agricultural land.
- Tree plantations.

Goal: Determine whether greening is closely associated with water availability.

## 11.6 Species-Level Research

If field data becomes available, investigate specific native plants and their changing distribution.

This is outside the initial satellite-only scope.

## 11.7 Interactive Research Dashboard

Optional final product:

- Interactive map.
- Year selector.
- NDVI trends.
- Climate charts.
- Study-zone comparison.
- Exportable results.

This could later be implemented using Flask and a web frontend.

---

# 8. Risks and Limitations

## 12.1 Satellite Resolution

Small vegetation patches may be missed by coarse satellite products.

## 12.2 Mixed Pixels

A satellite pixel may contain trees, soil, buildings and grass simultaneously.

## 12.3 Snow and Clouds

Snow can make vegetation appear absent, while clouds can distort observations.

## 12.4 Seasonal Variation

A greener summer does not necessarily indicate long-term ecological recovery.

## 12.5 Land-Use Confounding

Urban expansion and irrigation can create artificial greening signals.

## 12.6 Climate Data Limitations

Station data may be sparse, while gridded data may not fully represent local mountain conditions.

## 12.7 Correlation vs Causation

A relationship between rainfall and NDVI does not prove that rainfall caused the entire trend.

## 12.8 Historical Data Availability

The longest available satellite record may not have consistent quality across the entire period.

## 12.9 Ecological Interpretation

NDVI measures vegetation reflectance, not biodiversity, ecosystem health or native species richness directly.

## 12.10 Field Validation

Without field observations, it may be difficult to distinguish native vegetation recovery from introduced or irrigated vegetation.

---

# 9. Definition of Success

The project will be considered successful if it can:

- Establish a defensible historical study period.
- Produce reproducible satellite vegetation statistics.
- Compare Leh urban greenery with natural mountain slopes.
- Integrate rainfall and temperature.
- Identify areas of greening and browning.
- Distinguish likely human-managed greening from natural vegetation trends.
- Explain limitations honestly.
- Produce a research report supported by data.
- Provide a foundation for further ecological investigation.

The project does not need to prove that greening is good or bad everywhere.

Its purpose is to establish what changed, where it changed, and what the evidence suggests about why.

---

# 10. Final Research Philosophy

The central principle of this project is:

> **Measure vegetation change first. Interpret ecological meaning second.**

The study should not begin with the assumption that more greenery is good or bad.

It should instead investigate:

- What vegetation existed historically?
- What vegetation exists today?
- Where did change occur?
- What environmental factors changed?
- What human interventions occurred?
- What are the ecological consequences?
- What remains uncertain?

A successful project will produce a more nuanced understanding of Leh's changing landscape and provide a scientific basis for discussing future greening and restoration efforts in Ladakh.

---
