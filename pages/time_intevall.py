import streamlit as st

from app.read_data import POLLUTANTS, UNIT, WEATHER, load_air_quality, load_weather

st.set_page_config(page_title='Zeitlicher Verlauf', layout='wide')
st.title('Zeitlicher Verlauf')

air = load_air_quality()
weather = load_weather()

# ========================================================================================
# Schadstoffe
st.header('Schadstoffe')
RESOLUTIONS = {'Stunde': 'h', 'Tag': 'D', 'Woche': 'W', 'Monat': 'MS'}

col1, col2 = st.columns([3, 1])
selected = col1.multiselect('Schadstoffe', list(POLLUTANTS), default=list(POLLUTANTS),
                            format_func=POLLUTANTS.get)
resolution = col2.selectbox('Auflösung', list(RESOLUTIONS), index=1)

if selected:
    values = air[selected]
    if resolution != 'Stunde':
        values = values.resample(RESOLUTIONS[resolution]).mean()
    values = values.tz_localize(None).rename(columns=POLLUTANTS)
    st.line_chart(values)
    st.caption(f'{resolution}smittelwerte in {UNIT}. Lücken sind fehlende Messwerte.')
else:
    st.info('Bitte mindestens einen Schadstoff auswählen.')

# ========================================================================================
# Wetter
st.header('Wetter')
weather_col = st.selectbox('Wetterwert', [c for c in WEATHER if c in weather.columns],
                           format_func=WEATHER.get)
st.line_chart(weather[weather_col].rename(WEATHER[weather_col]))
st.caption('Tageswerte. Vom 15. bis 21.03. fehlen die Wetterdaten.')
