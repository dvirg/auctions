#!python3

"""
Simulation experiment for our AAAI 2020 paper, with recipes that are vectors of ones.
Comparing McAfee's double auction to our SBB auctions.
With using stock market real data.

Since:  2020-08
Author: Dvir Gilor

"""

import experiment_ascending_auction_recipetree_stock

import experiment_ascending_auction_recipetree_random

results_file = "results/experiment_recipetree"

nums_of_agents = [2, 4, 6, 10, 16, 26, 50, 100, 500, 1000, 2000, 5000, 10000, 20000, 50000,100000, 200000, 500000, 1000000]

print("\n\n###### TEST MULTI RECIPE AUCTION WITH A SINGLE PATH: [1,1,1]")

iterations = 50000
prices = [[[400, 300, 200, 100],[-1, -11],[-2, -22],[-3, -33],[-4, -44],[-5, -55],[-6, -66]]]

recipes_111 = [1, [2, [0, None]]] # buyer <- sellerB <- sellerA; [1,1,1]
recipes_4paths = [0, [1, [2, None, 3, None], 4, [5, None, 6, None]]]
recipe_paper_start = [0, [6, [2, None], 3, [4, [5, None]]]]

recipe_paper_example = [0, [1, None, 2, [3, None]]]

recipes = [recipe_paper_example] #recipes_111, recipes_4paths, recipe_paper_example, recipe_paper_start]

run_stock = True
for recipe in recipes:
    if run_stock:
        experiment_ascending_auction_recipetree_stock.experiment(results_file + "_stock.csv", recipe=recipe,
                                                                 agent_counts = [1,0.5,0.5,0.5], agent_values = [2,2,1,1],
                                                                 nums_of_agents=nums_of_agents
                                                                 #,
                                                       #stocks_prices=prices,
                                                       #stock_names=["demo"]
                                                       )
    else:
        experiment_ascending_auction_recipetree_random.experiment(results_file + "_random.csv",
                                                                  recipe=recipe,
                                                                  value_ranges   = [(1,1000),(-1000,-1)],
                                                                  nums_of_agents = (2, 4, 6, 10, 16, 26, 50, 100, 500, 1000),
                                                                  num_of_iterations = iterations,
                                                                  agent_counts = [1,0.5,0.5,0.5],
                                                                  agent_values = [2,2,1,1]
                                                                  )


