import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
pio.templates.default = "plotly_dark"

st.set_page_config(page_title='Covid Tracker App', page_icon=':microbe:', layout='wide')

def _max_width_():
    max_width_str = "max-width: 1300px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )

_max_width_()

st.title('Covid Tracker App')

def load_data():
    return pd.read_csv('https://opendata.ecdc.europa.eu/covid19/nationalcasedeath_eueea_daily_ei/csv/data.csv')

def world_cumulated(df_world_filtered_int):

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=df_world_filtered_int['dateRep'],
        y=df_world_filtered_int['cumulated_cases'],
        name='Cases',
        mode='lines'
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df_world_filtered_int['dateRep'],
        y=df_world_filtered_int['cumulated_deaths'],
        name='Deaths',
        mode='lines'
    ), secondary_y=True)

    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="Cases", secondary_y=False)
    fig.update_yaxes(title_text="Deaths", secondary_y=True)

    fig.update_layout(width=1000, height=600, title='Cumulated Cases and Deaths in the World', title_x=0.5)

    return fig

def world_new_cases(df_world_filtered_int):

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_world_filtered_int['dateRep'],
        y=df_world_filtered_int['cases'],
        name='Cases per Day',
        mode='lines'
    ))

    fig.add_trace(go.Scatter(
        x=df_world_filtered_int['dateRep'],
        y=df_world_filtered_int['rolling_cases'],
        name='7-day Rolling Average',
        mode='lines'
    ))

    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Cases per Day")

    fig.update_layout(width=1000, height=600, title='New Cases in the World', title_x=0.5)

    return fig

def filter_country(country, df_filtered):
    df_country = df_filtered[df_filtered['countriesAndTerritories'] == country].sort_values(by='dateRep')[['dateRep', 'countriesAndTerritories', 'cases', 'deaths']]
    df_country[['cases', 'deaths']] = df_country[['cases', 'deaths']]
    df_country['rolling_cases'] = df_country['cases'].rolling(7).mean().round(0)
    df_country['rolling_deaths'] = df_country['deaths'].rolling(7).mean().round(0)
    df_country = df_country[df_country['dateRep'] >= '2020-03-01']
    df_country.reset_index(drop=True, inplace=True)
    return df_country

def cases_country(df_country):

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_country['dateRep'],
        y=df_country['cases'],
        name='Cases per Day',
        mode='lines'
    ))

    fig.add_trace(go.Scatter(
        x=df_country['dateRep'],
        y=df_country['rolling_cases'],
        name='7-day Rolling Average',
        mode='lines'
    ))

    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Cases per Day")

    fig.update_layout(width=1000, height=600, title=f'New Cases in {country} per Day', title_x=0.5)

    return fig

def deaths_country(df_country):

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_country['dateRep'],
        y=df_country['deaths'],
        name='Deaths per Day',
        mode='lines'
    ))

    fig.add_trace(go.Scatter(
        x=df_country['dateRep'],
        y=df_country['rolling_deaths'],
        name='7-day Rolling Average',
        mode='lines'
    ))

    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Deaths per Day")

    fig.update_layout(width=1000, height=600, title=f'New Deaths in {country} per Day', title_x=0.5)

    return fig

df = load_data()


df['dateRep'] = pd.to_datetime(df['dateRep'], infer_datetime_format=True)
df_filtered = df[df['dateRep'] >= '2020-02-20'].sort_values(by='dateRep')
df_world = df_filtered.groupby('dateRep').sum().reset_index()
df_world = df_world[['dateRep', 'cases', 'deaths']]
df_world['cases'] = df_world['cases'].astype(int)
df_world['deaths'] = df_world['deaths'].astype(int)
df_world['cumulated_cases'] = df_world['cases'].cumsum()
df_world['cumulated_deaths'] = df_world['deaths'].cumsum()
df_world['rolling_cases'] = df_world['cases'].rolling(7).mean().round(0)
df_world['rolling_deaths'] = df_world['deaths'].rolling(7).mean().round(0)
df_world_filtered = df_world[df_world['dateRep'] >= '2020-03-01']
df_world_filtered_int = df_world_filtered.copy()
df_world_filtered_int[['rolling_cases', 'rolling_deaths']] = df_world_filtered[['rolling_cases', 'rolling_deaths']].astype(int)

with st.sidebar:
    'Please select a country:'
    country = st.selectbox('Country', df['countriesAndTerritories'].unique())
    df_country = filter_country(country, df_filtered)

st.markdown('## World Analysis')
st.write(' ')


col1, col2, col3 = st.columns([6,1,6])

with col1:
    st.plotly_chart(world_cumulated(df_world_filtered_int))

with col3:
    st.plotly_chart(world_new_cases(df_world_filtered_int))

st.markdown('## Country Analysis')
st.write(' ')

df_country = filter_country(country, df_filtered)

growth_cases = (df_country.iloc[-1]['rolling_cases'] - df_country.iloc[-2]['rolling_cases']) / df_country.iloc[-2]['rolling_cases'] * 100
growth_deaths = (df_country.iloc[-1]['rolling_deaths'] - df_country.iloc[-2]['rolling_deaths']) / df_country.iloc[-2]['rolling_deaths'] * 100

col1, col2, col3 = st.columns([6,1,6])

with col1:
    
    growth_cases = (df_country.iloc[-1]['rolling_cases'] - df_country.iloc[-2]['rolling_cases']) / df_country.iloc[-2]['rolling_cases'] * 100
    growth_deaths = (df_country.iloc[-1]['rolling_deaths'] - df_country.iloc[-2]['rolling_deaths']) / df_country.iloc[-2]['rolling_deaths'] * 100
    st.write('Current growth rate of cases:')
    st.write(f'{growth_cases:.2f}%')
    st.write(' ')
    st.plotly_chart(cases_country(df_country))

with col3 :
    
    growth_cases = (df_country.iloc[-1]['rolling_cases'] - df_country.iloc[-2]['rolling_cases']) / df_country.iloc[-2]['rolling_cases'] * 100
    growth_deaths = (df_country.iloc[-1]['rolling_deaths'] - df_country.iloc[-2]['rolling_deaths']) / df_country.iloc[-2]['rolling_deaths'] * 100
    st.write('Current growth rate of deaths:')
    st.write(f'{growth_deaths:.2f}%')
    st.write(' ')
    st.plotly_chart(deaths_country(df_country))

