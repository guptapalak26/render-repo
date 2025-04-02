import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import numpy as np
# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
# Define the server
server = app.server
# Create the dataset
def load_data():
    fifa_data = {
        'Year': [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 
                1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022],
        'Winner': ['Uruguay', 'Italy', 'Italy', 'Uruguay', 'West Germany', 'Brazil', 'Brazil', 
                  'England', 'Brazil', 'West Germany', 'Argentina', 'Italy', 'Argentina', 
                  'West Germany', 'Brazil', 'France', 'Brazil', 'Italy', 'Spain', 'Germany', 'France', 'Argentina'],
        'Runner-Up': ['Argentina', 'Czechoslovakia', 'Hungary', 'Brazil', 'Hungary', 'Sweden', 
                     'Czechoslovakia', 'West Germany', 'Italy', 'Netherlands', 'Netherlands', 
                     'West Germany', 'West Germany', 'Argentina', 'Italy', 'Brazil', 'Germany', 
                     'France', 'Netherlands', 'Argentina', 'Croatia', 'France'],
        'Winning_Score': ['4-2', '2-1', '4-2', '2-1', '3-2', '5-2', '3-1', '4-2', '4-1', '2-1', 
                         '3-1', '3-1', '3-2', '1-0', '0-0 (3-2)', '3-0', '2-0', '1-1 (5-3)', 
                         '1-0', '1-0', '4-2', '3-3 (4-2)']
    }
    
    # Host countries dictionary
    host_countries = {
        1930: "Uruguay", 1934: "Italy", 1938: "France", 1950: "Brazil", 
        1954: "Switzerland", 1958: "Sweden", 1962: "Chile", 1966: "England", 
        1970: "Mexico", 1974: "West Germany", 1978: "Argentina", 1982: "Spain", 
        1986: "Mexico", 1990: "Italy", 1994: "United States", 1998: "France", 
        2002: "South Korea & Japan", 2006: "Germany", 2010: "South Africa", 
        2014: "Brazil", 2018: "Russia", 2022: "Qatar"
    }
    
    df = pd.DataFrame(fifa_data)
    
    # Add host countries to the dataframe
    df['Host'] = df['Year'].map(host_countries)
    
    # Standardize country names (West Germany → Germany)
    df['Winner'] = df['Winner'].replace('West Germany', 'Germany')
    df['Runner-Up'] = df['Runner-Up'].replace('West Germany', 'Germany')
    df['Host'] = df['Host'].replace('West Germany', 'Germany')
    
    # Calculate win counts for each country
    win_counts = df['Winner'].value_counts().reset_index()
    win_counts.columns = ['Country', 'Wins']
    
    # Calculate runner-up counts for each country
    runnerup_counts = df['Runner-Up'].value_counts().reset_index()
    runnerup_counts.columns = ['Country', 'Runner-Up Times']
    
    return df, win_counts, runnerup_counts
