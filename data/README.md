# Data Notes

This folder contains the local files used by the Dash app.

## Included Files

- `colorado_county_acs_periods.csv`: ACS 5-year Data Profile values for Colorado counties across non-overlapping estimate periods.
- `colorado_county_acs_2024.csv`: single-period ACS 2020-2024 extract kept as a fallback data file.
- `colorado_counties.geojson`: Colorado county boundary geometries used for the choropleth map.

## Census Source

The ACS data comes from the U.S. Census Data API:

```text
https://api.census.gov/data/{year}/acs/acs5/profile
```

The multi-period CSV includes these ACS release years and estimate periods:

```text
2014 release -> 2010-2014 ACS 5-year estimates
2019 release -> 2015-2019 ACS 5-year estimates
2024 release -> 2020-2024 ACS 5-year estimates
```

The dashboard uses selected Data Profile variables from:

```text
DP03: Economic characteristics
DP04: Housing characteristics
DP05: Demographic and housing estimates
```

Because Census variable codes can change between ACS releases, `scripts/download_census_data.py` uses year-specific variable mappings and writes stable column names for the app.

## Regenerating Data

To regenerate the ACS CSV, set `US_CENSUS_API_KEY` and run:

```bash
python scripts/download_census_data.py
```

The included CSV lets the app run locally without a Census API key.
