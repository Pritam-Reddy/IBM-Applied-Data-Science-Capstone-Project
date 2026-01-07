# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a Launch Site Drop-down Input Component
    # We create a dropdown with options for All Sites and each individual site.
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a Range Slider to Select Payload
    # Slider to filter data by Payload Mass (kg)
    dcc.RangeSlider(
        id='payload-slider',
        min=0, 
        max=10000, 
        step=1000,
        marks={0: '0', 100: '100', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback function for the Pie Chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # If ALL sites selected, show total success counts (Class=1) relative to each site
        # Note: Pie chart values=class (1s) will sum up the successes per site
        fig = px.pie(
            spacex_df, 
            values='class', 
            names='Launch Site', 
            title='Total Success Launches By Site'
        )
        return fig
    else:
        # If specific site selected, filter and show Success (1) vs Failure (0) count
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Group by class to get counts of 0 and 1
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        fig = px.pie(
            site_counts, 
            values='count', 
            names='class', 
            title=f'Total Success Launches for site {entered_site}'
        )
        return fig

# TASK 4: Callback function for the Scatter Plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_chart(entered_site, payload_range):
    # Filter data based on the slider range first
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if entered_site == 'ALL':
        # Render scatter plot for all sites
        fig = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)', 
            y='class', 
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites'
        )
        return fig
    else:
        # Filter again for the specific site
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_filtered_df, 
            x='Payload Mass (kg)', 
            y='class', 
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for {entered_site}'
        )
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port=8050)
