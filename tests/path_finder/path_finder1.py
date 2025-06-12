from rdflib import ConjunctiveGraph
from rdflib import Graph, URIRef
from typing import List

def find_all_paths(graph: Graph, start: URIRef, target: URIRef, max_depth: int = 20) -> List[List[URIRef]]:
    paths = []

    def dfs(current, path, depth):
        if depth > max_depth:
            return
        path.append(current)
        if current == target:
            paths.append(path.copy())
        else:
            for _, _, obj in graph.triples((current, None, None)):
                dfs(obj, path, depth + 1)
        path.pop()

    dfs(start, [], 0)
    return paths

# data = ConjunctiveGraph()
# data.parse("O11+trees.trig", format="trig")
#
# GRAPHS = {}
#     for i in data.contexts():
#       Class = str(i.identifier).split("#")[-1]
#       GRAPHS[Class] = data._graph(i.identifier)
#
#     namespaces = {}
#     for (prefix, namespace) in data.namespaces():
#       if BASE in namespace:
#         namespaces[prefix] = namespace

g = Graph()
g.parse("test0.trig", format="trig")


for t in g.triples((None, None, None)):
    print(t)


start = URIRef("http://example.org/A#")
target = URIRef("http://example.org/A#A")

paths = find_all_paths(g, start, target)

for i, path in enumerate(paths):
    print(f"Path {i+1}: {[str(node) for node in path]}")
