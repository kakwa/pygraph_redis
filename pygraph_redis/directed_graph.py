# -*- coding: utf-8 -*-

import redis
import re
import os

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
            (default @@@) (string)
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
        self.transactions = {} #dictionnary of transactions

        self.re_check_separator = re.compile(separator, 0) 
                #compiled regular expression used to check 
                #that separator is not in the key
                #(warn about possible key collision)

        self.legacy_mode = False #small flag for a legacy mode 
        #(support of lua scripting in both python-redis and redis-server


        #a small lua script to handle the has_root option
        # first arg is the node name, second arg is the node predecessors key
        self.lua_handle_no_predecessor = ("""
        local rootismember = redis.call('SISMEMBER', ARGV[2], '%(ROOT)s')
        local card = redis.call('SCARD', ARGV[2])
        if card == 0 
            then redis.call('SADD', ARGV[2], '%(ROOT)s')
                 redis.call('SADD', '%(ROOTSUCC)s', ARGV[1])
        end
        if card > 1 and rootismember == 1
        then redis.call('SREM', ARGV[2], '%(ROOT)s')
             redis.call('SREM', '%(ROOTSUCC)s', ARGV[1])
        end
        """ % {
            'ROOTSUCC' : self._gen_key(self.root, ['successors', ]),
            'ROOT' : self.root
            }
        )

        #we try to register the script
        try:
            self._handle_no_predecessor_script = self.connexion.register_script(
                self.lua_handle_no_predecessor)

        except redis.exceptions.ResponseError:
            #server is to old for lua scripting
            self.legacy_mode = True
            self.logger.info('redis server < 2.6.0, using legacy mode, no atomicity')

        except AttributeError:
            #redis-pyton is to old for lua scripting
            self.legacy_mode = True
            self.logger.info('redis-python < 2.7.0, using legacy mode, no atomicity')


        #if we are not in legacy mode, we try to register other lua scripts
        if not self.legacy_mode:

            #a small lua script to remove all the attributes of a given node
            # first arg is the node name, second arg is the node attributs key
            self.lua_remove_all_attributs = ("""
            local attributs = redis.call('SMEMBERS', ARGV[1]..'%(sep)sattributs_list')
            for i, attribut in ipairs(attributs) do
                redis.call('DEL', ARGV[1]..'%(sep)sattribut%(sep)s'..attribut)
            end
            redis.call('DEL', ARGV[1]..'%(sep)sattribut_list')
            """ % {
                'sep' : self.separator
                }
            )

            #we register the script
            #<graph name><sep><node_name><sep><variable_name>[<sep><other>]*
            self.remove_all_attributes_script = self.connexion.register_script(
                    self.lua_remove_all_attributs)

            #a small lua script to remove a node from its predecessors and successors
            # first arg is the node name
            self.lua_remove_node_successors_predecessors = ("""
            local predecessors = redis.call('SMEMBERS', '%(graph)s%(sep)s'..ARGV[1]..'%(sep)spredecessors')
            local successors = redis.call('SMEMBERS', '%(graph)s%(sep)s'..ARGV[1]..'%(sep)ssuccessors')
            for i, predecessor in ipairs(predecessors) do
                redis.call('SREM', '%(graph)s%(sep)s'..predecessor..'%(sep)ssuccessors', ARGV[1])
                        end
            for i, successor in ipairs(successors) do
                local predecessors_key = '%(graph)s%(sep)s'..successor..'%(sep)spredecessors'
                redis.call('SREM', predecessors_key, ARGV[1])
            end 
            """ % {
                'sep' : self.separator, 
                'graph' : self.graph
                }
            )
            self.lua_handle_root_remove = ("""
            for i, successor in ipairs(successors) do
                local predecessors_key = '%(graph)s%(sep)s'..successor..'%(sep)spredecessors'
                local card = redis.call('SCARD', predecessors_key)
                if card == 0 
                then redis.call('SADD', predecessors_key, '%(ROOT)s')
                    redis.call('SADD', '%(ROOTSUCC)s', successor)
                end
            end
            """ % {
                'sep' : self.separator, 
                'graph' : self.graph,
                'ROOTSUCC' : self._gen_key(self.root, ['successors', ]),
                'ROOT' : self.root
                }
            )

            if has_root:
                #we register the script
                self.remove_node_successors_predecessors_script = self.connexion.register_script(
                    self.lua_remove_node_successors_predecessors +
                    self.lua_handle_root_remove
                    )
            else:
                #we register the script
                self.remove_node_successors_predecessors_script = self.connexion.register_script(
                    self.lua_remove_node_successors_predecessors)




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

        trans_id = self._gen_transaction()
    
        for successor in successors:
            #for each successor, adding "node"
            #as a predecessor of "successor"
            self._add_predecessor(successor, node, trans_id)
            #for each successor, adding "successor" 
            #as a successor of "node"
            self._add_successor(node, successor, trans_id)
            #handleling node with no predecessor
            self._handle_no_predecessor(successor, trans_id)

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
            self._add_successor(predecessor, node, trans_id)
            #for each predecessor, adding "predecessor" 
            #as a predecessor of "node"
            self._add_predecessor(node, predecessor, trans_id)
            #handleling node with no predecessor
            self._handle_no_predecessor(predecessor, trans_id)

            self.logger.debug("ensure node %(node)s is successor"\
                " of %(predecessor)s" % {
                'predecessor': predecessor,
                'node': node
                }
                )

        #handleling node with no predecessor
        self._handle_no_predecessor(node, trans_id)
        
        #adding the attributs
        for attribut_name in attributs:
            #attribut_name is a key of the dictionary (must be unicode string)
            #value is the value attached to this key (could be set or string)
            value = attributs[attribut_name]

            self.logger.debug("adding attibut %(attribut_name)s"\
                    " node %(node)s" % {
                    'attribut_name': attribut_name,
                    'node': node
                    }
            )
            #ensure that attribut_name doesn't contain the separator
            #(redis key collisition)
            self._ensure_not_separator(attribut_name)
            #adding the attribut
            self._add_attribut(node, attribut_name, value, trans_id)
        #we execute the pipe
        self.transactions[trans_id].execute()

        #if we use older versions of redis server or redis-python, no lua script
        if self.legacy_mode:
            for successor in successors:
                self._handle_no_predecessor_legacy(successor, trans_id)
            for predecessor in predecessors:
                self._handle_no_predecessor_legacy(predecessor, trans_id)
            self._handle_no_predecessor_legacy(node, trans_id)
            self.transactions[trans_id].execute()
        del self.transactions[trans_id]

    def write_off_node(self, node, successors, predecessors, attributs):
        """remove given successors, predecessors, attributs to a given node
        node: the name of the node (string)
        successors: list of chidren (string list)
        predecessors: list of predecessors (string list)
        attributs: attributes of the node (dictionnary or list of string)
        """

        trans_id = self._gen_transaction()
        self.transactions[trans_id] = self.connexion.pipeline()

        #removing the successors
        for successor in successors:
            #reverse of write_on_node
            self._remove_predecessor(successor, node, trans_id)
            self._remove_successor(node, successor, trans_id)
            self._handle_no_predecessor(successor, trans_id)

            self.logger.debug("ensure node %(node)s is no longer"\
                " predecessor of %(successor)s" % {
                'successor': successor,
                'node': node
                }
                )

        #removing the predecessors
        for predecessor in predecessors:
            #reverse of write_on_node
            self._remove_predecessor(node, predecessor, trans_id)
            self._remove_successor(predecessor, node, trans_id)
            self._handle_no_predecessor(predecessor, trans_id)

            self.logger.debug("ensure node %(node)s is no longer"\
                " successor of %(predecessor)s" % {
                'predecessor': predecessor,
                'node': node
                }
            )

        #handleling the orphans
        self._handle_no_predecessor(node, trans_id)
        
        #removing the attributs
        for attribut_name in attributs:
            #reverse of write_on_node
            self._remove_attribut(node, attribut_name, trans_id)
            self.logger.debug("remove attibut %(attribut_name)s on"\
                " node %(node)s" % {
                'attribut_name': attribut_name,
                'node': node
                }
            )
        #we execute the pipe
        self.transactions[trans_id].execute()

        #if we use older versions of redis server or redis-python, no lua script
        if self.legacy_mode:
            for successor in successors:
                self._handle_no_predecessor_legacy(successor, trans_id)
            for predecessor in predecessors:
                self._handle_no_predecessor_legacy(predecessor, trans_id)
            self._handle_no_predecessor_legacy(node, trans_id)
            self.transactions[trans_id].execute()
            self._clean_root(trans_id)
            self.transactions[trans_id].execute()
        del self.transactions[trans_id]

    def remove_node(self, node):
        """completly remove a given node from the graph
        node: the name of the node (string)
        """

        trans_id = self._gen_transaction()

        if self.legacy_mode:
            successors = self.get_successors(node)
            predecessors = self.get_predecessors(node)

            for attribut_name in self.get_attributs_list(node):
                #remove each attribut of the node
                self._remove_attribut(node, attribut_name, trans_id)

            for successor in successors:
                #here, only handle the succesors
                #(node will be removed completely later)
                self._remove_predecessor(successor, node, trans_id)
                self._handle_no_predecessor_legacy(successor, trans_id)
 
                self.logger.debug("ensure node %(node)s is no longer"\
                    " predecessor of %(successor)s" % {
                    'successor': successor, 
                    'node': node
                    }
                )

            for predecessor in predecessors:
                #here, only handle the predecessor
                #(node will be removed completely later)
                self._remove_successor(node, predecessors, trans_id)
                self._handle_no_predecessor_legacy(predecessor, trans_id)
 
                self.logger.debug("ensure node %(node)s is no longer"\
                    " successor of %(predecessor)s" % {
                    'predecessor': predecessor,
                    'node': node
                    }
                )
        else:
            base_key = self._gen_key(node,[])
            self.remove_all_attributes_script(args=[base_key], 
                client=self.transactions[trans_id])
            self.remove_node_successors_predecessors_script(args=[node],
                client=self.transactions[trans_id])


        self.logger.debug("remove node %(node)s from database" % {
            'node': node
            }
        )
 
        #remove all the other keys of the node
        redis_key = self._gen_key(node, ['attributs_list', ])
        self.transactions[trans_id].delete(redis_key)

        redis_key = self._gen_key(node, ['successors', ])
        self.transactions[trans_id].delete(redis_key)

        redis_key = self._gen_key(node, ['predecessors', ])
        self.transactions[trans_id].delete(redis_key)

        self.transactions[trans_id].execute()

        #if we use older versions of redis server or redis-python, no lua script
        if self.legacy_mode:
            for successor in successors:
                self._handle_no_predecessor_legacy(successor, trans_id)
            for predecessor in predecessors:
                self._handle_no_predecessor_legacy(predecessor, trans_id)
            self.transactions[trans_id].execute()
            self._clean_root(trans_id)
            self.transactions[trans_id].execute()
        del self.transactions[trans_id]



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
        return self._encode_set(self.connexion.smembers(redis_key))

    def get_attribut_len(self, node, attribut_name):
        """return the value of a given attribut of a node
           node: the name of the node (string)
           attribut_name: the name of the attribut (string)
           return: the length of the attribut 
                (0 if key does not exists)
                (1 if key is a string)
                (cardinal of the set if key is a set)
        """

        self.logger.debug("get attribut length of %(attribut_name)s"\
            " of node %(node)s" % {
            'attribut_name': attribut_name,
            'node': node
            }
        )

        #get the attribut value (different type handling)
        redis_key = self._gen_key(node, ['attribut', attribut_name ])
        #get the attribut type
        key_type = self.connexion.type(redis_key).decode('utf-8')
        if key_type == 'string':
            return 1 
        elif key_type == 'set':
            return self.connexion.scard(redis_key)
        else:
            return 0

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
        redis_key = self._gen_key(node, ['attribut', attribut_name ])
        #get the attribut type
        key_type = self.connexion.type(redis_key).decode('utf-8')
        if key_type == 'string':
            return self.connexion.get(redis_key).decode('utf-8')
        elif key_type == 'set':
            return self._encode_set(self.connexion.smembers(redis_key))
        else:
            return None 

    def _encode_set(self, set_in):
        """convert a set of bytes into a set of utf8
           (redis gives us bytes, this lib output utf8)
           set_in: set of bytes
           return: same set, but utf-8
        """
        res = set([])
        for entry in set_in:
            res.add(entry.decode('utf-8'))
        return res
    
    def _gen_transaction(self):
        """function returning a transaction id and creating the associated pipeline"""
        trans_id = os.urandom(32)
        self.transactions[trans_id] = self.connexion.pipeline()
        #walk around redis-py bug (seen in at least 2.7.5)
        #https://github.com/kakwa/redis-py/commit/9e0ca54f3f147f5271fa7a1f0159c256bd5b1b84
        self.transactions[trans_id].echo('')
        return trans_id
            
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
        for subtype in type_list:
            key = key + self.separator + subtype
        return key   

    def _add_attribut(self, node, attribut_name, value, trans_id):
        """add an attribut to a node
        node: the node name (string)
        attribut_name: name of the attribut (string)
        value: value of the attribut (string or set of string)
        trans_id: a transaction ID (int)
        """
        #different handling for string or set of string
        if type(value) is str: 
            #if it's a string
            #adding the attribut value
            redis_key = self._gen_key(node, ['attribut', attribut_name ])
            self.transactions[trans_id].delete(redis_key)
            self.transactions[trans_id].set(redis_key, value)

        elif type(value) is set:
            #set it's a set
            redis_key = self._gen_key(node, ['attribut', attribut_name ])
            self.transactions[trans_id].delete(redis_key)
            for sub_value in value:
                #adding the attribut value (it's a set -> loop)
                self.transactions[trans_id].sadd(redis_key, sub_value) 
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
        self.transactions[trans_id].sadd(redis_key, attribut_name)

    def _remove_attribut(self, node, attribut_name, trans_id):
        """remove an attribut from a node
        node: the node name (string)
        attribut_name: name of the attribut (string)
        trans_id: a transaction ID (int)
        """
        redis_key = self._gen_key(node, ['attribut', attribut_name ])
        self.transactions[trans_id].delete(redis_key)
        redis_key = self._gen_key(node, ['attributs_list', ])
        self.transactions[trans_id].srem(redis_key, attribut_name)

    def _ensure_not_separator(self, name):
        """Check if the separator is contained in passed arg
        if so, it returns 1 and issue a log (level warning)
        otherwise, it returns 0
        It is used to prevent key collision
        name: the string to check (string)
        """
        test = self.re_check_separator.search(name)  
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
        """get the relatives of a node (successors xor predecessors)
        relative_type: type of relatives ('successors' or 'predecessors')
        node: node to query (string)
        """
        redis_key = self._gen_key(node, [relative_type, ])

        self.logger.debug("get %(relative_type)s of node %(node)s, "\
            "requested key: %(key)s" % {
            'relative_type': relative_type,
            'node' : node,
            'key' : redis_key
            }
        )

        return self._encode_set(self.connexion.smembers(redis_key))

    def _remove_predecessor(self, node, predecessor, trans_id):
        """remove a predecessor from a node
        node: the node name (string)
        predecessor: the predecessor name (string)
        trans_id: a transaction ID (int)
        """
        self._remove_relative('predecessors', node, predecessor, trans_id)

    def _remove_successor(self, node, successor, trans_id):
        """remove a successor from a node
        node: the node name (string)
        successor: the successor name (string)
        trans_id: a transaction ID (int)
        """
        self._remove_relative('successors', node, successor, trans_id)

    def _remove_relative(self, relative_type, node, relative, trans_id):
        """remove a relative from a node:
        relative_type: "successors" or "predecessors" (string)
        node: node name (string)
        relative: name of the relative (string)
        trans_id: a transaction ID (int)
        """
        redis_key = self._gen_key(node, [relative_type, ])

        self.transactions[trans_id].srem(redis_key
            , "%(relative)s" % {
                'relative' : relative
                }
        )

    def _add_successor(self, node, relative, trans_id):
        """add a successor to a node
        node: name of the node (string)
        relative: name of the successor (string)
        trans_id: a transaction ID (int)
        """
        self._add_relative('successors', node, relative, trans_id)

    def _add_predecessor(self, node, relative, trans_id):
        """add a predecessor to a node
        node: name of the node (string)
        relative: name of the predecessor (string)
        trans_id: a transaction ID (int)
        """
        self._add_relative('predecessors', node, relative, trans_id)

    def _add_relative(self, relative_type, node, relative, trans_id):
        """ this function adds a relative to a node:
        relative_type: "successors" or "predecessors" (string)
        node: node name (string)
        relative: name of the relative (string)
        trans_id: a transaction ID (int)
        """
        redis_key = self._gen_key(node, [relative_type, ])

        self.transactions[trans_id].sadd(redis_key
        , "%(relative)s" % {
        'relative' : relative
        })

    def _handle_no_predecessor(self, node, trans_id):
        """handle root, if node has no predecessor, graph root becomes
             its predecessor
        if node as graph root and another node, remove graph root 
            as predecessor
        node: node name (string)
        trans_id: a transaction ID (int)
        """
        if self.legacy_mode:
            return

        if not self.has_root:
            return

        if node == self.root:
            return

        redis_key = self._gen_key(node, ['predecessors', ])
        self._handle_no_predecessor_script(args=[node, redis_key],
                client=self.transactions[trans_id])

    def _clean_root(self, trans_id):
        """clean the root after a removal, it removes left-over former 
        successors
        used for legacy mode (no lua scripting)
        trans_id: a transaction ID (int)
        """
        successors = self.get_successors(self.root)
        for successor in successors:
            redis_key = self._gen_key(successor, ['attributs_list', ])
            if self.connexion.exists(redis_key) == 0:
                self._remove_successor(self.root, successor, trans_id)
        return

    def _handle_no_predecessor_legacy(self, node, trans_id):
        """handle root, if node has no predecessor, graph root becomes
             its predecessor
        if node as graph root and another node, remove graph root 
            as predecessor
        used for legacy mode (no lua scripting)
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
            self._add_predecessor(node, self.root, trans_id)
            self._add_successor(self.root, node, trans_id)

        elif card > 1 and rootismember == 1:
            self._remove_predecessor(node, self.root, trans_id)
            self._remove_successor(self.root, node, trans_id)
