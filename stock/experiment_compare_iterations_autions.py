#!python3


"""
A utility for performing simulation experiments on auction mechanisms.
The experiment is similar to the one described by McAfee (1992), Table I (page 448).
In each experiment, we measure the actual vs. the optimal gain-from-trade.
This experiment using the real prices from Stock market. the prices are in csv files in stocks folder.

The results are printed to a CSV file. The columns are:

* stock_name - The stock name which the prices came from.
* recipe - (1,1) for McAfee; can be any vector of ones, e.g. (1,1,1),
    for our trade-reduction mechanism, or any vector of positive integers for our ascending-auction mechanism.
* num_possible_trades = n = total number of potential procurement-sets
    (e.g. if n=100 and recipe=[1,2] then there are 100 buyers and 200 sellers).
* optimal_count = k = number of deals in the optimal trade, averaged over all iterations.
                       Note that k <= n. E.g., there may be 100 buyers and 100 sellers, but only 50 procurement-sets with positive GFT, so k=50.
* optimal_gft - OPT = gain-from-trade in the optimal trade,
* optimal_trade_with_gft_zero - OPT = gain-from-trade in the optimal trade, including sets with GFT=0
* auction_count = k' = number of deals done by our auction,  averaged over all iterations.
                       Theoretically, since at most one deal is removed, it should be  either k or k-1.
* count_ratio = %k' = auction_count / optimal_count  * 100%.
* auction_gft = GFT = gain-from-trade in the auction, including auctioneer
* auction_gft_ratio = %GFT = auction_gft / optimal_gft * 100%.
              Theoretically it should be at least 1 - 1/k.
              In the results, it is usually higher.
* auction_market_gft = Market GFT = gain-from-trade in the auction, not including auctioneer.
* market_gft_ratio = Market %GFT = auction_market_gft / optimal_gft * 100%.
              Theoretically it should be at least 1 - 1/k.
              In the results, it is usually higher.

Recommended: add manually at the beginning of the file the header line:
,recipe,n,k,k+0,OPT_GFT,OPT_GFT+0,McAfee_k',%k',gft,%gft,market_gft,market_%gft,McAfee_Without_Heuristic_k',%k',gft,%gft,market_gft,market_%gft,SBB_External_Competition_k',%k',gft,%gft,market_gft,market_%gft,SBB_Ascending_Prices_k,%k',gft,%gft,market_gft,market_%gft

Author: Dvir Gilor
Since:  2020-08

"""


from markets import Market
from agents import AgentCategory

from tee_table.tee_table import TeeTable
from collections import OrderedDict
from get_stocks_data import getStocksPrices

TABLE_COLUMNS = ["stock_name", "recipe", "num_possible_trades", "optimal_count", "optimal_count_with_gft_zero",
                 "optimal_gft", "optimal_gft_with_gft_zero"]
AUCTION_COLUMNS = ["auction_count", "count_ratio", "auction_gft", "auction_gft_ratio",
                   "auction_market_gft", "market_gft_ratio"]

