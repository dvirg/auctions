#!python3

"""
Simulation experiment for our AAAI 2020 paper, with recipes that are vectors of ones.
Comparing McAfee's double auction to our SBB auctions.

Since:  2020-11
Author: Dvir Gilor

"""

from experiment_comparing_sbb import experiment

from mcafee_protocol import mcafee_trade_reduction
from trade_reduction_protocol import budget_balanced_trade_reduction
from ascending_auction_protocol import budget_balanced_ascending_auction
import sys

results_file = "results/comparing_sbbs.csv"
iterations = 10

recipes = [(1,2),(1,3),(1,4),(1,8),(1,16),(2,2),(2,3),(1,1,1),(2,2,2),(1,2,3,4),(1,2,3),(1,2,2)]
# recipes += [(i, j) for i in range(1, 10) for j in range(16, 17)]
# recipes += [(i, j, k) for i in range(1, 10) for j in range(1, 10) for k in range(1, 10)]
# recipes += [(i, j, k, m) for i in range(1, 5) for j in range(1, 5) for k in range(1, 5) for m in range(1, 5)]
# recipes += [(i, j, k, m, o) for i in range(1, 5) for j in range(1, 5) for k in range(1, 5) for m in range(1, 5) for o in range(1, 5)]
nums_of_agents = (2, 3, 4, 5, 10, 15, 25, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000)#, 1000, 2000, 5000)#, 10000, 20000, 50000, 100000, 200000, 500000)

experiment(results_file, recipes=recipes, value_ranges   = [(1, 1000)] + [(-1000,1)]*4,
           nums_of_agents = nums_of_agents, num_of_iterations = iterations
           )
