from datetime import datetime
from funcs import *
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional, List

TEXT_STYLE = "Arial"
TEXT_SIZE = 12
TEXT_COLOR = "#005ce6"
BACKGROUND_COLOR = "#f4f4f4"

# plot 1
def get_revenue_plot(df: pd.DataFrame, date_start: Optional[str], date_end: Optional[str], category_value: Optional[List[str]], region_value: Optional[List[str]], shipcountry_value: Optional[List[str]]):
    filtered_df = filter_dataframe(df, date_start, date_end, category_value, region_value, shipcountry_value)
    if len(filtered_df) != 0:
        filtered_df  = filtered_df[['orderdate', 'revenue']].resample('W-MON', on='orderdate').sum().reset_index().sort_values('orderdate')
    
    # detect anomalies with IsolationForest
    filtered_df = anomaly_detection(filtered_df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_df['orderdate'], y=filtered_df['revenue'], mode='lines', name='Revenue'))
    fig.add_trace(go.Scatter(x=filtered_df.loc[filtered_df['anomaly'] == -1, 'orderdate'], y=filtered_df.loc[filtered_df['anomaly'] == -1, 'revenue'], mode='markers', name='Anomaly'))
    fig.update_layout(font=dict(family=TEXT_STYLE, size=TEXT_SIZE, color=TEXT_COLOR),
                      plot_bgcolor=BACKGROUND_COLOR,
                      paper_bgcolor=BACKGROUND_COLOR,
                      title = 'Revenue per week',
                      title_x = 0.5,)
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Revenue')
    return fig

# plot 2
def get_sunburst_plot(df: pd.DataFrame, date_start: Optional[str], date_end: Optional[str], region_value: Optional[List[str]], shipcountry_value: Optional[List[str]]):
    """
    Return sunburst plot for top 3 categories by sum of revenue of selected time period
    In each category show top 3 products and others as a separate product by sum of revenue of selected time period
    """
    filtered_df = filter_dataframe(df, date_start, date_end, None, region_value, shipcountry_value)
    if len(filtered_df) != 0:
        filtered_df = filtered_df.groupby(['categoryname', 'productname']).agg({'revenue': 'sum'}).reset_index()
        filtered_df = filtered_df.sort_values('revenue', ascending=False)
        top3_categories = filtered_df.groupby('categoryname').agg({'revenue': 'sum'}).reset_index().nlargest(3, 'revenue')['categoryname'].to_list()
        filtered_df = filtered_df.loc[filtered_df['categoryname'].isin(top3_categories)]
        filtered_df['rank'] = filtered_df.groupby('categoryname')['revenue'].rank(ascending=False)
        filtered_df.loc[filtered_df['rank'] > 3, 'productname'] = 'Other'
        filtered_df.sort_values(['categoryname', 'revenue'], inplace=True, ascending=False)
    fig = px.sunburst(filtered_df, path=['categoryname', 'productname'], values='revenue', 
                      title='Top 3 categories by sum of revenue of selected time period',
                      color='categoryname', color_discrete_sequence=px.colors.qualitative.Pastel,)
    fig.update_layout(margin=dict(t=10, l=0, r=0, b=50), title_y=0.05, title_x=0.5,
                      font=dict(family=TEXT_STYLE, size=TEXT_SIZE, color=TEXT_COLOR),
                      plot_bgcolor=BACKGROUND_COLOR, paper_bgcolor=BACKGROUND_COLOR)
    return fig

# plot 4
def get_horisontal_box_plot(df: pd.DataFrame, date_start: Optional[str], date_end: Optional[str], category_value: Optional[List[str]], shipcountry_value: Optional[List[str]]):
    """
    Count mean revenue per week for each region and show it as a horisontal box plot
    """
    filtered_df = filter_dataframe(df, date_start, date_end, category_value, None, shipcountry_value)
    if len(filtered_df) != 0:
        filtered_df = filtered_df[['orderdate', 'revenue', 'region']].groupby(['region', pd.Grouper(key='orderdate', freq='W-MON')]).mean().reset_index().sort_values('orderdate')
    fig =  px.box(filtered_df, x="revenue", y="region", orientation='h', 
                  color='region', title='Mean revenue per week for each region',
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(title_x=0.5, font=dict(family=TEXT_STYLE, size=TEXT_SIZE, color=TEXT_COLOR),
                      plot_bgcolor=BACKGROUND_COLOR, paper_bgcolor=BACKGROUND_COLOR)
    return fig

# plot 3 tables
def data_bars_diverging(df: pd.DataFrame, column: str, color_above='#0074D9', color_below='#FF4136'):
    neg_count = len(df[df[column] <= 0]) + 1
    pos_count = len(df[df[column] > 0])
    bounds_neg = np.linspace(0, 0.5, neg_count)
    bounds_pos = np.linspace(0.5, 1, pos_count)
    bounds = np.concatenate((bounds_neg, bounds_pos), axis=0)

    ranges = df[column].to_list()
    ranges.append(0)
    ranges = sorted(ranges)
    midpoint = 0

    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        min_bound_percentage = bounds[i - 1] * 100
        max_bound_percentage = bounds[i] * 100
        style = {
            'if': {
                'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'paddingBottom': 8,
            'paddingTop': 8,
        }
        if max_bound > midpoint:
            background = (
                """
                    linear-gradient(90deg,
                    white 0%,
                    white 50%,
                    {color_above} 50%,
                    {color_above} {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(
                    max_bound_percentage=max_bound_percentage,
                    color_above=color_above
                )
            )
        else:
            background = (
                """
                    linear-gradient(90deg,
                    white 0%,
                    white {min_bound_percentage}%,
                    {color_below} {min_bound_percentage}%,
                    {color_below} 50%,
                    white 50%,
                    white 100%)
                """.format(
                    min_bound_percentage=min_bound_percentage,
                    color_below=color_below
                )
            )
        style['background'] = background
        styles.append(style)
    return styles

# plot 3.1 table top ship countries
def get_top_shipcountries_table(df: pd.DataFrame, date_start: Optional[str], date_end: Optional[str], category_value: Optional[List[str]], region_value: Optional[List[str]], sort_by):
    filtered_df = filter_dataframe(df, date_start, date_end, category_value, region_value, None)
    if len(filtered_df) != 0:
        filtered_df = filtered_df.groupby('shipcountry').agg({'revenue': 'sum'}).reset_index().sort_values('revenue', ascending=False)
        if len(sort_by) != 0:
            filtered_df = filtered_df.sort_values(sort_by[0]['column_id'], 
                                                  ascending=sort_by[0]['direction'] == 'asc',
                                                  inplace=False)
    return filtered_df.to_dict('records'), data_bars_diverging(filtered_df, 'revenue')


# plot 3.2 table top clients
def get_top_clients_table(df: pd.DataFrame, date_start: Optional[str], date_end: Optional[str], category_value: Optional[List[str]], region_value: Optional[List[str]], shipcountry_value: Optional[List[str]], sort_by):
    filtered_df = filter_dataframe(df, date_start, date_end, category_value, region_value, shipcountry_value)
    if len(filtered_df) != 0:
        filtered_df = filtered_df.groupby('customerid').agg({'revenue': 'sum'}).reset_index().sort_values('revenue', ascending=False)
        if len(sort_by) != 0:
            filtered_df = filtered_df.sort_values(sort_by[0]['column_id'], 
                                                  ascending=sort_by[0]['direction'] == 'asc',
                                                  inplace=False)
    return filtered_df.to_dict('records'), data_bars_diverging(filtered_df, 'revenue')