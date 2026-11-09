# system modules
import pandas as pd
import plotly.express as px
import streamlit as st

# own modules
from app.read_data import AQI_COLORS, AQI_LEVELS, POLLUTANTS, UNIT, load_air_quality


st.set_page_config(page_title='Polution Analysis', layout='wide',
                   page_icon=':chart_with_upwards_trend:',
                   initial_sidebar_state='expanded')

st.title('Luftqualität Köln')
st.sidebar.header("Menu")


st.sidebar.markdown('''
---
Created by [Johann Schaible](https://www.th-koeln.de/personen/johann.schaible/)
''')



air = load_air_quality()

# ========================================================================================
# Überblick der Daten und erste deskriptive Statistik
st.header('Überblick')
st.write(f'Messstation {air["station"].iloc[0]}, {len(air)} Stundenwerte im Jahr 2025.')

cols = st.columns(len(POLLUTANTS))
for col, (key, name) in zip(cols, POLLUTANTS.items()):
    col.metric(f'{name} · Jahresmittel ({UNIT})', f'{air[key].mean():.1f}'.replace('.', ','))

stats = air[list(POLLUTANTS)].rename(columns=POLLUTANTS).describe().T
stats = stats.rename(columns={'count': 'Anzahl', 'mean': 'Mittelwert', 'std': 'Std.-Abw.',
                              'min': 'Min', 'max': 'Max'})
st.dataframe(stats.round(1), use_container_width=True)

# ========================================================================================
# Allgemeiner Luftqualitätsindex
st.header('Luftqualitätsindex')
share = air['aqi'].value_counts(normalize=True).reindex(AQI_LEVELS) * 100
fig = px.bar(x=share.index, y=share.values, color=share.index,
             color_discrete_map=AQI_COLORS,
             labels={'x': 'Indexstufe', 'y': 'Anteil der Stunden (%)', 'color': 'Indexstufe'})
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# ========================================================================================
# Luftqualitätsindex nach Monaten
st.header('Luftqualitätsindex nach Monaten')
monthly = pd.crosstab(air['monat'], air['aqi'], normalize='index') * 100
monthly = monthly.reset_index().melt(id_vars='monat', var_name='Indexstufe', value_name='Anteil')
fig = px.bar(monthly, x='monat', y='Anteil', color='Indexstufe',
             color_discrete_map=AQI_COLORS, category_orders={'Indexstufe': AQI_LEVELS},
             labels={'monat': 'Monat', 'Anteil': 'Anteil der Stunden (%)'})
fig.update_traces(offsetgroup=None)  # sonst stehen die Stufen nebeneinander statt gestapelt
fig.update_layout(barmode='stack')
fig.update_xaxes(dtick=1)
st.plotly_chart(fig, use_container_width=True)
st.caption('Im Dezember fehlen fast alle Messwerte, der Monat ist daher kaum aussagekräftig.')