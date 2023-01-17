import streamlit as st
import pandas as pd
import requests

# get token


def get_token():
    url = "http://localhost:8000/login"
    payload = {
        "username": "jandre",
        "password": "9907"
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    return response.json()['token']


# get cars
def get_cars(token):
    url = "http://0.0.0.0:8000/cars"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.request("GET", url, headers=headers)

    cars = []
    for car in response.json():
        cars.append(car['registration'])

    return response.json(), cars


def get_logs(token, registration):
    url = f"http://0.0.0.0:8000/logs/{registration}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    response = requests.request("GET", url, headers=headers)
    return response.json()

token = get_token()

cars, registrations = get_cars(token)
df_cars = pd.DataFrame(cars)

#logs
col1, col2 = st.columns(2)

df_logs = pd.DataFrame(get_logs(token, registrations[0]))
df_logs['Price per Liter'] = df_logs['totalcost'] / df_logs['litersPurchase']
df_logs['Liters per KM'] = df_logs['distance'] /df_logs['litersPurchase'] 
df_logs =  df_logs[['date', 'odometer', 'distance', 'litersPurchase', 'totalcost', 'Price per Liter', 'Liters per KM']]
#change date to date
df_logsLine = df_logs[['date', 'Price per Liter']]
df_logsLine = df_logsLine.rename(columns={'date': 'index'}).set_index('index')
#metrice for average price per liter
col1.metric("Average Price per Liter", df_logs['Price per Liter'].mean().round(2))
col2.metric("Average KM per Liter", df_logs['Liters per KM'].mean().round(2))
st.header("Logs")
st.line_chart(df_logsLine)










