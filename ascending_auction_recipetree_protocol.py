#!python3

"""
function budget_balanced_ascending_auction
Implementation of a multiple-clock strongly-budget-balanced ascending auction for a multi-lateral market.

Allows multiple recipes, but only of the following kind:

    [1, x, y, z, ...]

where x, y, z, etc. are either 0 or 1.

I.e., there is a single buyer category and n-1 seller categories, and
a single buyer may wish to buy different combinations or products.

The smallest interesting example is:

    [ [1, 1, 0, 0], [1, 0, 1, 1] ]

Author: Erel Segal-Halevi
Since:  2020-03
"""

from agents import AgentCategory, EmptyCategoryException, MAX_VALUE
from markets import Market
from trade import Trade, TradeWithSinglePrice
from prices import SimultaneousAscendingPriceVectors, PriceStatus
from typing import *
from recipetree import RecipeTree

import logging, sys, math
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
# To enable tracing, set logger.setLevel(logging.INFO)


EPSILON = 0.00001

class TradeWithMultipleRecipes(Trade):
    """
    Represents the outcome of budget_balanced_ascending_auction.
    See there for details.
    """
    def __init__(self, categories:List[AgentCategory], recipe_tree:RecipeTree, prices:List[float]):
        self.categories = categories
        self.num_categories = len(categories)
        self.recipe_tree = recipe_tree
        self.prices = prices
        (self.num_of_deals_cache, self.num_of_deals_explanation_cache) = recipe_tree.num_of_deals_explained(prices)
        self.gft_cache = recipe_tree.optimal_trade_GFT()

    def num_of_deals(self):
        return self.num_of_deals_cache

    def gain_from_trade(self, including_auctioneer:bool=True):
        return self.gft_cache

    def __repr__(self):
        if self.num_of_deals_cache==0:
            return "No trade"
        return self.num_of_deals_explanation_cache.rstrip()


def budget_balanced_ascending_auction(
        market:Market, ps_recipe_struct: List[Any])->TradeWithMultipleRecipes:
    """
    Calculate the trade and prices using generalized-ascending-auction.
    Allows multiple recipes, but they must be represented by a *recipe tree*.

    :param market:           contains a list of k categories, each containing several agents.
    :param ps_recipe_struct: a nested list of integers. Each integer represents a category-index.
                             The nested list represents a tree, where each path from root to leaf represents a recipe.
                             For example: [0, [1, None]] is a single recipe with categories {0,1}.
                                    [0, [1, None, 2, None]] is two recipes with categories {0,1} and {0,2}.

    :return: Trade object, representing the trade and prices.

    >>> logger.setLevel(logging.WARNING)
    >>> # ONE BUYER, ONE SELLER
    >>> recipe_11 = [0, [1, None]]
    >>>
    >>> market = Market([AgentCategory("buyer", [9.]),  AgentCategory("seller", [-4.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, recipe_11))
    Traders: [buyer: [9.0], seller: [-4.0]]
    No trade

    >>> market = Market([AgentCategory("buyer", [9.,8.]),  AgentCategory("seller", [-4.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, recipe_11))
    Traders: [buyer: [9.0, 8.0], seller: [-4.0]]
    seller: 1 potential deals, price=-8.0
    buyer: all 1 traders selected, price=8.0
    seller: all 1 traders selected
    1 deals overall

    >>> logger.setLevel(logging.WARNING)
    >>> market = Market([AgentCategory("buyer", [9.]), AgentCategory("seller", [-4.,-3.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, recipe_11))
    Traders: [buyer: [9.0], seller: [-3.0, -4.0]]
    No trade

    >>> logger.setLevel(logging.WARNING)
    >>> market = Market([AgentCategory("buyer", [9.,8.]),  AgentCategory("seller", [-4.,-3.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, recipe_11))
    Traders: [buyer: [9.0, 8.0], seller: [-3.0, -4.0]]
    seller: 1 potential deals, price=-4.0
    buyer: 1 out of 2 traders selected, price=4.0
    seller: all 1 traders selected
    1 deals overall
    """
    logger.info("\n#### Multi-Recipe Budget-Balanced Ascending Auction\n")
    logger.info(market)
    logger.info("Procurement-set recipe struct: {}".format(ps_recipe_struct))

    remaining_market = market.clone()
    recipe_tree = RecipeTree(remaining_market.categories, ps_recipe_struct)
    logger.info("Tree of recipes: {}".format(recipe_tree.paths_to_leaf()))
    ps_recipes = recipe_tree.recipes()
    logger.info("Procurement-set recipes: {}".format(ps_recipes))


    optimal_trade, optimal_count, optimal_GFT = recipe_tree.optimal_trade()
    logger.info("For comparison, the optimal trade has k=%d, GFT=%f: %s\n", optimal_count,optimal_GFT,optimal_trade)
    # optimal_trade = market.optimal_trade(ps_recipe)[0]

    #### STOPPED HERE

    prices = SimultaneousAscendingPriceVectors(ps_recipes, -MAX_VALUE)
    while True:
        largest_category_size, combined_category_size, indices_of_prices_to_increase = recipe_tree.largest_categories(indices=True)
        logger.info("\n")
        logger.info(remaining_market)
        logger.info("Largest category indices are %s. Largest category size = %d, combined category size = %d", indices_of_prices_to_increase, largest_category_size, combined_category_size)

        if combined_category_size == 0:
            logger.info("\nCombined category size is 0 - no trade!")
            logger.info("  Final price-per-unit vector: %s", prices)
            logger.info(remaining_market)
            return TradeWithMultipleRecipes(remaining_market.categories, recipe_tree, prices.map_category_index_to_price())

        increases = []
        for category_index in indices_of_prices_to_increase:
            category = remaining_market.categories[category_index]
            target_price = category.lowest_agent_value() if category.size()>0 else MAX_VALUE
            increases.append((category_index, target_price, category.name))

        logger.info("Planned price-increases: %s", increases)
        prices.increase_prices(increases)
        map_category_index_to_price = prices.map_category_index_to_price()

        if prices.status == PriceStatus.STOPPED_AT_ZERO_SUM:
            logger.info("\nPrice crossed zero.")
            logger.info("  Final price-per-unit vector: %s", map_category_index_to_price)
            logger.info(remaining_market)
            return TradeWithMultipleRecipes(remaining_market.categories, recipe_tree, map_category_index_to_price)

        for category_index in range(market.num_categories):
            category = remaining_market.categories[category_index]
            if map_category_index_to_price[category_index] is not None \
                and category.size()>0 \
                and category.lowest_agent_value() <= map_category_index_to_price[category_index]:
                    category.remove_lowest_agent()
                    logger.info("{} after: {} agents remain".format(category.name, category.size()))




if __name__ == "__main__":
    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))
