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
from jupyter_dash import JupyterDash

from funcs import get_dataframe, columns_rus
from drawer import *

SMALL_CARD_HEIGHT = '18rem'
MEDIUM_CARD_HEIGHT = '34rem'
TITLE_TEXT_SIZE = 24
TEXT_SIZE = 14
TEXT_COLOR = '#808080'
MARGIN_BOTTOM = "8px"

app = JupyterDash('app', external_stylesheets=[dbc.themes.BOOTSTRAP])
# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# load config file
with open('config.json', 'r') as f:
    config_file = json.load(f)

df = get_dataframe()
df.orderdate = pd.to_datetime(df.orderdate)
df = df.sort_values('orderdate')

#######################################
########## Data constants #############
#######################################

shipcountries_list = df.shipcountry.unique()
region_list = df.region.unique()
categories_list = df.categoryname.unique()

#######################################
######## Interactive forms ############
#######################################

date_form = dbc.Form([
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

category_form = dbc.Form([
    html.Div([
        dcc.Dropdown(
            id="category_dropdown",
            placeholder='Категория товара',
            value=None,
            options=[{'label': category, 'value': category} for category in categories_list],
            multi=True
        )
    ])
])

region_form = dbc.Form([
    html.Div([
        dcc.Dropdown(
            id="region_dropdown",
            placeholder='Регион продаж',
            value=None,
            options=[{'label': category, 'value': category} for category in region_list],
            multi=True
        )
    ])
])
    
shipcountry_form = dbc.Form([
    html.Div([
        dcc.Dropdown(
            id="shipcountry_dropdown",
            placeholder='Страна поставки',
            value=None,
            options=[{'label': category, 'value': category} for category in shipcountries_list],
            multi=True
        )
    ])
])

#######################################
############## Elements ###############
#######################################

# Forms for interactive card
interactive_cards = dbc.CardGroup(
    [
        dbc.Card([
            dbc.CardHeader("Период"),
            dbc.CardBody(
                [
                    date_form
                ]
            )
        ]),
        dbc.Card([
            dbc.CardHeader("Выбор категории товара"),
            dbc.CardBody(
                [
                    category_form
                ]
            )
        ]),
        dbc.Card([
            dbc.CardHeader("Выбор региона продаж"),
            dbc.CardBody(
                [
                    region_form
                ]
            )
        ]),
        dbc.Card([
            dbc.CardHeader("Выбор страны поставки"),
            dbc.CardBody(
                [
                   shipcountry_form
                ]
            )
        ]),
    ]
)

# Interactive card
interactive_froms = dbc.Card([
    dbc.CardBody([
        html.Label(
            "Выбор параметров",
            style={ 
                    "test-align": "left",
                    "font-size": TITLE_TEXT_SIZE,
                    "margin-bottom": MARGIN_BOTTOM,
                }
        ),
        interactive_cards
    ])
])

# Description card
description_card = dbc.Card([
    dbc.CardBody([
        html.Label(
                config_file['themeSettings'][0]['title'],
                style={ 
                    "test-align": "left",
                    "font-size": TITLE_TEXT_SIZE, 
                    "margin-bottom": MARGIN_BOTTOM
                }
            ),
        html.Br(),
        html.Label(
            config_file['themeSettings'][0]['description'],
            style={
                "text-align": "left",
                "font-size": TEXT_SIZE,
                "color": TEXT_COLOR
            }
        ),
    ],)
], className="w-100 h-100")

#graph 1
revenue_plot = dbc.Card([
    dbc.CardBody([
        html.Label(
                "Динамика суммарных продаж с шагом одна неделя",
                style={ 
                    "test-align": "left",
                    "font-size": TITLE_TEXT_SIZE, 
                    "margin-bottom": MARGIN_BOTTOM,
                }
            ),
        html.Br(),
        dcc.Graph(
            id='revenue_plot_id',
            style={}
        )
        
    ])
])

# graph 2
top_categories = dbc.Card([
    dbc.CardBody([
        html.Label(
                "Топ 3 категории с тремя самыми продаваемыми товарами в категории",
                style={ 
                    "test-align": "left",
                    "font-size": TITLE_TEXT_SIZE, 
                    "margin-bottom": MARGIN_BOTTOM,
                }
            ),
        html.Br(),
        dcc.Graph(
            id='top_categories_id',
            style={}
        )
    ])
])

# graph 4
mean_bill_per_region = dbc.Card([
    dbc.CardBody([
        html.Label(
                "Средний чек по региону продаж (Западная Европа, США, и т.д.) за каждую неделю на всем периоде продаж",
                style={ 
                    "test-align": "left",
                    "font-size": TITLE_TEXT_SIZE, 
                    "margin-bottom": MARGIN_BOTTOM,
                }
            ),
        html.Br(),
        dcc.Graph(
            id='mean_bill_per_region_id',
            style={}
        )
    ])
])

# graph table 3.1
top_shipcountries = dbc.Card([
    dbc.CardBody([
        html.Label("Топ стран поставки по сумме заказов за выбранный период",
                   style={'font-size': TITLE_TEXT_SIZE,
                          'text-align': 'left',
                          "margin-bottom": MARGIN_BOTTOM,
                          },
                   ),
        html.Br(),
        html.Label("Страны отсортированы по прибыли. Можно изменять сортировку с помощью заголовков столбцов.",
                   style={'font-size': TEXT_SIZE,
                          'text-align': 'left',
                          'color': TEXT_COLOR,
                          "margin-bottom": MARGIN_BOTTOM,
                          },
                   ),
        html.Br(),
        dash_table.DataTable(
            id='top-shipcountries-revenue',
            sort_action='native',
            sort_by=[{'column_id': "revenue", 'direction': 'desc'}],
            columns=[{'name': columns_rus[i], 'id': i, 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed,
                                                                                       symbol=Symbol.yes,
                                                                                       symbol_prefix=u'$')}
                     for i in ["shipcountry", "revenue"]],
            style_cell={
                'width': '100px',
                'minWidth': '100px',
                'maxWidth': '100px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'text-align': 'left',
                'font-family': 'sans-serif',
                'font-size': '14px',
            },
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold',
                'text-align': 'left',
                'font-family': 'sans-serif',
                'font-size': '14px',
            },
            page_action='none',
            style_table={'height': '24rem', 'overflowY': 'auto'},
        )

    ],
        style={
            'height': MEDIUM_CARD_HEIGHT,
        }
    )
])

