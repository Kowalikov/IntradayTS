import json
from datetime import datetime
from urllib.request import urlopen
import matplotlib
matplotlib.use("macosx")
from matplotlib import pyplot as plt
from matplotlib import dates as mpl_dates
from collections import OrderedDict
import pandas as pd
import matplotlib.dates as mdates

#zrobić różne interwały
#zrobić bazę z różnych dni i analizę na ich podstawie na porę dnia
#interwały 5min są okej, zdążymy zrobić analizę
#docelowo ustawić okres czasu do treningu, walidacji oraz co mamy przewidywać
#oddzielny model na otwartą giełdę i na przewidywanie po zamknięciu na rano

def group_list(lst):
    res = [(el, lst.count(el)) for el in lst]
    return list(OrderedDict(res).items())

def readData(AV_API):
    api_adress = f"https://www.alphavantage.co/query?function={AV_API['function']}&symbol={AV_API['symbol']}&interval={AV_API['interval']}&outputsize={AV_API['output_size']}&datatype={AV_API['data_type']}&apikey={AV_API['api_key']}"
    with urlopen(api_adress) as response:
        source = response.read()
    data = json.loads(source)
    priceKey = 'Time Series (' + AV_API['interval'] + ')'
    print(data['Meta Data'], data[priceKey].keys(), sep="\n")

    timeStamp = []
    timeDate = []
    high = []
    for time in data[priceKey]:
        price = data[priceKey][time]["2. high"]
        date_date = datetime.strptime(time, '%Y-%m-%d %H:%M:%S').date()
        date_time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S').time()
        timeStamp.append(date_time)
        timeDate.append(date_date)
        high.append(float(price))

    days = group_list(timeDate)
    # formatted data
    formData = {
        'date': timeDate,
        'time stamps': timeStamp,
        'price': high
    }
    df = pd.DataFrame(data=formData)
    print(df)
    print(df.loc[df['date'] == days[0][0]]['price'])

    return df, days

def plotDays(df, days):
    for i in range(len(days)):
        x_dt = [datetime.combine(days[i][0], t) for t in df.loc[df['date'] == days[i][0]]['time stamps']]
        y = df.loc[df['date'] == days[i][0]]['price']
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot_date(x_dt, y, linestyle=None, marker=".")
        plt.gcf().autofmt_xdate()
        date_format = mpl_dates.DateFormatter('%b %Y')
        plt.gca().xaxis.set_major_formatter(date_format)
        whichDay=list(df.loc[df['date'] == days[i][0]]['date'])
        plt.title(str(whichDay[0])+ ' prices for ' + AV_API['symbol'])
        plt.ylabel('Price')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.tight_layout()
        plt.show()

# alpha vantage api
#mamy 500 requestów dziennie (24/25min dla 8godzinnej giełdy, działania tylko w czasie działania GPW akcje( 8:45-16:50, 17;00=17:05 dogrywka)
#compact ma zakres 100 rzeczy
#full 1113
#wczytanie i wyświetlenie wyników trwa mniej niż 10s (full)
AV_API = {
    'function': 'TIME_SERIES_INTRADAY',
    'symbol': 'IBM',
    # by default = compact, mozna dac full
    'output_size': 'full',
    'interval': '1min',
    # json lub csv
    'data_type': 'json',
    'api_key': 'FMNMZYOGQTQXAP9I'
}


df, days = readData(AV_API)
plotDays(df, days)


