from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, dcc, html, no_update


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "colorado_county_acs_2024.csv"
PERIOD_DATA_PATH = BASE_DIR / "data" / "colorado_county_acs_periods.csv"
GEOJSON_PATH = BASE_DIR / "data" / "colorado_counties.geojson"


METRICS = {
    "home_value_to_income_ratio": {
        "label": "Home value to income ratio",
        "format": ".1f",
        "description": "Median owner-occupied home value divided by median household income.",
        "palette": "YlOrRd",
    },
    "annual_rent_to_income_pct": {
        "label": "Annual rent to income",
        "format": ".1f",
        "suffix": "%",
        "description": "Median gross rent annualized as a share of median household income.",
        "palette": "PuBuGn",
    },
    "rent_burden_30_plus_pct": {
        "label": "Rent-burdened renter households",
        "format": ".1f",
        "suffix": "%",
        "description": "Renter households with gross rent equal to 30% or more of household income.",
        "palette": "OrRd",
    },
    "median_home_value": {
        "label": "Median home value",
        "format": "$,.0f",
        "description": "Median value of owner-occupied housing units.",
        "palette": "Teal",
    },
    "median_gross_rent": {
        "label": "Median gross rent",
        "format": "$,.0f",
        "description": "Median monthly gross rent.",
        "palette": "Blues",
    },
    "median_household_income": {
        "label": "Median household income",
        "format": "$,.0f",
        "description": "Median household income in 2024 inflation-adjusted dollars.",
        "palette": "Greens",
    },
    "poverty_rate_pct": {
        "label": "Poverty rate",
        "format": ".1f",
        "suffix": "%",
        "description": "Share of people whose income in the past 12 months was below poverty level.",
        "palette": "Reds",
    },
    "unemployment_rate_pct": {
        "label": "Unemployment rate",
        "format": ".1f",
        "suffix": "%",
        "description": "Civilian labor force unemployment rate.",
        "palette": "Oranges",
    },
    "white_alone_pct": {
        "label": "White alone population",
        "format": ".1f",
        "suffix": "%",
        "description": "Share of residents identifying as White alone, regardless of Hispanic or Latino origin.",
        "palette": "Cividis",
    },
    "black_or_african_american_alone_pct": {
        "label": "Black or African American alone population",
        "format": ".1f",
        "suffix": "%",
        "description": "Share of residents identifying as Black or African American alone.",
        "palette": "Magma",
    },
    "american_indian_alaska_native_alone_pct": {
        "label": "American Indian and Alaska Native alone population",
        "format": ".1f",
        "suffix": "%",
        "description": "Share of residents identifying as American Indian and Alaska Native alone.",
        "palette": "Oranges",
    },
    "asian_alone_pct": {
        "label": "Asian alone population",
        "format": ".1f",
        "suffix": "%",
        "description": "Share of residents identifying as Asian alone.",
        "palette": "Teal",
    },
    "native_hawaiian_pacific_islander_alone_pct": {
        "label": "Native Hawaiian and Pacific Islander alone population",
        "format": ".1f",
        "suffix": "%",
        "description": "Share of residents identifying as Native Hawaiian and Other Pacific Islander alone.",
        "palette": "Blues",
    },
    "some_other_race_alone_pct": {
        "label": "Some other race alone population",
        "format": ".1f",
        "suffix": "%",
        "description": "Share of residents identifying as some other race alone.",
        "palette": "Plasma",
    },
    "two_or_more_races_pct": {
        "label": "Two or more races population",
        "format": ".1f",
        "suffix": "%",
        "description": "Share of residents identifying as two or more races.",
        "palette": "Viridis",
    },
    "hispanic_or_latino_pct": {
        "label": "Hispanic or Latino population",
        "format": ".1f",
        "suffix": "%",
        "description": "Share of residents identifying as Hispanic or Latino, any race.",
        "palette": "Purples",
    },
    "white_non_hispanic_pct": {
        "label": "White non-Hispanic population",
        "format": ".1f",
        "suffix": "%",
        "description": "Share of residents identifying as White alone and not Hispanic or Latino.",
        "palette": "Greys",
    },
    "median_age": {
        "label": "Median age",
        "format": ".1f",
        "description": "Median age of county residents.",
        "palette": "Viridis",
    },
    "total_population": {
        "label": "Total population",
        "format": ",.0f",
        "description": "Total county population.",
        "palette": "Plasma",
    },
}

