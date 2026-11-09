"""Einlesen und Bereinigen der beiden CSV-Dateien im Ordner data/.

Annahmen:
- Die Zeitstempel der Luftdaten geben das Stunden-ENDE in deutscher Ortszeit an
  (am 30.03. fehlt 03:00, am 26.10. kommt 03:00 doppelt vor). Wir rechnen auf den
  Stunden-Beginn um. Die erste Zeile (01.01. 00:00) gehört damit zu 2024 und fällt weg.
- Eine Zeile hat ein deutsches Datumsformat (TT.MM.JJJJ HH:MM).
- Komplett leere Spalten (Ozon, SO2, Schnee, ...) werden entfernt.
- Ein Tagesmittel gilt nur, wenn mindestens 18 von 24 Stundenwerten vorliegen.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

POLLUTANTS = {"pm10": "PM10", "pm25": "PM2,5", "no2": "NO₂"}
UNIT = "µg/m³"
AQI_LEVELS = ["sehr gut", "gut", "mäßig", "schlecht", "sehr schlecht"]
AQI_COLORS = {
    "sehr gut": "#256abf",
    "gut": "#86b6ef",
    "mäßig": "#b5b3aa",
    "schlecht": "#ee8a87",
    "sehr schlecht": "#c62f2f",
}
WEATHER = {
    "tavg": "Temperatur Mittel (°C)",
    "tmin": "Temperatur Min (°C)",
    "tmax": "Temperatur Max (°C)",
    "prcp": "Niederschlag (mm)",
    "wspd": "Windgeschwindigkeit (km/h)",
    "pres": "Luftdruck (hPa)",
}


@st.cache_data
def load_air_quality() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "Luftqualitaet_Koeln_2025.csv", sep=";", encoding="utf-8-sig")
    df.columns = ["station", "datum", "pm10", "o3", "no2", "pm25", "so2", "aqi"]

    # Datum: ISO-Format, einzelne Zeilen im deutschen Format
    datum = pd.to_datetime(df["datum"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    datum = datum.fillna(pd.to_datetime(df["datum"], format="%d.%m.%Y %H:%M", errors="coerce"))

    # Stunden-Ende -> Stunden-Beginn, mit Zeitzone wegen der Zeitumstellung
    zeit = (datum - pd.Timedelta(hours=1)).dt.tz_localize("Europe/Berlin", ambiguous="infer")
    df = df.set_index(zeit.rename("zeit")).drop(columns="datum")

    df = df.dropna(axis="columns", how="all")  # Ozon und SO2 sind leer
    df["aqi"] = pd.Categorical(df["aqi"], categories=AQI_LEVELS, ordered=True)
    df = df[df.index.year == 2025]
    df["monat"] = df.index.month
    return df


@st.cache_data
def load_weather() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "Wetterdaten_Koeln_2025.csv", parse_dates=["date"])
    df = df.set_index("date").dropna(axis="columns", how="all")
    return df


def daily_means(air: pd.DataFrame) -> pd.DataFrame:
    """Tagesmittel je Schadstoff; NaN, wenn weniger als 18 Stundenwerte vorliegen."""
    values = air[list(POLLUTANTS)]
    days = values.index.tz_localize(None).normalize()
    means = values.groupby(days).mean()
    counts = values.groupby(days).count()
    return means.where(counts >= 18)
