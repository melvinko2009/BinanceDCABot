from matplotlib.colors import LinearSegmentedColormap
from pycoingecko import CoinGeckoAPI
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import requests
import arrow

plt.style.use('dark_background')


# Calculates normalized Risk for current Bitcoin price
# Attempt to replicate the Risk Metric from Benjamin Cowen
def getRiskForAsset(asset: str, draw=False) -> float:
    cg, df = CoinGeckoAPI(), pd.DataFrame()
    data = dict()

    # Get historic Data (CoinAPI)
    SMailApi_key = "57AFD1FA-8E94-4A70-941F-9D2DFB6F0533"
    GMailApi_key = "2CBC2FEF-6319-4982-9990-AC644FDE392D"
    url = 'https://rest.coinapi.io/v1/exchangerate/BTC/EUR/history?period_id=1DAY&time_start=2010-07-01T00:00:00' \
          f'&time_end=2014-01-01T00:00:00&limit=10000'
    headers = {'X-CoinAPI-Key': SMailApi_key}
    # coinApiData = requests.get(url, headers=headers).json()

    # If API is bad or limit is reached
    # for values in coinApiData:
    #   data[datetime.strptime(str(arrow.get(values['time_period_end']).datetime)[:-6], '%Y-%m-%d %H:%M:%S')] = values['rate_close']

    # Get  Market Data for asset (Coingecko)
    coingeckoData = cg.get_coin_market_chart_by_id(id=asset.lower(), vs_currency='eur', days='max')

    # Account for diminishing returns
    boostFactor2021, boostFactor2017, boostFactor2013 = np.sqrt(115 / 25), np.sqrt(500 / 115), np.sqrt(1200 / 500)

    for timestampAndPrice in coingeckoData['prices']:
        data[datetime.fromtimestamp(timestampAndPrice[0] / 1000)] = timestampAndPrice[1]

    df['Datum'], df['Preis'] = list(data.keys()), list(data.values())
    df = df.set_index('Datum')

    # calculate Moving Average (20,50,100, 350)
    SMA20, SMA50, SMA100, SMA350, STD50 = df.rolling(window=20, min_periods=2).mean(), df.rolling(window=50,
                                                                                                  min_periods=5).mean(), \
                                          df.rolling(window=100, min_periods=10).mean(), df.rolling(window=350,
                                                                                                    min_periods=35).mean(), \
                                          df.rolling(window=50, min_periods=5).std()

    # Normalized Volatility
    # normalizedStd = (SMA50/ STD50)['Preis']
    normalizedStd = (STD50 - np.nanmin(STD50)) / (np.nanmax(STD50) - np.nanmin(STD50))

    # Calculate Risk (totally adjustable)
    risk = (SMA50 / SMA350)['Preis'] + (SMA20 / SMA100 / 2)['Preis'] + (df['Preis'] / SMA50['Preis'] / 2) + \
           (df['Preis'] / SMA100['Preis'] / 2) + normalizedStd['Preis'] * 2

    # risk = risk.mask((df.index > datetime(2012, 1, 1, 00, 00)) & (df.index < datetime(2013, 2, 28, 00, 00)), risk * boostFactor2013)
    risk = risk.mask((df.index > datetime(2013, 3, 1, 00, 00)) & (df.index < datetime(2018, 5, 31, 00, 00)),
                     risk * boostFactor2017)
    risk = risk.mask((df.index > datetime(2018, 6, 1, 00, 00)), risk * boostFactor2021)

    # Normalize risk to scale of 0 to 1
    risk = np.sqrt(risk)
    normalizedRisk = (risk - np.nanmin(risk)) / (np.nanmax(risk) - np.nanmin(risk))

    # Fill Dataframe
    df['20 Day SMA'], df['50 Day SMA'], df['100 Day SMA'], df['350 SMA'], df['Risk'] = SMA20, SMA50, SMA100, \
                                                                                       SMA350, normalizedRisk
    # Draw the plot if wanted
    if draw:
        drawPlot(list(data.keys()), list(data.values()), df, asset)
    return df['Risk'][-1]


# Draws the historic Bitcoin Price with color coded risk
def drawPlot(x, y, df, asset):
    dateNumbers = mdates.date2num(x)
    points = np.array([dateNumbers, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    fig, ax = plt.subplots()
    fig.set_size_inches(13, 9)

    norm = plt.Normalize(np.nanmin(df['Risk']), np.nanmax(df['Risk']))
    cmap = LinearSegmentedColormap.from_list("cmap", [(0, 0, 1), (0, 1, 1), (1, 1, 0), (1, 0, 0)], N=200)
    lc = LineCollection(segments, cmap=cmap, norm=norm, linewidths=3)

    lc.set_array(np.array(df['Risk']))
    line = ax.add_collection(lc)
    fig.colorbar(line, ax=ax)

    ax.set_xlim(np.nanmin(dateNumbers), np.nanmax(dateNumbers))
    ax.set_ylim(np.nanmin(y) * 0.8, np.nanmax(y) * 1.5)
    ax.set_title(f"               {asset} Risk Metric", fontsize=20)
    ax.set_xlabel("Zeit", fontsize=16)
    ax.set_ylabel("Preis in €", fontsize=16)
    ax.set_yscale(value="log")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=9))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m-%Y'))
    ax.set_xticklabels([])
    plt.savefig('BTCRiskMetric.png')
    plt.show()
