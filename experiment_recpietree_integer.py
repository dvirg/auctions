#!python3

"""
Simulation experiment for our AAAI 2020 paper, with recipes that are vectors of ones.
Comparing McAfee's double auction to our SBB auctions.
With using stock market real data.

Since:  2020-08
Author: Dvir Gilor

"""

import experiment_ascending_auction_recipetree_integer_stocks

import experiment_ascending_auction_recipetree_integer_random

from os import listdir
from os.path import isfile, join
results_file = "results/experiment_recipetree"

file_index = "4"
nums_of_agents = [2, 4, 6, 10, 16, 26, 50, 100, 500, 1000, 2000, 5000, 10000, 20000, 50000,100000, 200000, 500000, 1000000]

print("\n\n###### TEST MULTI RECIPE AUCTION WITH 2 paths: [(1,2,0,0),(1,0,1,2]")

iterations = 10000
prices = [[[400, 300, 200, 100],[-1, -11],[-2, -22],[-3, -33],[-4, -44],[-5, -55],[-6, -66]]]

recipes_111 = [1, [2, [0, None]]] # buyer <- sellerB <- sellerA; [1,1,1]
recipes_4paths = [0, [1, [2, None, 3, None], 4, [5, None, 6, None]]]
recipe_paper_start = [0, [6, [2, None], 3, [4, [5, None]]]]

recipe_paper_example = [0, [1, None, 2, [3, None]]]

recipes = [recipe_paper_example] #recipes_111, recipes_4paths, recipe_paper_example, recipe_paper_start]

num_stocks = len([name for name in listdir('stocks') if isfile(join('stocks', name))])
print('num stocks:', num_stocks)

run_random = True #False #
run_binary = True #False #
for recipe in recipes:
    if run_random:
        experiment_ascending_auction_recipetree_integer_random.experiment(results_file + "_" + str(iterations) + "_integer_random" + file_index + ".csv",
                                                                  recipe=recipe,
                                                                  value_ranges   = [(1,1000),(-1000,-1)],
                                                                  nums_of_agents = (2, 4, 6, 10, 16, 26, 50, 100, 500, 1000, 2000),
                                                                  num_of_iterations = iterations,#5000,
                                                                  agent_counts = [1,1,1,1],#[2,2,1,2],#
                                                                  agent_values = [1,1,1,1],#[6,3,2,2],#
                                                                  recipe_tree_agent_counts = [1, 2, 1, 2],
                                                                  num_recipes=2
                                                                  )
        # experiment_ascending_auction_recipetree_integer_random.experiment(results_file + "_random.csv",
        #                                                           recipe=recipes_4paths, #recipe,
        #                                                           value_ranges   = [(1,1000),(-1000,-1)],
        #                                                           nums_of_agents = (2, 4, 6, 10, 16, 26, 50, 100, 500, 1000, 2000, 5000),
        #                                                           num_of_iterations = iterations,
        #                                                           agent_counts = [1,1,1,1,1,1,1],#[1,1,1,1],#[1,2,1,2],
        #                                                           agent_values = [1,1,1,1,1,1,1], #[3,1.5,1,1],
        #                                                           recipe_tree_agent_counts = [1, 2, 2, 1, 1, 2,1] # [1, 2, 1, 2]
        #                                                           )

        #else:
    if run_random:
        experiment_ascending_auction_recipetree_integer_stocks.experiment(results_file + "_" + str(iterations) + "_integer_stock" + file_index + ".csv",
                                                                  recipe=recipe,
                                                                  nums_of_agents = (2, 4, 6, 10, 16, 26, 50, 100, 500, 1000, 2000),
                                                                  num_of_iterations = round(iterations / num_stocks),#150,
                                                                  agent_counts = [1,1,1,1],#[1,2,1,2],
                                                                  agent_values = [1,-1,-1,-1],#[6,-3,-2,-2],
                                                                  recipe_tree_agent_counts = [1, 2, 1, 2],
                                                                  num_recipes=2
                                                                  )

    if run_binary:
        experiment_ascending_auction_recipetree_integer_random.experiment(results_file + "_" + str(iterations) + "_binary_random" + file_index + ".csv",
                                                                  recipe=recipe,
                                                                  value_ranges   = [(1,1000),(-1000,-1)],
                                                                  nums_of_agents = (2, 4, 6, 10, 16, 26, 50, 100, 500, 1000, 2000),
                                                                  num_of_iterations = iterations,#5000,
                                                                  agent_counts = [1,1,1,1],#[2,2,1,2],#
                                                                  agent_values = [1,1,1,1],#[6,3,2,2],#
                                                                  recipe_tree_agent_counts = [1, 1, 1, 1],
                                                                  num_recipes=2
                                                                  )
        # experiment_ascending_auction_recipetree_integer_random.experiment(results_file + "_random.csv",
        #                                                           recipe=recipes_4paths, #recipe,
        #                                                           value_ranges   = [(1,1000),(-1000,-1)],
        #                                                           nums_of_agents = (2, 4, 6, 10, 16, 26, 50, 100, 500, 1000, 2000, 5000),
        #                                                           num_of_iterations = iterations,
        #                                                           agent_counts = [1,1,1,1,1,1,1],#[1,1,1,1],#[1,2,1,2],
        #                                                           agent_values = [1,1,1,1,1,1,1], #[3,1.5,1,1],
        #                                                           recipe_tree_agent_counts = [1, 2, 2, 1, 1, 2,1] # [1, 2, 1, 2]
        #                                                           )

        experiment_ascending_auction_recipetree_integer_stocks.experiment(results_file + "_" + str(iterations) + "_binary_stock" + file_index + ".csv",
                                                                  recipe=recipe,
                                                                  nums_of_agents = (2, 4, 6, 10, 16, 26, 50, 100, 500, 1000, 2000),
                                                                  num_of_iterations = round(iterations / num_stocks),#150,
                                                                  agent_counts = [1,1,1,1],#[1,2,1,2],
                                                                  agent_values = [1,-1,-1,-1],#[6,-3,-2,-2],
                                                                  recipe_tree_agent_counts = [1, 1, 1, 1],
                                                                  num_recipes=2
                                                                  )

