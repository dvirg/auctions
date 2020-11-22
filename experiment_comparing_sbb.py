#!python3


"""
A utility for performing simulation experiments on auction mechanisms.
The experiment is similar to the one described by McAfee (1992), Table I (page 448).
In each experiment, we measure the actual vs. the optimal gain-from-trade.

The results are printed to a CSV file. The columns are:

* recipe - (1,1) for McAfee; can be any vector of ones, e.g. (1,1,1), for our trade-reduction mechanism, or any vector of positive integers for our ascending-auction mechanism.
* num_of_agents - n = total number of potential procurement-sets (e.g. if n=100 and recipe=[1,2] then there are 100 buyers and 200 sellers).
* mean_optimal_count - k = number of deals in the optimal trade, averaged over all iterations.
                       Note that k <= n. E.g., there may be 100 buyers and 100 sellers, but only 50 procurement-sets with positive GFT, so k=50.
* mean_auction_count - number of deals done by our auction,  averaged over all iterations.
                       Theoretically, since at most one deal is removed, it should be  either k or k-1.
* count_ratio  = mean_auction_count / mean_optimal_count  * 100%.
* mean_optimal_gft - OPT = gain-from-trade in the optimal trade, 	averaged over all iterations.
* mean_auction_gft - GFT = gain-from-trade in the auction, averaged over all iterations.
* gft_ratio  = mean_auction_gft / mean_optimal_gft * 100%.
              Theoretically it should be at least 1 - 1/k.
              In the results, it is usually higher.

Since:  2020-10
Author: Dvir Gilor

"""


from markets import Market
from agents import AgentCategory
from typing import Callable

from tee_table.tee_table import TeeTable
from collections import OrderedDict
from trade_reduction_protocol import budget_balanced_trade_reduction
from ascending_auction_protocol import budget_balanced_ascending_auction

TABLE_COLUMNS = ["recipe", "external_wins_gft", "tie_gft", "ascending_wins_gft", "external_wins_k", "tie_k", "ascending_wins_k",
                 "external_wins", "tie", "ascending_wins"]

def experiment(results_csv_file:str, recipes:tuple, value_ranges:list, nums_of_agents:list, num_of_iterations:int):
    """
    Run an experiment similar to McAfee (1992) experiment on the given auction.

    :param recipes: list of recipes.
    :param nums_of_agents: a list of the numbers of agents with which to run the experiment.
    :param value_ranges: for each category, a pair (min_value,max_value). The value for each agent in this category is selected uniformly at random between min_value and max_value.
    :param num_of_iterations: how many times to repeat the experiment for each num of agents.
    """
    results_table = TeeTable(TABLE_COLUMNS, results_csv_file)
    for recipe in recipes:
        recipe_str = ":".join(map(str,recipe))
        num_of_categories = len(recipe)
        external_wins_gft = tie_gft = ascending_wins_gft = 0
        external_wins_k = tie_k = ascending_wins_k = 0
        for num_of_agents_per_category in nums_of_agents:
            external_sum_auction_count = ascending_sum_auction_count = 0  # count the number of deals done the ascending auction.
            external_sum_auction_gft = ascending_sum_auction_gft = 0
            agents_recipe_values = [sum(recipe) - recipe[0]] + [recipe[0] for _ in range(1,len(recipe))]
            for _ in range(num_of_iterations):
                market = Market([
                    AgentCategory.uniformly_random("agent", num_of_agents_per_category*recipe[category],
                                                   value_ranges[category][0]*agents_recipe_values[category],
                                                   value_ranges[category][1]*agents_recipe_values[category])
                    for category in range(num_of_categories)
                ])
                (optimal_trade, _) = market.optimal_trade(recipe)
                external_auction_trade = budget_balanced_trade_reduction(market, recipe)
                ascending_auction_trade = budget_balanced_ascending_auction(market, recipe)

                external_sum_auction_count += external_auction_trade.num_of_deals()
                ascending_sum_auction_count += ascending_auction_trade.num_of_deals()

                external_sum_auction_gft += external_auction_trade.gain_from_trade()
                ascending_sum_auction_gft += ascending_auction_trade.gain_from_trade()

            if external_sum_auction_count > ascending_sum_auction_count:
                external_wins_k += 1
            elif external_sum_auction_count == ascending_sum_auction_count:
                tie_k += 1
            else:
                ascending_wins_k += 1

            if external_sum_auction_gft > ascending_sum_auction_gft:
                external_wins_gft += 1
            elif external_sum_auction_gft == ascending_sum_auction_gft:
                tie_gft += 1
            else:
                ascending_wins_gft += 1
        num_agents = len(nums_of_agents)
        results_table.add(OrderedDict((
            ("recipe", recipe),
            ("external_wins_gft", int(external_wins_gft*100 / num_agents)),
            ("tie_gft", int(tie_gft*100 / num_agents)),
            ("ascending_wins_gft", int(ascending_wins_gft*100 / num_agents)),
            ("external_wins_k", int(external_wins_k*100 / num_agents)),
            ("tie_k", int(tie_k*100 / num_agents)),
            ("ascending_wins_k", int(ascending_wins_k*100 / num_agents)),
            ("external_wins", external_wins_gft),
            ("tie", tie_gft),
            ("ascending_wins", ascending_wins_gft),
        )))
    results_table.done()
