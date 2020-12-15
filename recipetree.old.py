#!python3

"""
A tree in which each node is an agent category,
and each path from root to leaf is a recipe.

For more information on tree implementations in Python, see here:
https://stackoverflow.com/q/2358045/827927
"""

from typing import *
from anytree import Node, NodeMixin, RenderTree
from agents import AgentCategory
import logging, sys, collections

logger = logging.getLogger(__name__)


# Code from https://stackoverflow.com/a/2158532/827927
def flatten(l):
    for el in l:
        if isinstance(el, collections.abc.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el



class RecipeTree (NodeMixin):
    """
    A tree in which each node is an agent category,
    and each path from root to leaf is a recipe.

    >>> buyer = AgentCategory("buyer", [60,40,20,-30])
    >>> seller = AgentCategory("seller", [-10,-30,-50])
    >>> producerA = AgentCategory("producerA", [-1, -3, -5])
    >>> producerB = AgentCategory("producerB", [-2, -4, -6, -8])
    >>> categories = [buyer, seller, producerA, producerB]  # Indices: 0, 1, 2, 3

    >>> tree = RecipeTree(categories, [0, None])  # buyer
    >>> tree.combined_values()
    [60, 40, 20, -30]
    >>> tree.combined_values_detailed()
    [60, 40, 20, -30]
    >>> tree.optimal_trade_GFT()
    120
    >>> tree.largest_categories()[-1]
    ['buyer']
    >>> tree.paths_to_leaf()
    [['buyer']]
    >>> tree.num_of_deals()
    4
    >>> print(tree.num_of_deals_explained(prices=[1,2,3,4])[1])
    buyer: 4 potential deals, price=1
    <BLANKLINE>

    >>> tree = RecipeTree(categories, [0, [1, None]])   # buyer -> seller
    >>> tree.combined_values()
    [50, 10, -30]
    >>> tree.combined_values_detailed()
    [(60, -10), (40, -30), (20, -50)]
    >>> tree.optimal_trade_GFT()
    60
    >>> tree.largest_categories()[-1]
    ['buyer']
    >>> tree.paths_to_leaf()
    [['buyer', 'seller']]
    >>> tree.num_of_deals()
    3
    >>> print(tree.num_of_deals_explained(prices=[1,2,3,4])[1])
    seller: 3 potential deals, price=2
    buyer: 3 out of 4 traders selected, price=1
    seller: all 3 traders selected
    <BLANKLINE>

    >>> tree = RecipeTree(categories, [0, [2, None, 3, None]])   # buyer -> producerA, buyer -> producerB
    >>> tree.combined_values()
    [59, 38, 17, -34]
    >>> tree.combined_values_detailed()
    [(60, -1), (40, -2), (20, -3), (-30, -4)]
    >>> tree.optimal_trade_GFT()
    114
    >>> tree.largest_categories()[-1]
    ['producerA', 'producerB']
    >>> tree.paths_to_leaf()
    [['buyer', 'producerA'], ['buyer', 'producerB']]
    >>> tree.recipes()
    [[1, 0, 1, 0], [1, 0, 0, 1]]
    >>> tree.num_of_deals()
    4
    >>> print(tree.num_of_deals_explained(prices=[1,2,3,4])[1])
    producerA: 3 potential deals, price=3
    producerB: 4 potential deals, price=4
    buyer: all 4 traders selected, price=1
    producerA + producerB: 4 out of 7 traders selected
    <BLANKLINE>


    >>> tree = RecipeTree(categories, [0, [1, None, 2, [3, None]]])   # buyer -> seller, buyer -> producerA -> producerB
    >>> tree.combined_values()
    [57, 33, 10, -41]
    >>> tree.combined_values_detailed()
    [(60, -1, -2), (40, -3, -4), (20, -10), (-30, -5, -6)]
    >>> tree.optimal_trade_GFT()
    100
    >>> tree.largest_categories()[-1]
    ['seller', 'producerB']
    >>> tree.largest_categories(indices=True)[-1]
    [1, 3]
    >>> tree.paths_to_leaf()
    [['buyer', 'seller'], ['buyer', 'producerA', 'producerB']]
    >>> tree.paths_to_leaf(indices=True)
    [[0, 1], [0, 2, 3]]
    >>> tree.recipes()
    [[1, 1, 0, 0], [1, 0, 1, 1]]
    >>> tree.num_of_deals()
    4
    >>> print(tree.num_of_deals_explained(prices=[1,2,3,4])[1])
    seller: 3 potential deals, price=2
    producerB: 4 potential deals, price=4
    producerA: all 3 traders selected, price=3
    producerB: 3 out of 4 traders selected
    buyer: all 4 traders selected, price=1
    seller + producerA: 4 out of 6 traders selected
    <BLANKLINE>

    >>> buyer = AgentCategory("buyer", [90,80,70,60,50,40])
    >>> seller = AgentCategory("seller", [-10,-30,-50])
    >>> producerA = AgentCategory("producerA", [-1, -3, -5,-7])
    >>> producerB = AgentCategory("producerB", [-2, -4])
    >>> categories = [buyer, seller, producerA, producerB]  # Indices: 0, 1, 2, 3
    >>> tree = RecipeTree(categories, [0, [1, None, 2, [3, None]]])   # buyer -> seller, buyer -> producerA -> producerB
    >>> tree.combined_values_detailed()
    [(90, -1, -2), (80, -3, -4), (70, -10), (60, -30), (50, -50)]
    >>> tree.combined_values()
    [87, 73, 60, 30, 0]
    >>> tree.optimal_trade_GFT()
    250
    >>> tree.num_of_deals()
    5
    >>> tree.largest_categories()[-1]
    ['buyer']

    >>> producerA.values = [-1, -3, -5, -7, -9, -11, -13]
    >>> producerB.values = [-2, -4, -6, -8, -10]
    >>> tree.largest_categories()[-1]
    ['seller', 'producerA']
    """

    def __init__(self, categories:List[AgentCategory], category_indices:List[Any]):
        """
        :param category:
        :param parent:
        :param children:
        :param categories:
        """
        if len(category_indices)%2!=0:
            raise ValueError("RecipeTree must be initialized with an even-length list, containing indices and their children.")

        self.num_categories = len(categories)
        self_index = category_indices[0]
        children_indices = category_indices[1]

        self.category_index = self_index
        self.category = self_category = categories[self_index]
        self.name = self_category.name if isinstance(self_category, AgentCategory) else self_category

        if children_indices is not None:
            children = []
            for child_index in range(0,len(children_indices),2):
                child = RecipeTree(categories, children_indices[child_index:child_index+2])
                children.append(child)
            self.children = children



    def paths_to_leaf(self, indices=False, prefix=[]) -> List[List[Any]]:
        """
        Get all paths from this node to a leaf.

        :param indices: if True, each element in the path is a node index. Otherwise, it is the node name.
        """
        self_id = self.category_index if indices==True else self.name
        if len(self.children)==0:
            paths = [prefix + [self_id]]
        else:
            paths = []
            for child in self.children:
                paths_from_child_to_leaf = child.paths_to_leaf(indices = indices, prefix = prefix + [self_id])
                paths += paths_from_child_to_leaf
        return paths

    @staticmethod
    def recipe_from_path(path:List[int], num_categories:int)->List[int]:
        """
        Converts a path from the root to a leaf into a recipe.
        :param path: a list of indices of categories.
        :return: a list of zeros and ones.

        >>> RecipeTree.recipe_from_path([0, 2, 3], 5)
        [1, 0, 1, 1, 0]
        """
        result = [0]*num_categories
        for index in path:
            result[index] = 1
        return result


    def recipes(self) -> List[List[int]]:
        """
        Get all recipes (lists of 0 and 1) represented by this recipe-tree.
        Each path from root to leaf represents a single recipe.
        """
        paths_to_leaf = self.paths_to_leaf(indices=True)
        return [RecipeTree.recipe_from_path(path, self.num_categories) for path in paths_to_leaf]





    def combined_values(self) -> list:
        """
        Combine the values in all categories of the current subtree into a single value-list.
        Categories in siblings are combined by uniting the sets and sorting it in descending order.
        Categories in parent-child are combined by sorting each set in descending order and creating elementwise sums.
        """
        self_values = self.category.values
        if len(self.children) == 0:
            values = self_values
        else:
            children_values = sum([child.combined_values() for child in self.children], [])
            children_values.sort(reverse=True)
            values = [a+b for (a,b) in zip(self_values, children_values)]
        return values


    def combined_values_detailed(self) -> list:
        """
        Combine the values in all categories of the current subtree into a single value-list.
        Categories in siblings are combined by uniting the sets and sorting it in descending order.
        Categories in parent-child are combined by sorting each set in descending order and creating elementwise sums.

        Similar to combined_values, but keeps all the summed-up values instead of just the sum.
        """
        self_values = self.category.values
        if len(self.children) == 0:
            values = self_values
        else:
            children_values = sum([child.combined_values_detailed() for child in self.children], [])
            # logger.debug("children_values: %s",children_values)
            children_values.sort(reverse=True, key=lambda x: sum(x) if (isinstance(x,list) or isinstance(x,tuple)) else x)
            values = [tuple(flatten(t)) for t in zip(self_values, children_values)]
        return values

    def optimal_trade(self)->(list,int,float):
        """
        :return: a tuple:
        * first element is the list of deals in the optimal trade;
        * second element is the optimal num of deals (k);
        * third is the optimal GFT.
        """
        values = self.combined_values_detailed()
        optimal_trade_values = [t for t in values if sum(t)>0]
        optimal_trade_count = len(optimal_trade_values)
        optimal_trade_values_GFT = sum(flatten(optimal_trade_values))
        return (optimal_trade_values, optimal_trade_count, optimal_trade_values_GFT)

    def optimal_trade_GFT(self) -> int:
        """
        Calculate the maximum possible GFT for the given category tree.
        """
        return sum([v for v in self.combined_values() if v > 0])


    def largest_categories(self, indices=False) -> (int,list):
        """
        Return a list of category names,
        such that each path from root to leaf contains one such category,
        and these are the categories with the largest number of traders.

        :param indices: if True, each element in the path is a node index. Otherwise, it is the node name.
        :return (largest category size, combined category size, list of largest categories)

        >>> categories = [AgentCategory(str(size), [1]*size) for size in range(10)]  # create categories in various sizes
        >>> RecipeTree(categories, [6, None]).largest_categories(indices=True)
        (6, 6, [6])
        >>> RecipeTree(categories, [6, [8, None]]).largest_categories(indices=True)[-1]
        [8]
        >>> RecipeTree(categories, [8, [6, None]]).largest_categories(indices=True)[-1]
        [8]
        >>> RecipeTree(categories, [6, [8, [7,None]]]).largest_categories(indices=True)[-1]
        [8]
        >>> RecipeTree(categories, [7, [8, [6,None]]]).largest_categories(indices=True)[-1] != [6]
        True
        >>> RecipeTree(categories, [7, [8, [5, [6,None]]]]).largest_categories(indices=True)[-1] != [5]
        True
        >>> RecipeTree(categories, [6, [3, None, 4, [2,None]]]).largest_categories(indices=True)[-1]
        [6]
        >>> RecipeTree(categories, [6, [3, None, 2, [4,None]]]).largest_categories(indices=True)[-1]
        [6]
        >>> RecipeTree(categories, [6, [3, None, 7, [5,None]]]).largest_categories(indices=True)[-1]
        [3, 7]
        >>> RecipeTree(categories, [6, [3, None, 5, [7,None]]]).largest_categories(indices=True)[-1]
        [3, 7]
        >>> RecipeTree(categories, [5, [6, [4,None], 4, [6,None]]]).largest_categories(indices=True)[-1]
        [6, 6]
        >>> RecipeTree(categories, [7, [6, [4,None], 4, [6,None]]]).largest_categories(indices=True)[-1]
        [6, 6]
        >>> RecipeTree(categories, [8, [6, [4,None], 4, [6,None]]]).largest_categories(indices=True)[-1]
        [6, 6]
        >>> RecipeTree(categories, [9, [6, [4,None], 4, [6,None]]]).largest_categories(indices=True)[-1]
        [9]
        >>> RecipeTree(categories, [6, [0, None, 6, None]]).largest_categories(indices=True)
        (6, 6, [0, 6])
        >>> RecipeTree(categories, [6, [6, None, 0, None]]).largest_categories(indices=True)
        (6, 6, [6, 0])

        >>> categories = [AgentCategory(str(index), [22,11]) for index in range(10)]  # create categories of the same size
        >>> tree = RecipeTree(categories, [0, [1, [2, [3, [4, None]]]]])
        >>> tree.largest_categories(indices=True)[-1]
        [4]
        >>> x=categories[4].values.pop()
        >>> tree.largest_categories(indices=True)[-1]
        [0]
        >>> x=categories[0].values.pop()
        >>> tree.largest_categories(indices=True)[-1]
        [1]
        >>> x=categories[1].values.pop()
        >>> tree.largest_categories(indices=True)[-1]
        [2]
        >>> x=categories[2].values.pop()
        >>> tree.largest_categories(indices=True)[-1]
        [3]
        >>> x=categories[3].values.pop()
        >>> tree.largest_categories(indices=True)[-1]
        [4]
        """
        self_category_size = self.category.size()
        self_category_index_or_name = self.category_index if indices else self.name
        if len(self.children) == 0:
            largest_category_size = combined_category_size = self_category_size
            largest_categories = [self_category_index_or_name]
        else:
            children_combined_category_size = 0
            children_largest_category_size = 0
            children_largest_categories = []
            for child in self.children:
                (child_largest_category_size, child_combined_category_size, child_largest_categories) = child.largest_categories(indices=indices)
                children_largest_category_size = max(children_largest_category_size,child_largest_category_size)
                children_combined_category_size += child_combined_category_size
                children_largest_categories += child_largest_categories
            if children_combined_category_size >= self_category_size:
                largest_category_size = children_largest_category_size
                combined_category_size = self_category_size
                largest_categories = children_largest_categories
            else:
                largest_category_size = self_category_size
                combined_category_size = children_combined_category_size
                largest_categories = [self_category_index_or_name]
        return (largest_category_size, combined_category_size, largest_categories)


    def num_of_deals(self)->int:
        """
        Calculates the maximum number of deals that can be done using the recipes in this recipe-tree.
        :return:
        """
        self_num_of_deals = self.category.size()
        if len(self.children) == 0:
            num_of_deals = self_num_of_deals
        else:
            sum_children_num_of_deals = sum([child.num_of_deals() for child in self.children])
            num_of_deals = min(sum_children_num_of_deals,self_num_of_deals)
        return num_of_deals


    def num_of_deals_explained(self, prices:List[float])->str:
        """
        Return a detailed explanation of the number of deals done,
        including what categories require randomization.
        :return: A representation string.
        """
        self_num_of_deals = self.category.size()
        self_price = prices[self.category_index]
        if len(self.children) == 0:
            num_of_deals = self_num_of_deals
            explanation = "{}: {} potential deals, price={}\n".format(self.name, self_num_of_deals, self_price)
        else:
            children_num_of_deals_explained = [child.num_of_deals_explained(prices) for child in self.children]
            # logger.debug(children_num_of_deals_explained)
            children_num_of_deals = [t[0] for t in children_num_of_deals_explained]
            sum_children_num_of_deals = sum(children_num_of_deals)
            # logger.debug(children_num_of_deals)
            children_explanations = [t[1] for t in children_num_of_deals_explained]
            # logger.debug(children_explanations)
            children_names = [child.name for child in self.children]
            sum_children_names = " + ".join(children_names)
            num_of_deals = min(sum_children_num_of_deals,self_num_of_deals)
            explanation = "".join(children_explanations)
            if num_of_deals==self_num_of_deals:
                explanation += "{}: all {} traders selected, price={}\n".format(self.name, self_num_of_deals, self_price)
            else:
                explanation += "{}: {} out of {} traders selected, price={}\n".format(self.name, num_of_deals, self_num_of_deals, self_price)
            if num_of_deals == sum_children_num_of_deals:
                explanation += "{}: all {} traders selected\n".format(sum_children_names, sum_children_num_of_deals)
            else:
                explanation += "{}: {} out of {} traders selected\n".format(sum_children_names, num_of_deals, sum_children_num_of_deals)
        explanation += "{} deals overall\n".format(num_of_deals)
        return (num_of_deals,explanation)





if __name__=="__main__":
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    import doctest
    (failures,tests) = doctest.testmod(report=True)
    print ("doctest: {} failures, {} tests".format(failures,tests))

    buyer = AgentCategory("buyer", [17, 14, 13, 9, 6])
    seller = AgentCategory("seller", [-1, -3, -4, -5, -8, -10])
    producerA = AgentCategory("producerA", [-1, -3, -5])
    producerB = AgentCategory("producerB", [-1, -4, -6])
    categories = [buyer, seller, producerA, producerB]  # Indices: 0, 1, 2, 3

    tree = RecipeTree(categories, [0, [1, None, 2, [3, None]]])   # buyer -> seller, buyer -> producerA -> producerB

    print("Tree structure: ")
    for pre, fill, node in RenderTree(tree):
        print("{}{}".format(pre,node.name))
    # buyer
    # ├── seller
    # └── producerA
    #     └── producerB

    print("Paths from root to leaf: ", tree.paths_to_leaf())

