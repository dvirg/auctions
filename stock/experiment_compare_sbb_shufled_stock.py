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
* gft = GFT = gain-from-trade in the auction, including auctioneer
* gft_ratio = %GFT = gft / optimal_gft * 100%.
              Theoretically it should be at least 1 - 1/k.
              In the results, it is usually higher.

Recommended: add manually at the beginning of the file the header line:
,recipe,n,k,k+0,OPT_GFT,SBB_External_Competition_k',%k',gft,%gft,SBB_Ascending_Prices_k,%k',gft,%gft

Author: Dvir Gilor
Since:  2020-08

"""


from markets import Market
from agents import AgentCategory

from tee_table.tee_table import TeeTable
from collections import OrderedDict
from get_stocks_data import getStocksPricesShuffled

import random

def experiment(results_csv_file: str, auction_functions: list, auction_names: str, recipe: tuple, iterations:int, nums_of_agents:list = None,
               stocks_prices: list = None, stock_names: list = None):
    """
    Run an experiment similar to McAfee (1992) experiment on the given auction.
    :param results_csv_file: the experiment result file.
    :param auction_functions: list of functions for executing the auction under consideration.
    :param auction_names: titles of the experiment, for printouts.
    :param recipe: can be any vector of ones, e.g. (1,1,1), for our trade-reduction mechanism, or any vector of positive integers for our ascending-auction mechanism.
    :param nums_of_agents: list of n(s) for number of possible trades to make the calculations.
    :param stocks_prices: list of prices for each stock and each agent.
    :param stock_names: list of stocks names which prices are belongs, for naming only.
    """
    TABLE_COLUMNS = ["stockname", "recipe", "numpossibletrades", "optimalcount", "optimalcountwithgftzero",
                     "optimalgft"]
    AUCTION_COLUMNS = ["auctioncount", "countratio", "gft", "gftratio"]
    print(recipe)
    if stocks_prices is None:
        (stocks_prices, stock_names) = getStocksPricesShuffled()
    column_names = TABLE_COLUMNS
    column_names += [auction_name + column for auction_name in auction_names for column in AUCTION_COLUMNS]
    results_table = TeeTable(column_names, results_csv_file)
    recipe_str = ":".join(map(str,recipe))
    recipe_sum = sum(recipe)
    if nums_of_agents is None:
        nums_of_agents = [10000000]
    average_total_results = {}
    for num_of_agents_per_category in nums_of_agents:
        average_total_results[str(num_of_agents_per_category)] = []

    for i in range(len(stocks_prices)):
        total_results = {}
        for num_of_agents_per_category in nums_of_agents:
            total_results[str(num_of_agents_per_category)] = []
        stock_prices = stocks_prices[i]
        last_iteration = False
        for num_of_agents_per_category in nums_of_agents:
            for iteration in range(iterations):
                num_of_possible_ps = min(num_of_agents_per_category, int(len(stock_prices)/recipe_sum))
                if last_iteration and num_of_possible_ps < num_of_agents_per_category:
                    break
                if num_of_possible_ps < num_of_agents_per_category:
                    if last_iteration:
                        break
                last_iteration = True
                categories = []
                buyer_agent_count = recipe[0]
                index = 0
                for category in recipe:
                    next_index = index + num_of_possible_ps * category
                    price_value_multiple = -1 * buyer_agent_count if index > 0 else recipe_sum - buyer_agent_count
                    categories.append(AgentCategory("agent", [int(price * price_value_multiple) for price in stock_prices[index:next_index]]))
                    index = next_index
                market = Market(categories)

                (optimal_trade, _) = market.optimal_trade(ps_recipe=list(recipe), max_iterations=10000000, include_zero_gft_ps=False)
                optimal_count = optimal_trade.num_of_deals()
                optimal_gft = optimal_trade.gain_from_trade()
                (optimal_trade_with_gft_zero, _) = market.optimal_trade(ps_recipe=list(recipe), max_iterations=10000000)
                optimal_count_with_gft_zero = optimal_trade_with_gft_zero.num_of_deals()

                results = [("stockname", stock_names[i]), ("recipe", recipe_str),
                           ("numpossibletrades", round(num_of_possible_ps)), ("optimalcount", optimal_count),
                           ("optimalcountwithgftzero", optimal_count_with_gft_zero),
                           ("optimalgft", optimal_gft)]
                for auction_index in range(len(auction_functions)):
                    if 'mcafee' in auction_names[auction_index]:
                        results.append((auction_name + "auctioncount", 0))
                        results.append((auction_name + "countratio", 0))
                        results.append((auction_name + "gft", 0))
                        results.append((auction_name + "gftratio", 0))

                    auction_trade = auction_functions[auction_index](market, recipe)
                    auction_count = auction_trade.num_of_deals()
                    # for j in range(len(stocks_prices[i])):
                    #     print(sorted(stocks_prices[i][j][:num_of_possible_ps*recipe[j]]))
                    if(auction_trade.num_of_deals() > optimal_trade_with_gft_zero.num_of_deals()):
                        # print(sorted(stocks_prices[i][0][:num_of_possible_ps*recipe[0]]))
                        # print(sorted(stocks_prices[i][1][:num_of_possible_ps*recipe[1]]))
                        print("Warning!!! the number of deals in action is greater than optimal!")
                        print("Optimal num of deals: ", optimal_trade.num_of_deals())
                        print("Auction num of deals: ", auction_trade.num_of_deals())
                        print("Auction name: ", auction_names[auction_index])
                    gft = auction_trade.gain_from_trade(including_auctioneer=False)
                    auction_name = auction_names[auction_index]
                    results.append((auction_name + "auctioncount", auction_trade.num_of_deals()))
                    results.append((auction_name + "countratio",
                                    0 if optimal_count_with_gft_zero==0 else (auction_count / optimal_count_with_gft_zero) * 100))
                    results.append((auction_name + "gft", gft))
                    results.append((auction_name + "gftratio", 0 if optimal_gft==0 else gft / optimal_gft*100))

                #results_table.add(OrderedDict(results))
                if len(total_results[str(num_of_agents_per_category)]) == 0:
                    total_results[str(num_of_agents_per_category)] = results[0:len(results)]
                else:
                    sum_result = total_results[str(num_of_agents_per_category)]
                    for index in range(len(results)):
                        if index > 2:
                            sum_result[index] = (results[index][0], sum_result[index][1] + results[index][1])
        for num_of_agents_per_category in nums_of_agents:
            results = total_results[str(num_of_agents_per_category)]
            if len(results) == 0:
                continue
            for index in range(len(results)):
                if index > 2:
                    if 'ratio' in results[index][0]:
                        results[index] = (results[index][0], results[index][1]/iterations)
                    else:
                        results[index] = (results[index][0], results[index][1]/iterations)
                #elif index == 0:
                #    results[index] = (results[index][0], 'Average')
            results_table.add(OrderedDict(results))

            if len(average_total_results[str(num_of_agents_per_category)]) == 0:
                average_total_results[str(num_of_agents_per_category)] = results[0:len(results)]
            else:
                sum_result = average_total_results[str(num_of_agents_per_category)]
                for index in range(len(results)):
                    if index > 2:
                        sum_result[index] = (sum_result[index][0], sum_result[index][1] + results[index][1])
    for num_of_agents_per_category in nums_of_agents:
        results = average_total_results[str(num_of_agents_per_category)]
        if len(results) == 0:
            continue
        for index in range(len(results)):
            if index > 2:
                if 'ratio' in results[index][0]:
                    results[index] = (results[index][0], int(results[index][1]/len(stocks_prices)*1000)/1000)
                else:
                    results[index] = (results[index][0], round(results[index][1]/len(stocks_prices), 1))
            elif index == 0:
                results[index] = (results[index][0], 'Average')
        results_table.add(OrderedDict(results))
    results_table.done()

