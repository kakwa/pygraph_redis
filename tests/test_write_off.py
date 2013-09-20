# -*- coding: utf-8 -*-
from common_test import *

def write_off(root):

    graph = Directed_graph(r_server, 'uniq2', logger, has_root = root)

    generic_clean(graph)
    create_generic_graph(graph)

    nodes = nodes_generic.copy()

    def clean():
        generic_clean(graph)

    def check():
        #we check that we have the correct successors/predecessors for each nodes
        for node in nodes:
            expected = get_predecessors(node, nodes, root)
            got = graph.get_predecessors(node)
            assert print_test(got, expected, node, "predecessors", clean)

            expected = get_successors(node, nodes, root)
            got = graph.get_successors(node)
            assert print_test(got, expected, node, "successors", clean)

    def clean1():
        print(WHITE + "write off on node " + node1_generic + WHITE)
        graph.write_off_node(node1_generic, [node3_generic], [],[convert('☭jack')])
        nodes[node1_generic]['successors'] = [node4_generic]
        nodes[node3_generic]['predecessors'] = [node2_generic]

    check()

    clean1()
    check()

    name = node1_generic
    got = graph.get_attributs_list(name)
    expected = {convert('spare☭')}
    assert print_test(got, expected, name, "attributes list", clean)

    clean()

class Test_write_off(unittest.TestCase):

    def test_without_root(self):
        print("\nTest write off without root")
        write_off(False)

    def test_with_root(self):
        print("\nTest write off with root")
        write_off(True)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
