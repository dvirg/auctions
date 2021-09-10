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

Author: Dvir Gilor
Since:  2021-03
"""

from agents import AgentCategory, EmptyCategoryException, MAX_VALUE
from markets import Market
from trade import Trade, TradeWithSinglePrice
from prices_integer import SimultaneousAscendingPriceVectors, PriceStatus
from typing import *
from recipetree_integer import RecipeTree

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
    def __init__(self, categories:List[AgentCategory], recipe_tree:RecipeTree, prices:List[float], agent_counts:List[int]=None):
        self.categories = categories
        self.num_categories = len(categories)
        self.recipe_tree = recipe_tree
        self.agent_counts = agent_counts if agent_counts else [1] * len(categories)
        self.prices = prices
        (self.num_of_deals_cache, self.num_of_deals_explanation_cache, self.kmin, self.kmax, self.path_counters) = recipe_tree.num_of_deals_explained(prices)
        self.gft_cache = recipe_tree.optimal_trade_GFT()

    def num_of_deals(self):
        return self.num_of_deals_cache

    def path_counters(self):
        return self.path_counters

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


def budget_balanced_ascending_auction(market:Market, ps_recipe_struct: List[Any], agent_counts:List[int]=None)->TradeWithMultipleRecipes:
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
    >>> # ONE BUYER, ONE SELLER
    >>> recipe_11 = [0, [1, None]]
    >>> agent_counts = [1, 2, 1, 2]
    >>> recipe_1100_1011 = [0, [1, None, 2, [3, None]]]
    >>>
    >>> market = Market([AgentCategory("buyer", [101,101,101,101,101]), AgentCategory("seller1", [-1,-90]), AgentCategory("seller2", [-1,-90]), AgentCategory("seller", [-50, -50, -50, -50, -50, -50])])
    >>> RecipeTree(market.categories, [0, [1, None, 2, None, 3, None]], [1,2,2,2]).optimal_trade_with_counters()
    ([([101, -1, -90], {'counter': 1, 'index': 1}), ([101, -1, -90], {'counter': 1, 'index': 2}), ([101, -50, -50], {'counter': 3, 'index': 3}), ([101, -50, -50], {'counter': 3, 'index': 3}), ([101, -50, -50], {'counter': 3, 'index': 3})], 5, 23, 1, 3, {'1': 1, '2': 1, '3': 3})
    >>> print(market); print(budget_balanced_ascending_auction(market, [0, [1, None, 2, None, 3, None]], [1,2,2,2]))
    Traders: [buyer: [101, 101, 101, 101, 101], seller1: [-1, -90], seller2: [-1, -90], seller: [-50, -50, -50, -50, -50, -50]]
    seller1: 0 potential deals, price=-50.5
    seller2: 0 potential deals, price=-50.5
    seller: 3 potential deals, price=-50.5
    buyer: all 3 remaining traders selected, price=101.0
    (seller1 + seller2 + seller): all 3 remaining deals selected
    3 deals overall

    >>> market = Market([AgentCategory("buyer", [101,101,101]), AgentCategory("seller1", [-1,-90]), AgentCategory("seller2", [-1,-90]), AgentCategory("seller", [-50, -50, -50, -50, -50, -50])])
    >>> RecipeTree(market.categories, [0, [1, None, 2, None, 3, None]], [1,2,2,2]).optimal_trade_with_counters()
    ([([101, -1, -90], {'counter': 1, 'index': 1}), ([101, -1, -90], {'counter': 1, 'index': 2}), ([101, -50, -50], {'counter': 1, 'index': 3})], 3, 21, 1, 1, {'1': 1, '2': 1, '3': 1})
    >>> print(market); print(budget_balanced_ascending_auction(market, [0, [1, None, 2, None, 3, None]], [1,2,2,2]))
    Traders: [buyer: [101, 101, 101], seller1: [-1, -90], seller2: [-1, -90], seller: [-50, -50, -50, -50, -50, -50]]
    seller1: 0 potential deals, price=-50.0
    seller2: 0 potential deals, price=-50.0
    seller: 2 potential deals, price=-50.0
    buyer: 2 out of 3 remaining traders selected, price=100.0
    (seller1 + seller2 + seller): all 2 remaining deals selected
    2 deals overall


    >>> market = Market([AgentCategory("buyer", [27.,21., 17.,11., 3.]), AgentCategory("seller", [-4.0, -5.0, -11.0]), AgentCategory("A", [-2.0, -3.0, -11.0]), AgentCategory("B", [-1.0, -2.0, -8.0])])
    >>> RecipeTree(market.categories, recipe_1100_1011, agent_counts).optimal_trade_with_counters()
    ([([27.0, -2.0, -1.0, -2.0], {'counter': 1, 'index': 3}), ([21.0, -4.0, -5.0], {'counter': 1, 'index': 1})], 2, 34.0, 1, 1, {'3': 1, '1': 1})
    >>> print(market); print(budget_balanced_ascending_auction(market, recipe_1100_1011, agent_counts))
    Traders: [buyer: [27.0, 21.0, 17.0, 11.0, 3.0], seller: [-4.0, -5.0, -11.0], A: [-2.0, -3.0, -11.0], B: [-1.0, -2.0, -8.0]]
    seller: 1 potential deals, price=-8.5
    B: 1 potential deals, price=-7.0
    A: all 1 remaining traders selected, price=-3.0
    (B): all 1 remaining deals selected
    buyer: all 2 remaining traders selected, price=17.0
    (seller + A): all 2 remaining deals selected
    2 deals overall

    >>> market = Market([AgentCategory("buyer", [17.,11.]), AgentCategory("seller", [-5.0]), AgentCategory("A", [-3.0]), AgentCategory("B", [-2.0])])
    >>> print(market); print(budget_balanced_ascending_auction(market, recipe_1100_1011))
    Traders: [buyer: [17.0, 11.0], seller: [-5.0], A: [-3.0], B: [-2.0]]
    No trade


    >>> market = Market([AgentCategory("buyer", [9.]),  AgentCategory("seller", [-4.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, recipe_11))
    Traders: [buyer: [9.0], seller: [-4.0]]
    No trade

    >>> market = Market([AgentCategory("buyer", [9.,8.]),  AgentCategory("seller", [-4.])])
    >>> print(market); print(budget_balanced_ascending_auction(market, recipe_11))
    Traders: [buyer: [9.0, 8.0], seller: [-4.0]]
    seller: 1 potential deals, price=-8.0
    buyer: all 1 remaining traders selected, price=8.0
    (seller): all 1 remaining deals selected
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
    buyer: 1 out of 2 remaining traders selected, price=4.0
    (seller): all 1 remaining deals selected
    1 deals overall

    """


    logger.info("\n#### Multi-Recipe Budget-Balanced Ascending Auction\n")
    logger.info(market)
    logger.info("Procurement-set recipe struct: {}".format(ps_recipe_struct))
    logger.info("Procurement-set recipe agent counts: {}".format(agent_counts))

    remaining_market = market.clone()
    recipe_tree = RecipeTree(remaining_market.categories, ps_recipe_struct, agent_counts)
    logger.info("Tree of recipes: {}".format(recipe_tree.paths_to_leaf()))
    ps_recipes = recipe_tree.recipes()
    logger.info("Procurement-set recipes: {}".format(ps_recipes))


    optimal_trade, optimal_count, optimal_GFT = recipe_tree.optimal_trade()
    logger.info("For comparison, the optimal trade has k=%d, GFT=%f: %s\n", optimal_count,optimal_GFT,optimal_trade)
    # optimal_trade = market.optimal_trade(ps_recipe)[0]

    #### STOPPED HERE

    prices = SimultaneousAscendingPriceVectors(ps_recipes, -MAX_VALUE, agent_counts)
    while True:
        largest_category_size, combined_category_size, indices_of_prices_to_increase = recipe_tree.largest_categories(indices=True)
        logger.info("\n")
        logger.info(remaining_market)
        logger.info("Largest category indices are %s. Largest category size = %d, combined category size = %d", indices_of_prices_to_increase, largest_category_size, combined_category_size)

        if combined_category_size == 0:
            logger.info("\nCombined category size is 0 - no trade!")
            logger.info("  Final price-per-unit vector: %s", prices)
            logger.info(remaining_market)
            return TradeWithMultipleRecipes(remaining_market.categories, recipe_tree, prices.map_category_index_to_price(), agent_counts)

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
            return TradeWithMultipleRecipes(remaining_market.categories, recipe_tree, map_category_index_to_price, agent_counts)

        remove_lowest_agent(market, remaining_market, map_category_index_to_price, indices_of_prices_to_increase)

def remove_lowest_agent(market, remaining_market, map_category_index_to_price, indices_of_prices_to_increase):
    for category_index in range(market.num_categories):
        if category_index not in indices_of_prices_to_increase:
            continue
        category = remaining_market.categories[category_index]
        if map_category_index_to_price[category_index] is not None \
            and category.size() > 0 \
            and category.lowest_agent_value() <= map_category_index_to_price[category_index]:
                category.remove_lowest_agent()
                logger.info("{} after: {} agents remain".format(category.name, category.size()))
                return
    logger.error("Should have remove someone, and didn't remove: {}, {}, {}, {}", market, remaining_market, map_category_index_to_price, indices_of_prices_to_increase)



if __name__ == "__main__":
    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("{} failures, {} tests".format(failures,tests))
