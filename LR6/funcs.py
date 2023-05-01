"""Utils and CRUD functions"""

import sqlite3
import pandas as pd

PATH = "northwind.db"

def get_dataframe(path = PATH) -> pd.DataFrame:
    con=sqlite3.Connection(path)
    df=pd.read_sql('''with revenues as (SELECT
    shipregion,
    customerid,
    orders.orderid,
    orderdate,
    productid,
    (unitprice*quantity*(1-discount)) as revenue
    from orders,"order details"
    on orders.orderid="order details".orderid
    group by orderdate,shipregion,customerid,orders.orderid, productid)
    SELECT orderdate,shipregion, customerid,sum(revenue) as revenuedaily,
    count(orderid) as ordersdaily
    from revenues
    group by orderdate;''',con=con)
    return df