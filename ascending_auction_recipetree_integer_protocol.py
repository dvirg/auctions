#!python3

"""
function budget_balanced_ascending_auction
Implementation of a multiple-clock strongly-budget-balanced ascending auction for a multi-lateral market.

Allows multiple recipes, but only of the following kind:

    [x, y, z, ...]

where x, y, z, etc. are positive integers (or zero).
For each recipe r1, r2. for every index i, if r1[i] > 0 and r2[i] > 0 so there must be: r1[i] = r2[i]

I.e., there is a single buyer category and n-1 seller categories, and
a single buyer may wish to buy different combinations or products.

The smallest interesting example is:

    [ [1, 2, 0, 0], [1, 0, 1, 2] ]

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
        (self.num_of_deals_cache, self.num_of_deals_explanation_cache, self.kmin, self.kmax) = recipe_tree.num_of_deals_explained(prices)
        self.gft_cache = recipe_tree.optimal_trade_GFT()

    def num_of_deals(self):
        return self.num_of_deals_cache

    def min_num_of_deals(self):
        return self.kmin

    def max_num_of_deals(self):
        return self.kmax

    def gain_from_trade(self, including_auctioneer:bool=True):
        return self.gft_cache

    def optimal_trade(self):
        return self.recipe_tree.optimal_trade()

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

    >>> logger.setLevel(logging.DEBUG)
    >>> # ONE BUYER, ONE SELLER #[0, [1, None]]
    >>> recipe_11 = {'index': 0, 'count': 1, 'children': [{'index': 1, 'count': 1, 'children': []}]}
    >>>
    >>> #[0, [1, None, 2, [3, None]]]
    >>> recipe_1100_1011 = {'index': 0, 'count': 1, 'children': [{'index': 1, 'count': 2, 'children': []}, {'index': 2, 'count': 1, 'children': [{'index': 2, 'count': 2, 'children': []}]}]}
    >>>
    >>> market = Market([AgentCategory("buyer", [19.0, 18.0, 17.0, 13.0, 6.0, 2.0]), AgentCategory("seller", [-2.0, -2.0, -3.0, -4.0, -5.0, -8.0]), AgentCategory("A", [-1.0, -3.0, -5.0, -7.0]), AgentCategory("B", [-1.0, -2.0, -3.0, -4.0, -6.0, -8.0])])
    >>> print(market); print(budget_balanced_ascending_auction(market, recipe_1100_1011))
    Traders: [buyer: [19.0, 18.0, 17.0, 13.0, 6.0, 2.0], seller: [-2.0, -2.0, -3.0, -4.0, -5.0, -8.0], A: [-1.0, -3.0, -5.0, -7.0], B: [-1.0, -2.0, -3.0, -4.0, -6.0, -8.0]]
    seller: 2 potential deals, price=-5.0
    B: 2 potential deals, price=-2.0
    A: all 1 traders selected, price=-3.0
    B: all 2 traders selected
    buyer: 3 out of 4 traders selected, price=9.0
    seller + A: all 2 traders selected
    3 deals overall

    >>> market = Market([AgentCategory("buyer", [17.,11.]), AgentCategory("seller", [-5.0]), AgentCategory("A", [-3.0]), AgentCategory("B", [-2.0])])
    >>> print(market); print(budget_balanced_ascending_auction(market, recipe_1100_1011))
    Traders: [buyer: [17.,11.], seller: [-5.0], A: [-3.0], B: [-2.0]]


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
