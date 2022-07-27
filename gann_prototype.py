import pandas as pd
import pandas_ta as ta
import btalib
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import mplfinance as fplt
import matplotlib.dates as mpdates
import pathlib
import numpy as np
import math
import datetime
from datetime import timedelta
import json
import requests
import calendar
import time

def GetCandlesticks(pair, granularity):

    # Current GMT time in a tuple format
    current_GMT = time.gmtime()

    # ts stores timestamp
    end = calendar.timegm(current_GMT)
    tme = (4*60)*60
    start = int(end) - tme
    pair = pair
    granularity = int(granularity)

    url = "https://api.exchange.coinbase.com/products/"+pair+"/candles?granularity="+str(granularity)+"&start="+str(start)+"&end="+str(end)
    #url = "https://api.exchange.coinbase.com/products/"+pair+"/candles?granularity="+str(granularity)


    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers)
    lst = json.loads(response.text)
    df = pd.DataFrame(lst, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['time'], unit='s')

    df = df.set_index('date')
    df = df.reindex(index=df.index[::-1])

    return df

def GannLines(candles, pair, granularity):
    df_candlesticks = candles
    pair = pair
    granularity = int("5")

    #Acquire high and low 24 hours in past
    twenty_four_hour_low = float(df_candlesticks['low'].min())
    twenty_four_hour_high = float(df_candlesticks['high'].max())

    #Square roots of high/low
    sqrt_twenty_four_hour_low = math.sqrt(twenty_four_hour_low)
    sqrt_twenty_four_hour_high = math.sqrt(twenty_four_hour_high)

    #Gann lists for degree angles per candle trigger...will add to dataframe after population
    gann_45_ascending = []
    gann_45_descending = []
    gann_26_ascending_21 = []
    gann_26_ascending_12 = []
    gann_26_descending_21 = []
    gann_26_descending_12 = []

    gann_45_ascending_predictive = []
    gann_45_descending_predictive = []
    gann_45_predictive_time = []
    gann_26_ascending_12_predictive = []
    gann_26_ascending_21_predictive = []
    gann_26_descending_12_predictive = []
    gann_26_descending_21_predictive = []

    #Degree calculation in decimals
    degree_45_positive = .0125
    degree_45_negative = -.0125
    degree_26_positive = .007292
    degree_26_negative = -.007292
    degree_63_positive =  .017708
    degree_63_negative = -.017708

    #Gann 45 descending
    df_candlesticks.reset_index(inplace=True)
    index_count = len(df_candlesticks.index)
    count = 0
    as_index = df_candlesticks[['high']].idxmax().item()
    as_count = 0
    pd_count = 1
    if count < index_count:
        while count < as_index:
            gann_45_descending.append(np.nan)
            count += 1
        if count == as_index:
            if count < index_count:
                gann_45_descending.append((sqrt_twenty_four_hour_high + (degree_45_negative*as_count))**2)
                count += 1
                as_count += 1
        while count < index_count:
            gann_45_descending.append((sqrt_twenty_four_hour_high + ((degree_45_negative*granularity)*as_count))**2)
            as_count += 1
            count += 1
    df_candlesticks['descending_45'] = gann_45_descending

    if granularity == 5:
        while pd_count != 80:
            if df_candlesticks['descending_45'].iloc[-1] != float(df_candlesticks['descending_45'].iloc[-1]):
                while pd_count != 80:
                    gann_45_descending_predictive.append((sqrt_twenty_four_hour_high + (degree_45_negative*pd_count))**2)
                    time = df_candlesticks['date'].iloc[-1] + datetime.timedelta(seconds=pd_count*300)
                    gann_45_predictive_time.append(time)
                    pd_count +=1

            else:
                gann_45_descending_predictive.append((math.sqrt(df_candlesticks['descending_45'].iloc[-1]) + ((degree_45_negative*granularity)*pd_count))**2)
                time = df_candlesticks['date'].iloc[-1] + datetime.timedelta(seconds=pd_count*300)
                gann_45_predictive_time.append(time)
                pd_count += 1

    elif granularity == 30:
        while pd_count != 9:
            if df_candlesticks['descending_45'].iloc[-1] != float(df_candlesticks['descending_45'].iloc[-1]):
                while pd_count != 9:
                    gann_45_descending_predictive.append((sqrt_twenty_four_hour_high + (degree_45_negative*pd_count))**2)
                    time = df_candlesticks['date'].iloc[-1] + datetime.timedelta(seconds=pd_count*1800)
                    gann_45_predictive_time.append(time)
                    pd_count +=1

            else:
                gann_45_descending_predictive.append((math.sqrt(df_candlesticks['descending_45'].iloc[-1]) + ((degree_45_negative*granularity)*pd_count))**2)
                time = df_candlesticks['date'].iloc[-1] + datetime.timedelta(seconds=pd_count*1800)
                gann_45_predictive_time.append(time)
                pd_count += 1

    elif granularity == 1440:
        while pd_count != 21:
            if df_candlesticks['descending_45'].iloc[-1] != float(df_candlesticks['descending_45'].iloc[-1]):
                while pd_count != 21:
                    gann_45_descending_predictive.append((sqrt_twenty_four_hour_high + (degree_45_negative*pd_count))**2)
                    time = df_candlesticks['date'].iloc[-1] + datetime.timedelta(days=pd_count)
                    gann_45_predictive_time.append(time)
                    pd_count +=1

            else:
                gann_45_descending_predictive.append((math.sqrt(df_candlesticks['descending_45'].iloc[-1]) + ((degree_45_negative*granularity)*pd_count))**2)
                time = df_candlesticks['date'].iloc[-1] + datetime.timedelta(days=pd_count)
                gann_45_predictive_time.append(time)
                pd_count += 1


    #Gann 45 descending 2:1
    count = 0
    as_index = df_candlesticks[['high']].idxmax().item()
    as_count = 0
    pd_count = 1
    if count < index_count:
        while count < as_index:
            gann_26_descending_21.append(np.nan)
            count += 1
        if count == as_index:
            if count < index_count:
                gann_26_descending_21.append((sqrt_twenty_four_hour_high + (degree_26_negative*as_count))**2)
                count += 1
                as_count += 1
        while count < index_count:
            gann_26_descending_21.append((sqrt_twenty_four_hour_high + ((degree_26_negative*granularity)*as_count))**2)
            as_count += 1
            count += 1
    df_candlesticks['descending_21'] = gann_26_descending_21

    if granularity == 5:
        while pd_count != 80:
            if df_candlesticks['descending_21'].iloc[-1] != float(df_candlesticks['descending_21'].iloc[-1]):
                while pd_count != 80:
                    gann_26_descending_21_predictive.append((sqrt_twenty_four_hour_high + (degree_26_negative*pd_count))**2)
                    pd_count +=1
            else:
                gann_26_descending_21_predictive.append((math.sqrt(df_candlesticks['descending_21'].iloc[-1]) + ((degree_26_negative*granularity)*pd_count))**2)
                pd_count += 1

    elif granularity == 30:
        while pd_count != 9:
            if df_candlesticks['descending_21'].iloc[-1] != float(df_candlesticks['descending_21'].iloc[-1]):
                while pd_count != 9:
                    gann_26_descending_21_predictive.append((sqrt_twenty_four_hour_high + (degree_26_negative*pd_count))**2)
                    pd_count +=1
            else:
                gann_26_descending_21_predictive.append((math.sqrt(df_candlesticks['descending_21'].iloc[-1]) + ((degree_26_negative*granularity)*pd_count))**2)
                pd_count += 1

    elif granularity == 1440:
        while pd_count != 21:
            if df_candlesticks['descending_21'].iloc[-1] != float(df_candlesticks['descending_21'].iloc[-1]):
                while pd_count != 21:
                    gann_26_descending_21_predictive.append((sqrt_twenty_four_hour_high + (degree_26_negative*pd_count))**2)
                    pd_count +=1
            else:
                gann_26_descending_21_predictive.append((math.sqrt(df_candlesticks['descending_21'].iloc[-1]) + ((degree_26_negative*granularity)*pd_count))**2)
                pd_count += 1

    #Gann 45 descending 1:2
    count = 0
    as_index = df_candlesticks[['high']].idxmax().item()
    as_count = 0
    pd_count = 1
    if count < index_count:
        while count < as_index:
            gann_26_descending_12.append(np.nan)
            count += 1
        if count == as_index:
            if count < index_count:
                gann_26_descending_12.append((sqrt_twenty_four_hour_high + (degree_63_negative*as_count))**2)
                count += 1
                as_count += 1
        while count < index_count:
            gann_26_descending_12.append((sqrt_twenty_four_hour_high + ((degree_63_negative*granularity)*as_count))**2)
            as_count += 1
            count += 1
    df_candlesticks['descending_12'] = gann_26_descending_12

    if granularity == 5:
        while pd_count != 80:
            if df_candlesticks['descending_12'].iloc[-1] != float(df_candlesticks['descending_12'].iloc[-1]):
                while pd_count != 80:
                    gann_26_descending_12_predictive.append((sqrt_twenty_four_hour_high + (degree_63_negative*pd_count))**2)
                    pd_count +=1
            else:
                gann_26_descending_12_predictive.append((math.sqrt(df_candlesticks['descending_12'].iloc[-1]) + (degree_63_negative*granularity)*pd_count)**2)
                pd_count += 1

    elif granularity == 30:
        while pd_count != 9:
            if df_candlesticks['descending_12'].iloc[-1] != float(df_candlesticks['descending_12'].iloc[-1]):
                while pd_count != 9:
                    gann_26_descending_12_predictive.append((sqrt_twenty_four_hour_high + (degree_63_negative*pd_count))**2)
                    pd_count +=1
            else:
                gann_26_descending_12_predictive.append((math.sqrt(df_candlesticks['descending_12'].iloc[-1]) + (degree_63_negative*granularity)*pd_count)**2)
                pd_count += 1

    elif granularity == 1440:
        while pd_count != 21:
            if df_candlesticks['descending_12'].iloc[-1] != float(df_candlesticks['descending_12'].iloc[-1]):
                while pd_count != 21:
                    gann_26_descending_12_predictive.append((sqrt_twenty_four_hour_high + (degree_63_negative*pd_count))**2)
                    pd_count +=1
            else:
                gann_26_descending_12_predictive.append((math.sqrt(df_candlesticks['descending_12'].iloc[-1]) + (degree_63_negative*granularity)*pd_count)**2)
                pd_count += 1

    #Gann 45 ascending
    count = 0
    as_index = df_candlesticks[['low']].idxmin().item()
    as_count = 0
    pd_count = 1
    if count < index_count:
        while count < as_index:
            gann_45_ascending.append(np.nan)
            count += 1
        if count == as_index:
            if count < index_count:
                gann_45_ascending.append((sqrt_twenty_four_hour_low + ((degree_45_positive)*as_count))**2)
                count += 1
                as_count += 1
        while count < index_count:
            gann_45_ascending.append((sqrt_twenty_four_hour_low + ((degree_45_positive*granularity)*as_count))**2)
            as_count += 1
            count += 1
    df_candlesticks['ascending_45'] = gann_45_ascending

    if granularity == 5:
        while pd_count != 80:
            if df_candlesticks['ascending_45'].iloc[-1] != float(df_candlesticks['ascending_45'].iloc[-1]):
                while pd_count != 80:
                    gann_45_ascending_predictive.append((sqrt_twenty_four_hour_low + (degree_45_positive*pd_count))**2)
                    pd_count +=1
            else:
                gann_45_ascending_predictive.append((math.sqrt(df_candlesticks['ascending_45'].iloc[-1]) + ((degree_45_positive*granularity)*pd_count))**2)
                pd_count += 1

    elif granularity == 30:
        while pd_count != 9:
            if df_candlesticks['ascending_45'].iloc[-1] != float(df_candlesticks['ascending_45'].iloc[-1]):
                while pd_count != 9:
                    gann_45_ascending_predictive.append((sqrt_twenty_four_hour_low + (degree_45_positive*pd_count))**2)
                    pd_count +=1
            else:
                gann_45_ascending_predictive.append((math.sqrt(df_candlesticks['ascending_45'].iloc[-1]) + ((degree_45_positive*granularity)*pd_count))**2)
                pd_count += 1

    elif granularity == 1440:
        while pd_count != 21:
            if df_candlesticks['ascending_45'].iloc[-1] != float(df_candlesticks['ascending_45'].iloc[-1]):
                while pd_count != 21:
                    gann_45_ascending_predictive.append((sqrt_twenty_four_hour_low + (degree_45_positive*pd_count))**2)
                    pd_count +=1
            else:
                gann_45_ascending_predictive.append((math.sqrt(df_candlesticks['ascending_45'].iloc[-1]) + ((degree_45_positive*granularity)*pd_count))**2)
                pd_count += 1

    #Gann 45 ascending 2:1
    count = 0
    as_index = df_candlesticks[['low']].idxmin().item()
    as_count = 0
    pd_count = 1
    if count < index_count:
        while count < as_index:
            gann_26_ascending_21.append(np.nan)
            count += 1
        if count == as_index:
            if count < index_count:
                gann_26_ascending_21.append((sqrt_twenty_four_hour_low + (degree_26_positive*as_count))**2)
                count += 1
                as_count += 1
        while count < index_count:
            gann_26_ascending_21.append((sqrt_twenty_four_hour_low + ((degree_26_positive*granularity)*as_count))**2)
            as_count += 1
            count += 1
    df_candlesticks['ascending_21'] = gann_26_ascending_21

    if granularity == 5:
        while pd_count != 80:
            if df_candlesticks['ascending_21'].iloc[-1] != float(df_candlesticks['ascending_21'].iloc[-1]):
                while pd_count != 80:
                    gann_26_ascending_21_predictive.append((sqrt_twenty_four_hour_low + (degree_26_positive*pd_count))**2)
                    pd_count +=1
            else:
                gann_26_ascending_21_predictive.append((math.sqrt(df_candlesticks['ascending_21'].iloc[-1]) + ((degree_26_positive*granularity)*pd_count))**2)
                pd_count += 1

    if granularity == 30:
        while pd_count != 9:
            if df_candlesticks['ascending_21'].iloc[-1] != float(df_candlesticks['ascending_21'].iloc[-1]):
                while pd_count != 9:
                    gann_26_ascending_21_predictive.append((sqrt_twenty_four_hour_low + (degree_26_positive*pd_count))**2)
                    pd_count +=1
            else:
                gann_26_ascending_21_predictive.append((math.sqrt(df_candlesticks['ascending_21'].iloc[-1]) + ((degree_26_positive*granularity)*pd_count))**2)
                pd_count += 1

    if granularity == 1440:
        while pd_count != 21:
            if df_candlesticks['ascending_21'].iloc[-1] != float(df_candlesticks['ascending_21'].iloc[-1]):
                while pd_count != 21:
                    gann_26_ascending_21_predictive.append((sqrt_twenty_four_hour_low + (degree_26_positive*pd_count))**2)
                    pd_count +=1
            else:
                gann_26_ascending_21_predictive.append((math.sqrt(df_candlesticks['ascending_21'].iloc[-1]) + ((degree_26_positive*granularity)*pd_count))**2)
                pd_count += 1


    #Gann 45 ascending 1:2
    count = 0
    as_index = df_candlesticks[['low']].idxmin().item()
    as_count = 0
    pd_count = 1
    if count < index_count:
        while count < as_index:
            gann_26_ascending_12.append(np.nan)
            count += 1
        if count == as_index:
            if count < index_count:
                gann_26_ascending_12.append((sqrt_twenty_four_hour_low + ((degree_63_positive)*as_count))**2)
                count += 1
                as_count += 1
        while count < index_count:
            gann_26_ascending_12.append((sqrt_twenty_four_hour_low + ((degree_63_positive*granularity)*as_count))**2)
            as_count += 1
            count += 1
    df_candlesticks['ascending_12'] = gann_26_ascending_12

    if granularity == 5:
        while pd_count != 80:
            if df_candlesticks['ascending_12'].iloc[-1] != float(df_candlesticks['ascending_12'].iloc[-1]):
                while pd_count != 80:
                    gann_26_ascending_12_predictive.append((sqrt_twenty_four_hour_low + (degree_63_positive*pd_count))**2)
                    pd_count +=1
            else:
                gann_26_ascending_12_predictive.append((math.sqrt(df_candlesticks['ascending_12'].iloc[-1]) + ((degree_63_positive*granularity)*pd_count))**2)
                pd_count += 1

    elif granularity == 30:
        while pd_count != 9:
            if df_candlesticks['ascending_12'].iloc[-1] != float(df_candlesticks['ascending_12'].iloc[-1]):
                while pd_count != 9:
                    gann_26_ascending_12_predictive.append((sqrt_twenty_four_hour_low + (degree_63_positive*pd_count))**2)
                    pd_count +=1
            else:
                gann_26_ascending_12_predictive.append((math.sqrt(df_candlesticks['ascending_12'].iloc[-1]) + ((degree_63_positive*granularity)*pd_count))**2)
                pd_count += 1

    elif granularity == 1440:
        while pd_count != 21:
            if df_candlesticks['ascending_12'].iloc[-1] != float(df_candlesticks['ascending_12'].iloc[-1]):
                while pd_count != 21:
                    gann_26_ascending_12_predictive.append((sqrt_twenty_four_hour_low + (degree_63_positive*pd_count))**2)
                    pd_count +=1
            else:
                gann_26_ascending_12_predictive.append((math.sqrt(df_candlesticks['ascending_12'].iloc[-1]) + ((degree_63_positive*granularity)*pd_count))**2)
                pd_count += 1

    df_45_predictions = pd.DataFrame()
    df_45_predictions['date'] = gann_45_predictive_time
    df_45_predictions['descending_45_predictions'] = gann_45_descending_predictive
    df_45_predictions['ascending_45_predictions'] = gann_45_ascending_predictive
    df_45_predictions['ascending_21_predictions'] = gann_26_ascending_21_predictive
    df_45_predictions['ascending_12_predictions'] = gann_26_ascending_12_predictive
    df_45_predictions['descending_21_predictions'] = gann_26_descending_21_predictive
    df_45_predictions['descending_12_predictions'] = gann_26_descending_12_predictive
    df_candlesticks = df_candlesticks

    result = df_candlesticks.to_json(orient="columns")
    gann = df_45_predictions.to_json(orient="columns")

    return df_45_predictions, df_candlesticks, granularity, pair

