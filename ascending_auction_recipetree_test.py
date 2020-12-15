#!python3

"""
Unit-test for multiple-clock strongly-budget-balanced ascending auction.

Author: Erel Segal-Halevi
Since:  2019-08
"""

from markets import Market
from agents import AgentCategory, MAX_VALUE
import ascending_auction_recipetree_protocol, ascending_auction_test, prices

import logging

def show_log():
    ascending_auction_recipetree_protocol.logger.setLevel(logging.INFO)
    prices.logger.setLevel(logging.INFO)

def hide_log():
    ascending_auction_recipetree_protocol.logger.setLevel(logging.WARNING)
    prices.logger.setLevel(logging.WARNING)

hide_log()


from typing import *
import unittest

def ps_recipe_to_recipe_struct(ps_recipe:List[int])->List[Any]:
    """
    Converts a single PS recipe to a struct that represents a tree with a single path.
    The tree is arranged such that the category order is preserved.

    >>> ps_recipe_to_recipe_struct([1])
    [0, None]
    >>> ps_recipe_to_recipe_struct([1,1])
    [1, [0, None]]
    >>> ps_recipe_to_recipe_struct([1,1,1])
    [1, [2, [0, None]]]
    >>> ps_recipe_to_recipe_struct([1,1,1,1])
    [1, [2, [3, [0, None]]]]
    >>> ps_recipe_to_recipe_struct([1,0,1,1])
    [2, [3, [0, None]]]
    """
    result = None
    ps_recipe_reverse = list(enumerate(ps_recipe))
    ps_recipe_reverse.reverse()
    ps_recipe_reverse = ps_recipe_reverse[-1:] + ps_recipe_reverse[:-1]
    for category_index,category_count in ps_recipe_reverse:
        if category_count>0:
            result = [category_index, result]
    return result


class TestAscendingAuctionWithSingleRecipe(ascending_auction_test.TestAscendingAuction):
    """
    This TestCase class runs all the unittests written for the single-recipe ascending_auction_protocol,
    on the multi-recipe ascending_auction protocol.
    The results should be the same.
    """

    # Override the check_market function so that it uses the multi-recipe protocol instead of the single-recipe protocol.
    def _check_market(self, market: Market, ps_recipe:List[int], expected_num_of_deals:int, expected_prices:List[float]):
        # ps_recipes = [ps_recipe]  # a recipe-vector with a single recipe
        ps_recipe_struct = ps_recipe_to_recipe_struct(ps_recipe)
        trade = ascending_auction_recipetree_protocol.budget_balanced_ascending_auction(market, ps_recipe_struct)
        self.assertEqual(trade.num_of_deals(), expected_num_of_deals)

        for i, expected_price in enumerate(expected_prices):
            if expected_price is not None:
                self.assertEqual(trade.prices[i], expected_price)


    # Override the test of [1,2] recipe, since currently only binary recipes are supported.
    def test_market_1_2(self):
        pass



