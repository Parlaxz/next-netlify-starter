import json

import requests
import pandas as pd
import ast
from pandas.io.json import json_normalize
import shopify

url = 'https://api.printify.com/v1/'
token = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6Ijc1YzJlOGE0NmQzOTBmNTkyNGU3NmQ4OGM3M2Q4YjBkOGQwZjY4ZWVhYjMzY2U1NDljZDEzMjJhYTVjMDljMzFjZWRhNWIwMzliMTVlNWRhIiwiaWF0IjoxNjQ2ODUzMzE5LCJuYmYiOjE2NDY4NTMzMTksImV4cCI6MTY3ODM4OTMxOSwic3ViIjoiNzkwMDM1MiIsInNjb3BlcyI6WyJzaG9wcy5tYW5hZ2UiLCJzaG9wcy5yZWFkIiwiY2F0YWxvZy5yZWFkIiwib3JkZXJzLnJlYWQiLCJvcmRlcnMud3JpdGUiLCJwcm9kdWN0cy5yZWFkIiwicHJvZHVjdHMud3JpdGUiLCJ3ZWJob29rcy5yZWFkIiwid2ViaG9va3Mud3JpdGUiLCJ1cGxvYWRzLnJlYWQiLCJ1cGxvYWRzLndyaXRlIiwicHJpbnRfcHJvdmlkZXJzLnJlYWQiXX0.Aq6t1exH1tAizCv-q_AuY_whXi0eEG8s4vX3npasuWa6fd0RSEuHlFIbiJt72XbfA9_8GaOKc3dQnJP-vBQ'
shopify_token = "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"

import datetime
from datetime import timezone
from datetime import datetime
from requests.auth import HTTPBasicAuth
from dateutil import parser
from datetime import timedelta


def loadPrintify():
    payload = {'page': '1'}
    r = requests.get(url + 'shops/2666622/orders.json', headers={'Authorization': token}, params=payload)
    total = r.json()['last_page']
    orders = pd.DataFrame([])
    for i in range(total):
        payload = {'page': i+1}
        print(i)
        r = requests.get(url + 'shops/2666622/orders.json', headers={'Authorization': token}, params=payload)
        orders = orders.append(pd.DataFrame(r.json()))

    orders['data'].to_excel("./data/appended_orders.xlsx")

def updateOrders():
    orders = pd.read_excel("./data/appended_orders.xlsx")
    jsonF = ast.literal_eval(orders['data'][0])
    id = jsonF['id']

    payload = {'page': '1'}
    r = requests.get(url + 'shops/2666622/orders.json', headers={'Authorization': token}, params=payload)
    total = r.json()['last_page']

    br = False
    appendList = pd.DataFrame([])
    for i in range(total):
        payload = {'page': i + 1}
        r = requests.get(url + 'shops/2666622/orders.json', headers={'Authorization': token}, params=payload)
        batch = pd.DataFrame(r.json())
        data = batch['data']
        for i in range(10):
            if data[i]['id'] == id:
                br = True
                break
            else:

                appendList = appendList.append(batch.iloc[i])
        if br:
            break


    combined = appendList.append(orders, ignore_index=True)
    combined['data'].to_excel("./data/appended_orders.xlsx")

def only_dict(d):
    '''
    Convert json string representation of dictionary to a python dict
    '''
    return ast.literal_eval(d)

def list_of_dicts(ld):
    '''
    Create a mapping of the tuples formed after
    converting json strings of list to a python list
    '''
    return dict([(list(d.values())[1], list(d.values())[0]) for d in ast.literal_eval(ld)])


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def calculateDailyCost(numDays):
    updateOrders()


    orders = pd.read_excel("./data/appended_orders.xlsx")

    base = datetime.today()
    date_list = [base - timedelta(days=x) for x in range(numDays)]
    dateStrings = {x.strftime("%d-%m-%Y"):0 for x in date_list}
    print(dateStrings)
    data = []
    #convert orders to local time
    for order in orders['data']:
        order = ast.literal_eval(order)
        order['date'] = parser.parse(order['created_at'])
        order['date'] = utc_to_local(order['date'])
        price = (order['total_price'] + order['total_shipping'] + order['total_tax'])/100.0
        dateStrings[order['date'].strftime("%d-%m-%Y")] = dateStrings[order['date'].strftime("%d-%m-%Y")] + price

    for date in dateStrings:
        data.append(
            {'date': date, 'price': dateStrings[date]})

    df = pd.DataFrame(data)
    df.to_csv("j.csv", index = False)
    df.to_json("./json/data.json", orient="records")


