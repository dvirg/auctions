#!python3

"""
Imports stock prices from csv files downloaded from Yahoo.

Author: Dvir Gilor
Since:  2020-08
"""
import pandas as pd
from os import listdir
from os.path import isfile, join
STOCKS = 'stocks'
POSITIVE_TYPES = ['High', 'Close']
NEGATIVE_TYPES = ['Open', 'Low']

def getPrices(stockFile:str, recipe:tuple):
    df = pd.read_csv(stockFile)
    data = [*[df[type].to_numpy() for type in POSITIVE_TYPES], *[-1*df[type].to_numpy() for type in NEGATIVE_TYPES]]
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

def getStocksPrices(recipe:tuple):
    onlyfiles = [f for f in listdir(STOCKS) if isfile(join(STOCKS, f))]
    return [getPrices(join(STOCKS, stockFile), recipe) for stockFile in onlyfiles], [f[0:-4] for f in onlyfiles]


