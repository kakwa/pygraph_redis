#!/usr/bin/env python

#importing directed_graph
from pygraph_redis.directed_graph import Directed_graph
import redis

#creating the redis connexion
r_server = redis.Redis("localhost")

#creating a basic logger
import logging

def main():
    logging.basicConfig(format = u'%(levelname)s %(message)s')
    logger = logging.getLogger(u'redis')
    logger.parent.setLevel(logging.ERROR)

    #creating the graph object
    graph = Directed_graph(r_server, u'uniq', logger, has_root = True)

    RED = '\033[91m'
    ORANGE = '\033[93m'
    GREEN = '\033[92m'

    #adding some nodes
    node1 = u'level_1_1'
    node2 = u'level_1_2'
    node3 = u'level_2_1'
    node4 = u'level_2_2'
    node5 = u'level_3_1'

    node1_predecessors = []
    node1_successors = [node3,node4]

    node2_predecessors = []
    node2_successors = [node3,node4]

    node3_predecessors = [node1,node2]
    node3_successors = [node5]

    node4_predecessors = [node1,node2]
    node4_successors = [node5]

    node5_predecessors = []
    node5_successors = []

    def clean():
        graph.remove_node(node1)
        graph.remove_node(node2)
        graph.remove_node(node3)
        graph.remove_node(node4)
        graph.remove_node(node5)
        graph.remove_node(graph.root)

    def print_test(got,expected,node,nature):
        if got != expected:
            print RED + "ERROR: "+ node + " " + nature +" is not as it should be"
            print ORANGE +"GOT:"
            print got 
            print "EXPECTED:"
            print expected 
            clean()
            return 1
        else:
            print GREEN + node + " " + nature +": Ok"


    attributes = {u'jack': set([u'1',u'2']), u'spare': u'youpi'}

    graph.write_on_node(node3, node3_successors, node3_predecessors, attributes)
    graph.write_on_node(node4, node4_successors, node4_predecessors, attributes)
    graph.write_on_node(node1, node1_successors, node1_predecessors, attributes)
    graph.write_on_node(node2, node2_successors, node2_predecessors, attributes)
    graph.write_on_node(node5, node5_successors, node5_predecessors, attributes)

    #printing some predecessors or successors
    name = graph.root
    got = graph.get_successors(name)
    expected = set(['level_1_2', 'level_1_1']) 
    if print_test(got, expected, name, "successors") == 1:
        return 1

    got = graph.get_predecessors(name)
    expected = set([]) 
    if print_test(got, expected, name, "predecessors") == 1:
        return 1

    name = node1
    got = graph.get_successors(name)
    expected = set(['level_2_1', 'level_2_2'])
    if print_test(got, expected, name, "successors") == 1:
        return 1

    got = graph.get_predecessors(name)
    expected = set(['RO_@@@_OT'])
    if print_test(got, expected, name, "predecessors") == 1:
        return 1

    name = node2
    got = graph.get_successors(name)
    expected = set(['level_2_1', 'level_2_2'])
    if print_test(got, expected, name, "successors") == 1:
        return 1

    got = graph.get_predecessors(name)
    expected = set(['RO_@@@_OT'])
    if print_test(got, expected, name, "predecessors") == 1:
        return 1

    name = node3
    got = graph.get_successors(name)
    expected = set(['level_3_1']) 
    if print_test(got, expected, name, "successors") == 1:
        return 1

    got = graph.get_predecessors(name)
    expected = set(['level_1_2', 'level_1_1'])
    if print_test(got, expected, name, "predecessors") == 1:
        return 1

    name = node4
    got = graph.get_successors(name)
    expected = set(['level_3_1']) 
    if print_test(got, expected, name, "successors") == 1:
        return 1

    got = graph.get_predecessors(name)
    expected = set(['level_1_2', 'level_1_1'])
    if print_test(got, expected, name, "predecessors") == 1:
        return 1

    name = node5
    got = graph.get_successors(name)
    expected = set([])
    if print_test(got, expected, name, "successors") == 1:
        return 1

    got = graph.get_predecessors(name)
    expected = set(['level_2_1', 'level_2_2'])
    if print_test(got, expected, name, "predecessors") == 1:
        return 1


    clean()
    return 0

if __name__ == "__main__":
    exit(main())
