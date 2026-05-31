"""Download Colorado county ACS 5-year profile data for the dashboard.

The script expects a Census API key in the US_CENSUS_API_KEY environment
variable and writes a local CSV for the Dash app to use.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd


API_BASE_URL = "https://api.census.gov/data/{year}/acs/acs5/profile"
DEFAULT_YEARS = ["2014", "2019", "2024"]
DEFAULT_OUTPUT = Path("data/colorado_county_acs_periods.csv")
PERIOD_LABELS = {
    "2014": "2010-2014",
    "2019": "2015-2019",
    "2024": "2020-2024",
}

BASE_VARIABLES = {
    "DP05_0001E": "total_population",
    "DP05_0018E": "median_age",
    "DP03_0062E": "median_household_income",
    "DP03_0009PE": "unemployment_rate_pct",
    "DP03_0128PE": "poverty_rate_pct",
    "DP04_0089E": "median_home_value",
    "DP04_0134E": "median_gross_rent",
    "DP04_0046PE": "owner_occupied_pct",
    "DP04_0047PE": "renter_occupied_pct",
    "DP04_0141PE": "rent_30_to_34_9_pct",
}

YEAR_VARIABLES = {
    "2014": {
        "DP04_0140PE": "rent_35_plus_pct",
        "DP05_0032PE": "white_alone_pct",
        "DP05_0033PE": "black_or_african_american_alone_pct",
        "DP05_0034PE": "american_indian_alaska_native_alone_pct",
        "DP05_0039PE": "asian_alone_pct",
        "DP05_0047PE": "native_hawaiian_pacific_islander_alone_pct",
        "DP05_0052PE": "some_other_race_alone_pct",
        "DP05_0030PE": "two_or_more_races_pct",
        "DP05_0066PE": "hispanic_or_latino_pct",
        "DP05_0072PE": "white_non_hispanic_pct",
    },
    "2019": {
        "DP04_0142PE": "rent_35_plus_pct",
        "DP05_0037PE": "white_alone_pct",
        "DP05_0038PE": "black_or_african_american_alone_pct",
        "DP05_0039PE": "american_indian_alaska_native_alone_pct",
        "DP05_0044PE": "asian_alone_pct",
        "DP05_0052PE": "native_hawaiian_pacific_islander_alone_pct",
        "DP05_0057PE": "some_other_race_alone_pct",
        "DP05_0058PE": "two_or_more_races_pct",
        "DP05_0071PE": "hispanic_or_latino_pct",
        "DP05_0077PE": "white_non_hispanic_pct",
    },
    "2024": {
        "DP04_0142PE": "rent_35_plus_pct",
        "DP05_0037PE": "white_alone_pct",
        "DP05_0045PE": "black_or_african_american_alone_pct",
        "DP05_0053PE": "american_indian_alaska_native_alone_pct",
        "DP05_0061PE": "asian_alone_pct",
        "DP05_0069PE": "native_hawaiian_pacific_islander_alone_pct",
        "DP05_0074PE": "some_other_race_alone_pct",
        "DP05_0075PE": "two_or_more_races_pct",
        "DP05_0090PE": "hispanic_or_latino_pct",
        "DP05_0096PE": "white_non_hispanic_pct",
    },
}


def variables_for_year(year: str) -> dict[str, str]:
    if year not in YEAR_VARIABLES:
        raise ValueError(
            f"No variable map is configured for {year}. "
            f"Configured years: {', '.join(YEAR_VARIABLES)}."
        )
    return {**BASE_VARIABLES, **YEAR_VARIABLES[year]}


def build_url(year: str, api_key: str) -> str:
    variables = variables_for_year(year)
    params = {
        "get": ",".join(["NAME", *variables.keys()]),
        "for": "county:*",
        "in": "state:08",
        "key": api_key,
    }
    return f"{API_BASE_URL.format(year=year)}?{urlencode(params)}"


def download_county_profile(year: str, api_key: str) -> pd.DataFrame:
    variables = variables_for_year(year)
    url = build_url(year, api_key)
    try:
        with urlopen(url, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Census API request failed for {year}: {body}") from error

    df = pd.DataFrame(payload[1:], columns=payload[0])

    df = df.rename(columns={"NAME": "county_name", **variables})
    df["county_name"] = df["county_name"].str.replace(", Colorado", "", regex=False)
    df["fips"] = df["state"] + df["county"]
    df["release_year"] = int(year)
    df["estimate_period"] = PERIOD_LABELS.get(year, f"{int(year) - 4}-{year}")

    numeric_columns = list(variables.values())
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["rent_burden_30_plus_pct"] = df["rent_30_to_34_9_pct"] + df["rent_35_plus_pct"]
    df["home_value_to_income_ratio"] = (
        df["median_home_value"] / df["median_household_income"]
    )
    df["annual_rent_to_income_ratio"] = (
        df["median_gross_rent"] * 12 / df["median_household_income"]
    )
    df["annual_rent_to_income_pct"] = df["annual_rent_to_income_ratio"] * 100

    ordered_columns = [
        "fips",
        "state",
        "county",
        "county_name",
        "release_year",
        "estimate_period",
        *numeric_columns,
        "rent_burden_30_plus_pct",
        "home_value_to_income_ratio",
        "annual_rent_to_income_ratio",
        "annual_rent_to_income_pct",
    ]
    return df[ordered_columns].sort_values("county_name").reset_index(drop=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download Colorado county ACS profile data from the Census API."
    )
    parser.add_argument(
        "--years",
        nargs="+",
        default=DEFAULT_YEARS,
        help="ACS release years to download. Defaults to 2014 2019 2024.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="CSV output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    api_key = os.getenv("US_CENSUS_API_KEY")
    if not api_key:
        raise SystemExit(
            "Missing US_CENSUS_API_KEY. Set it in your shell before running this script."
        )

    frames = []
    for year in args.years:
        print(f"Downloading ACS {PERIOD_LABELS.get(year, year)}...")
        frames.append(download_county_profile(year, api_key))

    df = pd.concat(frames, ignore_index=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)

    print(f"Wrote {len(df):,} rows to {args.output}")
    print(f"Columns: {', '.join(df.columns)}")


if __name__ == "__main__":
    main()