# graph table 3.2
top_clients = dbc.Card([
    dbc.CardBody([
        html.Label("Топ клиентов по сумме заказов за выбранный период",
                   style={'font-size': TITLE_TEXT_SIZE,
                          'text-align': 'left',
                          "margin-bottom": MARGIN_BOTTOM,
                          },
                   ),
        html.Br(),
        html.Label("Клиенты отсортированы по прибыли. Можно изменять сортировку с помощью заголовков столбцов.",
                   style={'font-size': TEXT_SIZE,
                          'text-align': 'left',
                          'color': TEXT_COLOR,
                          "margin-bottom": MARGIN_BOTTOM,
                          },
                   ),
        html.Br(),
        dash_table.DataTable(
            id='top-clients-revenue',
            sort_action='native',
            sort_by=[{'column_id': "revenue", 'direction': 'desc'}],
            columns=[{'name': columns_rus[i], 'id': i, 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed,
                                                                                       symbol=Symbol.yes,
                                                                                       symbol_prefix=u'$')}
                     for i in ["customerid", "revenue"]],
            style_cell={
                'width': '100px',
                'minWidth': '100px',
                'maxWidth': '100px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'text-align': 'left',
                'font-family': 'sans-serif',
                'font-size': '14px',
            },
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold',
                'text-align': 'left',
                'font-family': 'sans-serif',
                'font-size': '14px',
            },
            page_action='none',
            style_table={'height': '24rem', 'overflowY': 'auto'},
        )

    ],
        style={
            'height': MEDIUM_CARD_HEIGHT,
        }
    )
])

# graph 3 tables
top_tables = dbc.CardGroup([
    top_shipcountries,
    top_clients
])



