import copy
import json
import os

import rdflib
from rdflib import ConjunctiveGraph
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from BricksAndTreeSemantics import BASE
from BricksAndTreeSemantics import FILE_FORMAT
from BricksAndTreeSemantics import MYTerms
from BricksAndTreeSemantics import ONTOLOGY_REPOSITORY
from BricksAndTreeSemantics import RDFSTerms
from BricksAndTreeSemantics import RDF_PRIMITIVES
from BricksAndTreeSemantics import extractNameFromIRI
from BricksAndTreeSemantics import makeClassURI
from BricksAndTreeSemantics import makeItemURI
from Utilities import find_path_back_triples
from Utilities import debugging
from Utilities import find_all_leaves
from Utilities import get_all_paths_by_name
from Utilities import get_subtree
from Utilities import saveBackupFile


# DEBUGG = False

class Instances(dict):
  def __init__(self):
    super(Instances, self).__init__()
    self = {}

  def addInstance(self, instance, value="undefined", path=None):
    assert path, "addInstance: no path defined"

    self[instance] = {}
    self[instance]["value"] = value
    self[instance]["path"] = path


# noinspection PyProtectedMember
def makeFileName(project_name, what):
  file_name = os.path.join(ONTOLOGY_REPOSITORY, project_name) + "+%s." % what + FILE_FORMAT
  return file_name


def do__loadFromFile(file_name):
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


def do__addItemToGraph(Class, ClassOrSubClass, g, name):
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


def do__makeNewGraph(newName):
  new_graph = Graph()
  classURI = makeItemURI(newName, newName)
  itemURI = makeItemURI(newName, "")
  triple = (URIRef(classURI), RDFSTerms["is_class"], RDFSTerms["class"])
  new_graph.add(triple)
  new_graph.bind(newName, classURI)
  new_graph.bind(newName, itemURI)
  return new_graph


def do__renameURI(newName, oldName, uri):
  uri_name = extractNameFromIRI(uri)
  if uri_name == oldName:  # handle classes
    uri_name = newName

  uri_new = URIRef(makeItemURI(newName, uri_name))
  return uri_new


def do__renameItem(graph_name, graph, oldName, type,newName):
  item_uri = URIRef(makeItemURI(graph_name, oldName))
  new_item_uri = URIRef(makeItemURI(graph_name, newName))
  triple = item_uri, None, None
  for s, p, o in graph.triples(triple):
    graph.remove((s, p, o))
    new_triple = (new_item_uri, p, o)
    graph.add(new_triple)
  triple = None, None, item_uri
  for s, p, o in graph.triples(triple):
    graph.remove((s, p, o))
    new_triple = (s, p, new_item_uri)
    graph.add(new_triple)


def do__attachBrick(brick_name, s_or_o, tree_name):
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
    s_or_o_new = URIRef(tree_name_space_item + "%s" % s_name)
  return s_or_o_new


def do__prepareConjunctiveGraph(graphs):
  pass
  conjunctiveGraph = ConjunctiveGraph("Memory")
  for cl in graphs:
    for s, p, o in graphs[cl].triples((None, None, None)):
      itemURI = makeItemURI(cl, "")
      classURI = makeClassURI(cl)
      conjunctiveGraph.bind(cl, itemURI)
      conjunctiveGraph.get_context(classURI).add((s, p, o))
  return conjunctiveGraph


def do__writeQuadFile(conjunctiveGraph, f):
  # saveBackupFile(f)
  inf = open(f, "w")
  inf.write(conjunctiveGraph.serialize(format=FILE_FORMAT))
  inf.close()

  # makeMessageBox("saved to file:\n   %s" % f, buttons=["OK"])

  fs = f + "_"
  inf = open(fs, "w")
  inf.write(conjunctiveGraph.serialize(format="turtle"))
  inf.close()


def copyGraph(oldName, old_graph, newName, new_graph):
  for s, p, o in old_graph.triples((None, None, None)):
    if p != RDFSTerms["is_class"]:
      s_new = s
      o_new = o
      if oldName in str(s):
        s_new = do__renameURI(newName, oldName, s)
      if oldName in str(o):
        o_new = do__renameURI(newName, oldName, o)
      triple = s_new, p, o_new
      new_graph.add(triple)


