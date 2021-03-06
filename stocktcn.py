# -*- coding: utf-8 -*-
"""stocktcn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rQ0AO6h6w3PqSjBxYYA2_nv8qOMW6iZg

# Trial - NFLX with TCN
"""

pip install yfinance

pip install darts

import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import yfinance as yf
plt.style.use('fivethirtyeight')

from darts import TimeSeries
from darts.models import TCNModel, RNNModel
from darts.dataprocessing.transformers import Scaler
from darts.utils.timeseries_generation import datetime_attribute_timeseries
from darts.metrics import mape, r2_score, rmse
from darts.utils.missing_values import fill_missing_values
from darts.datasets import AirPassengersDataset, SunspotsDataset

"""# **Air sunspot Dataset**"""

# Read data
sp = SunspotsDataset().load()

# Scaling all data
scaler = Scaler()
sp = scaler.fit_transform(sp)
sp

# Create training and testing data
train_sp_transformed, val_sp_transformed = sp.split_after(pd.Timestamp('19401001'))

train_sp_transformed

val_sp_transformed

# TCN Model
model_sun = TCNModel(
    input_chunk_length=250,
    output_chunk_length=36,
    n_epochs=100,
    dropout=0,
    dilation_base=2,
    weight_norm=True,
    kernel_size=3,
    num_filters=6,
    nr_epochs_val_period=1,
    random_state=0
)

# Training
model_sun.fit(series=train_sp_transformed, val_series=val_sp_transformed, verbose=True)

# Backtest
backtest_sp = model_sun.historical_forecasts(
    sp,
    start=0.7,
    forecast_horizon=12,
    stride=10,
    retrain=False,
    verbose=True
)
sp[2000:].plot(label='actual')
backtest_sp.plot(label='backtest (H=12)')
plt.legend()

"""# **Stock dataset**"""

# Get the stock data
tickerSymbol = 'NFLX'
tickerData = yf.Ticker(tickerSymbol)
tickerDf = tickerData.history(period='1d', start='2015-1-1', end='2021-5-31')

# Show the stock data
tickerDf

# Check null values
tickerDf.isna().sum()

# Get the numbers of rows and columns in the dataset
print(tickerDf.shape)
print(tickerDf.info())
print(tickerDf.describe())

# Visualize the dataset
plt.figure(figsize = (20, 10))
plt.plot(tickerDf['Close'])
plt.title('NFLX Closing Price History')
plt.xlabel('Date', fontsize = 10)
plt.ylabel('Close Price $ USD', fontsize = 10)
plt.show()

# Create a timeseries object from a pandas dataframe
tickerSeries = TimeSeries.from_dataframe(tickerDf, value_cols='Close', 
                                         fill_missing_dates = True, freq='D')

# Copy dataset to fill the missing value
tes = tickerSeries.pd_dataframe(copy=True)

# Fill the missing value
tes = tes.fillna(method = 'ffill')

# Rename column name
tes = tes.rename(columns={'0':'Close'})

tes.head()

# Create a timeseries object from a pandas dataframe again
tickerSeries2 = TimeSeries.from_dataframe(tes, value_cols='Close', 
                                          fill_missing_dates = True, freq='D')

# Scaling Data
scaler = Scaler()
tickerSeries2 = scaler.fit_transform(tickerSeries2)
tickerSeries2

# Create training and validation dataset
train, val = tickerSeries2.split_after(0.8)

train

val

# TCN Model
tcn_model = TCNModel(
    n_epochs=100,
    input_chunk_length=1000,
    output_chunk_length=110,
    dropout=0.1,
    dilation_base=2,
    weight_norm=True,
    kernel_size=5,
    num_filters=3,
    random_state=0
)

# Training
tcn_model.fit(series=train, verbose=True)

# Backesting
backtest_tcn = tcn_model.historical_forecasts(
    tickerSeries2,
    start=0.9,
    forecast_horizon=5,
    stride=5,
    retrain=False,
    verbose=True
)

# Visualize
plt.figure(figsize=(20,10))
plt.title('TCN Model - NFLX Closing Price Prediction')
plt.xlabel('Date', fontsize = 10)
plt.ylabel('Close Price $ USD', fontsize = 10)
tickerSeries2[0:].plot(label='Train')
tickerSeries2[2100:].plot(label='Validation')
backtest_tcn.plot(label='Predictions')
plt.legend(fontsize=24, loc='best')
plt.show()

plt.figure(figsize=(20,10))
tickerSeries2[1800:].plot(label='Train')
tickerSeries2[2100:].plot(label='Validations')
backtest_tcn.plot(label='Predictions')
plt.legend(fontsize=24, loc='best')

# Backtesting data
backtest_tcn