#######################################
############### Layout ################
#######################################

app.layout = html.Div(children=[
    # description
    dbc.Row([
        dbc.Col(description_card, 
                style={'margin-top': '8px'}),
    ], style={
        'margin-top': '8px',
        'margin-bottom': '0px',
        }
    ),
    
    # interactive forms
    dbc.Row([
        dbc.Col([
            interactive_froms
        ])
    ], style={
        'margin-top': '8px',
        'margin-bottom': '0px',
        }
    ),
    
    # graph 1
    dbc.Row([
        dbc.Col([
            revenue_plot
        ])
    ], style={
        'margin-top': '8px',
        'margin-bottom': '0px',
        }
    ),
    
    # graph 4
    dbc.Row([
        dbc.Col([
            mean_bill_per_region
        ])
    ], style={
        'margin-top': '8px',
        'margin-bottom': '0px',
        }
    ),
    
    # graph 3.1 and 3.2
    dbc.Row([
        dbc.Col([
            top_tables
        ])
    ], style={
        'margin-top': '8px',
        'margin-bottom': '0px',
        }
    ),
    
    # graph 2
    dbc.Row([
        dbc.Col([
            top_categories
        ])
    ], style={
        'margin-top': '8px',
        'margin-bottom': '0px',
        }
    ),
],
    style={
        'margin-left': '16px',
        'margin-right': '16px',
    }
)


#######################################
############# Callbacks ###############
#######################################

@app.callback(
    Output('revenue_plot_id', 'figure'),
    [
        Input('date-form', "start_date"),
        Input('date-form', "end_date"),
        Input('category_dropdown', "value"),
        Input('region_dropdown', "value"),
        Input('shipcountry_dropdown', "value")
    ]
)
def update_revenue_plot(date_start, date_end, category_value, region_value, shipcountry_value):
    return get_revenue_plot(df, date_start, date_end, category_value, region_value, shipcountry_value)

@app.callback(
    Output('top_categories_id', 'figure'),
    [
        Input('date-form', "start_date"),
        Input('date-form', "end_date"),
        Input('region_dropdown', "value"),
        Input('shipcountry_dropdown', "value")
    ]
)
def update_sunburst_plot(date_start, date_end, region_value, shipcountry_value):
    return get_sunburst_plot(df, date_start, date_end, region_value, shipcountry_value)


@app.callback(
    Output('mean_bill_per_region_id', 'figure'),
    [
        Input('date-form', "start_date"),
        Input('date-form', "end_date"),
        Input('category_dropdown', "value"),
        Input('shipcountry_dropdown', "value")
    ]
)
def update_horisontal_box_plot(date_start, date_end, category_value, shipcountry_value):
    return get_horisontal_box_plot(df, date_start, date_end, category_value, shipcountry_value)

@app.callback(
    Output('top-shipcountries-revenue', 'data'),
    Output('top-shipcountries-revenue', 'style_data_conditional'),
    [
        Input('date-form', "start_date"),
        Input('date-form', "end_date"),
        Input('category_dropdown', "value"),
        Input('region_dropdown', "value"),
        Input('top-shipcountries-revenue', 'sort_by')
    ]
)
def update_top_shipcountries_table(date_start, date_end, category_value, region_value, sort_by):
    return get_top_shipcountries_table(df, date_start, date_end, category_value, region_value, sort_by)

@app.callback(
    Output('top-clients-revenue', 'data'),
    Output('top-clients-revenue', 'style_data_conditional'),
    [
        Input('date-form', "start_date"),
        Input('date-form', "end_date"),
        Input('category_dropdown', "value"),
        Input('region_dropdown', "value"),
        Input('shipcountry_dropdown', "value"),
        Input('top-clients-revenue', 'sort_by')
    ]
)
def update_top_clients_table(date_start, date_end, category_value, region_value, shipcountry_value, sort_by):
    return get_top_clients_table(df, date_start, date_end, category_value, region_value, shipcountry_value, sort_by)


#######################################
############## Run app ################
#######################################


if __name__ == "__main__":
    app.run_server(port=8050, debug=True)