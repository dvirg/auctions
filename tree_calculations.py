#!python3

"""
Imports stock prices from csv files downloaded from Yahoo.
The CSV files are stored in stocks directory.

Author: Dvir Gilor
Since:  2020-08
"""

def get_agents_analyze(recipe_tree:list):
    (maxDepth, maxAgentIndex) = get_depth_and_agents_size(recipe_tree)
    print(maxDepth, maxAgentIndex)
    agent_counts = [1] * (maxAgentIndex+1)
    print(agent_counts)
    analyze_recipe_tree(recipe_tree, agent_counts, maxDepth)
    agent_counts[0] = maxDepth-1
    return agent_counts


def analyze_recipe_tree(recipe_tree: list, agent_counts: list, depth: int):
    print(recipe_tree, agent_counts)
    for i in range(0, len(recipe_tree), 2):
        agent_index = recipe_tree[i]
        next_recipe_tree = recipe_tree[i + 1]
        if next_recipe_tree is None:
            agent_counts[agent_index] = depth
        else:
            analyze_recipe_tree(next_recipe_tree, agent_counts, depth - 1)


def get_depth_and_agents_size(recipe_tree):
    if recipe_tree is None:
        return 0, 0
    max_index = 0
    max_depth = 0
    for i in range(0, len(recipe_tree), 2):
        (depth, index) = get_depth_and_agents_size(recipe_tree[i + 1])
        max_index = max(max_index, recipe_tree[i], index)
        max_depth = max(max_depth, depth)
    return max_depth + 1, max_index

def get_children_counts(recipe_tree, category_size_list):
    return calculate_children_counts(recipe_tree, [0] * len(category_size_list))

def calculate_children_counts(recipe_tree, children_counts):
    for i in range(0, len(recipe_tree), 2):
        index = recipe_tree[i]
        if recipe_tree[i+1] is None:
            children_counts[index] = 1
        else:
            children_counts[index] = int(len(recipe_tree[i+1])/2)
            calculate_children_counts(recipe_tree[i+1], children_counts)
    return children_counts


recipes_111 = [1, [2, [0, None]]]  # buyer <- sellerB <- sellerA; [1,1,1]
#print(get_agents_analyze(recipes_111))
recipes_4paths = [0, [1, [2, None, 3, None], 4, [5, None, 6, None]]]
#print(get_agents_analyze(recipes_4paths))
print(get_children_counts(recipes_111, [1,1,1]))
print(get_children_counts(recipes_4paths, [1,1,1,1,1,1,1]))
