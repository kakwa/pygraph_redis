# -*- coding: utf-8 -*-
from common_test import *

def general(root):

    graph = Directed_graph(r_server, 'uniq', logger, has_root = root)

    create_generic_graph(graph)

    nodes = nodes_generic

    def clean():
        generic_clean(graph)

    #we check that we have the correct successors/predecessors for each nodes
    for node in nodes:
        expected = get_predecessors(node, nodes, root)
        got = graph.get_predecessors(node)
        assert print_test(got, expected, node, "predecessors", clean)

        expected = get_successors(node, nodes, root)
        got = graph.get_successors(node)
        assert print_test(got, expected, node, "successors", clean)

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


    clean()

class Test_general(unittest.TestCase):

    def test_general_without_root(self):
        general(False)

    def test_general_with_root(self):
        general(True)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
