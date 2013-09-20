#!/usr/bin/env python

from common_test import *
from datetime import datetime
import random
import sys

def performance(node_number, has_root):

    #max number of successors
    max_number_successors = 10
    #max number of predecessors
    max_number_predecessors = 10
    
    #performance target (number of insertions per seconde)
    target = 50
    
    #empty lists (initialization)
    nodes = []
    successors = []
    predecessors = []
    
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    
    #some fixed attributs
    fix_attributes = {'jack': set(['1','2']), 'spare': 'youpi'}
    
    #function transforming <number> -> node_<number>
    def create_name_from_number(integer):
        return 'node_' + str(integer)
    
    #function generating the graph in python structures
    def generate_tree(node_number):
    
        #we create node_number of nodes
        for node in range(node_number):
            #we create a nice name for the node (node_<number>)
            node_name = create_name_from_number(node)
            #we add it to the node
            nodes.append(node_name)
            successors_node = []
            #for each nodes, we create a random number of successors < max_number_successors
            for j in range(random.randint(1, max_number_successors)):
                successor_name = create_name_from_number(random.randint(1, node_number))
                successors_node.append(successor_name)
            predecessors_node = []
            #for each nodes, we create a random number of predecessors < max_number_predecessors
            for j in range(random.randint(1, max_number_predecessors)):
                predecessor_name = create_name_from_number(random.randint(1, node_number))
                predecessors_node.append(predecessor_name)
            #we add the successors of the node in the list of successors lists (same with the predecessors)
            successors.append(successors_node)
            predecessors.append(predecessors_node)
    
    print(OKBLUE + "creating " + str(node_number)  + " nodes")
    #calling the generation function
    generate_tree(node_number)
    
    #creating the redis connexion
    r_server = redis.Redis("localhost")
    
    #creating a basic logger
    logging.basicConfig(format = '%(message)s')
    logger = logging.getLogger('redis')
    logger.parent.setLevel(logging.CRITICAL)
    
    #creating the graph object
    graph = Directed_graph(r_server, 'uniq', logger, has_root = has_root)
    
    #we define two process to write the nodes
    def process_one():
        for i in range(0,node_number):
            graph.write_on_node(nodes[i],successors[i],predecessors[i],fix_attributes)
    
    
    #we get the date before the insertion
    t1 = datetime.now()
    #create and launch the two processes
    print(OKBLUE + "starting the insertion")
    process_one()
    
    #when the two processes are ended
    #we get the date after the insertion 
    t2 = datetime.now()
    c = t2 - t1
    
    #we print(the number of node inserted per second)
    print( OKBLUE + "insertion completed")
    perf = node_number / c.total_seconds()
    
    if perf > target:
        print( OKGREEN + "####\nadding " + str(perf) + " nodes/second\n####")
        return_1 = True
    else:
        print( WARNING + "####\nadding " + str(perf) + " nodes/second\n####")
        return_1 = False
    
    #we do exactly the same to delete the inserted nodes
    def process_one():
        for i in range(0,node_number):
            graph.remove_node(nodes[i])
    
    t1 = datetime.now()
    print(OKBLUE + "starting deleting the nodes")
    process_one()
   
    t2 = datetime.now()
    c = t2 - t1
    print(OKBLUE + "delete completed")
    
    perf = node_number / c.total_seconds()
    
    graph.remove_node(graph.root)
    if perf > target:
        print( OKGREEN + "####\nremoving " + str(perf) + " nodes/second\n####" + WHITE)
        return_2 = True
    else:
        print( WARNING + "####\nremoving " + str(perf) + " nodes/second\n####" + WHITE)
        return_2 = False

    return return_1 and return_2

class Test_general(unittest.TestCase):

    def test_performance_without_root(self):
        print('\nPerformance without root:')
        assert performance(400, False)

    def test_performance_with_root(self):
        print('\nPerformance with root:')
        assert performance(400, True)

def main():
    unittest.main()

if __name__ == '__main__':

    try: 
        sys.argv[1]
    except IndexError:
        node_number = 400
        print("using the default number of nodes: 400")
        print("you can change it by passing an arg to the script")
        main()
    else:
        node_number = int(sys.argv[1])
        print('\nPerformance without root:')
        performance(node_number, False)
        print('\nPerformance with root:')
        performance(node_number, True)

