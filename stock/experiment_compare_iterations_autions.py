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
* count = k' = number of deals done by our auction,  averaged over all iterations.
                       Theoretically, since at most one deal is removed, it should be  either k or k-1.
* count_ratio = %k' = count / optimal_count  * 100%.
* total_gft = GFT = gain-from-trade in the auction, including auctioneer
* total_gft_ratio = %GFT = total_gft / optimal_gft * 100%.
              Theoretically it should be at least 1 - 1/k.
              In the results, it is usually higher.
* market_gft = Market GFT = gain-from-trade in the auction, not including auctioneer.
* market_gft_ratio = Market %GFT = market_gft / optimal_gft * 100%.
              Theoretically it should be at least 1 - 1/k.
              In the results, it is usually higher.

Recommended: add manually at the beginning of the file the header line:
,recipe,n,k,k+0,OPT_GFT,OPT_GFT+0,McAfee_k',%k',total_gft,%total_gft,market_gft,market_%gft,McAfee_Without_Heuristic_k',%k',total_gft,%total_gft,market_gft,market_%gft,SBB_External_Competition_k',%k',gft,%gft,market_gft,market_%gft,SBB_Ascending_Prices_k,%k',gft,%gft,market_gft,market_%gft

Author: Dvir Gilor
Since:  2020-08

