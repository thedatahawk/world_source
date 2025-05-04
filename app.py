import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output


link_to_df = r'https://raw.githubusercontent.com/thedatahawk/datasets/refs/heads/main/world_sourcing.csv'
df = pd.read_csv(link_to_df, dtype={"year": str})


       
#Get unique values for dropdowns
selling_countries = df['selling_country'].unique()
industries = df['sourcing_industry_name'].unique()
value_options = [
    {'label': 'Foreign Production Exposure: Look Through', 'value': 'FPEM'},
    {'label': 'Foreign Production Exposure: Face Value', 'value': 'FPEMfv'},
    {'label': 'Foreign Production Exposure: Hidden', 'value': 'FPEMhe'}
]

#initialize Dash app
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Manufacturing Exposure by Country and Industry"),
html.Div([
    html.P([
        "This data tool is based on the work of Richard Baldwin, Rebecca Freeman & Angelos Theodorakopoulos as described in ",
        html.A(
            "Hidden Exposure: Measuring US Supply Chain Reliance",
            href="https://www.nber.org/papers/w31820",
            target="_blank", rel="noopener noreferrer"
        ),
        " and ",
        html.A(
            "Horses for Courses: Measuring Foreign Supply Chain Exposure",
            href="https://www.nber.org/papers/w30525",
            target="_blank", rel="noopener noreferrer"
        ),
        "."
    ]),
    html.P([
        "I am not affiliated in any way with the authors; any errors in the data tool are my own. Source data are from ",
        html.A(
            "OECD Trade in Value-Added.",
            href="https://www.oecd.org/en/topics/sub-issues/trade-in-value-added.html",
            target="_blank", rel="noopener noreferrer"
        ),
        "."
    ]),
    html.P([
        "For U.S. exposure by country, see ",
        html.A(
            "U.S. Source",
            href="https://us-source.onrender.com",
            target="_blank", rel="noopener noreferrer"
        ),
        "."
    ]),
    html.P("This tool displays three estimates of U.S. production exposure in manufacturing:"),
    html.Ul([
        html.Li("Face Value"),
        html.Li("Look Through"),
        html.Li("Hidden")
    ])
]),



    html.Div([
    html.Label("Select Sourcing Country:"),
    dcc.Dropdown(
        id='sourcing-country',
        options=[{'label': s , 'value': s} for s in selling_countries],
        value='United States',
        clearable=False,
        style={'width': '400px'}        
    )], style={'display': 'inline-block', 'margin-right': '20px'}),
    
    html.Div([
    html.Label("Select Selling Country:"),
    dcc.Dropdown(
        id='selling-country',
        options=[{'label': c , 'value': c} for c in selling_countries],
        value='United States',
        clearable=False,
        style={'width': '400px'}
    )
    ], style={'display': 'inline-block'}),
    
    html.Br(),
    html.Br(),
    
    html.Div([
    html.Label("Select Industry:"),
    dcc.Dropdown(
        id='industry',
        options=[{'label': i, 'value': i} for i in industries],
        value='Manuf. avg.',
        clearable=False,
        style={'width': '400px'}
        )
    ], style={'display': 'inline-block', 'margin-right': '20px'}),
    
    html.Div([
    html.Label("Select Exposure Metric:"),
    dcc.Dropdown(
        id='value-metric',
        options=value_options,
        value='FPEM',
        clearable=False,
        style={'width': '400px'}
        )
    ], style={'display': 'inline-block'}),
    
    dcc.Graph(id='line-chart'),
    
    html.Div(id='latest-value-text', style={'whiteSpace': 'pre-line'})
])    
        
@app.callback(
    [Output('line-chart', 'figure'),
     Output('latest-value-text', 'children')],
    [Input('sourcing-country', 'value'),
     Input('selling-country', 'value'),
     Input('industry', 'value'),
     Input('value-metric', 'value')]
)
def update_graph(selected_sourcing_country, selected_selling_country, selected_industry, selected_metric):
    filtered_df= df[(df['sourcing_country'] == selected_sourcing_country) & (df['selling_country'] == selected_selling_country) & (df['sourcing_industry_name'] == selected_industry)]
    fig = px.line(filtered_df, x= 'year', y = selected_metric, title=f'{selected_sourcing_country}  {selected_metric} exposure from {selected_selling_country} in the {selected_industry} industry')
   
    #most recent USA data
    country_df = df[(df['sourcing_country'] == selected_sourcing_country) & (df['selling_country'] == selected_sourcing_country)& (df['sourcing_industry_name'] == selected_industry)]
    if not country_df.empty:
        sorted_country_df = country_df.sort_values(by='year', ascending=True)
        first_year, first_value = sorted_country_df.iloc[0]['year'], round(sorted_country_df.iloc[0][selected_metric], 2)
        latest_year, latest_value = sorted_country_df.iloc[-1]['year'], round(sorted_country_df.iloc[-1][selected_metric], 2)
        change_value = round(latest_value - first_value, 2)
           
        latest_value_text = (
            f"For {selected_sourcing_country} in {selected_industry} using {selected_metric}: \n"
            f"- {first_year}: {first_value}. \n"
            f"- {latest_year}: {latest_value}. \n"
            f"- Percentage Point difference: {change_value}. "
        )
    else:
        latest_value_text = "No Data Available."
    
    return fig, latest_value_text


if __name__ == '__main__':
    app.run(debug=True)