def load_data() -> tuple[pd.DataFrame, dict]:
    source_path = PERIOD_DATA_PATH if PERIOD_DATA_PATH.exists() else DATA_PATH
    df = pd.read_csv(source_path, dtype={"fips": str, "state": str, "county": str})
    if "release_year" not in df.columns:
        df["release_year"] = 2024
        df["estimate_period"] = "2020-2024"
    with GEOJSON_PATH.open(encoding="utf-8") as file:
        counties = json.load(file)
    return df, counties


df, colorado_counties = load_data()
METRICS = {key: value for key, value in METRICS.items() if key in df.columns}
SCATTER_METRICS = {
    key: value
    for key, value in METRICS.items()
    if key not in {"total_population", "median_age"}
}
PERIODS = (
    df[["release_year", "estimate_period"]]
    .drop_duplicates()
    .sort_values("release_year")
    .reset_index(drop=True)
)
PERIOD_OPTIONS = [
    {"label": period, "value": index}
    for index, period in PERIODS["estimate_period"].items()
]
LATEST_PERIOD_INDEX = len(PERIODS) - 1
DATA_PERIOD_SUMMARY = (
    PERIODS.loc[0, "estimate_period"]
    if len(PERIODS) == 1
    else f"{PERIODS.loc[0, 'estimate_period']} through {PERIODS.loc[LATEST_PERIOD_INDEX, 'estimate_period']}"
)


def metric_label(metric: str) -> str:
    return METRICS[metric]["label"]


def metric_title(metric: str) -> str:
    suffix = METRICS[metric].get("suffix", "")
    return f"{metric_label(metric)}{f' ({suffix})' if suffix else ''}"


def format_value(value: float, metric: str) -> str:
    if pd.isna(value):
        return "Not available"
    value_format = METRICS[metric]["format"]
    if value_format.startswith("$"):
        formatted = "$" + format(value, value_format[1:])
    else:
        formatted = format(value, value_format)
    return f"{formatted}{METRICS[metric].get('suffix', '')}"


def make_options(metrics: dict[str, dict]) -> list[dict[str, str]]:
    return [{"label": details["label"], "value": key} for key, details in metrics.items()]


def make_kpi(title: str, value: str, note: str) -> html.Div:
    return html.Div(
        [html.Div(title, className="kpi-title"), html.Div(value, className="kpi-value"), html.Div(note, className="kpi-note")],
        className="kpi",
    )


