"""Utils and CRUD functions"""

import sqlite3
import pandas as pd
from typing import Optional, List
from datetime import datetime
from sklearn.ensemble import IsolationForest

PATH = "northwind.db"

columns_rus = {
    'shipcountry': 'Страна поставки', 
    'customerid': 'Идентификатор клиента', 
    'orderid': 'Идентификатор заказа',
    'orderdate': 'Дата заказа',
    'productid': 'Идентификатор товара',
    'revenue': 'Прибыль', 
    'productname': 'Продукт',
    'region': 'Регион', 
    'categoryname': 'Категория', 
    'categoryid': 'Идентификатор категории'
}

def get_dataframe(path = PATH) -> pd.DataFrame:
    con=sqlite3.Connection(path)
    df=pd.read_sql('''with revenues as (SELECT
    shipcountry,
    customerid,
    orders.orderid,
    orderdate,
    productid,
    (unitprice*quantity*(1-discount)) as revenue
    from orders,"order details"
    on orders.orderid="order details".orderid
    group by orderdate,shipcountry,customerid,orders.orderid, productid)
    SELECT 
    shipcountry,
    customerid,
    orderid,
    orderdate,
    revenues.productid,
    revenue,
    products.ProductName as productname,
    suppliers.Region as region,
    categories.CategoryName as categoryname,
    categories.CategoryID as categoryid
    FROM revenues
    INNER JOIN products on products.ProductID=revenues.ProductID
    INNER JOIN suppliers on suppliers.SupplierID=products.SupplierID
    INNER JOIN categories on categories.CategoryID=products.CategoryID;''',con=con)
    df.region.fillna("Unknown (None)", inplace=True)
    df["orderdate"] = pd.to_datetime(df["orderdate"])
    df = df.sort_values("orderdate")
    return df

def filter_dataframe_by_cat_column(df: pd.DataFrame, column_name: str, 
                                   allowed_value: List[str]) -> pd.DataFrame:
    """
    Returns filtered deep copy of dataframe
    :param df: dataframe to filter
    :param column_name: name of column to filter
    :param allowed_value: list of allowed values
    :return: filtered dataframe
    """
    return df.loc[df[column_name].isin(allowed_value)]

def filter_dataframe_by_ordinal_column(df: pd.DataFrame, 
                                       column_name: str, 
                                       allowed_upper_value = None,
                                       allowed_lower_value = None) -> pd.DataFrame:
    """
    Returns filtered deep copy of dataframe
    :param df: dataframe to filter
    :param column_name: name of column to filter
    :param allowed_upper_value: upper bound of allowed values
    :param allowed_lower_value: lower bound of allowed values
    :return: filtered dataframe
    """
    if allowed_upper_value is not None:
        return df.loc[df[column_name] <= allowed_upper_value]
    if allowed_lower_value is not None:
        return df.loc[df[column_name] >= allowed_lower_value]
    if allowed_lower_value is None and allowed_upper_value is None:
        raise TypeError("missing 1 requred positional argument 'allowed_upper_value' or 'allowed_lower_value'")
    
    # to prevent type error
    return df.copy()
    
def filter_dataframe(df: pd.DataFrame, 
                     start_date: Optional[str] = None, end_date: Optional[str] = None, category: Optional[List[str]] = None,
                     region: Optional[List[str]] = None, shipcountry: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Filters dataframe by given parameters
    :param df: dataframe to filter
    :param start_date: start date of period
    :param end_date: end date of period
    :param category: list of categories to filter
    :param region: list of regions to filter
    :param shipcountry: list of shipcountries to filter
    :return: filtered dataframe
    """
    if start_date is not None and end_date is not None:
        df = filter_dataframe_by_ordinal_column(df, "orderdate", 
                                                datetime.strptime(end_date, '%Y-%m-%d'), 
                                                datetime.strptime(start_date, '%Y-%m-%d'))
    if category is not None:
        if len(category) != 0:
            df = filter_dataframe_by_cat_column(df, "categoryname", category)
    if region is not None:
        if len(region) != 0:
            df = filter_dataframe_by_cat_column(df, "region", region)
    if shipcountry is not None:
        if len(shipcountry) != 0:
            df = filter_dataframe_by_cat_column(df, "shipcountry", shipcountry)
    return df
    
def anomaly_detection(df: pd.DataFrame, 
                      contamination: float = 0.07) -> pd.DataFrame:
    """
    Returns dataframe with anomaly column
    
    :param df: dataframe to detect anomalies
    :param contamination: contamination parameter for IsolationForest
    :return: dataframe with anomaly column
    """
    df = df.copy()
    df["anomaly"] = IsolationForest(contamination=contamination).fit_predict(df[["revenue"]])
    return df