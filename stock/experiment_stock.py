#!python3


"""
A utility for performing simulation experiments on auction mechanisms.
The experiment is similar to the one described by McAfee (1992), Table I (page 448).
In each experiment, we measure the actual vs. the optimal gain-from-trade.
This experiment using the real prices from Stock market. the prices are in csv files in stocks folder.

The results are printed to a CSV file. The columns are:

* stock_name - The stock name which the prices came from.
* auction_name - title of the experiment, for printouts.
* recipe - (1,1) for McAfee; can be any vector of ones, e.g. (1,1,1),
    for our trade-reduction mechanism, or any vector of positive integers for our ascending-auction mechanism.
* num_possible_trades = n = total number of potential procurement-sets
    (e.g. if n=100 and recipe=[1,2] then there are 100 buyers and 200 sellers).
* optimal_count = k = number of deals in the optimal trade, averaged over all iterations.
                       Note that k <= n. E.g., there may be 100 buyers and 100 sellers, but only 50 procurement-sets with positive GFT, so k=50.
* auction_count = k' = number of deals done by our auction,  averaged over all iterations.
                       Theoretically, since at most one deal is removed, it should be  either k or k-1.
* count_ratio  = auction_count / optimal_count  * 100%.
* optimal_gft - OPT = gain-from-trade in the optimal trade, 	averaged over all iterations.
* auction_gft - GFT = gain-from-trade in the auction, including auctioneer
* auction_gft_ratio  = auction_gft / optimal_gft * 100%.
              Theoretically it should be at least 1 - 1/k.
              In the results, it is usually higher.
* auction_market_gft - GFT = gain-from-trade in the auction, not including auctioneer.
* market_gft_ratio = auction_market_gft / optimal_gft * 100%.
              Theoretically it should be at least 1 - 1/k.
              In the results, it is usually higher.

Author: Dvir Gilor
Since:  2020-08

"""


from markets import Market
from agents import AgentCategory
from typing import Callable

from tee_table.tee_table import TeeTable
from collections import OrderedDict
from get_stocks_data import getStocksPrices

TABLE_COLUMNS = ["stock_name","auction_name", "recipe", "num_possible_trades", "optimal_count", "auction_count",
                 "count_ratio", "optimal_gft", "auction_gft", "auction_gft_ratio", "auction_market_gft", "market_gft_ratio"]

def experiment(results_csv_file:str, auction_function:Callable, auction_name:str, recipe:tuple,
               stocks_prices:list=None, stock_names:list=None):
    """
    Run an experiment similar to McAfee (1992) experiment on the given auction.
    :param results_csv_file: the experiment result file.
    :param auction_function: the function for executing the auction under consideration.
    :param auction_name: title of the experiment, for printouts.
    :param recipe: can be any vector of ones, e.g. (1,1,1), for our trade-reduction mechanism, or any vector of positive integers for our ascending-auction mechanism.
    :param stocks_prices: list of prices for each stock and each agent.
    :param stock_names: list of stocks names which prices are belongs, for naming only.
    """
    if stocks_prices is None:
        (stocks_prices, stock_names) = getStocksPrices(recipe)
    results_table = TeeTable(TABLE_COLUMNS, results_csv_file)
    recipe_str = ":".join(map(str,recipe))
    for i in range(len(stocks_prices)):
        market = Market([AgentCategory("agent", category) for category in stocks_prices[i]])
        num_of_possible_ps = min([len(stocks_prices[i][j])/recipe[j] for j in range(len(stocks_prices[i]))])
        (optimal_trade, _) = market.optimal_trade(recipe)
        auction_trade = auction_function(market, recipe)
        optimal_count = optimal_trade.num_of_deals()
        auction_count = auction_trade.num_of_deals()
        if(auction_trade.num_of_deals() > optimal_trade.num_of_deals()):
            print("Warning!!! the number of deals in action is greater than optimal!")
            print("Optimal num of deals: ", optimal_trade.num_of_deals())
            print("Auction num of deals: ", auction_trade.num_of_deals())
        optimal_gft = optimal_trade.gain_from_trade()
        auction_gft = auction_trade.gain_from_trade(including_auctioneer=True)
        auction_market_gft = auction_trade.gain_from_trade(including_auctioneer=False)
        results_table.add(OrderedDict((
            ("stock_name", stock_names[i]),
            ("auction_name", auction_name),
            ("recipe", recipe_str),
            ("num_possible_trades", round(num_of_possible_ps)),
            ("optimal_count", round(optimal_count,2)),
            ("auction_count", round(auction_count,2)),
            ("count_ratio", 0 if optimal_count==0 else int((auction_count / optimal_count) * 100000)/1000),
            ("optimal_gft", round(optimal_gft,2)),
            ("auction_gft", round(auction_gft,2)),
            ("auction_gft_ratio", 0 if optimal_gft==0 else round(auction_gft / optimal_gft*100,3)),
            ("auction_market_gft", round(auction_market_gft, 2)),
            ("market_gft_ratio", 0 if optimal_gft == 0 else round(auction_market_gft / optimal_gft * 100, 3)),
        )))
    results_table.done()