def loadShopify():
    shopify.Session.setup(api_key="e887a7c4b38d1405a2e673718317a766", secret="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")
    shop_url = "moshiproject.myshopify.com"
    api_version = '2020-10'
    session = shopify.Session(shop_url, api_version, shopify_token)
    shopify.ShopifyResource.activate_session(session)


    all_orders = []
    orders = shopify.Order.find(since_id=0, status='any', limit=250)
    all_orders = all_orders + orders

    page = 1
    while orders.has_next_page():
        print("Page number: "+str(page))
        page+=1
        orders = orders.next_page()
        all_orders = all_orders + orders

    df = pd.DataFrame(all_orders, columns = ['orderID'])
    df['json'] = df['orderID'].apply(lambda x : x.attributes)

    order_data = json_normalize(df['json'].tolist())
    order_data.to_csv("./data/shopify.csv", index = False)

    # save last update time
    now = datetime.now()
    date_time = order_data['created_at'].iloc[-1]
    date = parser.parse(date_time) + timedelta(minutes=1)
    date_time = date.strftime("%Y-%m-%dT%H:%M:%S%z")
    f = open("./data/last_check_date.txt", "w")
    f.write(date_time)
    f.close()


def updateShopify():
    #setup shopify API and access
    shopify.Session.setup(api_key="e887a7c4b38d1405a2e673718317a766", secret="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")
    shop_url = "moshiproject.myshopify.com"
    api_version = '2020-10'
    session = shopify.Session(shop_url, api_version, shopify_token)
    shopify.ShopifyResource.activate_session(session)

    #get last update time
    f = open("./data/last_check_date.txt", "r")
    update_date = f.read()
    f.close()

    #update orders
    all_orders = []
    orders = shopify.Order.find(since_id=0, status='any', limit=250, created_at_min= update_date)
    all_orders = all_orders + orders

    while orders.has_next_page():
        orders = orders.next_page()
        all_orders = all_orders + orders

    df = pd.DataFrame(all_orders, columns = ['orderID'])
    df['json'] = df['orderID'].apply(lambda x : x.attributes)
    order_data = json_normalize(df['json'].tolist())
    order_data.to_csv("./data/shopify.csv", mode = 'a', header = False, index = False)

    if len(order_data) > 0:
        # save last update time
        print(order_data)
        date_time = order_data['created_at'].iloc[-1]
        date = parser.parse(date_time) + timedelta(minutes=1)
        date_time = date.strftime("%Y-%m-%dT%H:%M:%S%z")
        f = open("./data/last_check_date.txt", "w")
        f.write(date_time)
        f.close()

def calcDailyRevenue(numDays):
    updateShopify()

    orders = pd.read_csv("./data/shopify.csv")

    base = datetime.today()
    date_list = [base - timedelta(days=x) for x in range(numDays)]
    dateStrings = {x.strftime("%d-%m-%Y"): 0 for x in date_list}
    data = []
    print(orders)
    # convert orders to local time
    for idx,order in orders.iterrows():

        order['date'] = parser.parse(order['created_at'])
        order['date'] = utc_to_local(order['date'])
        price = order['total_price'] *.971 -.3
        dateStrings[order['date'].strftime("%d-%m-%Y")] = dateStrings[order['date'].strftime("%d-%m-%Y")] + price

    for date in dateStrings:
        data.append(
            {'date': date, 'price': dateStrings[date]})

    df = pd.DataFrame(data)
    df.to_json("./json/shopifyDates.json", orient="records")

def calcDailyProfit(numDays):

    calcDailyRevenue(numDays)
    calculateDailyCost(numDays)
    revenue = pd.read_json("./json/shopifyDates.json")
    cost = pd.read_json("./json/data.json")

    profit = revenue['price'] - cost['price']
    print(profit)


    base = datetime.today()
    date_list = [base - timedelta(days=x) for x in range(numDays)]
    dateStrings = {x.strftime("%d-%m-%Y"): 0 for x in date_list}
    data = []
    i = 0
    for date in dateStrings:
        data.append(
            {'date': date, 'price': profit[i]})
        i+=1
    print(data)
    df = pd.DataFrame(data)
    df.to_json("./json/ProfitDates.json", orient="records")


if __name__ == '__main__':
    numDays = 400
    calcDailyProfit(numDays)

