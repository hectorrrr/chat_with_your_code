import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from flask import Flask, request, jsonify
import logging
from neomodel import config, db
import os
from dotenv import load_dotenv

from dash_utils import *

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
stylesheet=     [
                        {
                            'selector': 'node',
                            'style': {
                                'label': 'data(label)',
                                'text-valign': 'top', 
                                'text-halign': 'center',
                                'background-color': '#888',
                                'color': 'black',
                                'width': '60px',
                                'height': '60px',
                                'text-margin-y': '-10px'
                            }
                        },
                        {
                            'selector': 'edge',
                            'style': {
                                'width': 2,
                                'line-color': '#ccc',
                                'target-arrow-color': '#ccc',
                                'target-arrow-shape': 'triangle',
                                'curve-style': 'bezier'
                            }
                        },
                        {
                            'selector': '.red',
                            'style': {
                                'background-color': 'red'
                            }
                        },
                        {
                            'selector': 'node',
                            'style': {
                                'content': 'data(label)'
                            }
                        },
                        {
                            'selector': '.Function',
                            'style': {
                                'background-color': 'red',
                                'line-color': 'red'
                            }
                        },
                        {
                            'selector': '.Framework',
                            'style': {
                                'shape': 'triangle'
                            }
                        },
                        {
                            'selector': '[highlighted = "True"]',
                            'style': {
                                'background-color': 'yellow',
                                'line-color': 'yellow'
                            }
                        }
                ]


# Define the layout for Cytoscape
layout = {
    'name': 'breadthfirst',
    'directed': True,
    'roots': '[id = "data_preprocessing"], [id = "modelling"], [id = "visualization"]',  # Specify the root nodes
    'orientation': 'vertical',  # Set orientation to vertical
    'padding': 10,
    'spacingFactor': 1.5,  # Adjust spacing between nodes
    'animate': True,
    'circle': False,
    'animationDuration': 500
}


@app.callback(
    # [Output('card', 'children'),
    # ],
    [Output('card', 'children'),
    Output('card', 'style')],
    # Output('cytoscape-container', 'style')
    [Input('cytoscape-graph', 'tapNodeData')]
)
def display_node_data(data):
    if data is None:
        return "", {'width': '0%', 'float': 'left', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'overflow': 'hidden', 'transition': 'width 0.5s'}#, {'width': '100%', 'float': 'right', 'transition': 'width 0.5s'}

    file_path = "data_science_repo\\" + data.get('file_path') # TODO improve this
    # file_link = None
    if file_path:
        abs_file_path = os.path.abspath(file_path)
        file_link = html.A('Open in VS Code', href=f"vscode://file/{abs_file_path}", target="_blank", style={'color': '#007bff', 'textDecoration': 'none'})
    
        card_content = html.Div([
            html.H4(f"Node ID: {data['id']}"),
            html.P(f"Label: {data.get('label', 'N/A')}"),
            html.P(f"Description: {data.get('description', 'No description available')}"),
            html.P(f"File Path: {file_path}"),
            file_link
        ])
        
    else:
        card_content = html.Div([
            html.H4(f"Node ID: {data['id']}"),
            html.P(f"Label: {data.get('label', 'N/A')}"),
            html.P(f"Description: {data.get('description', 'No description available')}"),
        ])

    return card_content, {'width': '100%', 'float': 'left', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'overflow': 'auto', 'transition': 'width 0.5s'}#, {'width': '75%', 'float': 'right', 'transition': 'width 0.5s'}

if __name__ == '__main__':
    # Set up the database connection
    config.DATABASE_NAME = 'graphrag'
    neo4j_password = os.environ.get('NEO4J_PASSWORD')
    db.set_connection(url=f"bolt://neo4j:{neo4j_password}@localhost:7687")

    # Use the global variable for the database connection
    global db_connection
    db_connection = db

    # Initial full graph query
    try:
        mapped_nodes, mapped_relationships = initial_query(db_connection)
        logger.debug("Initial graph data loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading initial graph data: {e}")
    
    app.layout =  dbc.Container(
        [
            # Header Section
            dbc.Row([
                dbc.Col(html.Div([
                    html.H1(
                        "Data Science Knowledge Navigator", 
                        style={
                            'color': '#ffffff',  
                            'fontSize': '36px', 
                            'marginBottom': '10px',
                            'textShadow': '1px 1px 2px #000000'
                        }
                    ),
                    html.P(
                        "Visualize and Explore the Relationships Between Concepts, Functions, and Tools in Your Data Science Repository",
                        style={
                            'color': '#cce7ff',
                            'fontSize': '18px', 
                            'marginBottom': '20px',
                            'fontStyle': 'italic'
                        }
                    ),
                    html.Hr(style={'borderColor': '#ffffff'}),
                ], style={
                    'textAlign': 'center', 
                    'padding': '20px', 
                    'background': 'linear-gradient(90deg, #4b6cb7 0%, #182848 100%)', 
                    'color': '#ffffff'
                }))
            ]),

            # Main Content Area with Two Columns
            dbc.Row(
                [
                    # Left Column for Query and Card
                    dbc.Col([
                        dcc.Input(
                            id='input-question',
                            type='text',
                            placeholder='Enter your Cypher query here...',
                            style={'width': '100%', 'padding': '10px', 'marginBottom': '10px'}
                        ),
                        html.Button('Submit Query', id='submit-button', n_clicks=0, style={'width': '100%', 'padding': '10px'}), #
                        html.P("Enter a valid Cypher query and click 'Submit Query' to update the graph visualization.", style={'fontStyle': 'italic'}),
                        html.Div(id='card', style={
                            'padding': '20px',
                            'backgroundColor': '#f8f9fa',
                            'overflow': 'hidden',
                            'display': 'none',  # Initially hidden,
                            'height': '100%'
                        }),
                    ], width=3, style={'height': '100vh'}),  # Ensuring full viewport height for the left column

                    # Right Column for Cytoscape Graph
                    dbc.Col([
                        cyto.Cytoscape(
                            id='cytoscape-graph',
                            elements=mapped_nodes+mapped_relationships,  # Replace with your elements
                            style={'width': '100%', 'height': '100%'},
                            layout = layout,
                            stylesheet=stylesheet
                        )
                    ], width=9, style={'height': '100vh'})  # Ensuring full viewport height for the right column
                ],
                style={'height': '100vh'}  # Ensuring full viewport height for the row
            )
        ],fluid=True,
        style={'height': '100%'}
)

    app.run_server(debug=True)
