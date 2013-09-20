# -*- coding: utf-8 -*-
from common_test import *

def partial_removal(root):

    graph = Directed_graph(r_server, 'uniq', logger, has_root = root)

    create_generic_graph(graph)

    nodes = nodes_generic.copy()

    def clean():
        generic_clean(graph)

    def clean1():
        graph.remove_node(node1_generic)
        nodes.pop(node1_generic, 0)
        graph.remove_node(node2_generic)
        nodes.pop(node2_generic, 0)
        graph.remove_node(node3_generic)
        nodes.pop(node3_generic, 0)
        nodes[node4_generic]['predecessors'] = []
        nodes[node5_generic]['predecessors'] = []

    def clean2():
        graph.remove_node(node4_generic)
        nodes.pop(node4_generic, 0)
        graph.remove_node(node5_generic)
        nodes.pop(node5_generic, 0)

    def check():
        #we check that we have the correct successors/predecessors for each nodes
        for node in nodes:
            expected = get_predecessors(node, nodes, root)
            got = graph.get_predecessors(node)
            assert print_test(got, expected, node, "predecessors", clean)
 
            expected = get_successors(node, nodes, root)
            got = graph.get_successors(node)
            assert print_test(got, expected, node, "successors", clean)
 
    check()

    #same withe the root
    name = graph.root
    got = graph.get_successors(name)
    if root:
        expected = convert({'level_1_2', 'level_1_1☭'})
    else:
        expected = set([])
    assert print_test(got, expected, name, "successors", clean)
 
    got = graph.get_predecessors(name)
    expected = set([])
    assert print_test(got, expected, name, "predecessors", clean)


    clean1()

    check()

    #same withe the root
    name = graph.root
    got = graph.get_successors(name)
    if root:
        expected = convert({'level_2_2'})
    else:
        expected = set([])
    assert print_test(got, expected, name, "successors", clean)
 
    got = graph.get_predecessors(name)
    expected = set([])
    assert print_test(got, expected, name, "predecessors", clean)

    clean()

class Test_general(unittest.TestCase):

    def test_general_without_root(self):
        print('\nPartial removal without root:')
        partial_removal(False)

    def test_general_with_root(self):
        print('\nPartial removal with root:')
        partial_removal(True)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