app = Dash(__name__, title="Colorado Affordability Explorer")
server = app.server

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Colorado Affordability Explorer"),
                        html.P(
                            "Compare housing affordability across Colorado counties, then add income and demographic context to see where pressure shows up differently."
                        ),
                        html.Div(
                            [
                                html.Span("Data source"),
                                html.Strong(f"U.S. Census ACS 5-year estimates, {DATA_PERIOD_SUMMARY}"),
                                html.Small("County-level Data Profile tables DP03, DP04, and DP05."),
                            ],
                            className="source-note",
                        ),
                    ],
                    className="title-block",
                ),
                html.Div(id="kpi-strip", className="kpi-strip"),
            ],
            className="header",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Map and ranking metric"),
                        dcc.Dropdown(
                            id="metric-choice",
                            options=make_options(METRICS),
                            value="home_value_to_income_ratio",
                            clearable=False,
                        ),
                    ],
                    className="control",
                ),
                html.Div(
                    [
                        html.Label("Ranking view"),
                        dcc.RadioItems(
                            id="rank-mode",
                            options=[
                                {"label": "Highest", "value": "highest"},
                                {"label": "Lowest", "value": "lowest"},
                            ],
                            value="highest",
                            inline=True,
                        ),
                    ],
                    className="control compact",
                ),
                html.Div(
                    [
                        html.Label("Counties shown"),
                        dcc.Slider(
                            id="rank-count",
                            min=5,
                            max=20,
                            step=1,
                            value=10,
                            marks={5: "5", 10: "10", 15: "15", 20: "20"},
                        ),
                    ],
                    className="control compact",
                ),
            ],
            className="controls",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H2("ACS estimate period"),
                        html.P(
                            "Use non-overlapping 5-year ACS periods to compare how county affordability patterns change over time."
                        ),
                    ],
                    className="timeline-copy",
                ),
                html.Div(
                    [
                        html.Label("Period"),
                        dcc.RadioItems(
                            id="period-index",
                            options=PERIOD_OPTIONS,
                            value=LATEST_PERIOD_INDEX,
                            inline=True,
                        ),
                    ],
                    className="timeline-slider",
                ),
                html.Div(
                    [
                        dcc.Checklist(
                            id="animate-period",
                            options=[{"label": "Animate", "value": "animate"}],
                            value=[],
                        ),
                        dcc.Interval(id="period-interval", interval=1600, disabled=True),
                    ],
                    className="timeline-animate",
                ),
            ],
            className="timeline-bar",
        ),
        html.Div(id="metric-note", className="note"),
        html.Div(
            [
                html.Div([dcc.Graph(id="county-map", config={"displayModeBar": False})], className="viz viz-large"),
                html.Div([dcc.Graph(id="rank-chart", config={"displayModeBar": False})], className="viz"),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H2("Compare two metrics"),
                        html.P(
                            "Use this view to test whether affordability, income, and demographic patterns move together across counties."
                        ),
                        html.Div(
                            [
                                html.Label("Counties to highlight"),
                                dcc.Dropdown(
                                    id="county-choice",
                                    options=[
                                        {"label": county, "value": county}
                                        for county in df["county_name"].sort_values()
                                    ],
                                    value=["Denver County", "Boulder County", "Pitkin County"],
                                    multi=True,
                                ),
                            ],
                            className="scatter-control",
                        ),
                        html.Div(
                            [
                                html.Label("Scatter x-axis"),
                                        dcc.Dropdown(
                                            id="x-metric",
                                            options=make_options(SCATTER_METRICS),
                                            value="median_household_income",
                                            clearable=False,
                                        ),
                                    ],
                                    className="scatter-control",
                                ),
                                html.Div(
                                    [
                                        html.Label("Scatter y-axis"),
                                        dcc.Dropdown(
                                            id="y-metric",
                                            options=make_options(SCATTER_METRICS),
                                            value="median_home_value",
                                            clearable=False,
                                        ),
                                    ],
                                    className="scatter-control",
                                ),
                            ],
                            className="scatter-controls",
                        ),
                        dcc.Graph(id="scatter-chart", config={"displayModeBar": False}),
                    ],
                    className="viz scatter-viz",
                ),
            ],
            className="viz-grid",
        ),
        html.Div(
            [
                html.H2("Reading the dashboard"),
                html.P(
                    "Affordability is shown through both ownership and rental lenses. A county can have high income and still be difficult to buy into if home values rise faster than income."
                ),
                html.P(
                    "Demographic measures are included as context for comparison across communities; they should be interpreted alongside population size and local housing conditions."
                ),
            ],
            className="reader-note",
        ),
    ],
    className="page",
)


