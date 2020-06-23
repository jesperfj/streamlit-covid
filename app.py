import streamlit as st
import pandas as pd
import altair as alt

@st.cache(ttl=60*60*24)
def load_data():
    data = pd.read_csv("https://covidtracking.com/api/v1/states/daily.csv")
    data['date'] = pd.to_datetime(data['date'], format="%Y%m%d")    
    return data

data = load_data()
data = data.set_index('date')
data = data.groupby('state').rolling(7).mean().shift(periods=-7).diff(periods=-7).reset_index()
data.drop(data.tail(1).index,inplace=True)
picked_date = st.date_input("Date", value=data['date'].max()).strftime('%Y-%m-%d')
data = data[data['date'] == picked_date]
st.title(f'Weekly change in hospitalizations on {picked_date}')
st.write(alt.Chart(data).mark_bar().encode(
    y=alt.Y('state', sort='-x'),
    x=alt.X('hospitalizedCurrently', axis=alt.Axis(orient='top'))
    )
)