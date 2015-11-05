#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common_test import *

r_server = redis.Redis("localhost")

#creating the graph object
graph = Directed_graph(r_server, 'uniq', logger, has_root = True)

#adding some nodes
node1 = 'level_1_1'
node2 = 'level_1_2'
node3 = 'level_2_1'
node4 = 'level_2_2'
node5 = 'level_3_1'

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


attributes1 = {'☭jack': set(['1','2']), 'spare☭': '☭youpi'}
attributes2 = {'jacko': set(['1','2','test']), 'spare☭': '☭youpi', 'bip' : 'bip', 'bip' : 'bop'}
attributes3 = {'☭jack': set(['1','2']), 'spare☭': '☭youpi'}
attributes4 = {'☭jack': set(['1','2']), 'spare☭': '☭youpi'}
attributes5 = {'jacko': set(['1','2','test']), 'spare☭': '☭youpi', 'bip' : 'bip'}

def create_graph():
    graph.write_on_node(node3, node3_successors, node3_predecessors, attributes3)
    graph.write_on_node(node4, node4_successors, node4_predecessors, attributes4)
    graph.write_on_node(node1, node1_successors, node1_predecessors, attributes1)
    graph.write_on_node(node2, node2_successors, node2_predecessors, attributes2)
    graph.write_on_node(node5, node5_successors, node5_predecessors, attributes5)
 
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
        return 0

def attributes_values(legacy=False):
    if legacy:
        graph.legacy_mode = True

    create_graph()
    
    #printing some attributs list
    name = graph.root
    got = graph.get_attributs_list(name)
    expected = set([]) 
    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node1
    got = graph.get_attributs_list(name)
    expected = convert(set(['spare☭', '☭jack']))

    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node2
    got = graph.get_attributs_list(name)
    expected = convert({'jacko', 'spare☭', 'bip'})
    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node3
    got = graph.get_attributs_list(name)
    expected = convert({'☭jack', 'spare☭'})
    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node4
    got = graph.get_attributs_list(name)
    expected = convert({'☭jack', 'spare☭'})
    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node5
    got = graph.get_attributs_list(name)
    expected = convert({'jacko', 'spare☭', 'bip'})
    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node5
    got = graph.get_attributs_list(name)
    expected = convert({'jacko', 'spare☭', 'bip'})
    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node5
    got = graph.get_attribut(name,'jacko')
    expected =  convert(set(['1','2','test'] ))
    if print_test(got, expected, name, "attribut") == 1:
        graph.legacy_mode = False
        return False
    
    name = node5
    got = graph.get_attribut(name,'spare☭')
    expected =  convert('☭youpi')
    if print_test(got, expected, name, "attribut") == 1:
        graph.legacy_mode = False
        return False

    clean()

    print(GREEN + "printing attributs list after cleaning (must be empty)")

    #printing some attributs list after clean 
    name = graph.root
    got = graph.get_attributs_list(name)
    expected = set([]) 
    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node1
    got = graph.get_attributs_list(name)
    expected = set([])

    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node2
    got = graph.get_attributs_list(name)
    expected = set([]) 
    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node3
    got = graph.get_attributs_list(name)
    expected = set([]) 
    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node4
    got = graph.get_attributs_list(name)
    expected = set([]) 
    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node5
    got = graph.get_attributs_list(name)
    expected = set([]) 
    if print_test(got, expected, name, "attributs_list") == 1:
        graph.legacy_mode = False
        return False
 
    name = node5
    got = graph.get_attribut(name,'spare☭')
    expected =  None
    if print_test(got, expected, name, "attribut") == 1:
        graph.legacy_mode = False
        return False
 
    return True

def attributes_len(legacy=False):
    if legacy:
        graph.legacy_mode = True
    create_graph()

    #printing some attributs list
    name = node5
    got = graph.get_attribut_len(name,'jacko')
    expected = 3
    if print_test(got, expected, name, "attribut length") == 1:
        graph.legacy_mode = False
        return False

    name = node5
    got = graph.get_attribut_len(name, convert('spare☭'))
    expected =  1
    if print_test(got, expected, name, "attribut length") == 1:
        graph.legacy_mode = False
        return False

    name = node5
    got = graph.get_attribut_len(name, convert('spare☭_does_not_exists'))
    expected =  0
    if print_test(got, expected, name, "attribut length") == 1:
        graph.legacy_mode = False
        return False

    clean()

    return True

class Test_attributs(unittest.TestCase):

    def test_attributes_values(self):
        assert attributes_values()

    def test_attributes_len(self):
        assert attributes_len()

    def test_attributes_values_legacy(self):
        assert attributes_values(legacy=True)

    def test_attributes_len_legacy(self):
        assert attributes_len(legacy=True)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