@app.callback(
    Output("county-map", "figure"),
    Output("rank-chart", "figure"),
    Output("scatter-chart", "figure"),
    Output("metric-note", "children"),
    Output("kpi-strip", "children"),
    Input("metric-choice", "value"),
    Input("county-choice", "value"),
    Input("rank-mode", "value"),
    Input("rank-count", "value"),
    Input("period-index", "value"),
    Input("x-metric", "value"),
    Input("y-metric", "value"),
)
def update_dashboard(metric, selected_counties, rank_mode, rank_count, period_index, x_metric, y_metric):
    selected_counties = selected_counties or []
    period_index = LATEST_PERIOD_INDEX if period_index is None else int(period_index)
    period = PERIODS.iloc[period_index]
    period_df = df[df["release_year"] == period["release_year"]]
    selected = period_df[period_df["county_name"].isin(selected_counties)]

    fig_map = px.choropleth(
        period_df,
        geojson=colorado_counties,
        locations="fips",
        color=metric,
        color_continuous_scale=METRICS[metric]["palette"],
        hover_name="county_name",
        hover_data={
            "fips": False,
            metric: f":{METRICS[metric]['format']}",
            "median_household_income": ":$,.0f",
            "median_home_value": ":$,.0f",
            "median_gross_rent": ":$,.0f",
            "poverty_rate_pct": ":.1f",
        },
        labels={metric: metric_title(metric)},
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(
        title=f"{metric_label(metric)} by county, {period['estimate_period']}",
        margin={"l": 0, "r": 0, "t": 48, "b": 0},
        coloraxis_colorbar={"title": metric_label(metric), "thickness": 12},
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    fig_map.update_traces(marker_line_width=0.7, marker_line_color="#ffffff")

    ranked = (
        period_df.nlargest(rank_count, metric)
        if rank_mode == "highest"
        else period_df.nsmallest(rank_count, metric)
    )
    ranked = ranked.sort_values(metric, ascending=rank_mode == "lowest")
    fig_rank = px.bar(
        ranked,
        x=metric,
        y="county_name",
        orientation="h",
        color=metric,
        color_continuous_scale=METRICS[metric]["palette"],
        labels={metric: metric_title(metric), "county_name": ""},
        title=f"{rank_mode.title()} {rank_count} counties",
        text=ranked[metric].apply(lambda value: format_value(value, metric)),
    )
    fig_rank.update_layout(
        margin={"l": 8, "r": 8, "t": 48, "b": 12},
        coloraxis_showscale=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title=None,
        yaxis_title=None,
    )
    fig_rank.update_traces(textposition="outside", cliponaxis=False)

    scatter_colors = [
        "Highlighted counties" if county in selected_counties else "Other counties"
        for county in period_df["county_name"]
    ]
    fig_scatter = px.scatter(
        period_df,
        x=x_metric,
        y=y_metric,
        size="total_population",
        color=scatter_colors,
        color_discrete_map={
            "Highlighted counties": "#d1495b",
            "Other counties": "#2f6f73",
        },
        hover_name="county_name",
        labels={x_metric: metric_title(x_metric), y_metric: metric_title(y_metric)},
        title=f"{metric_label(y_metric)} vs. {metric_label(x_metric)}, {period['estimate_period']}",
    )
    fig_scatter.update_traces(
        marker={"line": {"width": 0.8, "color": "white"}, "opacity": 0.82},
        selector={"mode": "markers"},
    )
    if selected.empty:
        annotation_text = "Select counties above to highlight them in this comparison."
    elif len(selected) > 6:
        annotation_text = f"Highlighted: {len(selected)} selected counties"
    else:
        annotation_text = "Highlighted: " + ", ".join(selected["county_name"].tolist())
    fig_scatter.add_annotation(
        text=annotation_text,
        xref="paper",
        yref="paper",
        x=0,
        y=1.08,
        showarrow=False,
        align="left",
        font={"size": 12, "color": "#4d5a5d"},
    )
    fig_scatter.update_layout(
        margin={"l": 8, "r": 8, "t": 70, "b": 12},
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend={
            "title": "",
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
    )
    fig_scatter.update_xaxes(showgrid=True, gridcolor="#e7ecef")
    fig_scatter.update_yaxes(showgrid=True, gridcolor="#e7ecef")

    metric_note = f"{period['estimate_period']} ACS 5-year estimates. {metric_label(metric)}: {METRICS[metric]['description']}"
    kpis = [
        make_kpi(
            "Highest",
            format_value(period_df[metric].max(), metric),
            period_df.loc[period_df[metric].idxmax(), "county_name"],
        ),
        make_kpi("Median county", format_value(period_df[metric].median(), metric), "Median across 64 counties"),
        make_kpi(
            "Lowest",
            format_value(period_df[metric].min(), metric),
            period_df.loc[period_df[metric].idxmin(), "county_name"],
        ),
    ]

    return fig_map, fig_rank, fig_scatter, metric_note, kpis


@app.callback(
    Output("period-index", "value"),
    Output("period-interval", "disabled"),
    Input("period-interval", "n_intervals"),
    Input("animate-period", "value"),
    State("period-index", "value"),
)
def animate_period(_n_intervals, animate_value, current_period):
    if not animate_value or "animate" not in animate_value or LATEST_PERIOD_INDEX == 0:
        return no_update, True
    current_period = LATEST_PERIOD_INDEX if current_period is None else int(current_period)
    return (current_period + 1) % len(PERIODS), False


if __name__ == "__main__":
    app.run(debug=True)