def DisplayChart(gann_lines, candles, granularity, pair):
    df_45_predictions = gann_lines
    df_candlesticks = candles
    granularity = granularity
    pair = pair

    #df_45_predictions, df_candlesticks, granularity, pair = DemexData()
    newdf = pd.merge(df_candlesticks, df_45_predictions, how='outer',on='date',sort=True)
    new_df = pd.merge(df_45_predictions, df_candlesticks, how='outer',on='date',sort=True)
    newdf.index = pd.DatetimeIndex(newdf['date'])

    #add- plots = plt.subplot(df_candlesticks['descending'])
    apds = [fplt.make_addplot(newdf['descending_45'],secondary_y=False ,color='gray', type='line', width=.6),
            fplt.make_addplot(newdf['descending_21'], secondary_y=False, type='line', width=.6, color='gray'),
            fplt.make_addplot(newdf['descending_12'], secondary_y=False, type='line', width=.6, color='gray'),
            fplt.make_addplot(newdf['ascending_45'], secondary_y=False, type='line', width=.6, color='gray'),
            fplt.make_addplot(newdf['ascending_21'], secondary_y=False, type='line', width=.6, color='gray'),
            fplt.make_addplot(newdf['ascending_12'], secondary_y=False, type='line', width=.6, color='gray'),
            fplt.make_addplot(new_df['ascending_45_predictions'], secondary_y = False, type='line', width= .7, color='green'),
            fplt.make_addplot(new_df['ascending_21_predictions'], secondary_y = False, type='line', width= .7, color='darkgreen'),
            fplt.make_addplot(new_df['ascending_12_predictions'], secondary_y = False, type='line', width= .7, color='seagreen'),
            fplt.make_addplot(new_df['descending_45_predictions'], secondary_y = False, type ='line', width = .7, color='red'),
            fplt.make_addplot(new_df['descending_21_predictions'], secondary_y = False, type='line', width= .7, color='firebrick'),
            fplt.make_addplot(new_df['descending_12_predictions'], secondary_y = False, type='line', width= .7, color='darkred'),
            #fplt.make_addplot(new_df['sma'], secondary_y = False, type='line', width= .7, color='blue'),
            ]

    ourpath = pathlib.Path("") / "temp.png"

    fplt.plot(
        newdf,
        type='candle',
        style='charles',
        title= pair + " " +  '5 Minute Candles with GANN',
        ylabel='Price',
        addplot=apds,
        savefig=ourpath
    )
