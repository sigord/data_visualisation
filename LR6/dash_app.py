import dash
from dash import html
from dash import dcc
from dash import dash_table
from dash.dash_table.Format import Format, Scheme, Symbol
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import json
from datetime import date

from funcs import get_dataframe
from drawer import *

SMALL_CARD_HEIGHT = '18rem'
MEDIUM_CARD_HEIGHT = '34rem'

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

df = get_dataframe()
df.orderdate = pd.to_datetime(df.orderdate)
df = df.sort_values('orderdate')

#######################################
########## Data constants #############
#######################################


#######################################
######## Interactive forms ############
#######################################

date_form = dbc.FormGroup([
    dbc.Label("Период", html_for="date-form"),
    dcc.DatePickerRange(
        id="date-form",
        start_date=date(2016, 1, 1),
        end_date=date(2019, 1, 1),
        display_format='D MMM YYYY',
        # style={
        #     'color': "#e5e5e5 !important",
        # },
    )
])

#######################################
############## Elements ###############
#######################################



#######################################
############### Layout ################
#######################################

#######################################
############# Callbacks ###############
#######################################

if __name__ == "__main__":
    app.run_server(port=8050, debug=True)