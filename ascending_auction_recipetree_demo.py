#!python3

"""
Demonstration of a multiple-clock strongly-budget-balanced ascending auction
for a multi-lateral market with a recipe tree

Author: Erel Segal-Halevi
Since:  2020-08
"""

from markets import Market
from agents import AgentCategory
import ascending_auction_recipetree_protocol
from ascending_auction_recipetree_protocol import budget_balanced_ascending_auction
import prices

import logging
ascending_auction_recipetree_protocol.logger.setLevel(logging.INFO)
prices.logger.setLevel(logging.INFO)

# print("\n\n###### TEST MULTI RECIPE AUCTION WITH A SINGLE PATH: [1,1,1]")
# market = Market([
#     AgentCategory("buyer", [9, 8]),
#     AgentCategory("sellerA", [-1, -2]),
#     AgentCategory("sellerB", [-4, -3]),
# ])
# recipes_111 = [1, [2, [0, None]]] # buyer <- sellerB <- sellerA; [1,1,1]
# print(budget_balanced_ascending_auction(market, recipes_111))

# print("\n\n###### TEST MULTI RECIPE AUCTION WITH TWO EQUIVALENT RECIPES: [1,0,1] [1,1,0]")
# market = Market([
#     AgentCategory("buyer", [17, 14, 13, 9, 6]),
#     AgentCategory("sellerA", [-1, -3, -4, -5, -8, -10]),
#     AgentCategory("sellerB", [-2, -7, -11]),
# ])
# recipes_110_101 = [0, [1, None, 2, None]]  # buyer -> sellerA, buyer -> sellerB;   [[1, 1, 0], [1, 0, 1]]
# print(budget_balanced_ascending_auction(market, recipes_110_101))


# print("\n\n###### TEST MULTI RECIPE AUCTION WITH TWO DIFFERENT RECIPES: [1,1,0,0] [1,0,1,1]")
# market = Market([
#     AgentCategory("buyer", [17, 14, 13, 9, 6, 2]),
#     AgentCategory("seller", [-4, -5, -8, -10]),
#     AgentCategory("producerA", [-1, -3, -5]),
#     AgentCategory("producerB", [-1, -4, -6]),
# ])
# recipes_1100_1011 = [0, [1, None, 2, [3, None]]]  # buyer -> seller, buyer -> producerA -> producerB;   [[1,1,0,0],[1,0,1,1]]
# print(budget_balanced_ascending_auction(market, recipes_1100_1011))


# print("\n\n###### TEST MULTI RECIPE AUCTION - RICA'S EXAMPLE")
# market = Market([
#     AgentCategory("buyer",   [20, 19, 18, 17, 16, 15]),
#     AgentCategory("seller",   [-1, -2, -5, -6, -9, -10]),
#     AgentCategory("producerA", [-4, -8]),
#     AgentCategory("producerB", [-3, -7]),
# ])
# print(budget_balanced_ascending_auction(market, recipes_1100_1011))

import sys, os; sys.path.insert(0, os.path.abspath('..'))


print("\n\n###### TEST MULTI RECIPE AUCTION - 4 PATHS")

market = Market([
    AgentCategory("C0", [400, 300, 200, 100]),
    AgentCategory("C1", [-1, -11]),
    AgentCategory("C2", [-2, -22]),
    AgentCategory("C3", [-3, -33]),
    AgentCategory("C4", [-4, -44]),
    AgentCategory("C5", [-5, -55]),
    AgentCategory("C6", [-6, -66]),
])
recipes_4paths = [0, [1, [2, None, 3, None], 4, [5, None, 6, None]]]
# The recipes are:
#     1,1,1,0,0,0,0   [C0, C1, C2]
#     1,1,0,1,0,0,0   [C0, C1, C3]
#     1,0,0,0,1,1,0   [C0, C4, C5]
#     1,0,0,0,1,0,1   [C0, C4, C6]

print(budget_balanced_ascending_auction(market, recipes_4paths))
