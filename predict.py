import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as fplt
import numpy as np
import math
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from urllib.error import HTTPError
import requests
import json
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image

def connect(url, *args, **kwargs):
    try:
        if kwargs.get('param', None) is not None:
            response = requests.get(url,params)
        else:
            response = requests.get(url)
        response.raise_for_status()
        print('HTTP connection success!')
        return response
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def coinbase_records(ticker):
    ticker = ticker
    dataset = '200'
    REST_API = 'https://api.pro.coinbase.com'
    PRODUCTS = REST_API+'/products'
    MY_CURRENCIES = [ticker]
    response = connect(PRODUCTS)
    response_content = response.content
    response_text = response.text
    response_headers = response.headers

    df_currencies = pd.read_json (response_text)
    #print("\nNumber of columns in the dataframe: %i" % (df_currencies.shape[1]))
    #print("Number of rows in the dataframe: %i\n" % (df_currencies.shape[0]))
    columns = list(df_currencies.columns)

    currency_rows = []
    for currency in MY_CURRENCIES:
        response = connect(PRODUCTS+'/'+currency+'/stats')
        response_content = response.content
        data = json.loads(response_content.decode('utf-8'))
        currency_rows.append(data)
    # Create dataframe and set row index as currency name
    df_statistics = pd.DataFrame(currency_rows, index = MY_CURRENCIES)
    start_date = (datetime.today() - timedelta(days=300)).isoformat()
    end_date = datetime.now().isoformat()

    # Please refer to the coinbase documentation on the expected parameters
    params = {'start':start_date, 'end':end_date, 'granularity':86400}
    url = "https://api.exchange.coinbase.com/products/"+ ticker + "/candles?granularity=" + "86400"

    response = connect(url)
    response_text = response.text
    df_history = pd.read_json(response_text)
    # Add column names in line with the Coinbase Pro documentation
    df_history.columns = ['time','low','high','open','close','volume']

    # We will add a few more columns just for better readability
    df_history['date'] = pd.to_datetime(df_history['time'], unit='s')
    day = df_history[['date', 'close']]
    #Ensure close is a float value
    day = day.astype({'close': float})
    return day

def new_dataset(dataset, step_size):
    data_X, data_Y = [], []
    for i in range(len(dataset)-step_size-1):
        a = dataset[i:(i+step_size), 0]
        data_X.append(a)
        data_Y.append(dataset[i + step_size, 0])

    return np.array(data_X), np.array(data_Y)

def predict(records):
    # FOR REPRODUCIBILITY
    np.random.seed(7)

    # IMPORTING DATASET
    dataset = records
    dataset = dataset.reindex(index = dataset.index[::-1])

    # CREATING OWN INDEX FOR FLEXIBILITY
    obs = np.arange(1, len(dataset) + 1, 1)

    # TAKING DIFFERENT INDICATORS FOR PREDICTION
    close_val = dataset['close']

    # PREPARATION OF TIME SERIES DATASE
    close_val = np.reshape(close_val.values, (len(close_val),1)) # 1664
    scaler = MinMaxScaler(feature_range=(0, 1))
    close_val = scaler.fit_transform(close_val)

    # TRAIN-TEST SPLIT
    train_close = int(len(close_val) * 0.75)
    test_close = len(close_val) - train_close
    train_close, test_close = close_val[0:train_close,:], close_val[train_close:len(close_val),:]

    # TIME-SERIES DATASET (FOR TIME T, VALUES FOR TIME T+1)
    trainX, trainY = new_dataset(train_close, 1)
    testX, testY = new_dataset(test_close, 1)

    # RESHAPING TRAIN AND TEST DATA
    trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
    step_size = 1

    # LSTM MODEL
    model = Sequential()
    model.add(LSTM(32, input_shape=(1, step_size), return_sequences = True))
    model.add(LSTM(16))
    model.add(Dense(1))
    model.add(Activation('linear'))

    # MODEL COMPILING AND TRAINING
    model.compile(loss='mean_squared_error', optimizer='adam') # Try SGD, adam, adagrad and compare!!!
    model.fit(trainX, trainY, epochs=14, batch_size=1, verbose=2)

    # PREDICTION
    trainPredict = model.predict(trainX)
    testPredict = model.predict(testX)

    # DE-NORMALIZING FOR PLOTTING
    trainPredict = scaler.inverse_transform(trainPredict)
    trainY = scaler.inverse_transform([trainY])
    testPredict = scaler.inverse_transform(testPredict)
    testY = scaler.inverse_transform([testY])

    # TRAINING RMSE
    trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))
    #print('Train RMSE: %.2f' % (trainScore))

    # TEST RMSE
    testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
    #print('Test RMSE: %.2f' % (testScore))

    # CREATING SIMILAR DATASET TO PLOT TRAINING PREDICTIONS
    trainPredictPlot = np.empty_like(close_val)
    trainPredictPlot[:, :] = np.nan
    trainPredictPlot[step_size:len(trainPredict)+step_size, :] = trainPredict

    # CREATING SIMILAR DATASSET TO PLOT TEST PREDICTIONS
    testPredictPlot = np.empty_like(close_val)
    testPredictPlot[:, :] = np.nan
    testPredictPlot[len(trainPredict)+(step_size*2)+1:len(close_val)-1, :] = testPredict

    # DE-NORMALIZING MAIN DATASET
    close_val = scaler.inverse_transform(close_val)

    # PREDICT FUTURE VALUES
    last_val = testPredict[-1]
    #print("Last Value: " + str(last_val))
    last_val_scaled = last_val/last_val
    next_val = model.predict(np.reshape(last_val_scaled, (1,1,1)))
    #model.save('path/to/location')
    next_day = last_val.item() * next_val

    return next_day

def combine_predictions(ticker):
    exchange = 'coinbase'
    ticker = ticker
    epochs = 10
    dataset_rows = "365"
    if exchange == 'coinbase':
        records = coinbase_records(ticker)
    elif exchange == 'carbon':
        records = carbon_records(ticker)
    df_prediction = pd.DataFrame()
    count = 0
    while count != epochs:
        date = records.date.max() + timedelta(days=1)
        records = records.append({'date': date, 'close': predict(records)}, ignore_index=True)
        count += 1
    records.index = pd.DatetimeIndex(records['date'])
    records.sort_index(ascending=True, inplace=True)
    close = records['close']
    plt.style.use('dark_background')
    fig, ax = plt.subplots(tight_layout=True)
    ax.plot(records.index, close, 'g', label = 'Closing Plot with Predicted Values')
    ax.set_xlabel('Date')
    ax.set_ylabel('Close Value')
    plt.legend(loc = 'upper right')
    plt.xticks(
        rotation=45,
        horizontalalignment='right',
        fontweight='light',
        fontsize='x-large'
    )
    fig.savefig('temp.png', dpi=72)
