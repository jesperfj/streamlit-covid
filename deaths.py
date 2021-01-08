import worldpopulation
import pandas as pd
import streamlit as st

# For worldwide comparison, I look at death rates to follow the big question of whether the Swedish model will succeed
# The theory is that it's ok to have a lot of cases as long as people don't die.
# I'll probably add cases an hospitalizations at some point, if there is reliable and comparable data for it.

@st.cache(ttl=60*60*24)
def data():
    wd = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")

    # The data set has several rows per country. It looks like if we keep only rows without Province/State set then we'll get one row per country.
    wd = wd[wd['Province/State'].isna()]
    # Now we don't need these columns anymore
    wd.drop(columns=['Province/State','Lat','Long'],inplace=True)
    # The data set has a column per date. This turns it into a "detail table" with a row per country per date
    wd = pd.melt(wd, id_vars='Country/Region')
    # Set proper data type for date and rename columns
    wd['variable'] = pd.to_datetime(wd['variable'])
    wd.rename(columns = { 'variable': 'date', 'Country/Region': 'country'},inplace=True)

    # Load in world population and merge into data set
    world_pop = worldpopulation.load()
    wd = wd.merge(world_pop, on='country', suffixes=(False,False))

    # Calculate deaths per million
    wd['deaths_per_1M'] = wd['value']*float(1000000)/wd['country_population']

    return wd

@st.cache(ttl=60*60*24)
def diff(data,days):
    return data.set_index(['date', 'country']).groupby(level=1).diff(periods=days).reset_index()

