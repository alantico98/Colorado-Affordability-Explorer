"""Download Colorado county ACS 5-year profile data for the dashboard.

The script expects a Census API key in the US_CENSUS_API_KEY environment
variable and writes a local CSV for the Dash app to use.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd


API_BASE_URL = "https://api.census.gov/data/{year}/acs/acs5/profile"
DEFAULT_YEAR = "2024"
DEFAULT_OUTPUT = Path("data/colorado_county_acs_2024.csv")

VARIABLES = {
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
    "DP04_0142PE": "rent_35_plus_pct",
    "DP05_0090PE": "hispanic_or_latino_pct",
    "DP05_0096PE": "white_non_hispanic_pct",
}


def build_url(year: str, api_key: str) -> str:
    params = {
        "get": ",".join(["NAME", *VARIABLES.keys()]),
        "for": "county:*",
        "in": "state:08",
        "key": api_key,
    }
    return f"{API_BASE_URL.format(year=year)}?{urlencode(params)}"


def download_county_profile(year: str, api_key: str) -> pd.DataFrame:
    url = build_url(year, api_key)
    raw = pd.read_json(url)
    raw.columns = raw.iloc[0]
    df = raw.iloc[1:].reset_index(drop=True)

    df = df.rename(columns={"NAME": "county_name", **VARIABLES})
    df["county_name"] = df["county_name"].str.replace(", Colorado", "", regex=False)
    df["fips"] = df["state"] + df["county"]

    numeric_columns = list(VARIABLES.values())
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
    parser.add_argument("--year", default=DEFAULT_YEAR, help="ACS release year.")
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

    df = download_county_profile(args.year, api_key)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)

    print(f"Wrote {len(df):,} Colorado counties to {args.output}")
    print(f"Columns: {', '.join(df.columns)}")


if __name__ == "__main__":
    main()
