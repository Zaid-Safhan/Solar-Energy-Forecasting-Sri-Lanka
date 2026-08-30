from datetime import datetime, timedelta
from html import escape
from zoneinfo import ZoneInfo

import altair as alt
import pandas as pd
import requests
import streamlit as st

from forecasting import generate_forecast


st.set_page_config(
    page_title="Solar Energy Forecast",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
        :root {
            --navy: #0B1F33;
            --navy-soft: #163A52;
            --solar: #F6B73C;
            --solar-dark: #D99920;
            --green: #1B8F68;
            --page: #F5F7FA;
            --card: #FFFFFF;
            --muted: #667085;
            --border: #E4E7EC;
        }

        html, body, [class*="css"] {
            font-family: Inter, "Segoe UI", system-ui, -apple-system, sans-serif;
        }

        /* Hide Streamlit's top development toolbar for a cleaner app shell. */
        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu,
        footer {
            display: none !important;
        }

        /* Solar-themed illustrated page background. */
        .stApp {
            background-image:
                linear-gradient(
                    rgba(247, 250, 252, 0.42),
                    rgba(247, 250, 252, 0.52)
                ),
                url("data:image/svg+xml,%0A%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%201600%201000%22%3E%0A%20%20%3Cdefs%3E%0A%20%20%20%20%3ClinearGradient%20id%3D%22sky%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%220%22%20y2%3D%221%22%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23eaf5fb%22%2F%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%2255%25%22%20stop-color%3D%22%23f7fafc%22%2F%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%23fff6df%22%2F%3E%0A%20%20%20%20%3C%2FlinearGradient%3E%0A%20%20%20%20%3CradialGradient%20id%3D%22sunGlow%22%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23f6b73c%22%20stop-opacity%3D%220.28%22%2F%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%2250%25%22%20stop-color%3D%22%23f6b73c%22%20stop-opacity%3D%220.10%22%2F%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%23f6b73c%22%20stop-opacity%3D%220%22%2F%3E%0A%20%20%20%20%3C%2FradialGradient%3E%0A%20%20%20%20%3ClinearGradient%20id%3D%22panel%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23173f59%22%20stop-opacity%3D%220.10%22%2F%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%230b1f33%22%20stop-opacity%3D%220.05%22%2F%3E%0A%20%20%20%20%3C%2FlinearGradient%3E%0A%20%20%3C%2Fdefs%3E%0A%0A%20%20%3Crect%20width%3D%221600%22%20height%3D%221000%22%20fill%3D%22url%28%23sky%29%22%2F%3E%0A%0A%20%20%3Ccircle%20cx%3D%221370%22%20cy%3D%22135%22%20r%3D%22210%22%20fill%3D%22url%28%23sunGlow%29%22%2F%3E%0A%20%20%3Ccircle%20cx%3D%221370%22%20cy%3D%22135%22%20r%3D%2244%22%20fill%3D%22%23f6b73c%22%20fill-opacity%3D%220.16%22%2F%3E%0A%0A%20%20%3Cg%20stroke%3D%22%23f6b73c%22%20stroke-width%3D%225%22%20stroke-linecap%3D%22round%22%20opacity%3D%220.10%22%3E%0A%20%20%20%20%3Cline%20x1%3D%221370%22%20y1%3D%2250%22%20x2%3D%221370%22%20y2%3D%2210%22%2F%3E%0A%20%20%20%20%3Cline%20x1%3D%221370%22%20y1%3D%22220%22%20x2%3D%221370%22%20y2%3D%22260%22%2F%3E%0A%20%20%20%20%3Cline%20x1%3D%221285%22%20y1%3D%22135%22%20x2%3D%221245%22%20y2%3D%22135%22%2F%3E%0A%20%20%20%20%3Cline%20x1%3D%221455%22%20y1%3D%22135%22%20x2%3D%221495%22%20y2%3D%22135%22%2F%3E%0A%20%20%20%20%3Cline%20x1%3D%221310%22%20y1%3D%2275%22%20x2%3D%221280%22%20y2%3D%2245%22%2F%3E%0A%20%20%20%20%3Cline%20x1%3D%221430%22%20y1%3D%22195%22%20x2%3D%221460%22%20y2%3D%22225%22%2F%3E%0A%20%20%20%20%3Cline%20x1%3D%221430%22%20y1%3D%2275%22%20x2%3D%221460%22%20y2%3D%2245%22%2F%3E%0A%20%20%20%20%3Cline%20x1%3D%221310%22%20y1%3D%22195%22%20x2%3D%221280%22%20y2%3D%22225%22%2F%3E%0A%20%20%3C%2Fg%3E%0A%0A%20%20%3Cg%20transform%3D%22translate%2870%20745%29%20rotate%28-7%29%22%20opacity%3D%220.48%22%3E%0A%20%20%20%20%3Crect%20x%3D%220%22%20y%3D%220%22%20width%3D%22520%22%20height%3D%22185%22%20rx%3D%2212%22%20fill%3D%22url%28%23panel%29%22%20stroke%3D%22%230b1f33%22%20stroke-opacity%3D%220.06%22%2F%3E%0A%20%20%20%20%3Cg%20stroke%3D%22%230b1f33%22%20stroke-opacity%3D%220.055%22%20stroke-width%3D%222%22%3E%0A%20%20%20%20%20%20%3Cline%20x1%3D%22104%22%20y1%3D%220%22%20x2%3D%22104%22%20y2%3D%22185%22%2F%3E%0A%20%20%20%20%20%20%3Cline%20x1%3D%22208%22%20y1%3D%220%22%20x2%3D%22208%22%20y2%3D%22185%22%2F%3E%0A%20%20%20%20%20%20%3Cline%20x1%3D%22312%22%20y1%3D%220%22%20x2%3D%22312%22%20y2%3D%22185%22%2F%3E%0A%20%20%20%20%20%20%3Cline%20x1%3D%22416%22%20y1%3D%220%22%20x2%3D%22416%22%20y2%3D%22185%22%2F%3E%0A%20%20%20%20%20%20%3Cline%20x1%3D%220%22%20y1%3D%2261.7%22%20x2%3D%22520%22%20y2%3D%2261.7%22%2F%3E%0A%20%20%20%20%20%20%3Cline%20x1%3D%220%22%20y1%3D%22123.4%22%20x2%3D%22520%22%20y2%3D%22123.4%22%2F%3E%0A%20%20%20%20%3C%2Fg%3E%0A%20%20%3C%2Fg%3E%0A%0A%20%20%3Cg%20transform%3D%22translate%281110%20780%29%20rotate%286%29%22%20opacity%3D%220.28%22%3E%0A%20%20%20%20%3Crect%20x%3D%220%22%20y%3D%220%22%20width%3D%22390%22%20height%3D%22140%22%20rx%3D%2210%22%20fill%3D%22url%28%23panel%29%22%20stroke%3D%22%230b1f33%22%20stroke-opacity%3D%220.05%22%2F%3E%0A%20%20%20%20%3Cg%20stroke%3D%22%230b1f33%22%20stroke-opacity%3D%220.05%22%20stroke-width%3D%222%22%3E%0A%20%20%20%20%20%20%3Cline%20x1%3D%2297.5%22%20y1%3D%220%22%20x2%3D%2297.5%22%20y2%3D%22140%22%2F%3E%0A%20%20%20%20%20%20%3Cline%20x1%3D%22195%22%20y1%3D%220%22%20x2%3D%22195%22%20y2%3D%22140%22%2F%3E%0A%20%20%20%20%20%20%3Cline%20x1%3D%22292.5%22%20y1%3D%220%22%20x2%3D%22292.5%22%20y2%3D%22140%22%2F%3E%0A%20%20%20%20%20%20%3Cline%20x1%3D%220%22%20y1%3D%2270%22%20x2%3D%22390%22%20y2%3D%2270%22%2F%3E%0A%20%20%20%20%3C%2Fg%3E%0A%20%20%3C%2Fg%3E%0A%3C%2Fsvg%3E%0A");
            background-size: cover, cover;
            background-position: center, center;
            background-repeat: no-repeat, no-repeat;
            background-attachment: fixed, fixed;
            min-height: 100vh;
        }

        .block-container {
            position: relative;
            z-index: 1;
            max-width: 1420px;
            padding-top: 6.55rem;
            padding-bottom: 2.4rem;
        }

        .sticky-brand {
            position: fixed;
            top: 0.75rem;
            left: 50%;
            transform: translateX(-50%);
            width: min(calc(100% - 2rem), 1420px);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            background:
                radial-gradient(
                    circle at 88% 0%,
                    rgba(246,183,60,0.30),
                    transparent 31%
                ),
                linear-gradient(
                    135deg,
                    rgba(8,28,46,0.99) 0%,
                    rgba(18,57,78,0.98) 72%,
                    rgba(31,78,87,0.97) 100%
                );
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 17px;
            padding: 0.9rem 1.15rem;
            box-shadow: 0 10px 28px rgba(11,31,51,0.18);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }

        .brand-left {
            display: flex;
            align-items: center;
            min-width: 0;
            gap: 0.85rem;
        }

        .brand-icon {
            width: 42px;
            height: 42px;
            flex: 0 0 42px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            background: var(--solar);
            color: var(--navy);
            font-size: 1.35rem;
            box-shadow: 0 5px 14px rgba(246,183,60,0.22);
        }

        .brand-copy {
            min-width: 0;
        }

        .brand-title {
            color: #FFFFFF;
            font-size: 1.24rem;
            line-height: 1.2;
            font-weight: 780;
            letter-spacing: -0.025em;
            margin: 0;
        }

        .brand-subtitle {
            color: #DCE7F0;
            font-size: 0.82rem;
            line-height: 1.4;
            margin-top: 0.18rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .brand-status {
            flex: 0 0 auto;
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.42rem 0.72rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.09);
            color: #F8FAFC;
            border: 1px solid rgba(255,255,255,0.10);
            font-size: 0.76rem;
            font-weight: 670;
        }

        .brand-status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--solar);
            box-shadow: 0 0 0 3px rgba(246,183,60,0.13);
        }

        .section-title {
            color: var(--navy);
            font-size: 1.28rem;
            font-weight: 760;
            margin: 1.15rem 0 0.20rem 0;
        }

        .section-subtitle {
            color: var(--muted);
            margin: 0 0 0.60rem 0;
            font-size: 0.93rem;
        }

        .location-card {
            background: #F8FAFC;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.9rem 1rem;
            margin: 0.55rem 0 0.8rem 0;
        }

        .location-name {
            color: var(--navy);
            font-size: 1rem;
            font-weight: 720;
            margin-bottom: 0.2rem;
        }

        .location-meta {
            color: var(--muted);
            font-size: 0.82rem;
        }

        div[data-testid="stMetric"] {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 0.78rem 0.82rem 0.72rem 0.82rem;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.045);
        }

        div[data-testid="stMetric"] label { color: var(--muted) !important; }
        div[data-testid="stMetricValue"] { color: var(--navy); }

        .insight-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem 1.05rem;
            min-height: 112px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        }

        .insight-title {
            color: var(--navy);
            font-weight: 730;
            margin-bottom: 0.35rem;
        }

        .insight-text {
            color: var(--muted);
            line-height: 1.55;
            font-size: 0.92rem;
        }

        .status-pill {
            display: inline-block;
            border-radius: 999px;
            padding: 0.30rem 0.65rem;
            background: #EAF7F1;
            color: #167252;
            font-weight: 650;
            font-size: 0.78rem;
            margin-bottom: 0.4rem;
        }

        .forecast-note {
            color: var(--muted);
            font-size: 0.85rem;
            line-height: 1.55;
        }

        .detail-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.9rem 1rem;
            min-height: 80px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.035);
        }

        .detail-label {
            color: var(--muted);
            font-size: 0.78rem;
            margin-bottom: 0.3rem;
        }

        .detail-value {
            color: var(--navy);
            font-size: 1rem;
            font-weight: 720;
            line-height: 1.35;
        }

        .footer-note {
            color: #7B8495;
            font-size: 0.77rem;
            margin-top: 1.2rem;
            text-align: center;
        }

        div.stButton > button[kind="primary"] {
            background: var(--solar);
            color: var(--navy);
            border: 1px solid var(--solar);
            font-weight: 740;
        }

        div.stButton > button[kind="primary"]:hover {
            background: var(--solar-dark);
            border-color: var(--solar-dark);
            color: var(--navy);
        }

        div.stButton > button:disabled,
        div.stButton > button:disabled:hover {
            background: #E5E7EB !important;
            border-color: #E5E7EB !important;
            color: #98A2B3 !important;
            box-shadow: none !important;
            cursor: not-allowed !important;
            opacity: 1 !important;
        }

        div[data-testid="stForm"] {
            border: 1px solid var(--border);
            border-radius: 14px;
            background: #FFFFFF;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255,255,255,0.74);
            backdrop-filter: blur(5px);
            -webkit-backdrop-filter: blur(5px);
            border-radius: 16px;
        }


        /* Small refinements for the compact dashboard layout. */
        div[data-testid="stMetric"] {
            min-height: 104px;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.55rem;
            line-height: 1.15;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.80rem;
        }

        /* Keep dataframe/chart blocks visually compact. */
        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
        }

        /* Reduce excess empty vertical space around charts. */
        div[data-testid="stVegaLiteChart"] {
            margin-top: -0.15rem;
        }

        /* Make section headings inside the two-column results grid feel aligned. */
        .section-title + .section-subtitle {
            margin-top: 0;
        }

        @media (max-width: 760px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .sticky-brand {
                top: 0.45rem;
                width: calc(100% - 1rem);
                padding: 0.72rem 0.82rem;
                border-radius: 14px;
            }

            .block-container {
                padding-top: 6.2rem;
            }

            .brand-icon {
                width: 38px;
                height: 38px;
                flex-basis: 38px;
                font-size: 1.15rem;
            }

            .brand-title {
                font-size: 1.05rem;
            }

            .brand-subtitle {
                font-size: 0.74rem;
                max-width: 58vw;
            }

            .brand-status {
                display: none;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


DEFAULT_STATE = {
    "latitude": None,
    "longitude": None,
    "location_name": None,
    "location_source": None,
    "location_accuracy": None,
    "location_results": [],
    "forecast_result": None,
    "forecast_capacity": None,
    "forecast_location_name": None,
    "forecast_generated_at": None,
    "system_capacity_input": 5.0,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


def clear_forecast():
    st.session_state.forecast_result = None
    st.session_state.forecast_capacity = None
    st.session_state.forecast_location_name = None
    st.session_state.forecast_generated_at = None


def set_location(latitude, longitude, location_name, source, accuracy=None):
    changed = (
        st.session_state.latitude != float(latitude)
        or st.session_state.longitude != float(longitude)
    )

    st.session_state.latitude = float(latitude)
    st.session_state.longitude = float(longitude)
    st.session_state.location_name = location_name
    st.session_state.location_source = source
    st.session_state.location_accuracy = accuracy

    if changed:
        clear_forecast()


@st.cache_data(ttl=86400, show_spinner=False)
def reverse_geocode(latitude, longitude):
    url = "https://nominatim.openstreetmap.org/reverse"

    params = {
        "lat": round(float(latitude), 5),
        "lon": round(float(longitude), 5),
        "format": "jsonv2",
        "addressdetails": 1,
        "zoom": 18,
    }

    headers = {
        "User-Agent": "SolarEnergyForecastingSystem/1.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()
    address = data.get("address", {})

    preferred_keys = [
        "road",
        "neighbourhood",
        "suburb",
        "city_district",
        "town",
        "city",
        "village",
        "county",
    ]

    parts = []

    for key in preferred_keys:
        value = address.get(key)
        if value and value not in parts:
            parts.append(value)
        if len(parts) == 2:
            break

    country = address.get("country", "Sri Lanka")
    if country not in parts:
        parts.append(country)

    if parts:
        return ", ".join(parts)

    return f"{float(latitude):.5f}, {float(longitude):.5f}"


@st.cache_data(ttl=3600, show_spinner=False)
def search_locations(query):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": query.strip(),
        "count": 5,
        "language": "en",
        "format": "json",
        "countryCode": "LK",
    }

    response = requests.get(
        url,
        params=params,
        timeout=15,
    )
    response.raise_for_status()

    return response.json().get("results", [])


def location_result_label(item):
    parts = [item.get("name")]

    for key in ["admin2", "admin1", "country"]:
        value = item.get(key)
        if value and value not in parts:
            parts.append(value)

    return ", ".join([part for part in parts if part])


GEOLOCATION_COMPONENT = None

if hasattr(st.components, "v2"):
    GEOLOCATION_COMPONENT = st.components.v2.component(
        name="device_geolocation",
        html="""
            <div class="geo-wrap">
                <button id="geo-btn" type="button">
                    <span class="pin">●</span>
                    Use My Location
                </button>
                <span id="geo-status"></span>
            </div>
        """,
        css="""
            .geo-wrap {
                width: 100%;
                display: flex;
                align-items: center;
                gap: 12px;
                font-family: Inter, "Segoe UI", system-ui, sans-serif;
            }

            #geo-btn {
                min-height: 42px;
                border: 1px solid #D9DEE7;
                border-radius: 10px;
                background: #FFFFFF;
                color: #0B1F33;
                font-weight: 700;
                padding: 0 16px;
                cursor: pointer;
                transition: all 0.15s ease;
            }

            #geo-btn:hover {
                border-color: #F6B73C;
                box-shadow: 0 3px 10px rgba(15, 23, 42, 0.07);
            }

            #geo-btn:disabled {
                cursor: wait;
                opacity: 0.65;
            }

            .pin {
                color: #F6B73C;
                margin-right: 6px;
            }

            #geo-status {
                color: #667085;
                font-size: 13px;
            }
        """,
        js="""
            export default function(component) {
                const { parentElement, setStateValue } = component;
                const button = parentElement.querySelector("#geo-btn");
                const status = parentElement.querySelector("#geo-status");

                button.onclick = () => {
                    if (!navigator.geolocation) {
                        setStateValue("geo_result", {
                            ok: false,
                            error: "Location services are not supported by this browser."
                        });
                        return;
                    }

                    button.disabled = true;
                    status.textContent = "Detecting location...";

                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            setStateValue("geo_result", {
                                ok: true,
                                latitude: position.coords.latitude,
                                longitude: position.coords.longitude,
                                accuracy: position.coords.accuracy
                            });

                            status.textContent = "Location detected";
                            button.disabled = false;
                        },
                        (error) => {
                            let message = "Unable to access your location.";

                            if (error.code === 1) {
                                message = "Location permission was denied.";
                            } else if (error.code === 2) {
                                message = "Your location could not be determined.";
                            } else if (error.code === 3) {
                                message = "Location request timed out.";
                            }

                            setStateValue("geo_result", {
                                ok: false,
                                error: message
                            });

                            status.textContent = message;
                            button.disabled = false;
                        },
                        {
                            enableHighAccuracy: true,
                            timeout: 10000,
                            maximumAge: 0
                        }
                    );
                };
            }
        """,
    )


st.markdown(
    """
    <div class="sticky-brand">
        <div class="brand-left">
            <div class="brand-icon">☀</div>
            <div class="brand-copy">
                <div class="brand-title">Solar Energy Forecast</div>
                <div class="brand-subtitle">
                    Location-aware generation estimates for your rooftop solar system.
                </div>
            </div>
        </div>
        <div class="brand-status">
            <span class="brand-status-dot"></span>
            Weather-driven forecast
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown('<div class="section-title">Your System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Set your location and installed solar capacity.</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    left, right = st.columns([1.45, 1], gap="large")

    with left:
        st.markdown("#### Location")

        if GEOLOCATION_COMPONENT is not None:
            geo_result = GEOLOCATION_COMPONENT(
                default={"geo_result": None},
                on_geo_result_change=lambda: None,
                key="device_location",
                width="stretch",
                height=52,
            )

            device_result = getattr(geo_result, "geo_result", None)

            if device_result:
                if device_result.get("ok"):
                    latitude = round(float(device_result["latitude"]), 6)
                    longitude = round(float(device_result["longitude"]), 6)

                    device_changed = (
                        st.session_state.latitude != latitude
                        or st.session_state.longitude != longitude
                        or st.session_state.location_source != "device"
                    )

                    if device_changed:
                        with st.spinner("Finding your nearby area..."):
                            try:
                                place_name = reverse_geocode(latitude, longitude)
                            except requests.RequestException:
                                place_name = f"{latitude:.5f}, {longitude:.5f}"

                        set_location(
                            latitude,
                            longitude,
                            place_name,
                            "device",
                            device_result.get("accuracy"),
                        )
                else:
                    st.warning(
                        device_result.get(
                            "error",
                            "Location access was not available.",
                        )
                    )
        else:
            st.info(
                "Device location needs a newer Streamlit version. "
                "You can still enter a location manually below."
            )

        if (
            st.session_state.latitude is not None
            and st.session_state.longitude is not None
        ):
            safe_name = escape(st.session_state.location_name or "Selected location")

            source_text = "Location selected"

            if st.session_state.location_source == "device":
                source_text = "Detected automatically"
                if st.session_state.location_accuracy:
                    source_text += (
                        f" · accuracy about "
                        f"{st.session_state.location_accuracy:.0f} m"
                    )
            elif st.session_state.location_source == "search":
                source_text = "Selected from location search"
            elif st.session_state.location_source == "coordinates":
                source_text = "Coordinates entered manually"

            st.markdown(
                f"""
                <div class="location-card">
                    <div class="status-pill">Location ready</div>
                    <div class="location-name">{safe_name}</div>
                    <div class="location-meta">{source_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander(
            "Enter location manually",
            expanded=(st.session_state.latitude is None),
        ):
            with st.form("location_search_form", clear_on_submit=False):
                location_query = st.text_input(
                    "City or town",
                    placeholder="e.g. Kandy, Wattala, Galle",
                )

                search_clicked = st.form_submit_button("Find Location")

            if search_clicked:
                if len(location_query.strip()) < 2:
                    st.warning("Enter at least two characters.")
                else:
                    try:
                        with st.spinner("Searching..."):
                            st.session_state.location_results = search_locations(
                                location_query
                            )
                    except requests.RequestException:
                        st.error("Location search is temporarily unavailable.")

            if st.session_state.location_results:
                labels = [
                    location_result_label(item)
                    for item in st.session_state.location_results
                ]

                selected_index = st.selectbox(
                    "Select location",
                    options=range(len(labels)),
                    format_func=lambda index: labels[index],
                    key="manual_location_result",
                )

                if st.button("Use Selected Location", key="use_manual_place"):
                    item = st.session_state.location_results[selected_index]

                    set_location(
                        item["latitude"],
                        item["longitude"],
                        labels[selected_index],
                        "search",
                    )
                    st.rerun()

            with st.expander("Advanced: enter coordinates"):
                coord_left, coord_right = st.columns(2)

                with coord_left:
                    manual_lat = st.number_input(
                        "Latitude",
                        min_value=5.0,
                        max_value=10.0,
                        value=7.29060,
                        step=0.00001,
                        format="%.5f",
                    )

                with coord_right:
                    manual_lon = st.number_input(
                        "Longitude",
                        min_value=79.0,
                        max_value=82.0,
                        value=80.63360,
                        step=0.00001,
                        format="%.5f",
                    )

                if st.button("Use Coordinates", key="use_coordinates"):
                    try:
                        with st.spinner("Checking location..."):
                            manual_name = reverse_geocode(manual_lat, manual_lon)
                    except requests.RequestException:
                        manual_name = f"{manual_lat:.5f}, {manual_lon:.5f}"

                    set_location(
                        manual_lat,
                        manual_lon,
                        manual_name,
                        "coordinates",
                    )
                    st.rerun()

    with right:
        st.markdown("#### Solar System Capacity")

        system_capacity_kwp = st.number_input(
            "Installed system capacity (kWp)",
            min_value=0.5,
            max_value=100.0,
            step=0.1,
            format="%.2f",
            help=(
                "Enter the total installed DC capacity "
                "of your rooftop solar system."
            ),
            key="system_capacity_input",
            on_change=clear_forecast,
        )

        st.caption("Example: eight 550 W panels = 4.40 kWp.")

        location_ready = (
            st.session_state.latitude is not None
            and st.session_state.longitude is not None
        )

        generate_clicked = st.button(
            "Generate Forecast",
            type="primary",
            use_container_width=True,
            disabled=not location_ready,
        )

        if not location_ready:
            st.caption("Select or detect a location first.")

        if generate_clicked:
            try:
                with st.spinner("Preparing your solar forecast..."):
                    result = generate_forecast(
                        st.session_state.latitude,
                        st.session_state.longitude,
                        system_capacity_kwp,
                    )

                st.session_state.forecast_result = result
                st.session_state.forecast_capacity = system_capacity_kwp
                st.session_state.forecast_location_name = st.session_state.location_name
                st.session_state.forecast_generated_at = datetime.now(
                    ZoneInfo("Asia/Colombo")
                )

            except FileNotFoundError:
                st.error(
                    "The forecasting model files could not be loaded. "
                    "Check the Models folder."
                )

            except requests.RequestException:
                st.error(
                    "Weather data is temporarily unavailable. "
                    "Please try again shortly."
                )

            except ValueError as error:
                st.error(str(error))

            except Exception:
                st.error(
                    "The forecast could not be generated. "
                    "Please try again."
                )


if st.session_state.forecast_result is not None:
    result = st.session_state.forecast_result

    daily = result["daily"].copy()
    hourly = result["hourly"].copy()
    elevation = result["elevation"]
    forecast_capacity = st.session_state.forecast_capacity

    daily["date"] = pd.to_datetime(daily["date"])
    hourly["date"] = pd.to_datetime(hourly["date"])

    next_day = daily.iloc[0]
    total_energy = daily["system_energy_kwh"].sum()
    average_energy = daily["system_energy_kwh"].mean()
    best_row = daily.loc[daily["system_energy_kwh"].idxmax()]
    lowest_row = daily.loc[daily["system_energy_kwh"].idxmin()]

    sri_lanka_today = datetime.now(
        ZoneInfo("Asia/Colombo")
    ).date()

    first_forecast_date = next_day["date"].date()

    if first_forecast_date == sri_lanka_today:
        first_day_label = "Today"
    elif first_forecast_date == sri_lanka_today + timedelta(days=1):
        first_day_label = "Tomorrow"
    else:
        first_day_label = "Next Day"

    # Prepare the daily generation chart once, then place it in the right column.
    chart_data = daily[["date", "system_energy_kwh"]].copy()
    chart_data["date_label"] = chart_data["date"].dt.strftime("%a %d")
    date_order = chart_data["date_label"].tolist()

    bars = (
        alt.Chart(chart_data)
        .mark_bar(
            color="#F6B73C",
            cornerRadiusTopLeft=7,
            cornerRadiusTopRight=7,
            size=42,
        )
        .encode(
            x=alt.X(
                "date_label:N",
                sort=date_order,
                title=None,
                axis=alt.Axis(
                    labelAngle=0,
                    labelColor="#667085",
                    tickColor="#E4E7EC",
                    domainColor="#E4E7EC",
                ),
            ),
            y=alt.Y(
                "system_energy_kwh:Q",
                title="Energy (kWh)",
                scale=alt.Scale(zero=True),
                axis=alt.Axis(
                    labelColor="#667085",
                    titleColor="#667085",
                    gridColor="#EEF1F5",
                    domain=False,
                ),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date", format="%A, %d %B"),
                alt.Tooltip(
                    "system_energy_kwh:Q",
                    title="Energy (kWh)",
                    format=".2f",
                ),
            ],
        )
    )

    labels = (
        alt.Chart(chart_data)
        .mark_text(
            dy=-10,
            color="#0B1F33",
            fontSize=11,
            fontWeight="bold",
        )
        .encode(
            x=alt.X("date_label:N", sort=date_order),
            y="system_energy_kwh:Q",
            text=alt.Text("system_energy_kwh:Q", format=".1f"),
        )
    )

    # ------------------------------------------------------------------
    # COMPACT DESKTOP DASHBOARD
    # Left: forecast overview
    # Right: expected generation chart
    # ------------------------------------------------------------------
    overview_col, generation_col = st.columns([1.16, 1], gap="large")

    with overview_col:
        st.markdown(
            '<div class="section-title">Forecast Overview</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="section-subtitle">
                {escape(st.session_state.forecast_location_name or "Selected location")}
                · {forecast_capacity:.2f} kWp
            </div>
            """,
            unsafe_allow_html=True,
        )

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            first_day_label,
            f"{next_day['system_energy_kwh']:.1f} kWh",
        )
        m2.metric(
            "Forecast Total",
            f"{total_energy:.1f} kWh",
        )
        m3.metric(
            "Daily Average",
            f"{average_energy:.1f} kWh",
        )

        with m4:
            st.metric(
                "Best Day",
                best_row["date"].strftime("%d %b"),
            )
            st.caption(
                f"{best_row['system_energy_kwh']:.1f} kWh expected"
            )

    with generation_col:
        st.markdown(
            '<div class="section-title">Expected Solar Generation</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">Predicted energy across the forecast period.</div>',
            unsafe_allow_html=True,
        )
        st.altair_chart(
            (bars + labels).properties(height=270),
            use_container_width=True,
        )

    # ------------------------------------------------------------------
    # MAIN RESULTS GRID
    # Left: daily forecast + insights
    # Right: hourly forecast
    # ------------------------------------------------------------------
    results_left, results_right = st.columns([1.10, 1], gap="large")

    with results_left:
        st.markdown(
            '<div class="section-title">Daily Forecast</div>',
            unsafe_allow_html=True,
        )

        display_daily = daily[
            [
                "date",
                "system_energy_kwh",
                "system_peak_power_kw",
                "average_cloud_cover",
                "total_precipitation_mm",
            ]
        ].copy()

        display_daily["date"] = display_daily["date"].dt.strftime("%a, %d %b")
        display_daily.columns = [
            "Date",
            "Energy",
            "Peak Power",
            "Cloud Cover",
            "Rainfall",
        ]

        st.dataframe(
            display_daily,
            hide_index=True,
            use_container_width=True,
            height=300,
            column_config={
                "Energy": st.column_config.NumberColumn(
                    "Energy",
                    format="%.2f kWh",
                ),
                "Peak Power": st.column_config.NumberColumn(
                    "Peak Power",
                    format="%.2f kW",
                ),
                "Cloud Cover": st.column_config.NumberColumn(
                    "Cloud Cover",
                    format="%.1f %%",
                ),
                "Rainfall": st.column_config.NumberColumn(
                    "Rainfall",
                    format="%.1f mm",
                ),
            },
        )

        st.markdown(
            '<div class="section-title">Solar Insights</div>',
            unsafe_allow_html=True,
        )

        insight_left, insight_right = st.columns(2)
        best_date_text = best_row["date"].strftime("%A, %d %B")
        low_date_text = lowest_row["date"].strftime("%A, %d %B")

        with insight_left:
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="insight-title">☀️ Strongest Solar Day</div>
                    <div class="insight-text">
                        {best_date_text} has the highest expected generation
                        at approximately
                        <strong>{best_row['system_energy_kwh']:.1f} kWh</strong>.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with insight_right:
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="insight-title">⚡ Plan Daytime Energy Use</div>
                    <div class="insight-text">
                        Higher daytime electricity use may be better scheduled
                        during stronger solar periods. The lowest daily forecast
                        is approximately
                        <strong>{lowest_row['system_energy_kwh']:.1f} kWh</strong>
                        on {low_date_text}.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with results_right:
        st.markdown(
            '<div class="section-title">Hourly Forecast</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-subtitle">Inspect the expected solar power for a selected day.</div>',
            unsafe_allow_html=True,
        )

        available_dates = daily["date"].dt.date.tolist()

        selected_date = st.selectbox(
            "Select day",
            options=available_dates,
            format_func=lambda value: value.strftime("%A, %d %B"),
            key="compact_hourly_day",
        )

        selected_hourly = hourly[
            hourly["date"].dt.date == selected_date
        ].copy()

        selected_hourly = selected_hourly[
            selected_hourly["time_sl"].dt.hour.between(5, 19)
        ]

        selected_hourly["time_label"] = selected_hourly["time_sl"].dt.strftime(
            "%H:%M"
        )

        hourly_line = (
            alt.Chart(selected_hourly)
            .mark_line(
                color="#F6B73C",
                strokeWidth=3,
                point=alt.OverlayMarkDef(
                    filled=True,
                    fill="#FFFFFF",
                    stroke="#F6B73C",
                    size=45,
                ),
            )
            .encode(
                x=alt.X(
                    "time_label:N",
                    title=None,
                    sort=None,
                    axis=alt.Axis(
                        labelAngle=-35,
                        labelColor="#667085",
                        domainColor="#E4E7EC",
                        tickColor="#E4E7EC",
                    ),
                ),
                y=alt.Y(
                    "system_power_kw:Q",
                    title="Power (kW)",
                    scale=alt.Scale(zero=True),
                    axis=alt.Axis(
                        labelColor="#667085",
                        titleColor="#667085",
                        gridColor="#EEF1F5",
                        domain=False,
                    ),
                ),
                tooltip=[
                    alt.Tooltip("time_label:N", title="Time"),
                    alt.Tooltip(
                        "system_power_kw:Q",
                        title="Power (kW)",
                        format=".2f",
                    ),
                ],
            )
            .properties(height=230)
        )

        st.altair_chart(hourly_line, use_container_width=True)

        hourly_table = selected_hourly[
            ["time_sl", "system_power_kw", "cloud_cover", "temperature_2m"]
        ].copy()

        hourly_table["time_sl"] = hourly_table["time_sl"].dt.strftime("%H:%M")
        hourly_table.columns = [
            "Time",
            "Power",
            "Cloud Cover",
            "Temperature",
        ]

        st.dataframe(
            hourly_table,
            hide_index=True,
            use_container_width=True,
            height=280,
            column_config={
                "Power": st.column_config.NumberColumn(
                    "Power",
                    format="%.2f kW",
                ),
                "Cloud Cover": st.column_config.NumberColumn(
                    "Cloud Cover",
                    format="%.0f %%",
                ),
                "Temperature": st.column_config.NumberColumn(
                    "Temperature",
                    format="%.1f °C",
                ),
            },
        )

    # ------------------------------------------------------------------
    # FORECAST INFORMATION
    # ------------------------------------------------------------------
    st.markdown(
        '<div class="section-title" style="margin-top:1rem;">Forecast Information</div>',
        unsafe_allow_html=True,
    )

    generated_at = st.session_state.forecast_generated_at

    detail_1, detail_2, detail_3, detail_4 = st.columns(4)

    with detail_1:
        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">Location</div>
                <div class="detail-value">
                    {escape(st.session_state.forecast_location_name or "Selected location")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with detail_2:
        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">System Capacity</div>
                <div class="detail-value">{forecast_capacity:.2f} kWp</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with detail_3:
        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">Location Elevation</div>
                <div class="detail-value">{float(elevation):.0f} m</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with detail_4:
        updated_text = (
            generated_at.strftime("%d %b · %H:%M")
            if generated_at
            else "—"
        )
        st.markdown(
            f"""
            <div class="detail-card">
                <div class="detail-label">Last Updated</div>
                <div class="detail-value">{updated_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Forecast notes", expanded=False):
        st.markdown(
            """
            Forecast values are estimates based on expected weather,
            solar radiation, location and system capacity. Results are
            scaled to the installed capacity you enter. Actual rooftop
            generation can vary because of local shading, panel condition,
            soiling, installation characteristics, inverter performance
            and differences between forecast and actual weather.
            """
        )

    st.markdown(
        """
        <div class="footer-note">
            Weather data: Open-Meteo · Location names: © OpenStreetMap contributors
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    st.markdown(
        """
        <div class="forecast-note">
            Select your location and system capacity, then generate a forecast
            to see expected solar energy, daily conditions and hourly power.
        </div>
        """,
        unsafe_allow_html=True,
    )
