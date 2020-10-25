#!python3

"""
Simulation experiment for our AAAI 2020 paper, with recipes that are vectors of ones.
Comparing McAfee's double auction to our SBB auctions.
With using stock market real data.

Since:  2020-08
Author: Dvir Gilor

"""

from trade_reduction_protocol import budget_balanced_trade_reduction
from ascending_auction_protocol import budget_balanced_ascending_auction
from experiment_compare_iterations_autions_without_mcafee import experiment

results_file = "results/experiment_sbb_with_vectors_of_multi_stock"

recipes = [(1,2), (1,4), (1,8), (1,16),
           (2,2), (2,3), (3,3),
           (1,2,2), (2,2,2), (1,2,3), (4,2,6),
           (1,2,3,4), (4,3,2,1)]
nums_of_agents = (2, 3, 4, 5, 10, 15, 25, 50, 100, 500, 1000, 2000, 5000, 10000, 20000, 50000,
                  100000, 200000, 500000, 1000000)
# recipes = [(1, 2, 3, 4)]
# nums_of_agents = [100]

for recipe in recipes:
    experiment(results_file + str(recipe) + ".csv",
               [budget_balanced_trade_reduction, budget_balanced_ascending_auction],
               ["SBB_External_Competition", "SBB_Ascending_Prices"],
               recipe=recipe,
               nums_of_agents=nums_of_agents)


