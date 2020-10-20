import streamlit as st

import pandas as pd
import altair as alt
import population as pop
import election

@st.cache(ttl=60*60*24)
def load_data():
    data = pd.read_csv("https://covidtracking.com/api/v1/states/daily.csv")
    data['date'] = pd.to_datetime(data['date'], format="%Y%m%d") 
    data['positiveRate'] = data['positive']/data['totalTestResults'] 
    return data

@st.cache
def load_pop():
    return pop.population()

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



data = load_data()
population = load_pop()

data = data.merge(population[['ABBREV', 'NAME', 'POPESTIMATE2019']], left_on='state', right_on='ABBREV', suffixes=(False,False))
data['electionResult'] = data['NAME'].map(election.election_result)
data['hospitalizedCurrentlyPer100k'] = data['hospitalizedCurrently']*100000/data['POPESTIMATE2019']

# the rolling operation below needs an index
data = data.set_index('date')
data = data.groupby(['state','electionResult']).rolling(7).mean().shift(periods=-7)

# create a diff data set showing 7 day change
diffdata = data.diff(periods=-7).reset_index()

# Altair expects all columns, no indexes
data = data.reset_index()

# Drop the last record
diffdata.drop(diffdata.tail(1).index,inplace=True)

# Name column appropriately. If we want to chart other columns, we should rename them too
diffdata.rename(
    columns={
        "hospitalizedCurrently": "hospitalized7daychange",
        "positive": "positive7daychange",
        "totalTestResults": "totalTestResults7daychange"
    },inplace=True)

# Magic streamlit function that renders a date picker and assigns the picked value to picked_date
picked_date = st.sidebar.date_input("Snapshot date (only affects some charts)", value=diffdata['date'].max()).strftime('%Y-%m-%d')

#all_states = population[population['STATE']!=0]['ABBREV'].reset_index(drop=True)
#state_selections = st.sidebar.multiselect("State", all_states)

st.markdown("""
All COVID data below comes from [covidtracking.com](https://covidtracking.com/api). Daily values have been smoothened to a 7 day rolling average. 
Population data is from [census.gov](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html).
Election data is from [New York Times](https://www.nytimes.com/elections/2016/results/president).
""")

# 7 day change bar chart
st.title('Weekly change in hospitalizations')
st.write(f'Date: {picked_date}')
# The reason why picked_date was converted to string above is otherwise the data
# selection would not work in this line below.
st.write(alt.Chart(diffdata[diffdata['date'] == picked_date]).mark_bar().encode(
    y=alt.Y('state', sort='-x'),
    x=alt.X('hospitalized7daychange', axis=alt.Axis(orient='top')),
    tooltip=[alt.Tooltip("hospitalized7daychange:Q", title="7 day change", format=',.0d')]
    ).properties(
        width=800
    )
)

st.title('Hospitalizations per 100k now')
st.write(f'Date: {picked_date}')
# The reason why picked_date was converted to string above is otherwise the data
# selection would not work in this line below.
st.write(alt.Chart(data[data['date'] == picked_date]).mark_bar().encode(
    y=alt.Y('state', sort='-x'),
    x=alt.X('hospitalizedCurrentlyPer100k', axis=alt.Axis(orient='top')),
    color=alt.Color("electionResult:N",legend=None,scale=alt.Scale(range=['blue', 'grey','red'])),
    tooltip=[alt.Tooltip("hospitalizedCurrentlyPer100k:Q", title="hospitalized per 100k", format=',.0d')]
    ).properties(
        width=800
    )
)


# Render chart
st.title("Hospitalizations per 100k trend")

st.write(with_highlight('state',alt.Chart(data[data['date']>'2020/03/22']).mark_line().encode(
    x='date',
    y='hospitalizedCurrentlyPer100k',
    color=alt.Color('state', legend=None),
    strokeDash=alt.StrokeDash('state', legend=None),
    tooltip=['state',alt.Tooltip('hospitalizedCurrentlyPer100k:Q',title='value',format=',.0d')]
).properties(
    width=800,
    height=600)))

# Render chart
st.title("Change in hospitalizations last 7 days")
st.write(with_highlight('state',alt.Chart(diffdata[diffdata['date']>'2020/05/01']).mark_line().encode(
    x='date',
    y='hospitalized7daychange',
    color=alt.Color('state', legend=None),
    strokeDash=alt.StrokeDash('state', legend=None),
    tooltip=['state', alt.Tooltip('hospitalized7daychange',title='value',format=',.0d')]
).properties(
    width=800,
    height=600)
))

# Render chart
st.title("Positivity rate")
st.write("Puerto Rico is excluded")
st.write(with_highlight('state',alt.Chart(data[(data['date']>'2020/05/01') & (data['state']!='PR')]).mark_line().encode(
    x='date',
    y='positiveRate',
    color=alt.Color('state', legend=None),
    strokeDash=alt.StrokeDash('state', legend=None),
    tooltip=['state',alt.Tooltip('positiveRate:Q',format=',.0%')]
).properties(
    width=800,
    height=600)
))

data_by_electionresult = data[(data['electionResult']!='None') & (data['date'] > '2020/04/01')].groupby(['electionResult','date']).sum()['hospitalizedCurrently'].reset_index()
st.title("Hospitalizations in red and blue states")
st.write("Based on 2016 presidential election results")
st.write(alt.Chart(data_by_electionresult).mark_area().encode(
    x="date:T",
    y="hospitalizedCurrently:Q",
    color=alt.Color("electionResult:N",legend=None,scale=alt.Scale(range=['blue', 'red']))
).properties(
    width=800,
    height=600)
)


st.write("Below is the same data but not stacked")

st.write(alt.Chart(data_by_electionresult).mark_line().encode(
    x="date:T",
    y="hospitalizedCurrently:Q",
    color=alt.Color("electionResult:N",legend=None,scale=alt.Scale(range=['blue', 'red'])),
    tooltip=['electionResult:N', alt.Tooltip('hospitalizedCurrently',title='value',format=',.0d')]
).properties(
    width=800,
    height=600)
)