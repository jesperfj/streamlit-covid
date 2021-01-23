import streamlit as st
import pandas as pd
import altair as alt
import deaths
import uscoviddata
import uspopulation
import datetime


@st.cache(ttl=60*60*24)
def ca_hospital_data():
    return pd.read_csv("https://data.ca.gov/dataset/529ac907-6ba1-4cb7-9aae-8966fc96aeef/resource/42d33765-20fd-44b8-a978-b083b7542225/download/hospitals_by_county.csv")
    


def with_highlight(field, base):
    highlight = alt.selection(type='single', on='mouseover',
                          fields=[field], nearest=True)
    points = base.mark_circle().encode(
        opacity=alt.value(0)
    ).add_selection(
        highlight
    )
    lines = base.mark_line().encode(
        size=alt.condition(~highlight, alt.value(1), alt.value(3))
    )
    return points+lines

usdata,usdata_diff = uscoviddata.load_data()

st.title("Hospitalizations by US state per 100,000 inhabitants")
st.markdown("""
Sources: [covidtracking.com](https://covidtracking.com/api), [census.gov](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html)

Hospitalization data is more normalized than case data because testing rates (and thus known cases) varies too much across states. 
While less of a leading indicator, the 7 day change gives a reasonable early sign of trouble.
""")

# Magic streamlit function that renders a date picker and assigns the picked value to picked_date
picked_date = st.date_input("Date", value=usdata_diff['date'].max()).strftime('%Y-%m-%d')

# 7 day change bar chart
st.subheader('Change last 7 days')
# The reason why picked_date was converted to string above is otherwise the data
# selection would not work in this line below.
st.write(alt.Chart(usdata_diff[usdata_diff['date'] == picked_date]).mark_bar().encode(
    y=alt.Y('state', sort='-x'),
    x=alt.X('hospitalizedPer100k7daychange:Q', axis=alt.Axis(orient='top')),
    tooltip=[alt.Tooltip("hospitalizedPer100k7daychange:Q", title="7 day change", format=',.0d')]
    ).properties(
        width=800
    )
)

st.subheader('Total')
st.markdown("Red bars are republican states, blue bars are democratic states per 2016 presidential election")
# The reason why picked_date was converted to string above is otherwise the data
# selection would not work in this line below.
st.write(alt.Chart(usdata[usdata['date'] == picked_date]).mark_bar().encode(
    y=alt.Y('state', sort='-x'),
    x=alt.X('hospitalizedCurrentlyPer100k', axis=alt.Axis(orient='top')),
    tooltip=[alt.Tooltip("hospitalizedCurrentlyPer100k:Q", title="hospitalized per 100k", format=',.2f')]
    ).properties(
        width=800
    )
)


st.title("Trend for selected states")
all_states = usdata['state'].unique().tolist()
selected_states = st.multiselect("States", options=all_states, default=['CA','TX','FL','IL'])
start_date = st.date_input("Start date", value = datetime.date(2020, 4, 1))

filtered_usdata = usdata[(usdata['state'].isin(selected_states)) & (usdata['date'] > pd.to_datetime(start_date))]
filtered_usdata_diff = usdata_diff[(usdata_diff['state'].isin(selected_states)) & (usdata_diff['date'] > pd.to_datetime(start_date))]

st.subheader("Hospitalizations per 100k")
st.write(with_highlight('state',alt.Chart(filtered_usdata).mark_line().encode(
    x='date',
    y='hospitalizedCurrentlyPer100k',
    color=alt.Color('state'),
    tooltip=['state','date:T',alt.Tooltip('hospitalizedCurrentlyPer100k:Q',title='value',format=',.1d')]
).properties(
    width=800,
    height=600)))

# Render chart
st.subheader("Change last 7 days in hospitalizations per 100k")
st.write(with_highlight('state',alt.Chart(filtered_usdata_diff).mark_line().encode(
    x='date',
    y='hospitalizedPer100k7daychange',
    color=alt.Color('state'),
    tooltip=['state', 'date:T',alt.Tooltip('hospitalizedPer100k7daychange',title='value',format=',.1d')]
).properties(
    width=800,
    height=600)
))

ca_data = ca_hospital_data()

# The picked date may be ahead of available data
use_date = min(ca_data['todays_date'].max(),picked_date)

county_pop = uspopulation.county_population()
county_pop = county_pop[county_pop['state']=='CA']
ca_data = ca_data.merge(county_pop, left_on='county', right_on='county', suffixes=(False,False))
ca_data = ca_data[ca_data['todays_date']==use_date]
ca_data['hospitalized_per_100k'] = ca_data['hospitalized_covid_confirmed_patients']*100000/ca_data['population']

st.title("Hospitalizations per 100k in California counties")
st.write(f"Date: {use_date}")
st.write(alt.Chart(ca_data).mark_bar().encode(
    y=alt.Y('county', sort='-x'),
    x=alt.X('hospitalized_per_100k', axis=alt.Axis(orient='top')),
    tooltip=[alt.Tooltip("hospitalized_per_100k:Q", title="hospitalized per 100k", format=',.2f')]
    ).properties(
        width=800
    )
)

st.title("Deaths per million in selected countries")

wd = deaths.data()

available_countries = wd['country'].unique().tolist()
selected_countries = st.multiselect("Countries", options=available_countries, default=['Denmark','US','United Kingdom','Sweden','Japan','France','Germany'])

wd = wd[wd['country'].isin(selected_countries)]

wddiff = deaths.diff(wd,7)

st.subheader("Last 7 days")
st.write(with_highlight('country',alt.Chart(wddiff).mark_line().encode(
    x="date:T",
    y="deaths_per_1M:Q",
    color=alt.Color("country:N"),
    tooltip=['country:N', 'date:T', alt.Tooltip('deaths_per_1M',title='Deaths per 1M last 7 days',format=',.0d')]
).properties(
    width=800,
    height=600)
))

st.subheader("Total")
st.write(with_highlight('country',alt.Chart(wd).mark_line().encode(
    x="date:T",
    y="deaths_per_1M:Q",
    color=alt.Color("country:N"),
    tooltip=['country:N',  'date:T', alt.Tooltip('deaths_per_1M',title='Total deaths per 1M',format=',.0d')]
).properties(
    width=800,
    height=600)
))

