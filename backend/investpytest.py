import requests
import json
import investpy

code = '7203' #トヨタ自動車
stock_data = investpy.get_stock_historical_data(stock=code, country='japan', from_date='01/02/2021', to_date='28/03/2021')
stock_data.tail(5)