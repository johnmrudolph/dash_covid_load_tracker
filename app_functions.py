import pandas as pd
from datetime import datetime

def get_loc_index(date, app_data):
    return app_data[app_data['DATE'] == date].iloc[0].name

def get_slider_marks(key_dates, app_data):
    """Return monthly value of marks"""
    # reformat app data for date filtering
    app_data['DATE'] = pd.to_datetime(app_data['DATE'])
    app_data['DATETIME'] = pd.to_datetime(app_data['DATE'])
    # identify key COVID dates
    # create slider dictionary
    slider_dict = {}
    for n, key in enumerate(key_dates.keys()):
        loc_idx = int(get_loc_index(key, app_data))
        slider_dict[loc_idx] = {}
    return slider_dict

def make_annotations(x, y, shift, ax, ay, text):
    annot_dict = dict(
        xref='x',
        yref='y',
        x=x,
        y=y + shift,
        font=dict(color='rgb(127, 127, 127)'),
        xanchor='middle',
        yanchor='low',
        text='{}'.format(text),
        show_arrow=True,
        arrowhead=4,
        arrowcolor='rgb(255, 215, 0, 1)',
        ax=ax,
        ay=ay,
    )
    return annot_dict

def create_error_graph(start, end, app_data, key_dates):
    # get datetime index
    smoothed_df = app_data.groupby(['DATE'])['ERROR'].mean()
    # fill data items
    data = []
    data.append(
        {
            'x': smoothed_df.index, 
            'y': smoothed_df.values, 
            'type':'scatter',
            'mode': 'lines', 
            'line': dict(shape='spline', smoothing=24, color='rgb(123, 199, 255)'), 
            'fill': 'tozeroy', 
            'fillcolor': 'rgba(123, 199, 255, 0.15)'
        }
    )
    
    # fill layout if annotation in filtered data range
    annotations = []
    for key in key_dates.keys():
        if key in smoothed_df.index:
            annotations.append(make_annotations(key, smoothed_df[key], key_dates[key][0],
            key_dates[key][1], key_dates[key][2], key_dates[key][3]))

    layout = {
            'height': 550,
            'title': 'COVID Daily Load Impact',
            'xaxis': {
                'range': [start, end],
                'rangeslider': {'visible': True,},
                'rangeselector': {'visible': True}
            },
            'yaxis': {
                'tickformat': ',.0%',
                'title': 'COVID Daily Load Reduction (%)'
            },
            'annotations': annotations
        }

    return {'data': data, 'layout': layout}

def create_load_shape_graph(start, end, app_data, relayout):
    # check if slider has been updated
    hourly_df = app_data.set_index(['DATE']).loc[start:end]
    hourly_df = hourly_df.groupby(['HOUR'])[['PREDICTED_LOAD', 'LOAD']].mean()

    if relayout:
        if 'xaxis.range' in relayout:
            # plotly will return utc to miliseconds for any date between start and end
            dates = []
            for i in relayout['xaxis.range']:
                # rangeselector can return 2 different date formats
                try:
                    dates.append(datetime.strptime(i, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'))
                except:
                    dates.append(datetime.strptime(i, '%Y-%m-%d').strftime('%Y-%m-%d'))
            #  pull value from app data
            hourly_df = app_data.set_index('DATE').loc[dates[0]:dates[1]]
            hourly_df = hourly_df.groupby(['HOUR'])[['PREDICTED_LOAD', 'LOAD']].mean()
    
    # fill data items
    data = []
    data.append(
        {
            'x': hourly_df.index, 
            'y': hourly_df['PREDICTED_LOAD'].values, 
            'name': 'Predicted',
            'type':'scatter',
            'mode': 'lines+markers', 
            'line': dict(color='rgba(123, 199, 255, 1)'),
        }
    )

    data.append(
        {
            'x': hourly_df.index, 
            'y': hourly_df['LOAD'].values, 
            'name': 'Actual',
            'type':'scatter',
            'mode': 'lines+markers',
            'line': dict(color='rgba(255, 215, 0, 1)'), 
            'fillcolor': 'rgba(123, 199, 255, 0.05)',
            'fill': 'tonexty', 
        }
    )

    layout = {
        'height': 400,
        'title': 'Predicted vs Actual Hourly Load Shape',
        'xaxis': {
            'title': 'Hour of Day'
        },
        'yaxis': {
            'tickformat': ',.0',
            'title': 'Hourly Load (aMW)',
        }
    }

    return {'data': data, 'layout': layout}


def create_hourly_error_graph(start, end, app_data, relayout):

    hourly_df = app_data.set_index(['DATE']).loc[start:end]
    hourly_df = hourly_df.groupby(['HOUR'])['ERROR'].mean()

    if relayout:
        if 'xaxis.range' in relayout:
            # plotly will return utc to miliseconds for any date between start and end
            dates = []
            for i in relayout['xaxis.range']:
                # rangeselector can return 2 different date formats
                try:
                    dates.append(datetime.strptime(i, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'))
                except:
                    dates.append(datetime.strptime(i, '%Y-%m-%d').strftime('%Y-%m-%d'))
            #  pull value from app data
            hourly_df = app_data.set_index('DATE').loc[dates[0]:dates[1]]
            hourly_df = hourly_df.groupby(['HOUR'])['ERROR'].mean()

    # fill data items
    data = []
    data.append(
        {
            'x': hourly_df.index, 
            'y': hourly_df.values, 
            'type':'bar',
            'marker': {
                'color': 'rgba(123, 199, 255, 0.15)',
                'line': {
                    'color': 'rgba(123, 199, 255, 1)',
                    'width': 0.75,
                }
            },
        } 
    )

    layout = {
        'height': 400,
        'title': 'COVID Hourly Load Impact',
        'xaxis': {
            'title': 'Hour of Day'
        },
        'yaxis': {
            'tickformat': ',.0%',
            'title': 'COVID Hourly Load Reduction (%)',
        }
    }

    return {'data': data, 'layout': layout}

def create_led(var, led_dict, app_data, relayout):
    value = led_dict[var]
    # if daterange slider has been updated then extract date range
    if relayout:
        if 'xaxis.range' in relayout:
            # plotly will return utc to miliseconds for any date between start and end
            dates = [pd.to_datetime(i).strftime('%Y-%m-%d') for i in relayout['xaxis.range']]
            #  pull value from app data
            if var in ('ERROR'):
                value = (app_data.set_index('DATE').loc[dates[0]:dates[1]][var].mean() * 100).round(2)
            else:
                value = app_data.set_index('DATE').loc[dates[0]:dates[1]][var].mean().round(0)
    return value