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

Since:  2019-11
Author: Erel Segal-Halevi

"""


from markets import Market
from agents import AgentCategory
from typing import Callable

from tee_table.tee_table import TeeTable
from collections import OrderedDict

TABLE_COLUMNS = ["iterations","auction_name", "recipe", "num_of_agents",
                 "mean_optimal_count", "mean_auction_count", "count_ratio",
                 "mean_optimal_gft", "mean_auction_total_gft", "total_gft_ratio", "mean_auction_market_gft", "market_gft_ratio"]

def experiment(results_csv_file:str, auction_function:Callable, auction_name:str, recipe:tuple, value_ranges:list, nums_of_agents:list, num_of_iterations:int):
    """
    Run an experiment similar to McAfee (1992) experiment on the given auction.

    :param auction_function: the function for executing the auction under consideration.
    :param auction_name: title of the experiment, for printouts.
    :param nums_of_agents: a list of the numbers of agents with which to run the experiment.
    :param value_ranges: for each category, a pair (min_value,max_value). The value for each agent in this category is selected uniformly at random between min_value and max_value.
    :param num_of_iterations: how many times to repeat the experiment for each num of agents.
    """
    results_table = TeeTable(TABLE_COLUMNS, results_csv_file)
    recipe_str = ":".join(map(str,recipe))
    num_of_categories = len(recipe)
    for num_of_agents_per_category in nums_of_agents:
        sum_optimal_count = sum_auction_count = 0  # count the number of deals done in the optimal vs. the actual auction.
        sum_optimal_gft = sum_auction_total_gft = sum_auction_market_gft = 0
        for _ in range(num_of_iterations):
            market = Market([
                AgentCategory.uniformly_random("agent", num_of_agents_per_category*recipe[category], value_ranges[category][0], value_ranges[category][1])
                for category in range(num_of_categories)
            ])
            (optimal_trade, _) = market.optimal_trade(recipe)
            auction_trade = auction_function(market, recipe)

            sum_optimal_count += optimal_trade.num_of_deals()
            sum_auction_count += auction_trade.num_of_deals()

            sum_optimal_gft += optimal_trade.gain_from_trade()
            sum_auction_total_gft += auction_trade.gain_from_trade(including_auctioneer=True)
            sum_auction_market_gft += auction_trade.gain_from_trade(including_auctioneer=False)

        # print("Num of times {} attains the maximum GFT: {} / {} = {:.2f}%".format(title, count_optimal_gft, num_of_iterations, count_optimal_gft * 100 / num_of_iterations))
        # print("GFT of {}: {:.2f} / {:.2f} = {:.2f}%".format(title, sum_auction_gft, sum_optimal_gft, 0 if sum_optimal_gft==0 else sum_auction_gft * 100 / sum_optimal_gft))
        results_table.add(OrderedDict((
            ("iterations", num_of_iterations),
            ("auction_name", auction_name),
            ("recipe", recipe_str),
            ("num_of_agents", num_of_agents_per_category),
            ("mean_optimal_count", round(sum_optimal_count/num_of_iterations,2)),
            ("mean_auction_count", round(sum_auction_count/num_of_iterations,2)),
            ("count_ratio", 0 if sum_optimal_count==0 else int((sum_auction_count / sum_optimal_count) * 10000)/100),
            ("mean_optimal_gft", round(sum_optimal_gft/num_of_iterations,2)),
            ("mean_auction_total_gft", round(sum_auction_total_gft/num_of_iterations,2)),
            ("total_gft_ratio", 0 if sum_optimal_gft==0 else round(sum_auction_total_gft / sum_optimal_gft*100,2)),
            ("mean_auction_market_gft", round(sum_auction_market_gft / num_of_iterations, 2)),
            ("market_gft_ratio", 0 if sum_optimal_gft == 0 else round(sum_auction_market_gft / sum_optimal_gft * 100, 2)),
        )))
    results_table.done()
