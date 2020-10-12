#!python3

"""
function budget_balanced_ascending_auction
Implementation of a multiple-clock strongly-budget-balanced ascending auction for a multi-lateral market.

Author: Erel Segal-Halevi
Since:  2019-08
"""

from agents import AgentCategory, EmptyCategoryException, MAX_VALUE
from markets import Market
from trade import TradeWithSinglePrice
import prices
from prices import AscendingPriceVector, PriceStatus

import math, logging, sys
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
# logger.setLevel(logging.INFO)
# To enable tracing, set logger.setLevel(logging.INFO)


def budget_balanced_ascending_auction(market:Market, ps_recipe: list, max_iterations=999999999)->TradeWithSinglePrice:
    """
    Calculate the trade and prices using generalized-ascending-auction.
    :param market:   contains a list of k categories, each containing several agents.
    :param ps_recipe:  a list of integers, one integer per category.
                       Each integer i represents the number of agents of category i
                       that should be in each procurement-set.
    :return: Trade object, representing the trade and prices.

    >>> # ONE BUYER, ONE SELLER

    >>> market = Market([AgentCategory("buyer", [9.,8.]),  AgentCategory("seller", [-4.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, [1,1]))
    Traders: [buyer: [9.0, 8.0], seller: [-4.0]]
    No trade

    >>> market = Market([AgentCategory("seller", [-4.]), AgentCategory("buyer", [9.,8.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, [1,1]))
    Traders: [seller: [-4.0], buyer: [9.0, 8.0]]
    seller: [-4.0]: all 1 agents trade and pay -8.0
    buyer: [9.0]: all 1 agents trade and pay 8.0

    >>> market = Market([AgentCategory("buyer", [9.,8.]),  AgentCategory("seller", [-4.,-3.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, [1,1]))
    Traders: [buyer: [9.0, 8.0], seller: [-3.0, -4.0]]
    buyer: [9.0]: all 1 agents trade and pay 8.0
    seller: [-3.0, -4.0]: random 1 out of 2 agents trade and pay -8.0

    >>> # ONE BUYER, ONE SELLER, ONE MEDIATOR

    >>> market = Market([AgentCategory("seller", [-4.,-3.]), AgentCategory("buyer", [9.,8.]), AgentCategory("mediator", [-1.,-2.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, [1,1,1]))
    Traders: [seller: [-3.0, -4.0], buyer: [9.0, 8.0], mediator: [-1.0, -2.0]]
    seller: [-3.0]: all 1 agents trade and pay -4.0
    buyer: [9.0]: all 1 agents trade and pay 8.0
    mediator: [-1.0, -2.0]: random 1 out of 2 agents trade and pay -4.0

    >>> market = Market([AgentCategory("buyer", [9.,8.,7.]), AgentCategory("mediator", [-1.,-2.,-3.]), AgentCategory("seller", [-4.,-3.,-2.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, [1,1,1]))
    Traders: [buyer: [9.0, 8.0, 7.0], mediator: [-1.0, -2.0, -3.0], seller: [-2.0, -3.0, -4.0]]
    buyer: [9.0, 8.0]: all 2 agents trade and pay 7.0
    mediator: [-1.0, -2.0]: all 2 agents trade and pay -3.0
    seller: [-2.0, -3.0, -4.0]: random 2 out of 3 agents trade and pay -4.0


    >>> # ONE BUYER, TWO SELLERS

    >>> market = Market([AgentCategory("buyer", [9., 8., 7., 6.]),  AgentCategory("seller", [-6., -5., -4.,-3.,-2.,-1.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, [1,2]))
    Traders: [buyer: [9.0, 8.0, 7.0, 6.0], seller: [-1.0, -2.0, -3.0, -4.0, -5.0, -6.0]]
    buyer: [9.0]: all 1 agents trade and pay 8.0
    seller: [-1.0, -2.0, -3.0, -4.0]: random 2 out of 4 agents trade and pay -4.0

    >>> market = Market([AgentCategory("seller", [-4.,-3.,-2.,-1.]), AgentCategory("buyer", [9.,8.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, [2,1]))
    Traders: [seller: [-1.0, -2.0, -3.0, -4.0], buyer: [9.0, 8.0]]
    seller: [-1.0, -2.0, -3.0]: random 2 out of 3 agents trade and pay -4.0
    buyer: [9.0, 8.0]: random 1 out of 2 agents trade and pay 8.0


    >>> # ONE SELLER, ONE BUYER, ZERO MEDIATORS

    >>> market = Market([AgentCategory("seller", [-4.]), AgentCategory("buyer", [9.,8.]), AgentCategory("mediator", [-5, -7])])
    >>> print(market); print(budget_balanced_ascending_auction(market, [1,1,0]))
    Traders: [seller: [-4.0], buyer: [9.0, 8.0], mediator: [-5, -7]]
    seller: [-4.0]: all 1 agents trade and pay -8.0
    buyer: [9.0]: all 1 agents trade and pay 8.0

    """
    num_categories = market.num_categories
    if len(ps_recipe) != num_categories:
        raise ValueError(
            "There are {} categories but {} elements in the PS recipe".
                format(num_categories, len(ps_recipe)))

    relevant_category_indices = [i for i in range(num_categories) if ps_recipe[i]>0]

    logger.info("\n#### Budget-Balanced Ascending Auction\n")
    logger.info(market)
    logger.info("Procurement-set recipe: {}".format(ps_recipe))

    optimal_trade = market.optimal_trade(ps_recipe, max_iterations=max_iterations)[0]
    logger.info("For comparison, the optimal trade is: %s\n", optimal_trade)

    remaining_market = market.clone()
    prices = AscendingPriceVector(ps_recipe, -MAX_VALUE)

    # Functions for calculating the number of potential PS that can be supported by a category:
    fractional_potential_ps = lambda category_index: remaining_market.categories[category_index].size() / ps_recipe[category_index]
    integral_potential_ps   = lambda category_index: math.floor(remaining_market.categories[category_index].size() / ps_recipe[category_index])

    while True:
        # find a category with a largest number of potential PS, and increase its price
        main_category_index = max(relevant_category_indices, key=fractional_potential_ps)
        main_category = remaining_market.categories[main_category_index]
        logger.info("Chosen category: {} with {} agents and ratio {}".format(main_category.name, main_category.size(), fractional_potential_ps(main_category_index)))

        if main_category.size() == 0:
            logger.info("\nThe %s category became empty - no trade!", main_category.name)
            logger.info("  Final price-per-unit vector: %s", prices)
            break

        prices.increase_price_up_to_balance(main_category_index, main_category.lowest_agent_value(), main_category.name)
        if prices.status == PriceStatus.STOPPED_AT_ZERO_SUM:
            logger.info("\nPrice crossed zero.")
            logger.info("  Final price-per-unit vector: %s", prices)
            break

        main_category.remove_lowest_agent()
        logger.info("  {} price increases to {}: {} agents and ratio {}".format(main_category.name, prices[main_category_index], main_category.size(), fractional_potential_ps(main_category_index)))

    logger.info(remaining_market)
    return TradeWithSinglePrice(remaining_market.categories, ps_recipe, prices.prices)




if __name__ == "__main__":
    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("doctest: {} failures, {} tests".format(failures,tests))

    import unittest
    unittest.main(module="ascending_auction_test")
