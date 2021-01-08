import streamlit as st
import pandas as pd
import uspopulation
import election_results_2016


@st.cache(ttl=60*60*24)
def load_data():
    data = pd.read_csv("https://covidtracking.com/api/v1/states/daily.csv")
    data['date'] = pd.to_datetime(data['date'], format="%Y%m%d") 
    data['positiveRate'] = data['positive']/data['totalTestResults'] 
    population = uspopulation.state_population()

    data = data.merge(population[['ABBREV', 'NAME', 'POPESTIMATE2019']], left_on='state', right_on='ABBREV', suffixes=(False,False))
    data['electionResult'] = data['NAME'].map(election_results_2016.result_by_state)
    data['hospitalizedCurrentlyPer100k'] = data['hospitalizedCurrently']*100000/data['POPESTIMATE2019']

    # the rolling operation below needs an index
    data = data.set_index('date')
    data = data.groupby(['state','electionResult']).rolling(7).mean().shift(periods=-7)

    # create a diff data set showing 7 day change
    diffdata = data.diff(periods=-7).reset_index()

    # Then reset index
    data = data.reset_index()

    # Drop the last record
    diffdata.drop(diffdata.tail(1).index,inplace=True)

    # Name column appropriately. If we want to chart other columns, we should rename them too
    diffdata.rename(
       columns={
           "hospitalizedCurrently": "hospitalized7daychange",
           "hospitalizedCurrentlyPer100k": "hospitalizedPer100k7daychange",
           "positive": "positive7daychange",
           "totalTestResults": "totalTestResults7daychange"
       },inplace=True)


    return (data,diffdata)
