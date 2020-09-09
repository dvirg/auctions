import pandas as pd
from os import listdir
from os.path import isfile, join
STOCKS = 'stocks'
POSITIVE_TYPES = ['High', 'Close']
NEGATIVE_TYPES = ['Open', 'Low']

def getPrices(stockFile:str, recipe:tuple):
    df = pd.read_csv(stockFile)
    # max_stock_price = max(df['High'])
    # data = [*[df[type].to_numpy()/max_stock_price for type in POSITIVE_TYPES], *[-1*df[type].to_numpy()/max_stock_price for type in NEGATIVE_TYPES]]
    data = [*[df[type].to_numpy() for type in POSITIVE_TYPES], *[-1*df[type].to_numpy() for type in NEGATIVE_TYPES]]
    # print(data)
    if recipe == (1, 1):
        data = [[*data[0], *data[1]], [*data[2], *data[3]]]
    elif recipe == (2, 1):
        data = [[*data[0], *data[1]], data[2] + data[3]]
    elif recipe == (1, 2):
        data = [data[0] + data[1], [*data[2], *data[3]]]
    elif recipe == (2, 1, 1):
        data = [[*data[0], *data[1]], data[2], data[3]]
    elif len(recipe) == 3:
        data = [data[0] + data[1], data[2], data[3]]
    return data
#    flatData = [price for row in data for price in row]
#    print(len(flatData))
#    return flatData
# print(getPrices('stocks\T.csv',(1,1,1)))
# print(len(getPrices('stocks\T.csv',(1,1))))

def getStocksPrices(recipe:tuple):
    onlyfiles = [f for f in listdir(STOCKS) if isfile(join(STOCKS, f))]
    return [getPrices(join(STOCKS, stockFile), recipe) for stockFile in onlyfiles], [f[0:-4] for f in onlyfiles]
#print(getStocksPrices())

