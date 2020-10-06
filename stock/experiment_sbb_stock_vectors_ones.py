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

results_file = "results/experiment_sbb_with_vectors_of_ones_stock.csv"

for num_of_seller_categories in (2,4,8,16):
    num_of_categories = num_of_seller_categories+1
    experiment(results_file,
               [budget_balanced_trade_reduction, budget_balanced_ascending_auction],
               ["SBB_External_Competition", "SBB_Ascending_Prices"],
               recipe=num_of_categories*(1,),
               nums_of_agents = (2, 3, 4, 5, 10, 15, 25, 50, 100, 500, 1000, 2000, 5000, 10000, 20000, 50000,
                                 100000, 200000, 500000, 1000000))


