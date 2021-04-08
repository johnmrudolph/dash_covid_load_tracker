# -*- coding: utf-8 -*-
from dash_bootstrap_components._components.ModalHeader import ModalHeader
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc


from dash.dependencies import Input, Output, State

# relative imports
from app_functions import create_error_graph, create_load_shape_graph, create_hourly_error_graph, create_led

# How to add callback from range slider - scroll down a few comments
# https://stackoverflow.com/questions/46519518/how-to-range-slider-and-selector-with-plotly-dash

# get data for visual
app_data = pd.read_csv('https://raw.githubusercontent.com/johnmrudolph/dash_covid_load_tracker/master/database_upload_2021_04_07.csv')

# key dates
key_dates = {
    '2020-01-21': [0.005, 20, -65, 'First US COVID Case'],
    '2020-03-23': [-0.005, -30, 60, 'Washington Stay at Home Order']
}

# set date params
start_date = '2020-01-01'
end_date = '2020-05-01'

# intialize led values
led_dict = {}
for i in ['LOAD', 'PREDICTED_LOAD', 'ERROR']:
    if i in ('ERROR'):
        led_dict[i] = (app_data.set_index('DATE').loc[start_date:end_date][i].mean() * 100).round(2)
    else:
        led_dict[i] = app_data.set_index('DATE').loc[start_date:end_date][i].mean().round(0)

# define dashboard elements

# navbar
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

# TODO add dropdown menu for github and modal
navbar_button = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Button('About', id='open', color='primary', outline=True, className='ml-2'),
                dbc.Modal(
                    [
                        dbc.ModalHeader('Seattle COVID Load Tracker', className='modal_title_branded'),
                        dbc.ModalBody(
                            html.Div(
                                [
                                    "This is a ",
                                    html.A("Dash ",href='https://plot.ly', target='_blank', rel='noopener noreferrer'),
                                    "visualization to show the impact that COVID-19 has "
                                    "had on Seattle's electricity load. The impacts of COVID are estimated "
                                    "by fitting a pre-COVID model and using it "
                                    "to make out-of-sample, post-COVID predictions. Any large differences between "
                                    "the predictions and what actually happened will primarily be driven by the "
                                    "impacts of the COVID-19 stay-at-home measures. Github source code is linked below"
                                ]
                            )
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(html.A(html.I(className='fas fa-user-circle fa-2x'), 
                                        href='http://www.johnmrudolph.com', target='_blank', rel='noopener noreferrer')),
                                        dbc.Col(html.A(html.I(className='fab fa-github fa-2x'), 
                                        href='https://github.com/johnmrudolph/dash_covid_load_tracker/', target='_blank', rel='noopener noreferrer')),
                                        dbc.Col(dbc.Button('Close', id='close', color='primary', outline=True, className='ml-2'))
                                    ], 
                                    align='center'
                                )
                            ]
                        )
                    ],
                    id='about_modal',
                    centered=True
                )
            ]
        )
    ],
    no_gutters=True,
    className='ml-auto flex-nowrap mt-3 mt-md-0',
    align='center'
)

navbar = dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col(html.A(html.Img(src=PLOTLY_LOGO, height="30px"), 
                href='https://plot.ly', target='_blank', rel='noopener noreferrer')),
                dbc.Col(dbc.NavbarBrand(html.Div([
                    'Seattle ',
                    html.Span('|', style={'color': 'rgba(255, 215, 0, 1)'}), 
                    ' COVID Load Tracker'
                    ]), className='navbar_brand'))
            ], 
            align='center',
            no_gutters=True,
        ),
        dbc.NavbarToggler(id='navbar-toggler'),
        dbc.Collapse(navbar_button, id='navbar-collapse', navbar=True)
    ],
    className='navbar_styled'
)

# body
body = html.Div(
    [
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                            [dcc.Graph(
                                id='actual-load', 
                                figure=create_error_graph(start_date, end_date, app_data, key_dates)
                            )], 
                            className='pretty_container'
                            )
                        ], 
                        md=9                    
                    ),
                    dbc.Col(
                        [
                        html.Div(
                        [
                            html.Div(
                            [
                                daq.LEDDisplay(
                                    id='load-led',
                                    label='Actual Load (aMW)',
                                    value = led_dict['LOAD'],
                                    color = '#ffffff',
                                    backgroundColor = 'rgba(123, 199, 255, 0.7)',
                                ),
                                daq.LEDDisplay(
                                    id='pred-led',
                                    label='Predicted Load (aMW)',
                                    value = led_dict['PREDICTED_LOAD'],
                                    color = '#ffffff',
                                    backgroundColor = 'rgba(123, 199, 255, 0.7)'
                                ),
                                daq.LEDDisplay(
                                    id='error-led',
                                    label='Prediction Error (%)',
                                    value = led_dict['ERROR'],
                                    color = '#ffffff',
                                    backgroundColor = 'rgba(123, 199, 255, 0.7)'
                                )
                            ], className= 'pretty_container_stats_inside')
                        ], className = 'pretty_container_stats')
                        ],
                        md=2,
                        style = {
                            'display': 'grid',
                        }
                    )
                ],
            ), fluid=True
        ),
        # placeholder for load shape charts
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [dcc.Graph(
                                    id='load-shape', 
                                )], 
                                className='pretty_container'
                            )
                        ], md=6
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [dcc.Graph(
                                    id='hour-error', 
                                )], 
                                className='pretty_container'
                            )
                        ],md=6,
                    )
                ],
            ), fluid=True
        ),
    ], className='dashboard_body'
)

font_awesome = {
    'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
    'crossorigin': 'anonymous'
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, font_awesome])

server = app.server

app.layout = html.Div([navbar, body])

# callbacks

# for modal toggling
# for navbar toggling
@app.callback(
    Output('about_modal', 'is_open'),
    [Input('open', 'n_clicks'), Input('close', 'n_clicks')],
    [State('about_modal', 'is_open')]
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# for navbar toggling
@app.callback(
    Output('navbar-collapse', 'is_open'),
    [Input('navbar-toggler', 'n_clicks')],
    [State('navbar-collapse', 'is_open')]
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output('load-led', 'value'),
    [Input('actual-load', 'relayoutData')])
def update_led_load(relayoutData):
    # get datetime index
    value = create_led('LOAD', led_dict, app_data, relayoutData)
    return value

@app.callback(
    Output('pred-led', 'value'),
    [Input('actual-load', 'relayoutData')])
def update_led_load(relayoutData):
    # get datetime index
    value = create_led('PREDICTED_LOAD', led_dict, app_data, relayoutData)
    return value

@app.callback(
    Output('error-led', 'value'),
    [Input('actual-load', 'relayoutData')])
def update_led_load(relayoutData):
    # get datetime index
    value = create_led('ERROR', led_dict, app_data, relayoutData)
    return value

@app.callback(
    Output('load-shape', 'figure'),
    [Input('actual-load', 'relayoutData')])
def update_load_shape(relayoutData):
    figure = create_load_shape_graph(start_date, end_date, app_data, relayoutData)
    return figure

@app.callback(
    Output('hour-error', 'figure'),
    [Input('actual-load', 'relayoutData')])
def update_load_shape_error(relayoutData):
    figure = create_hourly_error_graph(start_date, end_date, app_data, relayoutData)
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)