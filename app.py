import streamlit as st

import pandas as pd
import altair as alt

@st.cache(ttl=60*60*24)
def load_data():
    data = pd.read_csv("https://covidtracking.com/api/v1/states/daily.csv")
    data['date'] = pd.to_datetime(data['date'], format="%Y%m%d")    
    return data

data = load_data()
data1 = data
data = data.set_index('date')
data = data.groupby('state').rolling(7).mean().shift(periods=-7)
diffdata = data.diff(periods=-7).reset_index()
data = data.reset_index()

diffdata.drop(diffdata.tail(1).index,inplace=True)
diffdata.rename(columns={"hospitalizedCurrently" : "hospitalized7daychange"},inplace=True)
picked_date = st.date_input("Date", value=diffdata['date'].max()).strftime('%Y-%m-%d')
st.title(f'Weekly change in hospitalizations on {picked_date}')
st.write(alt.Chart(diffdata[diffdata['date'] == picked_date]).mark_bar().encode(
    y=alt.Y('state', sort='-x'),
    x=alt.X('hospitalized7daychange', axis=alt.Axis(orient='top'))
    ).properties(
        width=800
    )
)
st.title("Hospitalizations by state over time")
st.write(alt.Chart(data[data['date']>'2020/03/22']).mark_line().encode(
    x='date',
    y='hospitalizedCurrently',
    color='state',
    strokeDash='state',
    tooltip='state'
).properties(
    width=800,
    height=600))

st.title("Change in hospitalizations last 7 days")
st.write(alt.Chart(diffdata[diffdata['date']>'2020/05/01']).mark_line().encode(
    x='date',
    y='hospitalized7daychange',
    color='state',
    strokeDash='state',
    tooltip='state'
).properties(
    width=800,
    height=600))