"""


from markets import Market
from agents import AgentCategory

from tee_table.tee_table import TeeTable
from collections import OrderedDict
from get_stocks_data import getStocksPricesShuffled
import random

def experiment(results_csv_file:str, auction_functions:list, auction_names:str, recipe:tuple, nums_of_agents=None,
               stocks_prices:list=None, stock_names:list=None, num_of_iterations=1000, run_with_stock_prices=True,
               report_diff=False):
    """
    Run an experiment similar to McAfee (1992) experiment on the given auction.
    :param results_csv_file: the experiment result file.
    :param auction_functions: list of functions for executing the auction under consideration.
    :param auction_names: titles of the experiment, for printouts.
    :param recipe: can be any vector of ones, e.g. (1,1,1), for our trade-reduction mechanism, or any vector of positive integers for our ascending-auction mechanism.
    :param stocks_prices: list of prices for each stock and each agent.
    :param stock_names: list of stocks names which prices are belongs, for naming only.
    """
    TABLE_COLUMNS = ["iterations", "stockname", "recipe", "numpossibletrades", "optimalcount", "gftratioformula",
                     "optimalcountwithgftzero", "optimalgft", "optimalgftwithgftzero"]
    AUCTION_COLUMNS = ["count", "countratio", "totalgft", "totalgftratio",
                       "marketgft", "marketgftratio"]

    if stocks_prices is None:
        (stocks_prices, stock_names) = getStocksPricesShuffled()
    column_names = TABLE_COLUMNS
    column_names += [auction_name + column for auction_name in auction_names for column in AUCTION_COLUMNS]
    results_table = TeeTable(column_names, results_csv_file)
    recipe_str = ":".join(map(str,recipe))
    recipe_sum = sum(recipe)
    recipe_sum_for_buyer = (recipe_sum-recipe[0])/recipe[0]
    if nums_of_agents is None:
        nums_of_agents = [10000000]
    #print(nums_of_agents)
    total_results = {}
    for num_of_agents_per_category in nums_of_agents:
        total_results[str(num_of_agents_per_category)] = []
    #print(total_results)
    for i in range(len(stocks_prices)):
        stock_prices = stocks_prices[i]
        for num_of_possible_ps in nums_of_agents:
            for iteration in range(num_of_iterations):
                categories = []
                if run_with_stock_prices:
                    while len(stock_prices) < num_of_possible_ps * recipe_sum:
                        stock_prices = stock_prices + stock_prices
                    random.shuffle(stock_prices)
                    index = 0
                    for category in recipe:
                        next_index = index + num_of_possible_ps * category
                        price_sign = recipe_sum_for_buyer if index == 0 else -1
                        #price_value_multiple = -1 * buyer_agent_count if index > 0 else recipe_sum - buyer_agent_count
                        categories.append(AgentCategory("agent", [int(price*price_sign) for price in stock_prices[index:next_index]]))
                        index = next_index
                else: #prices from random.
                    for index in range(len(recipe)):
                    #for category in recipe:
                        min_value = -100000 if index > 0 else recipe_sum_for_buyer
                        max_value = -1 if index > 0 else 100000 * recipe_sum_for_buyer
                        categories.append(AgentCategory.uniformly_random("agent", num_of_possible_ps*recipe[index],
                                                                         min_value, max_value))
                market = Market(categories)
                (optimal_trade, _) = market.optimal_trade(ps_recipe=list(recipe), max_iterations=10000000, include_zero_gft_ps=False)
                optimal_count = optimal_trade.num_of_deals()
                optimal_gft = optimal_trade.gain_from_trade()
                (optimal_trade_with_gft_zero, _) = market.optimal_trade(ps_recipe=list(recipe), max_iterations=10000000)
                optimal_count_with_gft_zero = optimal_trade_with_gft_zero.num_of_deals()
                optimal_gft_with_gft_zero = optimal_trade_with_gft_zero.gain_from_trade()

                results = [("iterations", num_of_iterations),
                           ("stockname", stock_names[i]),
                           ("recipe", recipe_str),
                           ("numpossibletrades", int(num_of_possible_ps)),
                           ("optimalcount", optimal_count),
                           ("gftratioformula", (optimal_count - 1) * 100 / (optimal_count if min(recipe) == max(recipe) and recipe[0] == 1 else optimal_count + 1) if optimal_count > 1 else 0),
                           ("optimalcountwithgftzero", optimal_count_with_gft_zero),
                           ("optimalgft", optimal_gft),
                           ("optimalgftwithgftzero", optimal_gft_with_gft_zero)]
                for auction_index in range(len(auction_functions)):
                    auction_trade = auction_functions[auction_index](market, recipe)
                    count = auction_trade.num_of_deals()
                    total_gft = auction_trade.gain_from_trade(including_auctioneer=True)
                    market_gft = auction_trade.gain_from_trade(including_auctioneer=False)
                    auction_name = auction_names[auction_index]
                    results.append((auction_name + "count", auction_trade.num_of_deals()))
                    if auction_names[auction_index] != "SBBExternalCompetition":
                        results.append((auction_name + "countratio",
                                        0 if optimal_count==0 else (count / optimal_count_with_gft_zero) * 100))
                        results.append((auction_name + "totalgft", total_gft))
                        results.append((auction_name + "totalgftratio", 0 if optimal_gft==0 else total_gft / optimal_gft_with_gft_zero*100))
                        results.append((auction_name + "marketgft", market_gft))
                        results.append((auction_name + "marketgftratio",
                                        0 if optimal_gft == 0 else market_gft / optimal_gft_with_gft_zero * 100))
                    else:
                        results.append((auction_name + "countratio",
                                        0 if optimal_count==0 else (count / optimal_count) * 100))
                        results.append((auction_name + "totalgft", total_gft))
                        results.append((auction_name + "totalgftratio", 0 if optimal_gft==0 else total_gft / optimal_gft*100))
                        results.append((auction_name + "marketgft", market_gft))
                        results.append((auction_name + "marketgftratio",
                                        0 if optimal_gft == 0 else market_gft / optimal_gft * 100))
                #We check which auction did better and print the market and their results.
                if report_diff:
                    gft_to_compare = -1
                    k_to_compare = -1
                    gft_found = False
                    k_found = False
                    for (label, value) in results:
                        if 'SBB' in label:
                            if gft_found is False and label.endswith('totalgft'):
                                if gft_to_compare < 0:
                                    gft_to_compare = value
                                elif gft_to_compare != value:
                                    with open('diff_in_mechanisms_gft2.txt', 'a') as f:
                                        f.write('There is diff in gft between two auctions: ' + str(gft_to_compare) + ' ' + str(value) + '\n')
                                        f.write(str(results) + '\n')
                                        if num_of_possible_ps < 10:
                                            f.write(str(market) + '\n')
                                    gft_found = True
                            elif k_found is False and label.endswith('count'):
                                if k_to_compare < 0:
                                    k_to_compare = value
                                elif k_to_compare != value:
                                    with open('diff_in_mechanisms_k2.txt', 'a') as f:
                                        f.write('There is diff in gft between two auctions: ' + str(k_to_compare) + ' ' + str(value) + '\n')
                                        f.write(str(results) + '\n')
                                        if num_of_possible_ps < 10:
                                            f.write(str(market) + '\n')
                                    k_found = True
                #results_table.add(OrderedDict(results))
                #print(results)
                if len(total_results[str(num_of_possible_ps)]) == 0:
                    total_results[str(num_of_possible_ps)] = results[0:len(results)]
                else:
                    sum_result = total_results[str(num_of_possible_ps)]
                    for index in range(len(results)):
                        if index > 3:
                            sum_result[index] = (results[index][0], sum_result[index][1] + results[index][1])
            #print(total_results)
        print(stock_names[i], end=',')
        #break
    print()
    division_number = num_of_iterations * len(stocks_prices)
    #division_number = num_of_iterations
    for num_of_possible_ps in nums_of_agents:
        results = total_results[str(num_of_possible_ps)]
        for index in range(len(results)):
            if 'gftratio' in results[index][0]:
                results[index] = (results[index][0], padding_zeroes(results[index][1] / division_number, 3))
            elif index > 3:
                results[index] = (results[index][0], padding_zeroes(results[index][1] / division_number, 2))
            elif index == 1:
                results[index] = (results[index][0], 'Average')
        #print(results)
        results_table.add(OrderedDict(results))
    results_table.done()


def padding_zeroes(result, num_digits:int):
    str_result = str(result)
    str_result += ("0" * num_digits) if '.' in str_result else '.' + ("0" * num_digits)
    return str_result[0 : str_result.index('.') + num_digits + 1]
