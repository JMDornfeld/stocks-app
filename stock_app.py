#I leveraged the code that we reviewed together in class. Worked with classmates (specifically Vince Hamalainen) via slack to collaborate and review

import csv
from dotenv import load_dotenv
import json
import os
import pdb
import requests
import datetime

def parse_response(response_text):
    # response_text can be either a raw JSON string or an already-converted dictionary
    if isinstance(response_text, str): # if not yet converted, then:
        response_text = json.loads(response_text) # convert string to dictionary

    results = []
    time_series_daily = response_text["Time Series (Daily)"] #> a nested dictionary
    for trading_date in time_series_daily: # FYI: can loop through a dictionary's top-level keys/attributes
        #pdb.set_trace()

        prices = time_series_daily[trading_date] #> {'1. open': '101.0924', '2. high': '101.9500', '3. low': '100.5400', '4. close': '101.6300', '5. volume': '22165128'}
        result = {
            "date": trading_date,
            "open": prices["1. open"],
            "high": prices["2. high"],
            "low": prices["3. low"],
            "close": prices["4. close"],
            "volume": prices["5. volume"]
        }
        results.append(result)
    return results

def write_prices_to_file(prices=[], filename="db/prices.csv"):
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for d in prices:
            row = {
                "timestamp": d["date"],
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"]
            }
            writer.writerow(row)

if __name__ == '__main__': # only execute if file invoked from the command-line, not when imported into other files, like tests

    load_dotenv()

    api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."

    # CAPTURE USER INPUTS (SYMBOL)

    symbol = input("Please input a stock symbol (e.g. AMZN):  ")

    try:
        float(symbol)
        quit("REQUEST ERROR, PLEASE TRY AGAIN. CHECK YOUR SYMBOL.")
    except ValueError as e:
        pass

    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"

    response = requests.get(request_url)

    if "Error Message" in response.text:
        print("REQUEST ERROR, PLEASE TRY AGAIN. CHECK YOUR SYMBOL.  ")
        quit("Stopping the program")

    # VALIDATE RESPONSE AND HANDLE ERRORS

    # PARSE RESPONSE (AS LONG AS THERE ARE NO ERRORS)

    daily_prices = parse_response(response.text)

    write_prices_to_file(prices=daily_prices, filename="db/prices.csv")

    print("Date & Time Program was Executed: ", datetime.datetime.now().strftime("%m-%d-%y %H:%M"))
    latest_date_refresh = daily_prices[0]["date"]
    print("Data was Refreshed on:  " + latest_date_refresh)
    latest_closing_price = daily_prices[0]["close"]
    latest_closing_price = float(latest_closing_price)
    latest_recent_average_high_price = 0
    j = 0
    for i in daily_prices:
        latest_recent_average_high_price += float(i["high"])
        j += 1
    latest_recent_average_high_price = latest_recent_average_high_price/j
    latest_recent_average_low_price = 0
    j = 0
    for i in daily_prices:
        latest_recent_average_low_price += float(i["low"])
        j += 1
    latest_recent_average_low_price = latest_recent_average_low_price/j

    range = latest_recent_average_high_price - latest_recent_average_low_price
    recommend_price = range * .5 + latest_recent_average_low_price
    if latest_closing_price < recommend_price:
        j = 1
    else:
        j = 2

    latest_closing_price = "${0:,.2f}".format(latest_closing_price)
    latest_recent_average_high_price = "${0:,.2f}".format(latest_recent_average_high_price)
    latest_recent_average_low_price = "${0:,.2f}".format(latest_recent_average_low_price)
    print("Latest Closing Price:    " + latest_closing_price)
    print("Recent Average Lowest Price:   " + latest_recent_average_low_price)
    print("Recent Average Highest Price:   " + latest_recent_average_high_price)

    if j == 1:
        print("This stock looks like it will continue to increase in price. Let's buy!")
    elif j == 2:
        print("This stock looks like it will stay stagnant or decrease in price. Let's not buy.")
