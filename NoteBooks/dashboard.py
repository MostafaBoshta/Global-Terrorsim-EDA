import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import lodingdata as ld

# Load data
path = r'F:\pythonProject\Data\cleanedData.csv'
loadData = ld.dataloader(path)
data = loadData.pdloader()
marks = {int(year): str(year) for year in data['iyear'].unique() if year % 5 == 0}
app = dash.Dash(__name__)
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

app.layout = html.Div([
    html.Div([
        html.H1('Global Terrorism Data Dashboard'),
        html.Div([
            dcc.Dropdown(
                id='location-filter',
                options=[{'label': loc, 'value': loc} for loc in data['region_txt'].unique()],
                multi=True,
                placeholder='Location',
                style={'width': '45%', 'display': 'inline-block', 'margin-right': '10px'}
            ),
            html.Div(
                dcc.RangeSlider(
                    id='year-slider',
                    min=data['iyear'].min(),
                    max=data['iyear'].max(),
                    marks=marks,
                    value=[data['iyear'].min(), data['iyear'].max()]
                ),
                style={'width': '45%', 'display': 'inline-block'}
            ),
        ], style={'display': 'flex', 'justify-content': 'space-between'}),
    ], style={'padding': '20px'}),

    html.Div([
        html.H2('Countires Attacks Distribution'),
        html.Div([
            dcc.Graph(id='country_kills_map'),
        ], className='six columns'),

        html.Div([
            html.H2('Kills by City'),
            dcc.Graph(id='kills_by_city_map'),
        ], className='six columns'),
    ], className='row'),

    html.Div([
        html.Div([
            html.H2('Successed Rate'),
            dcc.Graph(id='successed_rate'),
        ], className='six columns'),

        html.Div([
            html.H2('Kills by Region'),
            dcc.Graph(id='killsByRegion'),
        ], className='six columns'),
    ], className='row'),

    html.Div([
        html.H2('Attacks Over Time'),
        dcc.Graph(id='deaths-per-million-over-time'),
    ], style={'width': '100%'})
])

@app.callback(
    [Output('country_kills_map', 'figure'),
     Output('successed_rate', 'figure'),
     Output('kills_by_city_map', 'figure'),
     Output('killsByRegion', 'figure'),
     Output('deaths-per-million-over-time', 'figure')],
    [Input('location-filter', 'value'),
     Input('year-slider', 'value')]
)
def update_dashboard(selected_locations, selected_years):
    # Filter data based on selections
    filtered_df = data[(data['iyear'] >= selected_years[0]) & (data['iyear'] <= selected_years[1])]
    if selected_locations:
        filtered_df = filtered_df[filtered_df['region_txt'].isin(selected_locations)]
    
    # Generate plots
    countriesAttack = filtered_df.groupby('country_txt')['nkill'].count().reset_index()
    countriesAttack = countriesAttack.rename(columns={'nkill': 'AttacksNo'})
    countriesAttack['country_txt'] = countriesAttack['country_txt'].replace({'United States': 'United States of America', 'Tanzania': 'United Republic of Tanzania', 'Serbia': "Republic of Serbia"})
    geojson = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json'
    country_kills_map = px.choropleth_mapbox(countriesAttack, locations='country_txt', geojson=geojson, featureidkey="properties.name", color='AttacksNo', mapbox_style='carto-positron', zoom=1)
    successed_rate = px.pie(filtered_df, values='nkill', names='success', hole=.3)
    
    # Since regions are not valid for choropleth, use a different plot type
    kills_by_region = filtered_df.groupby('region_txt')['nkill'].sum().reset_index()
    kills_by_city_map = px.scatter_mapbox(filtered_df, lat='latitude', lon='longitude', size='nkill',color= 'nkill' ,zoom = 2, mapbox_style = 'open-street-map'
                ,hover_data=['country_txt' , 'city'],color_continuous_scale=px.colors.cyclical.IceFire)
    
    killsByRegion = px.bar(kills_by_region, x='region_txt', y='nkill')
    yearsAttacks = filtered_df.groupby('iyear')['nkill'].sum().reset_index()
    deaths_per_million_over_time = px.line(yearsAttacks, x='iyear', y='nkill', markers=True)
    
    return country_kills_map, successed_rate, kills_by_city_map, killsByRegion, deaths_per_million_over_time

if __name__ == '__main__':
    app.run_server(debug=True)