class TestAscendingAuctionWithTwoRecpies(unittest.TestCase):
    """
    This TestCase class runs unittests for settings with two recipes.
    """


    def _check_market(self, market: Market, ps_recipe_struct:List[Any], expected_num_of_deals:int, expected_prices:List[float]):
        trade = ascending_auction_recipetree_protocol.budget_balanced_ascending_auction(market, ps_recipe_struct)
        self.assertEqual(trade.num_of_deals(), expected_num_of_deals)
        for i, price in enumerate(expected_prices):
            if price is not None:
                self.assertEqual(trade.prices[i], expected_prices[i])


    def test_market_110_101(self):
        """
        Unit-tests with two recipes: [1,1,0] and [1,0,1].
        Note that the two latter categories are equivalent,
        so we expect the results to be identical to a single recipe [1,1].
        :return:
        """

        def check_110_101(buyers: List[float], sellersA: List[float], sellersB: List[float],
                           expected_num_of_deals: int, expected_prices: List[float]):
            market = Market([
                AgentCategory("buyer", buyers),
                AgentCategory("sellerA", sellersA),
                AgentCategory("sellerB", sellersB),
            ])
            # ps_recipes = [[1, 1, 0], [1, 0, 1]]
            ps_recipe_struct = [0, [1, None, 2, None]]
            self._check_market(market, ps_recipe_struct, expected_num_of_deals, expected_prices)

        check_110_101(buyers=[9,8], sellersA=[-4], sellersB=[-3],
            expected_num_of_deals=1, expected_prices=[4,-4,-4])

        # The following checks are based on the following:
        # check_1_1(buyers=[19,17,15,13,11,9], sellers=[-12,-10,-8,-6,-4,-2],
        #     expected_num_of_deals=4, expected_prices=[11,-11])

        check_110_101(buyers=[19,17,15,13,11,9], sellersA=[], sellersB=[-12,-10,-8,-6,-4,-2],
            expected_num_of_deals=4, expected_prices=[10,None,-10])
        check_110_101(buyers=[19,17,15,13,11,9], sellersA=[-12], sellersB=[-10,-8,-6,-4,-2],
            expected_num_of_deals=4, expected_prices=[10,-10,-10])
        check_110_101(buyers=[19,17,15,13,11,9], sellersA=[-4,-2], sellersB=[-12,-10,-8,-6],
            expected_num_of_deals=4, expected_prices=[10,-10,-10])
        check_110_101(buyers=[19,17,15,13,11,9], sellersA=[-10,-4], sellersB=[-12,-8,-6,-2],
            expected_num_of_deals=4, expected_prices=[10,-10,-10])
        check_110_101(buyers=[19,17,15,13,11,9], sellersA=[-12,-10,-8,-6,-4,-2], sellersB=[],
            expected_num_of_deals=4, expected_prices=[10,-10,None])


    def test_market_1100_1011(self):
        """
        Unit-tests with two recipes: [1,1,0,0] and [1,0,1,1].
        This is the smallest case in which multi-recipe substantially differs than single-recipe.
        :return:
        """

        def check_1100_1011(buyers: List[float], sellers: List[float], producers: List[float], movers: List[float],
                           expected_num_of_deals: int, expected_prices: List[float]):
            market = Market([
                AgentCategory("buyer", buyers),
                AgentCategory("seller", sellers),
                AgentCategory("producer", producers),
                AgentCategory("mover", movers),
            ])
            # ps_recipes = [[1, 1, 0, 0], [1, 0, 1, 1]]
            ps_recipe_struct = [0, [1, None, 2, [3, None]]]
            self._check_market(market, ps_recipe_struct, expected_num_of_deals, expected_prices)

        check_1100_1011(buyers=[19, 17, 15, 13, 11, 9], sellers=[-12, -10, -8, -6, -4, -2], producers=[], movers=[],
            expected_num_of_deals=4, expected_prices=[10.0, -10.0, None, None])
        # show_log()
        check_1100_1011(buyers=[19, 17, 15, 13, 11, 9], sellers=[], producers=[-6,-5,-4,-3,-2,-1], movers=[-6,-5,-4,-3,-2,-1],
            expected_num_of_deals=4, expected_prices=[10, None, -5, -5])
        # hide_log()


    def test_market_11100_10011(self):
        """
        Unit-tests with two recipes: [1,1,0,0] and [1,0,1,1].
        This is the smallest case in which multi-recipe substantially differs than single-recipe.
        :return:
        """

        def check_11100_10011(buyers: List[float], sellers1: List[float], sellers2: List[float], producers1: List[float], producers2: List[float],
                           expected_num_of_deals: int, expected_prices: List[float]):
            market = Market([
                AgentCategory("buyer", buyers),
                AgentCategory("seller1", sellers1),
                AgentCategory("seller2", sellers2),
                AgentCategory("producer1", producers1),
                AgentCategory("producer2", producers2),
            ])
            ps_recipe_struct = [0, [1, [2, None], 3, [4, None]]]
            self._check_market(market, ps_recipe_struct, expected_num_of_deals, expected_prices)

        check_11100_10011(buyers=[400, 300, 200, 100], sellers1=[-1, -2], sellers2=[-3, -4], producers1=[-5,-6], producers2=[-7,-8],
            expected_num_of_deals=2, expected_prices=[None, None, None, None, None])

    AgentCategory("buyer", [400, 300, 200, 100]),
    AgentCategory("seller1", [-1, -2]),
    AgentCategory("seller2", [-3, -4]),
    AgentCategory("producer1", [-5, -6]),
    AgentCategory("producer2", [-7, -8]),



if __name__ == '__main__':
    unittest.main()

