#!python3

"""
Unit-test for multiple-clock strongly-budget-balanced ascending auction.

Author: Erel Segal-Halevi
Since:  2019-08
"""

from markets import Market
from agents import AgentCategory, MAX_VALUE
import ascending_auction_protocol, prices

import logging
ascending_auction_protocol.logger.setLevel(logging.WARNING)
prices.logger.setLevel(logging.WARNING)

from typing import *
import unittest

class TestAscendingAuction(unittest.TestCase):

    ## Helper functions:

    def _check_market(self, market: Market, ps_recipe:List[int], expected_num_of_deals:int, expected_prices:List[float]):
        trade = ascending_auction_protocol.budget_balanced_ascending_auction(market, ps_recipe)
        self.assertEqual(trade.num_of_deals(), expected_num_of_deals)
        for i, expected_price in enumerate(expected_prices):
            if expected_price is not None:
                self.assertEqual(trade.prices[i], expected_price)


    ## Unit-tests:

    def test_market_1_1(self):
        """
        Test a standard buyer-seller market.
        """
        def check_1_1(buyers:List[float], sellers:List[float], expected_num_of_deals:int, expected_prices:List[float]):
            market = Market([
                AgentCategory("buyer", buyers),
                AgentCategory("seller", sellers),
            ])
            ps_recipe = [1,1]
            self._check_market(market, ps_recipe, expected_num_of_deals, expected_prices)

        check_1_1(buyers=[9], sellers=[-4],
            expected_num_of_deals=0, expected_prices=[None,None])
        check_1_1(buyers=[9,8], sellers=[-4],
            expected_num_of_deals=0, expected_prices=[None,None])
        check_1_1(buyers=[9], sellers=[-4,-3],
            expected_num_of_deals=1, expected_prices=[4,-4])
        check_1_1(buyers=[9,8], sellers=[-4,-3],
            expected_num_of_deals=1, expected_prices=[8,-8])

        # ALL POSITIVE VALUES:
        check_1_1(buyers=[4,3], sellers=[9,8],
            expected_num_of_deals=1, expected_prices=[3,-3])

        # ALL NEGATIVE VALUES:
        check_1_1(buyers=[-4,-3], sellers=[-9,-8],
            expected_num_of_deals=0, expected_prices=[None,None])

        # LARGER EXAMPLE
        check_1_1(buyers=[19,17,15,13,11,9], sellers=[-12,-10,-8,-6,-4,-2],
            expected_num_of_deals=4, expected_prices=[11,-11])



    def test_market_1_1_1(self):
        """
        Test a three-category market: buyer, mediator, seller
        """

        def check_1_1_1(buyers: List[float], mediators: List[float], sellers: List[float],
                           expected_num_of_deals: int, expected_prices: List[float]):
            market = Market([
                AgentCategory("buyer", buyers),
                AgentCategory("mediator", mediators),
                AgentCategory("seller", sellers),
            ])
            ps_recipe = [1, 1, 1]
            self._check_market(market, ps_recipe, expected_num_of_deals, expected_prices)

        check_1_1_1(buyers=[9,8], mediators=[-1,-2], sellers=[-4,-3],
            expected_num_of_deals=1, expected_prices=[8,-4,-4])
        check_1_1_1(buyers=[9,8], mediators=[-1,-2], sellers=[-4,-3,-10],
            expected_num_of_deals=1, expected_prices=[8,-4,-4])
        check_1_1_1(buyers=[9,8], mediators=[-1,-2], sellers=[-4,-3,-5],
            expected_num_of_deals=1, expected_prices=[8,-4,-4])
        check_1_1_1(buyers=[9,8], mediators=[-1,-2], sellers=[-4,-3,-2],
            expected_num_of_deals=1, expected_prices=[8,-5,-3])
        check_1_1_1(buyers=[9,8,7], mediators=[-1,-2,-3], sellers=[-4,-3,-2],
            expected_num_of_deals=2, expected_prices=[7,-3,-4])
        check_1_1_1(buyers=[9,8,4], mediators=[-1,-2,-3], sellers=[-4,-3,-2],
            expected_num_of_deals=2, expected_prices=[7,-3,-4])

        # RUNNING EXAMPLE FROM THE PAPER
        check_1_1_1(buyers=[17, 14, 13, 9, 6], mediators=[-1, -3, -4, -7, -10], sellers=[-1, -4, -5, -8, -11],
            expected_num_of_deals=2, expected_prices=[13,-7,-6])
        # SIMILAR EXAMPLE, WHERE PRICE STOPS BETWEEN SELLERS:
        check_1_1_1(buyers=[17, 14, 13, 9, 6], mediators=[-1, -4, -5, -8, -11], sellers=[-1, -3, -6, -7, -10],
            expected_num_of_deals=2, expected_prices=[13,-7,-6])
        # SIMILAR EXAMPLE, WHERE PRICE STOPS BETWEEN MEDIATORS:
        check_1_1_1(buyers=[17, 14, 13, 9, 6], mediators=[-1, -3, -6, -7, -10], sellers=[-1, -4, -6.5, -8, -11],
            expected_num_of_deals=2, expected_prices=[13, -6.5, -6.5])
        # SIMILAR EXAMPLE, WHERE PRICE STOPS BETWEEN BUYERS:
        check_1_1_1(buyers=[17, 14, 13, 9, 6], mediators=[-1, -3, -6, -7, -10], sellers=[-1, -4, -7.5, -8, -11],
            expected_num_of_deals=2, expected_prices=[13.5, -6, -7.5])


    def test_market_1_2(self):
        """
        Test a two-category market where each deal requires buyer + two sellers
        """

        def check_1_2(buyers: List[float], sellers: List[float], expected_num_of_deals: int,
                              expected_prices: List[float]):
            market = Market([
                AgentCategory("buyer", buyers),
                AgentCategory("seller", sellers),
            ])
            ps_recipe = [1, 2]
            self._check_market(market, ps_recipe, expected_num_of_deals, expected_prices)

        check_1_2(buyers=[9], sellers=[-4, -3],
            expected_num_of_deals=0, expected_prices=[9,-4.5])
        check_1_2(buyers=[9,8,7,6], sellers=[-6,-5,-4,-3,-2,-1],
            expected_num_of_deals=1, expected_prices=[8,-4])
        check_1_2(buyers=[9,8], sellers=[-4,-3,-2,-1],
            expected_num_of_deals=1, expected_prices=[8,-4])
        check_1_2(buyers=[9,8], sellers=[-6,-3,-2,-1],
            expected_num_of_deals=1, expected_prices=[8,-4])
        check_1_2(buyers=[9,8], sellers=[-4,-3,-2,-1],
            expected_num_of_deals=1, expected_prices=[8,-4])

        # PRICE CROSSES ZERO AT FIRST PHASE
        check_1_2(buyers=list(range(20)), sellers=[-3,-2,-1],
            expected_num_of_deals=1, expected_prices=[18,-9])


    def test_market_1_0_1(self):
        """
        Test a three-category market where the middle category has 0 in the recipe (edge case)
        """

        def check_1_0_1(buyers: List[float], mediators: List[float], sellers: List[float],
                           expected_num_of_deals: int, expected_prices: List[float]):
            market = Market([
                AgentCategory("buyer", buyers),
                AgentCategory("mediator", mediators),
                AgentCategory("seller", sellers),
            ])
            ps_recipe = [1, 0, 1]
            self._check_market(market, ps_recipe, expected_num_of_deals, expected_prices)

        check_1_0_1(buyers=[9,8], mediators=[-5,-7], sellers=[-4,-3],
            expected_num_of_deals=1, expected_prices=[8,None,-8])

if __name__ == '__main__':
    unittest.main()