def experiment(results_csv_file:str, auction_functions:list, auction_names:str, recipe:tuple,
               nums_of_agents=None, stocks_prices:list=None, stock_names:list=None):
    """
    Run an experiment similar to McAfee (1992) experiment on the given auction.
    :param results_csv_file: the experiment result file.
    :param auction_functions: list of functions for executing the auction under consideration.
    :param auction_names: titles of the experiment, for printouts.
    :param recipe: can be any vector of ones, e.g. (1,1,1), for our trade-reduction mechanism, or any vector of positive integers for our ascending-auction mechanism.
    :param stocks_prices: list of prices for each stock and each agent.
    :param stock_names: list of stocks names which prices are belongs, for naming only.
    """
    if stocks_prices is None:
        (stocks_prices, stock_names) = getStocksPrices(recipe)
    column_names = TABLE_COLUMNS
    column_names += [auction_name + '_' + column for auction_name in auction_names for column in AUCTION_COLUMNS]
    results_table = TeeTable(column_names, results_csv_file)
    recipe_str = ":".join(map(str,recipe))
    if nums_of_agents is None:
        nums_of_agents = [10000000]
    for i in range(len(stocks_prices)):
        last_iteration = False
        for num_of_agents_per_category in nums_of_agents:
            num_of_possible_ps = min(num_of_agents_per_category,
                                     min([len(stocks_prices[i][j])/recipe[j] for j in range(len(stocks_prices[i]))]))
            if last_iteration is True and num_of_possible_ps < num_of_agents_per_category:
                break
            if num_of_possible_ps < num_of_agents_per_category:
                if last_iteration is True:
                    break
                else:
                    last_iteration = True
                    market = Market([AgentCategory("agent", stocks_prices[i][j]) for j in range(len(stocks_prices[i]))])
            else:
                market = Market([AgentCategory("agent", stocks_prices[i][j][0:num_of_possible_ps*recipe[j]]) for j in range(len(stocks_prices[i]))])
            (optimal_trade, _) = market.optimal_trade(ps_recipe=recipe, max_iterations=10000000, include_zero_gft_ps=False)
            optimal_count = optimal_trade.num_of_deals()
            optimal_gft = optimal_trade.gain_from_trade()
            (optimal_trade_with_gft_zero, _) = market.optimal_trade(ps_recipe=recipe, max_iterations=10000000)
            optimal_count_with_gft_zero = optimal_trade_with_gft_zero.num_of_deals()
            optimal_gft_with_gft_zero = optimal_trade_with_gft_zero.gain_from_trade()

            results = [("stock_name", stock_names[i]), ("recipe", recipe_str),
                       ("num_possible_trades", round(num_of_possible_ps)), ("optimal_count", round(optimal_count,2)),
                       ("optimal_count_with_gft_zero", round(optimal_count_with_gft_zero,2)),
                       ("optimal_gft", round(optimal_gft,2)),
                       ("optimal_gft_with_gft_zero", round(optimal_gft_with_gft_zero,2))]
            for auction_index in range(len(auction_functions)):
                auction_trade = auction_functions[auction_index](market, recipe)
                auction_count = auction_trade.num_of_deals()
                if(auction_names[auction_index] == "SBB_External_Competition" and auction_trade.num_of_deals() > optimal_trade.num_of_deals()):
                    print("Warning!!! the number of deals in action is greater than optimal!")
                    print("Optimal num of deals: ", optimal_trade.num_of_deals())
                    print("Auction num of deals: ", auction_trade.num_of_deals())
                    print("Auction name: ", auction_names[auction_index])
                auction_gft = auction_trade.gain_from_trade(including_auctioneer=True)
                auction_market_gft = auction_trade.gain_from_trade(including_auctioneer=False)
                auction_name = auction_names[auction_index]
                results.append((auction_name + "_auction_count", round(auction_trade.num_of_deals(),2)))
                if auction_names[auction_index] != "SBB_External_Competition":
                    results.append((auction_name + "_count_ratio",
                                    0 if optimal_count==0 else int((auction_count / optimal_count_with_gft_zero) * 100000)/1000))
                    results.append((auction_name + "_auction_gft", round(auction_gft,2)))
                    results.append((auction_name + "_auction_gft_ratio", 0 if optimal_gft==0 else round(auction_gft / optimal_gft_with_gft_zero*100,3)))
                    results.append((auction_name + "_auction_market_gft", round(auction_market_gft, 2)))
                    results.append((auction_name + "_market_gft_ratio",
                                    0 if optimal_gft == 0 else round(auction_market_gft / optimal_gft_with_gft_zero * 100, 3)))
                else:
                    results.append((auction_name + "_count_ratio",
                                    0 if optimal_count==0 else int((auction_count / optimal_count) * 100000)/1000))
                    results.append((auction_name + "_auction_gft", round(auction_gft,2)))
                    results.append((auction_name + "_auction_gft_ratio", 0 if optimal_gft==0 else round(auction_gft / optimal_gft*100,3)))
                    results.append((auction_name + "_auction_market_gft", round(auction_market_gft, 2)))
                    results.append((auction_name + "_market_gft_ratio",
                                    0 if optimal_gft == 0 else round(auction_market_gft / optimal_gft * 100, 3)))

            results_table.add(OrderedDict(results))
    results_table.done()

