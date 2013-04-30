#!/usr/bin/env python

#importing directed_graph
from pygraph_redis.directed_graph import Directed_graph
import redis

#creating the redis connexion
r_server = redis.Redis("localhost")

#creating a basic logger
import logging
logging.basicConfig(format = '%(message)s')
logger = logging.getLogger('redis')
logger.parent.setLevel(logging.DEBUG)

#creating the graph object
graph = Directed_graph(r_server, 'uniq', logger)

#adding some nodes
graph.write_on_node('m1', ['c1', 'c2', 'c3', 'c4'], ['p1', 'p2', 'p3'],{'jack': set(['1','2']), 'spare': 'youpi'})
graph.write_on_node("m2", ["c1", "c3", "c4"], ["p2", "p3"],{'sape': '4139', 'guido': '4127'})
graph.write_on_node("m3", ["c1", "c3", "c4"], ["p2", "p3"],{})
graph.write_on_node("P1", ["p2", "p3"],[],{})

#printing some predecessors or successors
print(graph.get_predecessors("m1"))
print(graph.get_successors("m1"))
print(graph.get_predecessors("p2"))
print(graph.get_successors("p2"))
print(graph.get_successors("c3"))
print(graph.get_successors(graph.root))
print(graph.get_predecessors("c3"))

#getting an attributs list
print(graph.get_attributs_list('m2'))
#getting some attribut
print(graph.get_attribut('m2', 'guido'))
print(graph.get_attribut('m1', 'jack'))

#example of write off (suppression of some elements of a node, like predecessors, successors or attributs)
#getting the elements before
print(graph.get_attributs_list('m2'))
print(graph.get_predecessors("m2"))
print(graph.get_successors("m2"))

#removing the elements
graph.write_off_node("m2", ["c1"], ["p2", "p3"],['sape'])

#getting the elements after
print(graph.get_attributs_list('m2'))
print(graph.get_predecessors("m2"))
print(graph.get_successors("m2"))

#removing a node
graph.remove_node('m2')
print(graph.get_predecessors("m2"))
print(graph.get_successors("m2"))
print(graph.get_successors(graph.root))
