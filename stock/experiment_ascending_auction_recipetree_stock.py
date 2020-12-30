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
from get_stocks_data import getStocksTreePrices
from tree_calculations import get_agents_analyze
from ascending_auction_recipetree_protocol import budget_balanced_ascending_auction
from ascending_auction_recipetree_protocol import TradeWithMultipleRecipes
from recipetree import RecipeTree

def experiment(results_csv_file: str, recipe: list, agent_counts:list, agent_values:list,
               nums_of_agents:list = None, stocks_prices=None, stock_names=None):
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
    TABLE_COLUMNS = ["stockname", "recipe", "numpossibletrades",
                     "optimalcount", "optimalgft", "auctioncount", "countratio", "gft", "gftratio"]
    print('recipe:', recipe)
    results_table = TeeTable(TABLE_COLUMNS, results_csv_file)
    recipe_str = str(recipe).replace(',', '->')
    category_size_list = get_agents_analyze(recipe)
    if stocks_prices is None:
        (stocks_prices, stock_names) = getStocksTreePrices(recipe, agent_counts, agent_values)

    if nums_of_agents is None:
        nums_of_agents = [10000000]
    total_results = {}
    for num_of_agents_per_category in nums_of_agents:
        total_results[str(num_of_agents_per_category)] = []
    for i in range(len(stock_names)):
        last_iteration = False
        for num_of_agents_per_category in nums_of_agents:
            num_of_possible_ps = min(num_of_agents_per_category, len(stocks_prices[i][0]))
            if last_iteration is True and num_of_possible_ps < num_of_agents_per_category:
                break
            if num_of_possible_ps < num_of_agents_per_category:
                if last_iteration is True:
                    break
                else:
                    last_iteration = True
                    market = Market([AgentCategory("agent", stocks_prices[i][j]) for j in range(len(stocks_prices[i]))])
            else:
                market = Market([AgentCategory("agent", stocks_prices[i][j][0:int(num_of_possible_ps*agent_counts[j])]) for j in range(len(stocks_prices[i]))])
            if num_of_agents_per_category < 10:
                print(market.categories)
            recipe_tree = RecipeTree(market.categories, recipe)
            optimal_trade, optimal_count, optimal_gft = recipe_tree.optimal_trade()
            #print('optimal trade:', optimal_trade, optimal_count, optimal_gft)
            auction_trade = budget_balanced_ascending_auction(market, recipe)
            auction_count = auction_trade.num_of_deals()
            gft = auction_trade.gain_from_trade()
            #if auction_count < optimal_count - 1:
            #    #the auction count is less more than 1 than the optimal count.
            #    print('Warning!!!', 'optimal_count:', optimal_count, 'auction_count:', auction_count, 'num_of_possible_ps:', num_of_possible_ps)
            #    if num_of_possible_ps < 10:
            #        print(market.categories)
            #if optimal_count > 0 and gft < optimal_gft * (1 - 1/optimal_count):
            #    #the auction count is less more than 1 than the optimal count.
            #    print('Warning GFT!!!', 'optimal_count:', optimal_count, 'auction_count:', auction_count,
            #          'num_of_possible_ps:', num_of_possible_ps, 'optimal_gft:', optimal_gft, 'gft:', gft)
            #    if num_of_possible_ps < 20:
            #        print(market.categories)
            if optimal_count < auction_count :
                #the auction count is less more than 1 than the optimal count.
                print('Warning count!!!', 'optimal_count:', optimal_count, 'auction_count:', auction_count,
                      'num_of_possible_ps:', num_of_possible_ps, 'optimal_gft:', optimal_gft, 'gft:', gft)
                if num_of_possible_ps < 20:
                    print(market.categories)
            results = [("stockname", stock_names[i]),
                       ("recipe", recipe_str),
                       ("numpossibletrades", round(num_of_possible_ps)),
                       ("optimalcount", round(optimal_count, 1)),
                       ("optimalgft", round(optimal_gft, 1)),
                       ("auctioncount", round(auction_count,1)),
                       ("countratio", 0 if optimal_count==0 else int(auction_count / optimal_count*100000)/1000),
                       ("gft", round(gft,1)),
                       ("gftratio", 0 if optimal_gft==0 else int(gft / optimal_gft*100000)/1000)
                       ]
            results_table.add(OrderedDict(results))
            if len(total_results[str(num_of_agents_per_category)]) == 0:
                total_results[str(num_of_agents_per_category)] = results[0:len(results)]
            else:
                sum_result = total_results[str(num_of_agents_per_category)]
                for index in range(len(results)):
                    if index > 2:
                        sum_result[index] = (results[index][0], sum_result[index][1] + results[index][1])
    for num_of_agents_per_category in nums_of_agents:
        results = total_results[str(num_of_agents_per_category)]
        for index in range(len(results)):
            if index > 2:
                if 'ratio' in results[index][0]:
                    results[index] = (results[index][0], int(results[index][1]/len(stock_names)*1000)/1000)
                else:
                    results[index] = (results[index][0], round(results[index][1]/len(stock_names),1))
            elif index == 0:
                results[index] = (results[index][0], 'Average')
        results_table.add(OrderedDict(results))
    results_table.done()

