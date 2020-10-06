#!python3

"""
Imports stock prices from csv files downloaded from Yahoo.
The CSV files are stored in stocks directory.

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
    elif recipe == (1, 1, 1):
        data = [data[0] + data[1], data[2], data[3]]
    elif len(recipe) == 3 and recipe[1:] == recipe[:-1]:
        data = [data[0] + data[1], data[2], data[3]]
    else: # recipe[1:] == recipe[:-1]: #all numbers in recipe are identical
        buyers = [*data[0], *data[1]]
        sellers = [*data[2], *data[3]]
        size = len(recipe)
        sum_sellers = sum(recipe) - recipe[0]
        multiple = 1
        for v in recipe:
            multiple *= v
        split_data = [[] for i in range(size)]
        print(split_data)
        split_data[0] += [buyer for buyer in buyers for _ in range(recipe[0])]
        for i in range(len(sellers)*(len(recipe)-1)):
            split_data[(i % (size-1))+1] += [sellers[i % len(sellers)]/sum_sellers for _ in range(recipe[(i % (size-1))+1])]
        data = split_data
    print([len(category) for category in data])
    return data

def getStocksPrices(recipe:tuple):
    onlyfiles = [f for f in listdir(STOCKS) if isfile(join(STOCKS, f))]
    return [getPrices(join(STOCKS, stockFile), recipe) for stockFile in onlyfiles], [f[0:-4] for f in onlyfiles]


