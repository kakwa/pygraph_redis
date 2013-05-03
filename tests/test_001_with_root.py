#!/usr/bin/env python
# -*- coding: utf-8 -*-

#importing directed_graph
from pygraph_redis.directed_graph import Directed_graph
import redis
import sys

def convert(seti):
    if sys.version_info < (3, 0):
        if type(seti) == type(set([])):
            res = set([])
            for i in seti:
                res.add(i.decode('utf-8'))
            return res
        else:
            return seti.decode('utf-8')
    else:
        return seti


#creating the redis connexion
r_server = redis.Redis("localhost")

#creating a basic logger
import logging

def main():
    logging.basicConfig(format = '%(levelname)s %(message)s')
    logger = logging.getLogger('redis')
    logger.parent.setLevel(logging.ERROR)

    #creating the graph object
    graph = Directed_graph(r_server, 'uniq', logger, has_root = True)

    RED = '\033[91m'
    ORANGE = '\033[93m'
    GREEN = '\033[92m'

    #adding some nodes
    node1 = convert('level_1_1☭')
    node2 = convert('level_1_2')
    node3 = convert('☭level_2_1')
    node4 = convert('level_2_2')
    node5 = convert('level_3_1')

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
            print(RED + "ERROR: "+ node + " " + nature +" is not as it should be")
            print(ORANGE +"GOT:")
            print(got )
            print("EXPECTED:")
            print(expected )
            clean()
            return 1
        else:
            print(GREEN + node + " " + nature +": Ok")


    attributes = {convert('☭jack'): set([convert('1'),convert('2')]), convert('spare☭'): convert('☭youpi')}
 #
    graph.write_on_node(node3, node3_successors, node3_predecessors, attributes)
    graph.write_on_node(node4, node4_successors, node4_predecessors, attributes)
    graph.write_on_node(node1, node1_successors, node1_predecessors, attributes)
    graph.write_on_node(node2, node2_successors, node2_predecessors, attributes)
    graph.write_on_node(node5, node5_successors, node5_predecessors, attributes)
 
    #printing some predecessors or successors
    name = graph.root
    got = graph.get_successors(name)
    expected = convert({'level_1_2', 'level_1_1☭'}) 
    if print_test(got, expected, name, "successors") == 1:
        return 1
 
    got = graph.get_predecessors(name)
    expected = set([]) 
    if print_test(got, expected, name, "predecessors") == 1:
        return 1
 
    name = node1
    got = graph.get_successors(name)
    expected = set([node3, node4]) 
    if print_test(got, expected, name, "successors") == 1:
        return 1
 
    got = graph.get_predecessors(name)
    expected = set(['RO_@@@_OT'])
    if print_test(got, expected, name, "predecessors") == 1:
        return 1
 
    name = node2
    got = graph.get_successors(name)
    expected = set([node3, node4]) 
    if print_test(got, expected, name, "successors") == 1:
        return 1
 
    got = graph.get_predecessors(name)
    expected = set(['RO_@@@_OT'])
    if print_test(got, expected, name, "predecessors") == 1:
        return 1
 
    name = node3
    got = graph.get_successors(name)
    expected = set([node5]) 
    if print_test(got, expected, name, "successors") == 1:
        return 1
 
    got = graph.get_predecessors(name)
    expected = set([node2, node1]) 
    if print_test(got, expected, name, "predecessors") == 1:
        return 1
 
    name = node4
    got = graph.get_successors(name)
    expected = set([node5]) 
    if print_test(got, expected, name, "successors") == 1:
        return 1
 
    got = graph.get_predecessors(name)
    expected = set([node2, node1])
    if print_test(got, expected, name, "predecessors") == 1:
        return 1
 
    name = node5
    got = graph.get_successors(name)
    expected = set([])
    if print_test(got, expected, name, "successors") == 1:
        return 1
 
    got = graph.get_predecessors(name)
    expected = set([node3, node4])
    if print_test(got, expected, name, "predecessors") == 1:
        return 1
 
 
    clean()
    print(GREEN + "printing attributs list after cleaning (must be empty)")

    #printing some predecessors or successors
    name = graph.root
    got = graph.get_successors(name)
    expected = set([]) 
    if print_test(got, expected, name, "successors") == 1:
        return 1
 
    got = graph.get_predecessors(name)
    expected = set([]) 
    if print_test(got, expected, name, "predecessors") == 1:
        return 1
 
    name = node1
    got = graph.get_successors(name)
    expected = set([]) 
    if print_test(got, expected, name, "successors") == 1:
        return 1
 
    got = graph.get_predecessors(name)
    expected = set([]) 
    if print_test(got, expected, name, "predecessors") == 1:
        return 1
 
    name = node2
    got = graph.get_successors(name)
    expected = set([]) 
    if print_test(got, expected, name, "successors") == 1:
        return 1
 
    got = graph.get_predecessors(name)
    expected = set([]) 
    if print_test(got, expected, name, "predecessors") == 1:
        return 1
 
    name = node3
    got = graph.get_successors(name)
    expected = set([]) 
    if print_test(got, expected, name, "successors") == 1:
        return 1
 
    got = graph.get_predecessors(name)
    expected = set([]) 
    if print_test(got, expected, name, "predecessors") == 1:
        return 1
 
    name = node4
    got = graph.get_successors(name)
    expected = set([]) 
    if print_test(got, expected, name, "successors") == 1:
        return 1
 
    got = graph.get_predecessors(name)
    expected = set([]) 
    if print_test(got, expected, name, "predecessors") == 1:
        return 1
 
    name = node5
    got = graph.get_successors(name)
    expected = set([])
    if print_test(got, expected, name, "successors") == 1:
        return 1
 
    got = graph.get_predecessors(name)
    expected = set([]) 
    if print_test(got, expected, name, "predecessors") == 1:
        return 1
 

    return 0

if __name__ == "__main__":
    exit(main())
