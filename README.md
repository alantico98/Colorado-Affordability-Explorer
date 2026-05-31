# Colorado Affordability Explorer

A Dash application for comparing housing affordability across Colorado counties and adding demographic context to understand where housing pressure shows up differently.

The dashboard uses 2024 ACS 5-year county data from the U.S. Census API and a local county GeoJSON boundary file. The app is designed to run from local files after the data download step.

## App Features

- Colorado county choropleth map for selected affordability, income, housing, or demographic metrics.
- Ranked bar chart for the highest or lowest counties on the selected metric.
- Scatterplot for comparing two user-selected metrics.
- County highlighting for focused comparison.
- Narrative notes to help users interpret affordability measures carefully.

## Data

The included CSV is stored at:

```text
data/colorado_county_acs_2024.csv
```

The CSV was generated with:

```bash
python scripts/download_census_data.py
```

The download script expects a Census API key in:

```bash
US_CENSUS_API_KEY
```

The local map boundary file is stored at:

```text
data/colorado_counties.geojson
```

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python main.py
```

Open:

```text
http://127.0.0.1:8050
```

## Project Notes

The app focuses on explanation rather than data collection. Affordability is represented with ownership and rental metrics, including home-value-to-income ratio, annual rent-to-income percentage, and renter households paying 30% or more of income toward rent.
