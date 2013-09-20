# -*- coding: utf-8 -*-
from pygraph_redis.directed_graph import Directed_graph
import unittest
import redis
import sys
import logging

#gets the predecessors of a node from a hash of hash (as followed)
def get_predecessors(tested_node, nodes_list, has_root):
    predecessors_list = nodes_list[tested_node]['predecessors']
    for node in nodes_list:
        if tested_node in nodes_list[node]['successors']:
            predecessors_list.append(node)
    if has_root and predecessors_list == []:
        return set(['RO_@@@_OT'])
    else:
        return set(predecessors_list)

#gets the successors of a node from a hash of hash (as followed)
def get_successors(tested_node, nodes_list, has_root):
    successors_list = nodes_list[tested_node]['successors']
    for node in nodes_list:
        if tested_node in nodes_list[node]['predecessors']:
            successors_list.append(node)
    return set(successors_list)


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

logging.basicConfig(format = '%(levelname)s %(message)s')
logger = logging.getLogger('redis')
logger.parent.setLevel(logging.ERROR)

RED = '\033[91m'
ORANGE = '\033[93m'
GREEN = '\033[92m'
WHITE = '\033[0m'

def print_test(got, expected, node, nature, clean):
    if got != expected:
        print(RED + "ERROR: "+ node + " " + nature +" is not as it should be")
        print(ORANGE +"GOT:")
        print(got )
        print("EXPECTED:")
        print(expected)
        print(WHITE + '\n' )
        clean()
        return False
    else:
        print(GREEN + node + " " + nature +": Ok" + WHITE)
        return True

#we create the attributes for a small graph
node1_generic = convert('level_1_1☭')
node2_generic = convert('level_1_2')
node3_generic = convert('☭level_2_1')
node4_generic = convert('level_2_2')
node5_generic = convert('level_3_1')

nodes_generic = { node1_generic :
             { 'predecessors': [],
               'successors':   [node3_generic, node4_generic],
             },
          node2_generic :
             { 'predecessors': [],
               'successors':   [node3_generic, node4_generic],
             },
          node3_generic :
             { 'predecessors': [node1_generic, node2_generic],
               'successors':   [node5_generic],
             },
          node4_generic :
             { 'predecessors': [node1_generic, node2_generic],
               'successors':   [node5_generic],
             },
          node5_generic :
             { 'predecessors': [],
               'successors':   [],
             },
         }
attributes_generic = {convert('☭jack'): set([convert('1'),convert('2')]), convert('spare☭'): convert('☭youpi')}   
 

def generic_clean(graph):
    graph.remove_node(node1_generic)
    graph.remove_node(node2_generic)
    graph.remove_node(node3_generic)
    graph.remove_node(node4_generic)
    graph.remove_node(node5_generic)
    graph.remove_node(graph.root)

def create_generic_graph(graph):

    #we create the graph
    for node in nodes_generic:
        graph.write_on_node(node, nodes_generic[node]['successors'], nodes_generic[node]['predecessors'], attributes_generic)

