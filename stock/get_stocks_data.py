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
import random
STOCKS = 'stocks'
POSITIVE_TYPES = ['High', 'Close']
NEGATIVE_TYPES = ['Open', 'Low']
TYPES = [*POSITIVE_TYPES, *NEGATIVE_TYPES]


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
        split_data[0] += [buyer*sum_sellers for buyer in buyers for _ in range(recipe[0])]
        for i in range(len(sellers)*(len(recipe)-1)):
            split_data[(i % (size-1))+1] += [sellers[i % len(sellers)] for _ in range(recipe[(i % (size-1))+1])]
        data = split_data
    print([len(category) for category in data])
    long_data = []
    for i in range(len(data)):
        long_data.append([])
        for j in range(len(data[i])):
            long_data[i].append(int(data[i][j]*1000))
            # if data[i][j] <= 0.0001 and i == 0:
            #     data[i][j] = 0.0001
            # elif data[i][j] >= -0.0001 and i > 0:
            #     data[i][j] = -0.0001
            # else:
            #     data[i][j] = (int(data[i][j]*10000))/10000
    return long_data

def getStocksPrices(recipe:tuple):
    onlyfiles = [f for f in listdir(STOCKS) if isfile(join(STOCKS, f))]
    return [getPrices(join(STOCKS, stockFile), recipe) for stockFile in onlyfiles], [f[0:-4] for f in onlyfiles]


def getStocksTreePrices(recipe_tree: list, agents_counts: list, agents_values: list):
    onlyfiles = [f for f in listdir(STOCKS) if isfile(join(STOCKS, f))]
    return [get_prices_tree(join(STOCKS, stockFile), agents_counts, agents_values) for stockFile in onlyfiles], [f[0:-4] for f in onlyfiles]

def get_prices_tree(stock_file: str, agents_counts: list, agents_values: list):
    df = pd.read_csv(stock_file)
    data = []
    for t in TYPES:
        for price in df[t].to_numpy():
            data.append(int(price*1000))
    random.shuffle(data)
    print(len(data))
    split_data = [[] for _ in range(len(agents_counts))]
    recipe_size = sum(agents_counts)
    data_index = 0
    for agent_index in range(len(agents_counts)):
        for i in range(int(len(data) / recipe_size * agents_counts[agent_index])):
            sign = -1 if agent_index > 0 else 1
            split_data[agent_index].append(sign * data[data_index] * agents_values[agent_index])
            data_index += 1
    return split_data


#print(getPricesTree('stocks\\T.csv', (1,1)))

