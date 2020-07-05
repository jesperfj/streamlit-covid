import streamlit as st

import pandas as pd
import altair as alt

import population as pop

@st.cache
def load_data():
    return pop.population()

data = load_data()

st.write(data)

st.write(alt.Chart(data[data['STATE']!=0]).mark_bar().encode(
    y=alt.Y('NAME', sort='-x'),
    x=alt.X('POPESTIMATE2019', axis=alt.Axis(orient='top')),
    tooltip=[alt.Tooltip("POPESTIMATE2019:Q", title="2019 estimated", format=',')],
    ).properties(
        width=800
    )
)
