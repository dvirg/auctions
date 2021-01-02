#!python3

"""
Simulation experiment for our AAAI 2020 paper, with recipes that are vectors of ones.
Comparing McAfee's double auction to our SBB auctions.

Since:  2019-11
Author: Erel Segal-Halevi

"""

from experiment import  experiment

from mcafee_protocol import mcafee_trade_reduction
from trade_reduction_protocol import budget_balanced_trade_reduction
from ascending_auction_protocol import budget_balanced_ascending_auction
import sys

results_file = "results/experiment_sbb_with_vectors_of_ones.csv"
iterations = 50000

for num_of_seller_categories in (2,4,8,16):
    num_of_categories = num_of_seller_categories+1
    experiment(results_file,budget_balanced_ascending_auction, "SBB Ascending Prices", recipe=num_of_categories*(1,),
               value_ranges   = [(1, 1000*num_of_seller_categories)] + [(-1000,1)]*num_of_seller_categories,
               nums_of_agents = (2, 3, 4, 5, 10, 15, 25, 50, 100, 500, 1000),
               num_of_iterations = iterations
               )

    experiment(results_file,budget_balanced_trade_reduction, "SBB External Competition", recipe=num_of_categories*(1,),
               value_ranges   = [(1, 1000*num_of_seller_categories)] + [(-1000,1)]*num_of_seller_categories,
               nums_of_agents = (2, 3, 4, 5, 10, 15, 25, 50, 100, 500, 1000),
               num_of_iterations = iterations
               )
