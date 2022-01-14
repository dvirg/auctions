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
from tree_calculations import get_agents_analyze, get_children_counts
from ascending_auction_recipetree_integer_protocol import budget_balanced_ascending_auction
from ascending_auction_recipetree_integer_protocol import TradeWithMultipleRecipes
from recipetree_integer import RecipeTree
import random

def experiment(results_csv_file: str, recipe: list, nums_of_agents:list, num_of_iterations:int,
               agent_counts:list, agent_values:list, recipe_tree_agent_counts: list, num_recipes: int):
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
    TABLE_COLUMNS = ["stockname", "recipe", "numofagents",
                     "optimalkmin", "optimalkmax", "gftformula",
                     "optimalcount", "optimalgft", "auctioncount",
                     "auctionkmin", "auctionkmax", "countratio", "gft", "gftratio"]
    print('recipe:', recipe, 'size:', num_recipes)
    GFT_ROUND = 1
    K_ROUND = 2
    RATIO_ROUND = 3
    results_table = TeeTable(TABLE_COLUMNS, results_csv_file)
    recipe_str = str(recipe).replace(',', '->')
    stocks_prices, stock_names = getStocksPricesShuffled()
    sum_agent_counts = sum(agent_counts)
    is_binary = len(set(recipe_tree_agent_counts)) == 1

    total_results = {}
    for num_of_agents_per_category in nums_of_agents:
        total_results[str(num_of_agents_per_category)] = []
    for i in range(len(stock_names)):
        print(stock_names[i], end=' ')
        for num_of_agents_per_category in nums_of_agents:
            # print(num_of_agents_per_category, end=' ')
            if sum_agent_counts * num_of_agents_per_category > len(stocks_prices[i]):
                break

            for iteration in range(num_of_iterations):
                random.shuffle(stocks_prices[i])
                agents = []
                chunk_index = 0
                for category in range(len(agent_counts)):
                    next_chunk_index = chunk_index + num_of_agents_per_category * agent_counts[category]
                    agents.append(AgentCategory("agent", [value * agent_values[category] for value in stocks_prices[i][chunk_index:next_chunk_index]]))
                    chunk_index = next_chunk_index
                # agents.append(AgentCategory.uniformly_random("agent", int(nums_of_agents[i]*agent_counts[category]),
                #                                              value_ranges[sign][0]*agent_values[category],
                #                                              value_ranges[sign][1]*agent_values[category]))
                #agents.append(AgentCategory.uniformly_random("agent", nums_of_agents[i], value_ranges[sign][0], value_ranges[sign][1]))
                market = Market(agents)
                #print(market)
                #print(agents)
                recipe_tree = RecipeTree(market.categories, recipe, recipe_tree_agent_counts)
                optimal_trade, optimal_count, optimal_gft, kmin, kmax, categories_optimal_counters = recipe_tree.optimal_trade_with_counters()
                #print('counters:' + str(categories_counters))
                #print('optimal trade:', optimal_trade, optimal_count, optimal_gft)
                auction_trade = budget_balanced_ascending_auction(market, recipe, recipe_tree_agent_counts)
                auction_count = auction_trade.num_of_deals()
                auction_kmin = auction_trade.min_num_of_deals()
                auction_kmax = auction_trade.max_num_of_deals()
                path_counters = auction_trade.path_counters
                gft = auction_trade.gain_from_trade()
                #print('Compare:', categories_optimal_counters, path_counters)
                for counter in categories_optimal_counters.keys():
                    if categories_optimal_counters[counter] > path_counters[counter] + 1 and False:
                        print(market)
                        print('Compare:', categories_optimal_counters, path_counters)
                        print('Warning counters', str(counter), 'are not in same size!', categories_optimal_counters[counter], '!=', path_counters[counter])
                #for i in range(len(path_counters)):
                #    print('Compare:', categories_optimal_counters, path_counters)
                #if optimal_count > 0 and gft < optimal_gft * (kmin - 1)/(kmin + 2):
                    #the auction count is less more than 1 than the optimal count.
                #    print('Warning GFT!!!', 'optimal_count:', optimal_count, 'auction_count:', auction_count,
                #          'num_of_possible_ps:', nums_of_agents[i], 'optimal_gft:', optimal_gft, 'gft:', gft, 'lower bound:', optimal_gft * (1 - 1/optimal_count))
                #    if nums_of_agents[i] < 20:
                #        print(market.categories)
                results = [("stockname", stock_names[i]),
                           ("recipe", recipe_str),
                           ("numofagents", num_of_agents_per_category),
                           ("optimalcount", optimal_count),
                           ("optimalkmin", kmin),
                           ("optimalkmax", kmax),
                           ("gftformula", 0 if kmin <= num_recipes else (kmin - num_recipes) / (kmin + num_recipes) * 100),
                           ("optimalgft", optimal_gft),
                           ("auctioncount", auction_count),
                           ("auctionkmin", auction_kmin),
                           ("auctionkmax", auction_kmax),
                           ("countratio", 0 if optimal_count == 0 else auction_count / optimal_count * 100),
                           ("gft", gft),
                           ("gftratio", 0 if optimal_gft == 0 else gft / optimal_gft * 100)
                           ]
                # results_table.add(OrderedDict(results))
                if len(total_results[str(num_of_agents_per_category)]) == 0:
                    total_results[str(num_of_agents_per_category)] = results[0:len(results)]
                else:
                    sum_result = total_results[str(num_of_agents_per_category)]
                    for index in range(len(results)):
                        if index > 2:
                            sum_result[index] = (results[index][0], sum_result[index][1] + results[index][1])
    print()
    for num_of_agents_per_category in nums_of_agents:
        results = total_results[str(num_of_agents_per_category)]
        kmin = 0
        for index in range(len(results)):
            if results[index][0] == 'optimalkmin':
                kmin = results[index][1] / len(stock_names) / num_of_iterations
            if index > 2:
                if 'ratio' in results[index][0]:
                   results[index] = (results[index][0], int_round(results[index][1] / len(stock_names) / num_of_iterations, RATIO_ROUND))
                elif 'gft' in results[index][0]:
                   results[index] = (results[index][0], int_round(results[index][1] / len(stock_names) / num_of_iterations / 100, GFT_ROUND))
                else:
                    results[index] = (results[index][0], int_round(results[index][1] / len(stock_names) / num_of_iterations, K_ROUND))
            elif index == 0:
                results[index] = (results[index][0], 'Average')
            if results[index][0] == 'gftformula':
                if is_binary:
                    gft_formula = int_round(0 if kmin <= 1 else (kmin - 1) / kmin * 100, RATIO_ROUND)
                else:
                    gft_formula = int_round(0 if kmin <= num_recipes else (kmin - num_recipes) / (kmin + num_recipes) * 100, RATIO_ROUND)
                results[index] = (results[index][0], gft_formula)

        # results.append(('gftformula', 0 if kmin <= num_recipes else round((kmin - num_recipes) / (kmin + num_recipes) * 100, ROUND)))
        results_table.add(OrderedDict(results))

    results_table.done()

def int_round(number, size):
    if number == 0:
        return '0.' + ('0' * size)
    # power = (10 ** size)
    # rounded = str(int(number * power) / power)
    str_number = str(number)
    round_split = str_number.split('.')
    if len(round_split) == 1:
        return str_number + '.' + ('0' * size)
    elif len(round_split[1]) == size:
        return str_number
    elif len(round_split[1]) > size:
        return round_split[0] + '.' + round_split[1][0:size]
    else:
        return str_number + ('0' * (size - len(round_split[1])))