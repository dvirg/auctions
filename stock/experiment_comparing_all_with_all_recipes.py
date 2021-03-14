#!python3

"""
Simulation experiment for our AAAI 2020 paper, recipe (1,1).
Comparing McAfee's double auction to our SBB auctions.
With using stock market real data.

Since:  2020-08
Author: Dvir Gilor

"""

from experiment import experiment

from mcafee_protocol import mcafee_trade_reduction
from trade_reduction_protocol import budget_balanced_trade_reduction
from ascending_auction_protocol import budget_balanced_ascending_auction
from experiment_compare_iterations_autions import experiment

from functools import partial
mcafee_without_heuristic = partial(mcafee_trade_reduction, price_heuristic=False)
nums_of_agents = (2, 3, 4, 5, 10, 15, 25, 50, 100, 500, 1000)#, 2000, 5000)
sbb_names = ["SBBExternalCompetition", "SBBAscendingPrices"]
sbb_functions = [budget_balanced_trade_reduction, budget_balanced_ascending_auction]
mcafee_functions = [mcafee_trade_reduction, mcafee_without_heuristic]
mcafee_names = ["McAfee", "McAfeeWithoutHeuristic"]
num_of_iterations = 1000#
recipes = [(4,3,2,1), (3,2,1), (2,1), (2,2), (2,3), (3,3),
           #(1,2,2), (2,2,2), (1,2,3), (4,2,6),
           (1,2,3,4)]
#recipes = []
for recipe in recipes:
    experiment("results/experiment_sbb_with_vectors_of_multi_stock_" + str(recipe).replace(' ', '') + ".csv",
               sbb_functions,
               sbb_names,
               recipe=recipe,
               nums_of_agents=nums_of_agents,
               num_of_iterations=num_of_iterations)

    experiment("results/experiment_sbb_with_vectors_of_multi_random_" + str(recipe).replace(' ', '') + ".csv",
               sbb_functions,
               sbb_names,
               recipe=recipe,
               nums_of_agents=nums_of_agents,
               run_with_stock_prices=False,
               num_of_iterations=num_of_iterations)

if False:
    exit(0)
experiment("results/experiment_comparing_mcafee_to_sbb_stock.csv",
           mcafee_functions + sbb_functions,
           mcafee_names + sbb_names,
           recipe=(1,1),
           nums_of_agents = nums_of_agents,
           num_of_iterations=num_of_iterations)

experiment("results/experiment_comparing_mcafee_to_sbb_random.csv",
           mcafee_functions + sbb_functions,
           mcafee_names + sbb_names,
           recipe=(1,1),
           nums_of_agents = nums_of_agents,
           run_with_stock_prices=False,
           num_of_iterations=num_of_iterations)

for num_of_seller_categories in (2,4,8,16):
    num_of_categories = num_of_seller_categories+1
    experiment("results/experiment_sbb_with_vectors_of_ones_stock_shuffled_" + str(num_of_categories) + '.csv',
               sbb_functions,
               sbb_names,
               recipe=num_of_categories*(1,),
               nums_of_agents = nums_of_agents,
               num_of_iterations=num_of_iterations)

    experiment("results/experiment_sbb_with_vectors_of_ones_random_shuffled_" + str(num_of_categories) + '.csv',
               sbb_functions,
               sbb_names,
               recipe=num_of_categories*(1,),
               nums_of_agents = nums_of_agents,
               run_with_stock_prices=False,
               num_of_iterations=num_of_iterations)

for num_of_seller_categories in (2,4,8,16):
    experiment("results/experiment_sbb_with_vectors_of_multi_stock_(1," + str(num_of_seller_categories) + ").csv",
               sbb_functions,
               sbb_names,
               recipe=(1, num_of_seller_categories),
               nums_of_agents=nums_of_agents,
               num_of_iterations=num_of_iterations)

    experiment("results/experiment_sbb_with_vectors_of_multi_random_(1," + str(num_of_seller_categories) + ").csv",
               sbb_functions,
               sbb_names,
               recipe=(1, num_of_seller_categories),
               nums_of_agents=nums_of_agents,
               run_with_stock_prices=False,
               num_of_iterations=num_of_iterations)


