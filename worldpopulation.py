import pandas as pd
import streamlit as st
#import code


@st.cache
def load():
    data = pd.read_csv("https://raw.githubusercontent.com/datasets/population/master/data/population.csv")
    data.drop(columns = 'Country Code', inplace=True)
    data.replace('United States','US', inplace=True)
    max_year_indexes = data.groupby(['Country Name']).apply(lambda x: pd.Series({'value': x['Year'].idxmax()}))
    return data.iloc[max_year_indexes['value']].reset_index(drop=True).drop(columns=['Year']).rename(columns={'Country Name': 'country', 'Value': 'country_population'})
    
#code.interact(local=locals())
