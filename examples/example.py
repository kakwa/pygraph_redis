#!/usr/bin/env python

#importing directed_graph
from pygraph_redis.directed_graph import Directed_graph
import redis

#creating the redis connexion
r_server = redis.Redis("localhost")

#creating a basic logger
import logging
logging.basicConfig(format = u'%(message)s')
logger = logging.getLogger(u'redis')
logger.parent.setLevel(logging.DEBUG)

#creating the graph object
graph = Directed_graph(r_server, u'uniq', logger)

#adding some nodes
graph.write_on_node(u'm1', [u'c1', u'c2', u'c3', u'c4'], [u'p1', u'p2', u'p3'],{u'jack': set([u'1',u'2']), u'spare': u'youpi'})
graph.write_on_node(u"m2", [u"c1", u"c3", u"c4"], [u"p2", u"p3"],{u'sape': u'4139', u'guido': u'4127'})
graph.write_on_node(u"m3", [u"c1", u"c3", u"c4"], [u"p2", u"p3"],{})
graph.write_on_node(u"P1", [u"p2", u"p3"],[],{})

#printing some predecessors or successors
print graph.get_predecessors(u"m1")
print graph.get_successors(u"m1")
print graph.get_predecessors(u"p2")
print graph.get_successors(u"p2")
print graph.get_successors(u"c3")
print graph.get_successors(graph.root)
print graph.get_predecessors(u"c3")

#getting an attributs list
print graph.get_attributs_list(u'm2')
#getting some attribut
print graph.get_attribut(u'm2', u'guido')
print graph.get_attribut(u'm1', u'jack')

#example of write off (suppression of some elements of a node, like predecessors, successors or attributs)
#getting the elements before
print graph.get_attributs_list(u'm2')
print graph.get_predecessors(u"m2")
print graph.get_successors("m2")

#removing the elements
graph.write_off_node(u"m2", [u"c1"], [u"p2", u"p3"],[u'sape'])

#getting the elements after
print graph.get_attributs_list(u'm2')
print graph.get_predecessors(u"m2")
print graph.get_successors(u"m2")

#removing a node
graph.remove_node(u'm2')
print graph.get_predecessors(u"m2")
print graph.get_successors(u"m2")
print graph.get_successors(graph.root)
