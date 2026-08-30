from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "Models"
    / "final_random_forest_model.joblib"
)

FEATURE_PATH = (
    BASE_DIR
    / "Models"
    / "feature_columns.joblib"
)


def load_model():
    model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURE_PATH)

    return model, feature_columns


def fetch_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    hourly_variables = [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "cloud_cover",
        "wind_speed_10m",
        "global_tilted_irradiance",
        "diffuse_radiation",
        "sunshine_duration"
    ]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(hourly_variables),
        "timezone": "GMT",
        "forecast_hours": 192,
        "past_hours": 1,
        "tilt": 10,
        "azimuth": 0,
        "models": "gfs_seamless"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    forecast_json = response.json()

    elevation = forecast_json["elevation"]

    forecast_data = pd.DataFrame(
        forecast_json["hourly"]
    )

    forecast_data["time_utc"] = pd.to_datetime(
        forecast_data["time"],
        utc=True
    )

    forecast_data["time_sl"] = (
        forecast_data["time_utc"]
        .dt.tz_convert("Asia/Colombo")
    )

    forecast_data = forecast_data.drop(
        columns=["time"]
    )

    return forecast_data, elevation


def create_features(
    forecast_data,
    latitude,
    longitude,
    elevation,
    feature_columns
):
    data = forecast_data.copy()

    data["latitude"] = latitude
    data["longitude"] = longitude
    data["elevation"] = elevation

    data["hour"] = (
        data["time_sl"].dt.hour
    )

    data["day_of_year"] = (
        data["time_sl"].dt.dayofyear
    )

    data["hour_sin"] = np.sin(
        2 * np.pi
        * data["hour"]
        / 24
    )

    data["hour_cos"] = np.cos(
        2 * np.pi
        * data["hour"]
        / 24
    )

    data["day_of_year_sin"] = np.sin(
        2 * np.pi
        * data["day_of_year"]
        / 365.25
    )

    data["day_of_year_cos"] = np.cos(
        2 * np.pi
        * data["day_of_year"]
        / 365.25
    )

    data["gti_lag_1"] = (
        data[
            "global_tilted_irradiance"
        ].shift(1)
    )

    data["cloud_cover_lag_1"] = (
        data[
            "cloud_cover"
        ].shift(1)
    )

    # Remove the extra past hour used
    # only for creating lag features
    live_forecast = (
        data
        .iloc[1:]
        .copy()
        .reset_index(drop=True)
    )

    missing_features = [
        feature
        for feature in feature_columns
        if feature not in live_forecast.columns
    ]

    if missing_features:
        raise ValueError(
            "Missing model features: "
            + ", ".join(missing_features)
        )

    if (
        live_forecast[
            feature_columns
        ].isna().any().any()
    ):
        raise ValueError(
            "Missing values found in model features."
        )

    return live_forecast


def generate_predictions(
    live_forecast,
    model,
    feature_columns
):
    data = live_forecast.copy()

    data["predicted_P"] = 0.0

    active_mask = (
        data[
            "global_tilted_irradiance"
        ] > 0
    )

    data.loc[
        active_mask,
        "predicted_P"
    ] = model.predict(
        data.loc[
            active_mask,
            feature_columns
        ]
    )

    return data


def create_daily_forecast(
    live_forecast,
    system_capacity_kwp
):
    data = live_forecast.copy()

    data["date"] = (
        data["time_sl"].dt.date
    )

    hours_per_day = (
        data
        .groupby("date")
        .size()
    )

    complete_dates = (
        hours_per_day[
            hours_per_day == 24
        ]
        .index[:7]
    )

    if len(complete_dates) < 7:
        raise ValueError(
            "Seven complete forecast days "
            "are not available."
        )

    hourly_forecast = data[
        data["date"].isin(
            complete_dates
        )
    ].copy()

    hourly_forecast[
        "system_power_kw"
    ] = (
        hourly_forecast["predicted_P"]
        * system_capacity_kwp
        / 1000
    )

    daily_forecast = (
        hourly_forecast
        .groupby("date")
        .agg(
            predicted_energy_kwh=(
                "predicted_P",
                lambda x: x.sum() / 1000
            ),
            max_predicted_power_w=(
                "predicted_P",
                "max"
            ),
            average_cloud_cover=(
                "cloud_cover",
                "mean"
            ),
            total_precipitation_mm=(
                "precipitation",
                "sum"
            )
        )
        .reset_index()
    )

    daily_forecast[
        "system_energy_kwh"
    ] = (
        daily_forecast[
            "predicted_energy_kwh"
        ]
        * system_capacity_kwp
    )

    daily_forecast[
        "system_peak_power_kw"
    ] = (
        daily_forecast[
            "max_predicted_power_w"
        ]
        * system_capacity_kwp
        / 1000
    )

    return daily_forecast, hourly_forecast


def generate_forecast(
    latitude,
    longitude,
    system_capacity_kwp
):
    model, feature_columns = load_model()

    forecast_data, elevation = fetch_weather(
        latitude,
        longitude
    )

    live_forecast = create_features(
        forecast_data,
        latitude,
        longitude,
        elevation,
        feature_columns
    )

    live_forecast = generate_predictions(
        live_forecast,
        model,
        feature_columns
    )

    daily_forecast, hourly_forecast = (
        create_daily_forecast(
            live_forecast,
            system_capacity_kwp
        )
    )

    return {
        "daily": daily_forecast,
        "hourly": hourly_forecast,
        "elevation": elevation
    }
    