class DataModel:
  def __init__(self, root):
    self.brick_namespaces = {}
    self.tree_namespaces = {}
    self.BRICK_GRAPHS = {}
    self.TREE_GRAPHS = {}
    self.file_name_bricks = makeFileName(root, what="bricks")
    self.file_name_trees = makeFileName(root, what="trees")
    self.file_name_instances = makeFileName(root, what="instances")
    self.instance_counter = {}
    self.instances = {}

    self.number_of_bricks = {}

  def loadFromFile(self):
    """
    Loads the graphs and namespaces from the stored files.
    """
    # load the brick graphs
    self.BRICK_GRAPHS, self.brick_namespaces = do__loadFromFile(self.file_name_bricks)

    # check if the tree file exists
    exists = os.path.exists(self.file_name_trees)
    if exists:
      # load the tree graphs and namespaces
      self.TREE_GRAPHS, self.tree_namespaces = do__loadFromFile(self.file_name_trees)

    # check if the instances file exists
    exists = os.path.exists(self.file_name_instances)
    if exists:
      # load the instances from the file
      self.loadInstances(self.file_name_instances)

    pass

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
        if "instance" in s and what != "bricks":
          s = s + " -- " + self.instances[graphName][s]["value"]
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
    # elif what == "tree":
    else:
      g = self.TREE_GRAPHS[graphName]
    # else:
    #   print(">>>>>>>>>>>> should not come here")
    #   return names
    triple = (None, None, None)
    for subject, predicate, object in g.triples(triple):
      s = extractNameFromIRI(subject)
      o = extractNameFromIRI(object)
      names.add(s)
      names.add(o)
    return names

  # def removeItem(self, what_type_of_graph, brick, item):
  #   subject = URIRef(makeItemURI(brick, item))
  #   triple = (subject, None, None)
  #   self.__removeItemFromGraph(what_type_of_graph, brick, subject, triple)

  def removeItem(self, what_type_of_graph, tree_name, parent_name, item_name):
    subject = URIRef(makeItemURI(tree_name, item_name))
    object = URIRef(makeItemURI(tree_name, parent_name))
    triple = (subject, None, object)
    self.__removeItemFromGraph(what_type_of_graph, tree_name, triple)

  def __removeItemFromGraph(self, what_type_of_graph, name, triple):
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

  def item_add(self, Class, ClassOrSubClass, name):
    g = self.BRICK_GRAPHS[Class]
    do__addItemToGraph(Class, ClassOrSubClass, g, name)

  def addItemToTree(self, Class, ClassOrSubClass, name):
    g = self.TREE_GRAPHS[Class]
    do__addItemToGraph(Class, ClassOrSubClass, g, name)

  def primitive_add(self, Class, ClassOrSubClass, name, type):
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

  def modifyPrimitiveValue(self, tree_name, primitive_type, instance_value):
    pass
    instance, value = instance_value.split(":")
    graph = self.TREE_GRAPHS[tree_name]
    prefix = makeItemURI(tree_name, "")
    triple_search = (URIRef(prefix + instance),
                     RDFSTerms[primitive_type],
                     None)

    t = None
    p = None
    o = None
    for t in graph.triples(triple_search):
      s, p, o = t
    if t:
      graph.remove(t)
      s = URIRef(prefix + instance)
      triple_add = s, p, o
      graph.add(triple_add)
      self.instances[tree_name][instance]["value"] = value
    else:
      print(">>> something went wrong, Not triple found")
    pass

    # if DEBUGG:
    #   for ttt in graph.triples((None, None, None)):
    #     print(ttt)
    #   print("end")
    #   print(self.instances[tree_name])

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
    new_graph = do__makeNewGraph(newName)
    old_graph = self.BRICK_GRAPHS[oldName]
    copyGraph(oldName, old_graph, newName, new_graph)
    self.BRICK_GRAPHS[newName] = new_graph
    self.brick_namespaces[newName] = Namespace(makeItemURI(newName, newName))
    del self.BRICK_GRAPHS[oldName]

  def renameTree(self, oldName, newName):
    new_graph = do__makeNewGraph(newName)
    old_graph = self.TREE_GRAPHS[oldName]
    copyGraph(oldName, old_graph, newName, new_graph)
    self.TREE_GRAPHS[newName] = new_graph
    self.tree_namespaces[newName] = Namespace(makeItemURI(newName, ""))
    del self.TREE_GRAPHS[oldName]
    del self.tree_namespaces[oldName]

    # fix up instances:
    self.instances[newName] = copy.deepcopy(self.instances[oldName])

    for instance in self.instances[newName]:
      path = self.instances[newName][instance]["path"]
      newpath = path[0:-1] + newName
      self.instances[newName][instance]["path"] = newpath

      # for tree in list(self.instances.keys()):
      #   self.instances[newName] = {}
      #   if tree == oldName:
      #     paths = copy.copy(self.instances[oldName])
      #     for instance in paths:
      #       path = paths[instance]
      #       path[-1] = newName
      #       self.instances[newName][instance] = path
      del self.instances[oldName]

  def copyTree(self, from_name, to_name):

    from_graph = self.TREE_GRAPHS[from_name]
    to_graph = do__makeNewGraph(to_name)
    self.TREE_GRAPHS[to_name] = to_graph
    self.tree_namespaces[to_name] = Namespace(makeItemURI(to_name, ""))
    self.instances[to_name] = copy.deepcopy(self.instances[from_name])
    self.instance_counter[to_name] = copy.copy(self.instance_counter[from_name])
    copyGraph(from_name, from_graph, to_name, to_graph)
    pass

  def deleteTree(self, tree_name):
    del self.TREE_GRAPHS[tree_name]
    del self.tree_namespaces[tree_name]
    del self.instances[tree_name]
    return

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

    paths, properties, leaves = self.getTreePaths(tree_name)

    defined_paths = []
    for instance in self.instances[tree_name]:
      defined_path = self.instances[tree_name][instance]["path"]
      defined_paths.append(defined_path[1:])

    for p in paths:
      if not "instance" in p:
        for i in range(len(paths[p])):
          path = paths[p][i]
          empty = path[0] == ""
          defined = path[1:] in defined_paths
          if empty and not defined:
            print("found an empty leaf", path)
            self.instance_counter[tree_name] += 1
            instance_ID = "instance_%s" % (self.instance_counter[tree_name])
            print("counter", self.instance_counter[tree_name])
            subject_instance = URIRef(prefix + instance_ID)
            subject_empty = URIRef(prefix + "")
            type = properties[p][0][path[0]]
            predicate = RDFSTerms[type]
            object = URIRef(prefix + path[1])
            instance_path = [instance_ID + ":undefined"] + path[1:]

            # self.instances[tree_name][instance_ID] = (instance_path, "undefined")
            # self.instances[tree_name][instance_ID]["value"] = "undefined"
            self.instances[tree_name].addInstance(instance_ID,
                                                  value="undefined",
                                                  path=instance_path)
            graph.add((subject_instance, predicate, object))
            graph.remove((subject_empty, predicate, object))

    pass

  def renameItemInBrick(self, brick, old_name, type, new_name):
    g = self.BRICK_GRAPHS[brick]
    do__renameItem(brick,g , old_name, type , new_name)

  def renameValue(self, brick, old_name, new_name, type):
    g = self.BRICK_GRAPHS[brick]
    old_object = URIRef(makeItemURI(brick, old_name))
    new_object = URIRef(makeItemURI(brick, new_name))
    # object = URIRef(makeItemURI(brick, parent_name))
    triple = (Literal(""), RDFSTerms[type], old_object)
    g.remove(triple)
    triple = (Literal(""), RDFSTerms[type], new_object)
    g.add(triple)
    pass

  def renameItemInTree(self, brick, old_name, newName):
    graph = self.TREE_GRAPHS[brick]
    do__renameItem(brick, graph, old_name, newName)
    pass

  def linkBrickToItem(self, tree_name, tree_item_name, brick_name, new_tree=False):
    tree_graph = self.TREE_GRAPHS[tree_name]
    brick_graph = self.BRICK_GRAPHS[brick_name]
    # rule: keep brick name
    tree_name_space_item = makeItemURI(tree_name, "")
    s_ = URIRef(tree_name_space_item + "%s" % brick_name)
    o_ = URIRef(tree_name_space_item + tree_item_name)
    triple = (s_,
              RDFSTerms["is_defined_by"],
              o_)
    tree_graph.add(triple)

    for s, p, o in brick_graph.triples((None, None, None)):
      if p != RDFSTerms["is_class"]:
        s_new = do__attachBrick(brick_name,
                                   s,
                                   tree_name)
        o_new = do__attachBrick(brick_name,
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
    conjunctiveGraph = do__prepareConjunctiveGraph(graphs)
    file_name = makeFileName(project_name, "bricks")
    if not file_name:
      file_name = self.file_name_bricks
    do__writeQuadFile(conjunctiveGraph, file_name)
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
    conjunctiveGraph = do__prepareConjunctiveGraph(graphs)
    file_name = makeFileName(project_name, "trees")
    if not file_name:
      file_name = self.file_name_trees
    do__writeQuadFile(conjunctiveGraph, file_name)
    self.saveBricks(project_name)
    self.saveInstances(project_name)
    pass
    graphs = self.TREE_GRAPHS
    conjunctiveGraph = do__prepareConjunctiveGraph(graphs)
    file_name = makeFileName(project_name, "trees")
    if not file_name:
      file_name = self.file_name_trees
    do__writeQuadFile(conjunctiveGraph, file_name)
    self.saveBricks(project_name)
    self.saveInstances(project_name)
    pass

  def saveInstances(self, project_name):
    file_name = makeFileName(project_name, "instances")
    dump = json.dumps(self.instances, indent="  ")
    with open(file_name, "w+") as f:
      f.write(dump)

  def loadInstances(self, file_name=None):
    with open(file_name) as f:
      instances = json.load(f)

    self.instances = {}
    for tree_name in instances:
      self.instances[tree_name] = Instances()
      for i in instances[tree_name]:
        path = instances[tree_name][i]["path"]
        value = instances[tree_name][i]["value"]
        self.instances[tree_name].addInstance(i, value=value, path=path)

    self.instance_counter = {}
    for tree_name in self.instances:
      if self.instances[tree_name]:
        for i in self.instances[tree_name]:
          if i:
            s = i
            counter = s.split("_")[1]
            self.instance_counter[tree_name] = int(counter)
      else:
        self.instance_counter[tree_name] = -1
    pass

  def reduceGraph(self, tree_name):  # todo: fix
    pass
    prefix = makeItemURI(tree_name, "")
    tree_graph = self.TREE_GRAPHS[tree_name]

    instances = self.instances[tree_name]

    keep_target = []
    for instance_ID in instances:
      instance_value = instances[instance_ID]["value"]
      if instance_value != "undefined":
        keep_target.append(instance_ID)

    pass
    if not keep_target:
      return

    tree_name_instantiated = tree_name + "_i"
    self.tree_namespaces[tree_name_instantiated] = Namespace(makeItemURI(tree_name_instantiated, ""))
    graph = self.TREE_GRAPHS[tree_name_instantiated] = Graph("Memory")
    # make path

    for i in keep_target:
      instance_uri = URIRef(prefix + i)
      root_uri = URIRef(prefix + tree_name)
      for t in tree_graph.triples((instance_uri, None, None)):
        s, p, o = t

      if not t:
        print(">>>> no triple found")
      path_triples = find_path_back_triples(tree_graph, t, root_uri)
      for ii in range(len(path_triples[0])):
        t_ = path_triples[0][ii]
        s_, p_, o_ = t_

        s_new = do__renameURI(tree_name_instantiated, tree_name, s_)
        o_new = do__renameURI(tree_name_instantiated, tree_name, o_)
        triple = (s_new, p_, o_new)
        graph.add(triple)

    # finally, copy instantiated instances
    self.instances[tree_name_instantiated] = copy.deepcopy(self.instances[tree_name])
    pass

  def newTree(self, tree_name, brick_name):

    self.instance_counter[tree_name] = -1
    self.instances[tree_name] = Instances()

    tree_graph = do__makeNewGraph(tree_name)
    self.TREE_GRAPHS[tree_name] = tree_graph
    self.tree_namespaces[tree_name] = Namespace(makeItemURI(tree_name, ""))
    self.linkBrickToItem(tree_name, tree_name, brick_name, new_tree=True)

  def getTreeList(self):
    tree_list = sorted(self.TREE_GRAPHS.keys())
    return tree_list

  def getTreePaths(self, tree_name):
    namespace = self.tree_namespaces[tree_name]
    root_uri = URIRef(namespace + tree_name)
    graph = self.TREE_GRAPHS[tree_name]
    leaves, leave_properties = find_all_leaves(graph)

    paths = {}
    properties = {}
    instance_paths = self.instances[tree_name]
    for start in leaves:
      prop = leave_properties[start.split("#")[1] if "#" in start else str(start)].split("#")[1]
      paths[start], properties[start] = get_all_paths_by_name(graph, prop, start, root_uri)

      instance = start.split("#")[1]
      if instance in instance_paths:  # remove duplicated paths
        paths[start] = [instance_paths[instance]["path"]]
        for i in properties[start]:
          test_path = list(i.keys())
          if paths[start][0][1:-1] == test_path[1:]:
            # print("found it")
            properties[start] = [i]
    pass
    return paths, properties, leaves

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
