import copy
import json
import os

import rdflib
from rdflib import ConjunctiveGraph
from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef

from BricksAndTreeSemantics import BASE
from BricksAndTreeSemantics import FILE_FORMAT
from BricksAndTreeSemantics import MYTerms
from BricksAndTreeSemantics import ONTOLOGY_REPOSITORY
from BricksAndTreeSemantics import PRIMITIVES
from BricksAndTreeSemantics import RDFSTerms
from BricksAndTreeSemantics import RDF_PRIMITIVES
from BricksAndTreeSemantics import extractNameFromIRI
from BricksAndTreeSemantics import makeClassURI
from BricksAndTreeSemantics import makeItemURI
from PeriConto.src.Utilities import find_all_paths
from PeriConto.src.Utilities import get_all_paths_by_name
from Utilities import DEBUGG
from Utilities import debugging
from Utilities import find_path_back_triples
from Utilities import get_subtree
from Utilities import saveBackupFile, depth_first_iter


# DEBUGG = False


class DataModel:
  def __init__(self, root):
    self.brick_namespaces = {}
    self.tree_namespaces = {}
    self.BRICK_GRAPHS = {}
    self.TREE_GRAPHS = {}
    self.file_name_bricks = self.makeFileName(root, what="bricks")
    self.file_name_trees = self.makeFileName(root, what="trees")
    self.file_name_instances = self.makeFileName(root, what="instances")
    # self.brick_counter = {}
    self.instance_counter = {}
    self.instances = {}

    self.number_of_bricks = {}

  def loadFromFile(self, project_name):
    """
    that's a bit tricky. We need the brick numbers for each tree
    """
    self.BRICK_GRAPHS, self.brick_namespaces = self.__loadFromFile(self.file_name_bricks)
    exists = os.path.exists(self.file_name_trees)
    if exists:
      self.TREE_GRAPHS, self.tree_namespaces = self.__loadFromFile(self.file_name_trees)

    exists = os.path.exists(self.file_name_instances)
    if exists:
      self.loadInstances(self.file_name_instances)

  def __extractNumber(self, s):
    """
    that's a bit tricky. We need the brick numbers for each tree
    """
    n = "0"
    s = str(s)
    try:
      ss = s.split("#")[-1].split("_")[0]
      name = s.split("#")[-1].split("_")[1]
      no = int(ss)
    except:
      ss = None
      no = -1
      try:
        name = s.split("#")[1]
      except:
        name = s
    return no, name

  def makeFileName(self, project_name, what):
    file_name = os.path.join(ONTOLOGY_REPOSITORY, project_name) + "+%s." % what + FILE_FORMAT
    return file_name

  def __loadFromFile(self, file_name):
    data = ConjunctiveGraph("Memory")
    data.parse(file_name, format=FILE_FORMAT)

    GRAPHS = {}
    for i in data.contexts():
      Class = str(i.identifier).split("#")[-1]
      GRAPHS[Class] = data._graph(i.identifier)

    namespaces = {}
    for (prefix, namespace) in data.namespaces():
      if BASE in namespace:
        namespaces[prefix] = namespace

    return GRAPHS, namespaces

  def makeDataTuplesForGraph(self, graphName, what):
    if what == "bricks":
      graph = self.BRICK_GRAPHS[graphName]
    else:
      graph = self.TREE_GRAPHS[graphName]
    tuples_plus = []
    for subject, predicate, object in graph.triples((None, None, None)):
      debugging("--", subject, predicate, object)
      s = extractNameFromIRI(subject)
      p = MYTerms[predicate]
      o = extractNameFromIRI(object)
      if predicate in [RDFSTerms["is_defined_by"],
                       RDFSTerms["value"],
                       RDFSTerms["data_type"],
                       ] + RDF_PRIMITIVES:
        triple = s, p, o, -1
      else:
        triple = s, p, o, 1
      tuples_plus.append(triple)
    debugging("tuples", tuples_plus)
    return tuples_plus

  def getBrickList(self):
    return sorted(self.BRICK_GRAPHS.keys())

  def newBrick(self, brick_name):
    graphs = self.BRICK_GRAPHS
    graphs[brick_name] = Graph()
    classURI = makeItemURI(brick_name, brick_name)
    itemURI = makeItemURI(brick_name, "")
    triple = (URIRef(classURI), RDFSTerms["is_class"], RDFSTerms["class"])
    graphs[brick_name].add(triple)
    graphs[brick_name].bind(brick_name, classURI)
    self.brick_namespaces[brick_name] = classURI
    graphs[brick_name].bind(brick_name, itemURI)
    pass

  def removeBrick(self, name):
    del self.BRICK_GRAPHS[name]

  def getAllNamesInABrickOrATree(self, graphName, what):

    names = set()
    if what == "brick":
      g = self.BRICK_GRAPHS[graphName]
    elif what == "tree":
      g = self.TREE_GRAPHS[graphName]
    else:
      print(">>>>>>>>>>>> should not come here")
      return
    triple = (None, None, None)
    for subject, predicate, object in g.triples(triple):
      s = extractNameFromIRI(subject)
      o = extractNameFromIRI(object)
      names.add(s)
      names.add(o)
    return names

  def removeItem(self, what_type_of_graph, brick, item):
    subject = URIRef(makeItemURI(brick, item))
    triple = (subject, None, None)
    self.__removeItemFromGraph(what_type_of_graph, brick, subject, triple)

  def __removeItemFromGraph(self, what_type_of_graph, name, subject, triple):
    if what_type_of_graph == "bricks":
      graph = self.BRICK_GRAPHS[name]
    else:
      graph = self.TREE_GRAPHS[name]

    predicates = RDFSTerms.values()
    subtree = get_subtree(graph, triple[0], predicates)

    # now delete from the identified subtree
    to_delete = [triple]
    for n in subtree:
      for t in graph.triples((None, None, n)):
        to_delete.append(t)
    for t in to_delete:
      graph.remove(t)

    pass

  def addItem(self, Class, ClassOrSubClass, name):
    g = self.BRICK_GRAPHS[Class]
    self.__addItemToGraph(Class, ClassOrSubClass, g, name)

  def __addItemToGraph(self, Class, ClassOrSubClass, g, name):
    classURI = makeClassURI(Class)
    itemURI = makeItemURI(Class, "")
    if Class == ClassOrSubClass:
      o = URIRef(classURI)
    else:
      o = URIRef(itemURI + ClassOrSubClass)
    s = URIRef(itemURI + name)
    triple = (s, RDFSTerms["is_member"], o)
    g.add(triple)
    pass

  def addItemToTree(self, Class, ClassOrSubClass, name):
    g = self.TREE_GRAPHS[Class]
    self.__addItemToGraph(Class, ClassOrSubClass, g, name)

  def addPrimitive(self, Class, ClassOrSubClass, name, type):
    classURI = makeClassURI(Class)
    itemURI = makeItemURI(Class, "")
    if Class == ClassOrSubClass:
      s = URIRef(classURI)
    else:
      s = URIRef(itemURI + ClassOrSubClass)
    o = URIRef(itemURI + name)
    triple = (o, RDFSTerms["value"], s)
    self.BRICK_GRAPHS[Class].add(triple)
    oo = URIRef(itemURI + "")  # Literal("")
    triple = (oo, RDFSTerms[type], o)
    self.BRICK_GRAPHS[Class].add(triple)
    pass

  def modifyPrimitiveValue(self, tree_name, primitive_name, primitive_type, value, path):
    pass
    graph = self.TREE_GRAPHS[tree_name]
    prefix = makeItemURI(tree_name, "")
    triple_search = (URIRef(prefix + path[0]),
                     RDFSTerms[primitive_type],
                     None)
    instance_ID = value.split(":")[0]

    tree_uri = URIRef(makeItemURI(tree_name, tree_name))
    t = None
    for t in graph.triples(triple_search):
      s, p, o = t
    if t:
      graph.remove(t)
      s = URIRef(prefix + value)
      triple_add = s, p, o
      graph.add(triple_add)
      old_path = self.instances[tree_name][instance_ID]
      new_path = old_path
      new_path[0] = value
      self.instances[tree_name][instance_ID] = new_path
    else:
      print(">>> something went wrong, Not triple found")
    pass

    if DEBUGG:
      for ttt in graph.triples((None, None, None)):
        print(ttt)
      print("end")
      print(self.instances[tree_name])


  def modifyPrimitiveType(self, brick_name, primitive_name, new_type):
    graph = self.BRICK_GRAPHS[brick_name]
    prefix = makeItemURI(brick_name, "")
    name_uri = URIRef(prefix + primitive_name)
    primitive_uri = URIRef(prefix + new_type)
    triple = (None, None, name_uri)
    selected_triples = []
    for t in graph.triples(triple):
      selected_triples.append(t)
    if not t:
      print(">>>>>>>>>>  should not come here")
      return
    if len(selected_triples) > 1:
      print(">>>>>>>>>>  oops found more than one triple -- should only be one")
      return

    t = selected_triples[0]
    new_triple = primitive_uri, RDFSTerms[new_type], name_uri
    graph.add(new_triple)
    graph.remove(t)

  def renameBrick(self, oldName, newName):
    new_graph = self.__makeNewGraph(newName)
    old_graph = self.BRICK_GRAPHS[oldName]
    self.copyGraph(oldName, old_graph, newName, new_graph)
    del self.BRICK_GRAPHS[oldName]

  def renameTree(self, oldName, newName):
    new_graph = self.__makeNewGraph(newName)
    old_graph = self.TREE_GRAPHS[oldName]
    self.copyGraph(oldName, old_graph, newName, new_graph)
    del self.TREE_GRAPHS[oldName]

  def copyTree(self, from_name, to_name):

    from_graph = self.TREE_GRAPHS[from_name]
    to_graph = self.__makeNewGraph(to_name)
    self.TREE_GRAPHS[to_name] = to_graph
    self.tree_namespaces[to_name] = Namespace(makeItemURI(to_name, to_name))
    self.copyGraph(from_name, from_graph, to_name, to_graph)
    pass

  def deleteTree(self, tree_name):
    del self.TREE_GRAPHS[tree_name]
    return

  def __makeNewGraph(self, newName):
    new_graph = Graph()
    classURI = makeItemURI(newName, newName)
    itemURI = makeItemURI(newName, "")
    triple = (URIRef(classURI), RDFSTerms["is_class"], RDFSTerms["class"])
    new_graph.add(triple)
    new_graph.bind(newName, classURI)
    new_graph.bind(newName, itemURI)
    return new_graph

  def copyGraph(self, oldName, old_graph, newName, new_graph):
    for s, p, o in old_graph.triples((None, None, None)):
      if p != RDFSTerms["is_class"]:
        s_new = s
        o_new = o
        if oldName in str(s):
          s_new = self.__renameURI(newName, oldName, s)
        if oldName in str(o):
          o_new = self.__renameURI(newName, oldName, o)
        triple = s_new, p, o_new
        new_graph.add(triple)

  def replaceBlankWithUndefinedIdentifier(self, tree_name):
    """
    Replace blank node identifiers with unique undefined identifiers in a tree graph.

    This function traverses a tree graph starting from the given root and identifies
    blank nodes (nodes with empty names). For each blank node found, it generates a
    unique identifier in the format "instance_count:" and replaces the blank node
    with this new identifier. The function then updates the graph with these changes
    and maintains a path mapping for each new identifier.

    Args:
        tree_name (str): The name of the tree graph in which to replace blank node
                         identifiers.

    Side Effects:
        Modifies the specified tree graph by replacing blank nodes with uniquely
        generated identifiers and updates the instance path mapping.

    """
    graph = self.TREE_GRAPHS[tree_name]
    prefix = makeItemURI(tree_name, "")
    root = URIRef(prefix+tree_name)

    tree_uri = URIRef(makeItemURI(tree_name, tree_name))

    st = {}
    for depth, node, current_branch, parent, predicate, node_id, parent_id in depth_first_iter(graph, root):
      print(depth, node, current_branch, parent, predicate, node_id, parent_id)
      st[node_id] = (node, predicate, parent_id)
      # print(st)

    empty_triples = set()
    for node_id in st:
      s, p, parent_id = st[node_id]
      _, n = str(s).split("#")
      if n == "":
        o, _,_ =st[parent_id]
        print(s,p,o)
        empty_triples.add((s, p, o))

    empty = {}
    for triple in empty_triples:
      paths_by_names = get_all_paths_by_name(graph,s,root)
      empty[triple] = paths_by_names

    count = 0
    for triple in empty:
      s,p,o = triple
      paths = empty[triple]
      for path_names in paths:
        identifier = "instance_%s" % (count)
        new_path = copy.copy(path_names)
        new_path[0] = identifier
        id_s = URIRef(prefix + identifier)
        print(id_s, p, o)
        count += 1
        triple_identifier = (id_s, p, o)
        graph.add((triple_identifier))
        self.instances[tree_name][identifier] = new_path
      graph.remove((triple))

    pass
    # for primitive in PRIMITIVES:
    #   primitive_uri = URIRef(prefix + primitive)
    #   search_triple = (URIRef(prefix), RDFSTerms[primitive], None)
    #   for t in graph.triples(search_triple):
    #     s, p, o = t
    #     remove_triple = s, p, o
    #     print("remove triple", remove_triple)

        # if "instance" not in str(o):
        #   graph.remove(remove_triple)
        #
        #   # we generate a new triple which reflects the instance with number and its value
        #   value = "undefined"
        #   identifier = "instance_%s" % self.instance_counter[tree_name]
        #   identifier_value = identifier + ":%s" % (value)
        #   s_identifier = URIRef(makeItemURI(tree_name, identifier_value))
        #   self.instance_counter[tree_name] += 1
        #   # first the identifier triple
        #   p_identifier = RDFSTerms[primitive]
        #   triple_identifier = s_identifier, p_identifier, o
        #   graph.add(triple_identifier)
        #   tree_uri = URIRef(makeItemURI(tree_name, tree_name))
        #   path, path_names = find_path_back_triples(graph, triple_identifier, tree_uri)
        #   self.instances[tree_name][identifier] = path_names
        # print(">>> replacing",s, p, o)
    pass

  def __renameURI(self, newName, oldName, uri):
    uri_name = extractNameFromIRI(uri)
    if uri_name == oldName:  # handle classes
      uri_name = newName

    uri_new = URIRef(makeItemURI(newName, uri_name))
    return uri_new

  def renameItem(self, brick, item, newName):
    g = self.BRICK_GRAPHS[brick]
    self.__renameItem(brick, g, item, newName)
    pass

  def renameItemInTree(self, brick, item, newName):
    g = self.TREE_GRAPHS[brick]
    self.__renameItem(brick, g, item, newName)
    pass

  def __renameItem(self, brick, g, item, newName):
    item_uri = URIRef(makeItemURI(brick, item))
    new_item_uri = URIRef(makeItemURI(brick, newName))
    triple = (item_uri, None, None)
    for s, p, o in g.triples(triple):
      g.remove((s, p, o))
      new_triple = (new_item_uri, p, o)
      g.add(new_triple)
    triple = None, None, item_uri
    for s, p, o in g.triples(triple):
      g.remove((s, p, o))
      new_triple = (s, p, new_item_uri)
      g.add(new_triple)

  def __attachBrick(self, brick_name, s_or_o, tree_name):
    """
    Attaches a brick to a tree by updating the URI reference.

    Args:
        brick_name (str): The name of the brick.
        s_or_o (rdflib.term.URIRef): The subject or object URI reference.
        tree_name (str): The name of the tree.

    Returns:
        rdflib.term.URIRef: The updated URI reference with the tree namespace.
    """
    tree_name_space_item = makeItemURI(tree_name, "")
    s_or_o_new = s_or_o
    if brick_name in str(s_or_o):
      s_name = extractNameFromIRI(s_or_o)
      s_or_o_new = URIRef(tree_name_space_item + "%s" % (s_name))
    return s_or_o_new

  def linkBrickToItem(self, tree_name, tree_item_name, brick_name, new_tree=False):
    tree_graph = self.TREE_GRAPHS[tree_name]
    brick_graph = self.BRICK_GRAPHS[brick_name]
    for s, p, o in brick_graph.triples((None, RDFSTerms["is_class"], None)):
      # rule: keep brick name
      tree_name_space_item = makeItemURI(tree_name, "")
      s_ = URIRef(tree_name_space_item + "%s" % (brick_name))
      o_ = URIRef(tree_name_space_item + tree_item_name)
      triple = (s_,
                RDFSTerms["is_defined_by"],
                o_)
      tree_graph.add(triple)

    for s, p, o in brick_graph.triples((None, None, None)):
      if (p != RDFSTerms["is_class"]):
        s_new = self.__attachBrick(brick_name,
                                   s,
                                   tree_name)
        o_new = self.__attachBrick(brick_name,
                                   o,
                                   tree_name)
        triple = s_new, p, o_new
        tree_graph.add(triple)
    self.replaceBlankWithUndefinedIdentifier(tree_name)
    pass

  def saveBricks(self, project_name):
    """
    Saves the brick graphs to a file.

    This function prepares a conjunctive graph from the brick graphs and writes
    it to a file. If a specific file name is not provided, it uses the
    default file name for bricks.

    Args:
        project_name (str): The name of the project to construct the file name.

    """
    graphs = self.BRICK_GRAPHS
    conjunctiveGraph = self.__prepareConjunctiveGraph(graphs)
    file_name = self.makeFileName(project_name, "bricks")
    if not file_name:
      file_name = self.file_name_bricks
    self.__writeQuadFile(conjunctiveGraph, file_name)
    pass

  def saveBricksTreesAndInstances(self, project_name):
    """
    Saves the brick and tree graphs, and the instances to three files.

    This function prepares a conjunctive graph from the tree graphs and writes
    it to a file. If a specific file name is not provided, it uses the
    default file name for trees. Additionally, it saves the brick graphs and
    the instances to their respective files.

    Args:
        project_name (str): The name of the project to construct the file name.

    """
    graphs = self.TREE_GRAPHS
    conjunctiveGraph = self.__prepareConjunctiveGraph(graphs)
    file_name = self.makeFileName(project_name, "trees")
    if not file_name:
      file_name = self.file_name_trees
    self.__writeQuadFile(conjunctiveGraph, file_name)
    self.saveBricks(project_name)
    self.saveInstances(project_name)
    pass
    graphs = self.TREE_GRAPHS
    conjunctiveGraph = self.__prepareConjunctiveGraph(graphs)
    file_name = self.makeFileName(project_name, "trees")
    if not file_name:
      file_name = self.file_name_trees
    self.__writeQuadFile(conjunctiveGraph, file_name)
    self.saveBricks(project_name)
    self.saveInstances(project_name)
    pass

  def saveInstances(self, project_name):
    file_name = self.makeFileName(project_name, "instances")
    dump = json.dumps(self.instances, indent="  ")
    with open(file_name, "w+") as f:
      f.write(dump)

  def loadInstances(self, file_name=None):
    with open(file_name) as f:
      self.instances = json.load(f)

    self.instance_counter = {}
    for tree_name in self.instances:
      if self.instances[tree_name]:
        for i in self.instances[tree_name]:
          if i:
            s = i
            counter = s.split("_")[1]
            self.instance_counter[tree_name] = int(counter) + 1
      else:
        self.instance_counter[tree_name] = 0
    pass

  def reduceGraph(self, tree_name):
    pass
    prefix = makeItemURI(tree_name, "")
    tree_graph = self.TREE_GRAPHS[tree_name]

    instances = self.instances[tree_name]

    keep_target = []
    for instance_ID in instances:
      instance_value = instances[instance_ID][0].split(":")[1]
      instance_path = instances[instance_ID]
      if instance_value != "undefined":
        keep_target.append(instance_path)

    pass
    if not keep_target:
      return

    tree_name_instantiated = tree_name + "_i"
    self.tree_namespaces[tree_name_instantiated] = Namespace(makeItemURI(tree_name_instantiated, ""))
    graph = self.TREE_GRAPHS[tree_name_instantiated] = Graph("Memory")
    # make path
    for i in keep_target:
      for n in range(len(i[:-1])):
        s_n, o_n = i[n:n+2]
        print(s_n, o_n)
        s = makeItemURI(tree_name, s_n)
        o = makeItemURI(tree_name, o_n)

        triple_search = (URIRef(s), None, URIRef(o))

        s_new = self.__renameURI(tree_name_instantiated, tree_name, s)
        o_new = self.__renameURI(tree_name_instantiated, tree_name, o)
        for _, p, _ in tree_graph.triples(triple_search):
          triple = (s_new, p, o_new)
          graph.add(triple)

    pass

    # finally, copy instantiated instances
    self.instances[tree_name_instantiated] = copy.deepcopy(self.instances[tree_name])
    for instance_ID in self.instances[tree_name_instantiated]:
      path = copy.copy(self.instances[tree_name_instantiated][instance_ID])
      path[-1] = tree_name_instantiated
      self.instances[tree_name_instantiated][instance_ID] = path


    pass


  def __prepareConjunctiveGraph(self, graphs):
    pass
    conjunctiveGraph = ConjunctiveGraph("Memory")
    for cl in graphs:
      for s, p, o in graphs[cl].triples((None, None, None)):
        itemURI = makeItemURI(cl, "")
        classURI = makeClassURI(cl)
        conjunctiveGraph.bind(cl, itemURI)
        conjunctiveGraph.get_context(classURI).add((s, p, o))
    return conjunctiveGraph



  def newTree(self, tree_name, brick_name):

    self.instance_counter[tree_name] = 0
    self.instances[tree_name] = {}

    tree_graph = self.__makeNewGraph(tree_name)
    self.TREE_GRAPHS[tree_name] = tree_graph
    self.tree_namespaces[tree_name] = Namespace(makeItemURI(tree_name, ""))
    self.linkBrickToItem(tree_name, tree_name, brick_name, new_tree=True)

  def getTreeList(self):
    tree_list = sorted(self.TREE_GRAPHS.keys())
    return tree_list

  def __writeQuadFile(self, conjunctiveGraph, f):
    saveBackupFile(f)
    inf = open(f, "w")
    inf.write(conjunctiveGraph.serialize(format=FILE_FORMAT))
    inf.close()

    # makeMessageBox("saved to file:\n   %s" % f, buttons=["OK"])

    fs = f + "_"
    inf = open(fs, "w")
    inf.write(conjunctiveGraph.serialize(format="turtle"))
    inf.close()

  def getGraph(self, graphName, what):
    if what == "bricks":
      graph = self.BRICK_GRAPHS[graphName]
      namespace = self.brick_namespaces[graphName]
    else:
      graph = self.TREE_GRAPHS[graphName]
      namespace = self.tree_namespaces[graphName]

    root = URIRef(namespace + graphName)

    # Example usage:
    # for depth, node, current_branch, parent in depth_first_iter(g3, ABC.ABC):
    return graph, root
