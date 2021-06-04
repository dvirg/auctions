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
from tree_calculations import get_agents_analyze, get_children_counts
from ascending_auction_recipetree_integer_protocol import budget_balanced_ascending_auction
from ascending_auction_recipetree_protocol import TradeWithMultipleRecipes
from recipetree_integer import RecipeTree

def experiment(results_csv_file: str, recipe: list, value_ranges:list, nums_of_agents:list, num_of_iterations:int,
               agent_counts:list, agent_values:list, recipe_tree_agent_counts: list):
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
    TABLE_COLUMNS = ["iterations", "recipe", "numofagents",
                     "meanoptimalcount", "meanoptimalkmin", "meanoptimalkmax","gftformula",
                     "meanauctioncount", "countratio",
                     "meanoptimalgft", "meanauctiontotalgft", "totalgftratio"]
    print('recipe:', recipe)
    ROUND = 5
    results_table = TeeTable(TABLE_COLUMNS, results_csv_file)
    recipe_str = str(recipe).replace(',', '-')
    for i in range(len(nums_of_agents)):
        sum_optimal_count = sum_auction_count = sum_optimal_kmin = sum_optimal_kmax = 0  # count the number of deals done in the optimal vs. the actual auction.
        sum_optimal_gft = sum_auction_total_gft = sum_auction_market_gft = 0
        for iteration in range(num_of_iterations):
            #if iteration % 10000 == 0:
            #    print('iteration:', iteration)
            agents = []
            for category in range(len(recipe_tree_agent_counts)):
                sign = 0 if category == 0 else 1
                agents.append(AgentCategory.uniformly_random("agent", int(nums_of_agents[i]*agent_counts[category]),
                                                             value_ranges[sign][0]*agent_values[category],
                                                             value_ranges[sign][1]*agent_values[category]))
                #agents.append(AgentCategory.uniformly_random("agent", nums_of_agents[i], value_ranges[sign][0], value_ranges[sign][1]))
            market = Market(agents)
            #print(agents)
            recipe_tree = RecipeTree(market.categories, recipe, recipe_tree_agent_counts)
            optimal_trade, optimal_count, optimal_gft, kmin, kmax = recipe_tree.optimal_trade_with_counters()
            #print('optimal trade:', optimal_trade, optimal_count, optimal_gft)
            auction_trade = budget_balanced_ascending_auction(market, recipe, recipe_tree_agent_counts)
            auction_count = auction_trade.num_of_deals()
            gft = auction_trade.gain_from_trade()
            if optimal_count > 0 and gft < optimal_gft * (kmin - 1)/(kmin + 2):
                #the auction count is less more than 1 than the optimal count.
                print('Warning GFT!!!', 'optimal_count:', optimal_count, 'auction_count:', auction_count,
                      'num_of_possible_ps:', nums_of_agents[i], 'optimal_gft:', optimal_gft, 'gft:', gft, 'lower bound:', optimal_gft * (1 - 1/optimal_count))
                if nums_of_agents[i] < 20:
                    print(market.categories)

            sum_optimal_count += optimal_count
            sum_auction_count += auction_count

            sum_optimal_kmin += kmin
            sum_optimal_kmax += kmax

            sum_optimal_gft += optimal_gft
            sum_auction_total_gft += gft

            #if auction_count < optimal_count - 2:
                #the auction count is less more than 1 than the optimal count.
                #print('Warning!!!', 'optimal_count:', optimal_count, 'auction_count:', auction_count, 'num_of_possible_ps:', nums_of_agents[i])
                #if nums_of_agents[i] < 10:
                #    print(market.categories)

        # print("Num of times {} attains the maximum GFT: {} / {} = {:.2f}%".format(title, count_optimal_gft, num_of_iterations, count_optimal_gft * 100 / num_of_iterations))
        # print("GFT of {}: {:.2f} / {:.2f} = {:.2f}%".format(title, sum_auction_gft, sum_optimal_gft, 0 if sum_optimal_gft==0 else sum_auction_gft * 100 / sum_optimal_gft))
        kmin_mean = sum_optimal_kmin/num_of_iterations
        results_table.add(OrderedDict([
            ("iterations", num_of_iterations),
            ("recipe", recipe_str),
            ("numofagents", nums_of_agents[i]),
            ("meanoptimalcount", round(sum_optimal_count/num_of_iterations,ROUND)),
            ("meanoptimalkmin", kmin_mean),
            ("meanoptimalkmax", round(sum_optimal_kmax/num_of_iterations,ROUND)),
            ("gftformula", round((kmin_mean - 1)/(kmin_mean + 1)*100,ROUND) if (kmin_mean - 1)/(kmin_mean + 1) > 0 else 0),
            ("meanauctioncount", round(sum_auction_count/num_of_iterations,ROUND)),
            ("countratio", 0 if sum_optimal_count==0 else round((sum_auction_count / sum_optimal_count) * 100, ROUND)),
            ("meanoptimalgft", round(sum_optimal_gft/num_of_iterations,ROUND)),
            ("meanauctiontotalgft", round(sum_auction_total_gft/num_of_iterations,ROUND)),
            ("totalgftratio", 0 if sum_optimal_gft==0 else round(sum_auction_total_gft / sum_optimal_gft*100, ROUND)),
        ]))
    results_table.done()
