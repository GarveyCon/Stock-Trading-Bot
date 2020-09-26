"""
Daily Data Download
Connor Garvey
9/7/2020

Download daily data for each stock in the S&P 500 and add it to the Master Data .csv file.
Calculates SMAs and generates Buy/Sell signals.
"""

import pandas as pd
import numpy as np
from pandas_datareader import data
from datetime import date
import time
import requests
import json
import logging
from config import *            # This file contains the Alpaca API keys


# Data downloading function
def getTodaysData(symbols, masterData, buySellSignals, todays_date):
    # Download todays data for each stock and add to Master Data .csv
    failed_reads = []
    buy_symbols = []
    sell_symbols = []

    for i in range(0, len(symbols)):
        currentSym = symbols.iloc[i]['Symbol']
        logging.info('Getting data for ' + currentSym)
        print('Getting data for ' + currentSym)

        # Attempt 5 times before adding symbol to array to try later.
        attempts = 1
        while attempts < 5:
            try:
                symbol_data = data.DataReader(currentSym, 'yahoo', todays_date, todays_date)
                break
            except:
                attempts += 1
                print('Attempt number ' + str(attempts))
                time.sleep(0.5)

        if attempts == 5:
            print("No data returned. Attempting again later.")
            logging.warning('No data returned. ' + currentSym + ' added to list of failed symbols')
            failed_reads.append(currentSym)
            symbol_data = []
        else:
            logging.info(currentSym + ' data successfully downloaded')
            tempDF = symbol_data.iloc[0]['Close']

            # Get yestedays SMAs to check for crossovers
            yesterdaySMA20 = masterData[currentSym + ' SMA20'].iloc[-1]
            yesterdaySMA100 = masterData[currentSym + ' SMA100'].iloc[-1]

            # Add new value to Master Data and calculate SMAs
            masterData.at[todays_date, currentSym] = tempDF
            masterData.at[todays_date, currentSym + ' SMA20'] = masterData[currentSym].tail(20).mean()
            masterData.at[todays_date, currentSym + ' SMA100'] = masterData[currentSym].tail(100).mean()

            # Add Buy/Sell Signals
            if (masterData.at[todays_date, currentSym + ' SMA20'] < masterData.at[
                todays_date, currentSym + ' SMA100'] and
                    yesterdaySMA20 > yesterdaySMA100):
                masterData.at[todays_date, currentSym + ' Signal'] = "SELL"
                buySellSignals.at[todays_date, currentSym + ' Signal'] = "SELL"
                sell_symbols.append(currentSym)
                logging.info(currentSym + ' added to Sell list')
                print('SELL')
            elif (masterData.at[todays_date, currentSym + ' SMA20'] > masterData.at[
                todays_date, currentSym + ' SMA100'] and
                  yesterdaySMA20 < yesterdaySMA100):
                masterData.at[todays_date, currentSym + ' Signal'] = "BUY"
                buySellSignals.at[todays_date, currentSym + ' Signal'] = "BUY"
                buy_symbols.append(currentSym)
                logging.info(currentSym + ' added to Buy list')
                print('BUY')
            else:
                masterData.at[todays_date, currentSym + ' Signal'] = np.nan
                buySellSignals.at[todays_date, currentSym + ' Signal'] = np.nan
                print('No changes here')
            print("Complete")
            time.sleep(1)
            symbol_data = []

    failed_reads_df = pd.DataFrame(failed_reads, columns=['Symbol'])

    return masterData, buySellSignals, failed_reads_df, buy_symbols, sell_symbols


def openPosition(symbol):
    data = {
        "symbol": symbol,
        "qty": 1,
        "side": 'buy',
        "type": 'market',
        "time_in_force": 'gtc'
    }
    r = requests.post(orders_URL, json=data, headers=headers)
    return json.loads(r.content)


def getPositions():
    r = requests.get(positions_URL, headers=headers)
    print(r.content)
    return json.loads(r.content)


def closePosition(symbol):
    r = requests.delete(positions_URL + '/' + symbol, headers=headers)
    print(r.content)
    return json.loads(r.content)


def alpacaBuySell(buys, sells):
    open_positions = getPositions()
    for symbol in sells:
        for row in open_positions:
            if symbol == row.get('symbol'):
                closePosition(symbol)
                print(symbol + ' position has been closed.')

    for symbol in buys:
        openPosition(symbol)


#######################################################################################################################

# Get todays date
todays_date = str(date.today())
day = date.today().weekday()
# print(todays_date)

# Initialize logging
logging.basicConfig(filename= 'C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\Logs\\StockBot_Log_'
                               + todays_date + '.log',
                    filemode= 'w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logging.info(todays_date + ' Starting script')

# Open .csv files containing Stock Symbols, Stock Data, and Buy/Sell Signals as dataFrames
stockSymbols = pd.read_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\constituents.csv")
masterData = pd.read_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\MasterData.csv",
                         index_col="Date")
buySellSignals = pd.read_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\BuySellSignals.csv",
                             index_col="Date")
logging.info('MasterData, buySellSignals, stockSymbols .csv files imported')

# Declare URLs for Alpaca API endpoints
base_URL = 'https://paper-api.alpaca.markets'
account_URL = '{}/v2/account'.format(base_URL)
orders_URL = '{}/v2/orders'.format(base_URL)
positions_URL = '{}/v2/positions'.format(base_URL)
headers = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}

# Only runs if it is a weekday - this should be handled by the scheduler anyways
if day in range(5, 7):
    print('Not a weekday')
    logging.warning('Today is not a weekday. Exiting script')
    exit()

# Run data download
logging.info('Beginning data download')
masterData, buySellSignals, failed_symbols, buys, sells = getTodaysData(stockSymbols, masterData, buySellSignals,
                                                                        todays_date)
# Buy/Sell through Alpaca
logging.info('Beginning Buy/Sell process through Alpaca API')
alpacaBuySell(buys, sells)

# Retry failed symbols once, and then save off any symbols that still fail.
if len(failed_symbols) != 0:
    print('Attempting Failed Reads:')
    logging.info('Attempting to redownload data for failed symbols')
    print(failed_symbols)
    time.sleep(60)
    masterData, buySellSignals, failed_symbols, buys, sells = getTodaysData(failed_symbols, masterData, buySellSignals,
                                                                            todays_date)
    if len(failed_symbols) != 0:
        print('Symbols still failing will be saved off into failedReads.csv')
        logging.warning('The following symbols are still failing, and will be saved off to failedReads.csv')
        logging.warning(failed_symbols)
        failed_symbols.to_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\failedReads.csv")

# Buy/Sell again
logging.info('Beginning Buy/Sell process through Alpaca API for failed symbols')
alpacaBuySell(buys, sells)

# Save off data and signals
logging.info('Saving Master Data and Buy/Sell Signals to .csv')
masterData.to_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\MasterData.csv")
buySellSignals.to_csv("C:\\Users\\Connor Garvey\\Documents\\Data Stuff\\StockProject\\BuySellSignals.csv")

