import pandas as pd
import streamlit as st

from app.read_data import POLLUTANTS, UNIT, daily_means, load_air_quality

st.set_page_config(page_title='Grenzwerte', layout='wide')
st.title('Grenz- und Richtwerte')

air = load_air_quality()
daily = daily_means(air)

# (Quelle, Schadstoff, Mittelung, Grenzwert in µg/m³, erlaubte Überschreitungen pro Jahr)
# EU: 39. BImSchV (gültig 2025), EU 2030: Richtlinie (EU) 2024/2881, WHO: Leitlinien 2021.
# WHO-Tageswerte gelten als 99. Perzentil, hier umgesetzt als 4 erlaubte Tage.
LIMITS = [
    ('EU', 'pm10', 'Tag', 50, 35),
    ('EU', 'pm10', 'Jahr', 40, None),
    ('EU', 'pm25', 'Jahr', 25, None),
    ('EU', 'no2', 'Stunde', 200, 18),
    ('EU', 'no2', 'Jahr', 40, None),
    ('EU 2030', 'pm10', 'Tag', 45, 18),
    ('EU 2030', 'pm10', 'Jahr', 20, None),
    ('EU 2030', 'pm25', 'Tag', 25, 18),
    ('EU 2030', 'pm25', 'Jahr', 10, None),
    ('EU 2030', 'no2', 'Stunde', 200, 3),
    ('EU 2030', 'no2', 'Tag', 50, 18),
    ('EU 2030', 'no2', 'Jahr', 20, None),
    ('WHO', 'pm10', 'Tag', 45, 4),
    ('WHO', 'pm10', 'Jahr', 15, None),
    ('WHO', 'pm25', 'Tag', 15, 4),
    ('WHO', 'pm25', 'Jahr', 5, None),
    ('WHO', 'no2', 'Tag', 25, 4),
    ('WHO', 'no2', 'Jahr', 10, None),
]

# ========================================================================================
# Übersicht: eingehalten oder nicht?
rows = []
for source, pollutant, period, limit, allowed in LIMITS:
    if period == 'Jahr':
        measured = air[pollutant].mean()
        result = f'Jahresmittel {measured:.1f}'
        ok = measured <= limit
    else:
        values = air[pollutant] if period == 'Stunde' else daily[pollutant]
        count = int((values > limit).sum())
        result = f'{count} {"Stunden" if period == "Stunde" else "Tage"} darüber'
        ok = count <= allowed
    rows.append({'Quelle': source, 'Schadstoff': POLLUTANTS[pollutant], 'Mittelung': period,
                 f'Grenzwert ({UNIT})': limit, 'Erlaubte Überschreitungen': allowed,
                 'Messung 2025': result, 'Eingehalten': '✅ ja' if ok else '❌ nein'})

st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
st.caption('Tagesmittel zählen nur, wenn mindestens 18 von 24 Stundenwerten vorliegen.')

# ========================================================================================
# Tagesmittel im Vergleich zu einem Grenzwert
st.header('Tagesmittel und Grenzwert')
daily_limits = [lim for lim in LIMITS if lim[2] == 'Tag']
choice = st.selectbox('Grenzwert', daily_limits,
                      format_func=lambda lim: f'{lim[0]}: {POLLUTANTS[lim[1]]}, '
                                              f'Tagesmittel {lim[3]} {UNIT}')
source, pollutant, _, limit, allowed = choice

colors = {f'{POLLUTANTS[pollutant]} Tagesmittel': '#2a78d6', f'Grenzwert {source}': '#898781'}
chart = pd.DataFrame({
    f'{POLLUTANTS[pollutant]} Tagesmittel': daily[pollutant],
    f'Grenzwert {source}': limit,
})
# st.line_chart vergibt die Farben in alphabetischer Reihenfolge der Spaltennamen
st.line_chart(chart, color=[colors[c] for c in sorted(chart.columns)])
days_over = int((daily[pollutant] > limit).sum())
st.write(f'**{days_over} Tage** über {limit} {UNIT}, erlaubt sind {allowed}.')
