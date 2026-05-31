# Colorado Affordability Explorer

A Dash application for comparing housing affordability across Colorado counties and adding demographic context to understand where housing pressure shows up differently.

The app uses U.S. Census ACS 5-year county data and local GeoJSON boundaries. The included data covers non-overlapping estimate periods: 2010-2014, 2015-2019, and 2020-2024.

## Features

- Colorado county choropleth map for affordability, income, housing, and demographic metrics.
- Ranked bar chart showing the highest or lowest counties for the selected metric.
- Scatterplot for comparing two user-selected metrics.
- County highlighting in the scatterplot for focused comparison.
- Estimate-period selector and animation toggle for comparing non-overlapping ACS 5-year periods.
- Narrative notes and labels to help users interpret the dashboard.

## Run Locally

Create or activate a Python environment, then install dependencies:

```bash
pip install -r requirements.txt
```

If using `uv`, the equivalent command is:

```bash
uv pip install -r requirements.txt
```

Run the app:

```bash
python main.py
```

Open:

```text
http://127.0.0.1:8050
```

The app runs from included local data files, so a Census API key is not required to view the dashboard.

## Data

Primary app data:

```text
data/colorado_county_acs_periods.csv
```

Fallback single-period data:

```text
data/colorado_county_acs_2024.csv
```

Map boundary data:

```text
data/colorado_counties.geojson
```

See `data/README.md` for source details and notes about ACS periods, Census tables, and variable mappings.

## Regenerate Census Data

To regenerate the ACS CSV, set a Census API key:

```bash
export US_CENSUS_API_KEY="your_key_here"
```

Then run:

```bash
python scripts/download_census_data.py
```

To download a custom set of ACS release years:

```bash
python scripts/download_census_data.py --years 2014 2019 2024
```

The script writes:

```text
data/colorado_county_acs_periods.csv
```

## Project Notes

Affordability is represented through ownership and rental lenses, including home-value-to-income ratio, annual rent-to-income percentage, and renter households paying 30% or more of income toward rent. Demographic measures are included as context for comparison across communities and should be interpreted alongside population size and local housing conditions.