# Load data
df, win_counts, runnerup_counts = load_data()
all_winners = sorted(df['Winner'].unique())
all_years = sorted(df['Year'].unique())
# App layout
app.layout = html.Div([
    html.H1("FIFA World Cup Winners Dashboard", style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': 20}),
    
    html.Div([
        html.P("This interactive dashboard lets you explore the history of FIFA World Cup winners from 1930 to 2022.",
               style={'textAlign': 'center', 'fontSize': '16px', 'marginBottom': '20px'})
    ]),
    
    # Main selection containers
    html.Div([
        # Left column - Country selection
        html.Div([
            html.H3("World Cup Winners", style={'color': '#2c3e50'}),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in all_winners],
                value=all_winners[0],
                style={'marginBottom': '10px'}
            ),
            html.Div(id='country-info', style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),
        
        # Right column - Year selection
        html.Div([
            html.H3("World Cup by Year", style={'color': '#2c3e50'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in all_years],
                value=all_years[-1],  # Most recent by default
                style={'marginBottom': '10px'}
            ),
            html.Div(id='year-info', style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'marginBottom': '30px'}),
    
    # Choropleth map section
    html.Div([
        html.H3("World Cup Wins by Country", style={'color': '#2c3e50', 'textAlign': 'center'}),
        dcc.Graph(id='world-map')
    ], style={'marginBottom': '30px'}),
    
    # Tab section for additional statistics
    html.Div([
        html.H3("World Cup Statistics", style={'color': '#2c3e50', 'textAlign': 'center'}),
        dcc.Tabs([
            dcc.Tab(label="Winners Ranking", children=[
                dcc.Graph(id='winners-bar-chart')
            ]),
            dcc.Tab(label="Runner-Ups", children=[
                dcc.Graph(id='runnerups-bar-chart')
            ]),
            dcc.Tab(label="Win Timeline", children=[
                dcc.Graph(id='win-timeline')
            ])
        ])
    ]),
    
    # Footer
    html.Div([
        html.Hr(),
        html.P("Data source: FIFA World Cup official records (1930-2022)",
               style={'textAlign': 'center', 'fontSize': '12px', 'color': '#7f8c8d'})
    ])
], style={'margin': '0 auto', 'maxWidth': '1200px', 'padding': '20px'})
# Callbacks to update the display based on user selections
@app.callback(
    Output('country-info', 'children'),
    [Input('country-dropdown', 'value')]
)
def update_country_info(selected_country):
    if not selected_country:
        return html.P("Please select a country")
    
    count = win_counts[win_counts['Country'] == selected_country]['Wins'].values[0]
    win_years = df[df['Winner'] == selected_country]['Year'].tolist()
    win_years_str = ", ".join([str(year) for year in win_years])
    
    return [
        html.H4(f"🏆 {selected_country} has won the World Cup {count} times", style={'marginTop': '0'}),
        html.P(f"{selected_country} won in the following years: {win_years_str}")
    ]
@app.callback(
    Output('year-info', 'children'),
    [Input('year-dropdown', 'value')]
)
def update_year_info(selected_year):
    if not selected_year:
        return html.P("Please select a year")
    
    row = df[df['Year'] == selected_year].iloc[0]
    
    return [
        html.H4(f"{row['Year']} World Cup", style={'marginTop': '0'}),
        html.P(f"Winner: {row['Winner']}"),
        html.P(f"Runner-Up: {row['Runner-Up']}"),
        html.P(f"Final Score: {row['Winning_Score']}"),
        html.P(f"Host country: {row['Host']}")
    ]
@app.callback(
    Output('world-map', 'figure'),
    [Input('country-dropdown', 'value')]  # This input is just to trigger the callback, we don't use it
)
def update_map(dummy):
    # Create the choropleth map
    fig = px.choropleth(
        win_counts,
        locations="Country",
        locationmode='country names',
        color="Wins",
        hover_name="Country",
        color_continuous_scale=px.colors.sequential.Plasma,
        title="Number of World Cup Wins by Country"
    )
    
    fig.update_geos(
        subunitcolor="lightgray",
        showcountries=True,
        showsubunits=True,
        showframe=False,
        showcoastlines=True,
        projection_type='equirectangular'
    )
    
    fig.update_layout(
        height=600,
        margin={"r":0,"t":30,"l":0,"b":0}
    )
    
    return fig
@app.callback(
    Output('winners-bar-chart', 'figure'),
    [Input('country-dropdown', 'value')]  # This input is just to trigger the callback, we don't use it
)
def update_winners_chart(dummy):
    # Sort countries by number of wins for the bar chart
    sorted_wins = win_counts.sort_values('Wins', ascending=False)
    
    # Create the bar chart
    fig_bar = px.bar(
        sorted_wins, 
        x='Country', 
        y='Wins',
        color='Wins',
        color_continuous_scale=px.colors.sequential.Plasma,
        title="Countries Ranked by World Cup Wins"
    )
    
    fig_bar.update_layout(
        xaxis_title="Country", 
        yaxis_title="Number of World Cup Wins",
        margin={"r":20,"t":30,"l":20,"b":20}
    )
    
    return fig_bar
@app.callback(
    Output('runnerups-bar-chart', 'figure'),
    [Input('country-dropdown', 'value')]  # This input is just to trigger the callback, we don't use it
)
def update_runnerups_chart(dummy):
    # Sort runner-ups by the number of times
    sorted_runnerups = runnerup_counts.sort_values('Runner-Up Times', ascending=False)
    
    # Create the bar chart for runner-ups
    fig_runnerup = px.bar(
        sorted_runnerups, 
        x='Country', 
        y='Runner-Up Times',
        color='Runner-Up Times',
        color_continuous_scale=px.colors.sequential.Viridis,
        title="Countries Ranked by World Cup Runner-Up Finishes"
    )
    
    fig_runnerup.update_layout(
        xaxis_title="Country", 
        yaxis_title="Number of Runner-Up Finishes",
        margin={"r":20,"t":30,"l":20,"b":20}
    )
    
    return fig_runnerup
@app.callback(
    Output('win-timeline', 'figure'),
    [Input('country-dropdown', 'value')]  # This input is just to trigger the callback, we don't use it
)
def update_timeline(dummy):
    # Timeline visualization
    fig_timeline = px.scatter(
        df,
        x='Year',
        y='Winner',
        color='Winner',
        size=[15] * len(df),  # Constant size
        hover_data=['Runner-Up', 'Winning_Score', 'Host'],
        title="World Cup Winners Timeline (1930-2022)"
    )
    
    fig_timeline.update_traces(
        marker=dict(symbol='star', line=dict(width=2, color='DarkSlateGrey'))
    )
    
    fig_timeline.update_layout(
        xaxis_title="Year", 
        yaxis_title="Winning Country",
        margin={"r":20,"t":30,"l":20,"b":20}
    )
    
    return fig_timeline
# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
