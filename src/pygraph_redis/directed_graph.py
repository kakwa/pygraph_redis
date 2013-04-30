# -*- coding: utf-8 -*-

import redis
import re
import time

class Directed_graph:
    """this class implement directed graph inside redis"""

# redis key format:
#   <graph name><sep><node_name><sep><variable_name>[<sep><other>]*
#   
#   <graph name>: name of the graph
#   <sep>: the key fields separator 
#        (this string should not be in node_name or variable_name,
#         otherwise, there is a redis key collision possibility)
#   <node_name>: name of the node
#   <variable_name>: name of the variable
#   [<sep><other>]: optional extension
#
# to avoid key collision, you must carefully choose the separator
#   it must not be included in any node name or node attribut name.

    def __init__(self, connexion, graph, logger, 
                      separator = '@@@', has_root = False
                ):
        """initialize a Redisgraph instance
        connexion: a redis connexion
        graph: a graph name (string)
        logger: a logger 
        separator: fields separator must not be in an node name 
            (default @\U0001F4A9@) (string)
        has_root: flag to set if node with no predecessors must be linked 
            to a factice "root" node (default False) (boolean)
        """
        self.connexion = connexion  #the redis connexion
        self.graph = graph          #the name of the graph
        self.logger = logger        #the logger
        self.separator = separator  #the key separator
        self.has_root = has_root    #flag for handling of node 
                                    #   with no predecessor
        self.root = 'RO_' + self.separator + '_OT' #name of the root 
                                                    #   (ultimate predecessor)

    def get_root_name(self):
        """return the name of the graph root
           useful only if you have has_root flag enabled
        """
        return self.root

    def write_on_node(self, node, successors, predecessors, attributs):
        """add given successors, predecessors, attributs to a given node
                (create the node if doesn't exists) 
        node: the name of the node (string)
        successors: list of chidren (string list)
        predecessors: list of predecessors (string list)
        attributs: attributes of the node (dictionnary of string)
        """
        self._ensure_not_separator(node)
    
        for successor in successors:
            #for each successor, adding "node"
            #as a predecessor of "successor"
            self._add_predecessor(successor, node)
            #for each successor, adding "successor" 
            #as a successor of "node"
            self._add_successor(node, successor)
            #handleling node with no predecessor
            #self.handle_no_predecessor(successor)

            self.logger.debug("ensure node %(node)s is predecessor"\
                " of %(successor)s" % {
                'successor': successor,
                'node':node
                }
                )
        
        #if node has no predecessors, adding root as predecessor
        for predecessor in predecessors:
            #for each predecessor, adding "node" as
            #a successor of "predecessor"
            self._add_successor(predecessor, node)
            #for each predecessor, adding "predecessor" 
            #as a predecessor of "node"
            self._add_predecessor(node, predecessor)
            #handleling node with no predecessor
            self.handle_no_predecessor(predecessor)

            self.logger.debug("ensure node %(node)s is successor"\
                " of %(predecessor)s" % {
                'predecessor': predecessor,
                'node': node
                }
                )

        #handleling node with no predecessor
        self.handle_no_predecessor(node)
        
        #adding the attributs
        for attribut_name in attributs:
            #attribut_name is a key of the dictionary (must be unicode string)
            #value is the value attached to this key (could be set or string)
            value = attributs[attribut_name]

            self.logger.debug("adding attibut %(attribut_name)s"\
                " with value %(value)s on"\
                    " node %(node)s" % {
                    'attribut_name': attribut_name,
                    'value': value, 
                    'node':node
                    }
            )
            #ensure that attribut_name doesn't contain the separator
            #(redis key collisition)
            self._ensure_not_separator(attribut_name)
            #adding the attribut
            self._add_attribut(node, attribut_name, value)

    def write_off_node(self, node, successors, predecessors, attributs):
        """remove given successors, predecessors, attributs to a given node
        node: the name of the node (string)
        successors: list of chidren (string list)
        predecessors: list of predecessors (string list)
        attributs: attributes of the node (dictionnary or list of string)
        """
        #removing the successors
        for successor in successors:
            #reverse of write_on_node
            self._remove_predecessor(successor, node)
            self._remove_successor(node, successor)
            self.handle_no_predecessor(successor)

            self.logger.debug("ensure node %(node)s is no longer"\
                " predecessor of %(successor)s" % {
                'successor': successor,
                'node': node
                }
                )

        #removing the predecessors
        for predecessor in predecessors:
            #reverse of write_on_node
            self._remove_predecessor(node, predecessor)
            self._remove_successor(predecessor, node)
            self.handle_no_predecessor(predecessor)

            self.logger.debug("ensure node %(node)s is no longer"\
                " successor of %(predecessor)s" % {
                'predecessor': predecessor,
                'node': node
                }
            )

        #handleling the orphans
        self.handle_no_predecessor(node)
        
        #removing the attributs
        for attribut_name in attributs:
            #reverse of write_on_node
            self._remove_attribut(node, attribut_name)
            self.logger.debug("remove attibut %(attribut_name)s on"\
                " node %(node)s" % {
                'attribut_name':attribut_name,
                'node': node
                }
            )
    
    def remove_node(self, node):
        """completly remove a given node from the graph
        node: the name of the node (string)
        """
        for successor in self.get_successors(node):
            #here, only handle the succesors
            #(node will be removed completely later)
            self._remove_predecessor(successor, node)
            self.handle_no_predecessor(successor)

            self.logger.debug("ensure node %(node)s is no longer"\
                " predecessor of %(successor)s" % {
                'successor': successor, 
                'node': node
                }
            )

        for predecessor in self.get_predecessors(node):
            #here, only handle the predecessor
            #(node will be removed completely later)
            self._remove_successor(predecessor, node)
            self.handle_no_predecessor(predecessor)

            self.logger.debug("ensure node %(node)s is no longer"\
                " successor of %(predecessor)s" % {
                'predecessor': predecessor,
                'node': node
                }
            )

        for attribut_name in self.get_attributs_list(node):
            #remove each attribut of the node
            self._remove_attribut(node, attribut_name)

        self.logger.debug("remove node %(node)s from database" % {
            'node': node
            }
        )
 
        #remove all the other keys of the node
        redis_key = self._gen_key(node, ['attribut_list', ])
        self.connexion.delete(redis_key)

        redis_key = self._gen_key(node, ['successors', ])
        self.connexion.delete(redis_key)

        redis_key = self._gen_key(node, ['predecessors', ])
        self.connexion.delete(redis_key)

    def get_successors(self, node):
        """get the successors of a given node
           node: the node name (string)
           return: a set of successors
        """
        return self._get_relative('successors', node)

    def get_predecessors(self, node):
        """get the predecessors of a given node
           node: the node name (string)
           return: a set of predecessors
        """
        return self._get_relative('predecessors', node)

    def get_attributs_list(self, node):
        """return the attributs name list of a node
           node: the name of the node (string)
           return: set of attribut names
        """
        self.logger.debug("get attributs list of node %(node)s" % {
            'node': node
            }
        )
        redis_key = self._gen_key(node, ['attributs_list', ])
        return self.connexion.smembers(redis_key)

    def get_attribut(self, node, attribut_name):
        """return the value of a given attribut of a node
           node: the name of the node (string)
           attribut_name: the name of the attribut (string)
           return: the attribut value (either a set of string)
                    or a string
        """
        self.logger.debug("get attribut %(attribut_name)s"\
            " of node %(node)s" % {
            'attribut_name': attribut_name,
            'node': node
            }
        )

        #get the attribut value (different type handling)
        redis_key = self._gen_key(node, ['attribut', 'attribut_name' ])
        #get the attribut type
        key_type = self.connexion.type(redis_key)
        if key_type == 'string':
            return self.connexion.get(redis_key) 
        elif key_type == 'set':
            return self.connexion.smembers(redis_key)
        else:
            return None
 
            
    def _gen_key(self, node, type_list):
        """generate the key
        node: the name of the node (string)
        type_list: list of <variable_name> (string list)
        return: a key 
            <graph name><sep><node_name><sep><variable_name>[<sep><other>]*
            (string)
        """
        key = "%(graph)s%(separator)s%(node)s" % {
            'node' : node,
            'graph' : self.graph,
            'separator' :  self.separator
            }
        for t in type_list:
            key = key + self.separator + t
        return key   

    def _add_attribut(self, node, attribut_name, value):
        """add an attribut to a node
        node: the node name (string)
        attribut_name: name of the attribut (string)
        value: value of the attribut (string or set of string)
        """
        #different handling for string or set of string
        if type(value) is str: 
            #if it's a string
            #adding the attribut value
            redis_key = self._gen_key(node, ['attribut', 'attribut_name' ])
            self.connexion.delete(redis_key)
            self.connexion.set(redis_key, value)

        elif type(value) is set:
            #set it's a set
            redis_key = self._gen_key(node, ['attribut', 'attribut_name' ])
            self.connexion.delete(redis_key)
            for sub_value in value:
                #adding the attribut value (it's a set -> loop)
                self.connexion.sadd(redis_key, sub_value) 
        else:
            self.logger.debug("unhandle type %(type)s"\
                " for attribut %(attribut_name)s on"\
                    " node %(node)s" % {
                    'attribut_name': attribut_name,
                    'type': str(type(value)),
                    'node': node
                    }
            )

        redis_key = self._gen_key(node, ['attributs_list', ])
        self.connexion.sadd(redis_key, attribut_name)

    def _remove_attribut(self, node, attribut_name):
        redis_key = self._gen_key(node, ['attribut', 'attribut_name' ])
        self.connexion.delete(redis_key)
        redis_key = self._gen_key(node, ['attribut_type', 'attribut_name' ])
        self.connexion.delete(redis_key)

        redis_key = self._gen_key(node, ['attributs_list', ])
        self.connexion.srem(redis_key, attribut_name)

    def _ensure_not_separator(self, name):
        test = re.search(self.separator, name,0)
        if not test == None:
            self.logger.warning("attribut or node %(name)s already contains"\
                " key separator %(sep)s, this could lead to"\
                " strange behaviours (keys collision)" % {
                'name' : name,
                'sep' : self.separator
                }
            )         
            return 1
        else:
            return 0

    def _get_relative(self, relative_type, node):
        redis_key = self._gen_key(node, [relative_type, ])

        self.logger.debug("get %(relative_type)s of node %(node)s, "\
            "requested key: %(key)s" % {
            'relative_type': relative_type,
            'node' : node,
            'key' : redis_key
            }
        )

        return self.connexion.smembers(redis_key)

    def _remove_predecessor(self, node, predecessor):
        """remove a predecessor from a node
        node: the node name (string)
        predecessor: the predecessor name (string)
        """
        self._remove_relative('predecessors', node, predecessor)

    def _remove_successor(self, node, successor):
        """remove a successor from a node
        node: the node name (string)
        successor: the successor name (string)
        """
        self._remove_relative('successors', node, successor)

    def _remove_relative(self, relative_type, node, relative):
        """remove a relative from a node:
        relative_type: "successors" or "predecessors" (string)
        node: node name (string)
        relative: name of the relative (string)
        """
        redis_key = self._gen_key(node, [relative_type, ])

        self.connexion.srem(redis_key
            , "%(relative)s" % {
                'relative' : relative
                }
        )

    def _add_successor(self, node, relative):
        """add a successor to a node
        node: name of the node (string)
        relative: name of the successor (string)
        """
        self._add_relative('successors', node, relative)

    def _add_predecessor(self, node, relative):
        """add a predecessor to a node
        node: name of the node (string)
        relative: name of the predecessor (string)
        """
        self._add_relative('predecessors', node, relative)

    def _add_relative(self, relative_type, node, relative):
        """ this function adds a relative to a node:
        relative_type: "successors" or "predecessors" (string)
        node: node name (string)
        relative: name of the relative (string)
        """
        redis_key = self._gen_key(node, [relative_type, ])

        self.connexion.sadd(redis_key
        , "%(relative)s" % {
        'relative' : relative
        })

    def handle_no_predecessor(self, node):
        """handle root, if node has no predecessor, graph root becomes
             its predecessor
        if node as graph root and another node, remove graph root 
            as predecessor
        node: node name (string)
        """
        if not self.has_root:
            return

        if node == self.root:
            return

        redis_key = self._gen_key(node, ['predecessors', ])
        rootismember = self.connexion.sismember(redis_key, self.root)
        card = self.connexion.scard(redis_key)
        if card == 0:
            self._add_predecessor(node, self.root)
            self._add_successor(self.root, node)

        elif card > 1 and rootismember == 1:
            self._remove_predecessor(node, self.root)
            self._remove_successor(self.root, node)
            

