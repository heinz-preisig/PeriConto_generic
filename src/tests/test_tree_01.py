from rdflib import Graph, URIRef, Namespace

ABC = Namespace("http://example.org/ABC#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

def depth_first(graph, node, global_visited=None, depth=0):
    if global_visited is None:
        global_visited = set()

    print("  " * depth + node.split('#')[-1])
    global_visited.add(node)

    # Traverse incoming rdfs:member
    for child, _, _ in sorted(graph.triples((None, RDFS.member, node)), key=lambda t: t[0].split('#')[-1]):
        if child not in global_visited:
            traverse_branch(graph, child, global_visited, set(), depth + 1)

def traverse_branch(graph, node, global_visited, local_visited, depth):
    print("  " * depth + node.split('#')[-1])
    global_visited.add(node)
    local_visited.add(node)

    # Traverse rdfs:isDefinedBy links
    for _, _, defined in sorted(graph.triples((node, RDFS.isDefinedBy, None)), key=lambda t: t[2].split('#')[-1]):
        if defined not in global_visited:
            depth_first(graph, defined, global_visited, depth + 1)

    # Traverse rdf:value links
    for _, _, value in sorted(graph.triples((node, RDF.value, None)), key=lambda t: t[2].split('#')[-1]):
        if value not in local_visited:
            traverse_branch(graph, value, global_visited, local_visited, depth + 1)

    # Traverse nested members (if this node is also referenced)
    for child, _, _ in sorted(graph.triples((None, RDFS.member, node)), key=lambda t: t[0].split('#')[-1]):
        if child not in local_visited:
            traverse_branch(graph, child, global_visited, local_visited, depth + 1)

# RDF data
g = Graph()
g.parse(data='''
@prefix ABC: <http://example.org/ABC#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ABC: xsd:integer ABC:Int ;
    xsd:string ABC:S .

ABC:Ab rdfs:member ABC:A .

ABC:B a ABC:Class ;
    rdfs:isDefinedBy ABC:K,
                     ABC:L .

ABC:Int rdf:value ABC:A .

ABC:K rdfs:member ABC:ABC .

ABC:L rdfs:member ABC:ABC .

ABC:S rdf:value ABC:B .

ABC:A rdfs:member ABC:ABC .

ABC:ABC a ABC:Class .
''', format='turtle')

# Run the traversal
depth_first(g, ABC.ABC)


# from rdflib import Graph, URIRef, Namespace
# 
# def traverse(graph, node, visited=None, depth=0):
#     if visited is None:
#         visited = set()
# 
#     # Skip already visited nodes to avoid cycles
#     if node in visited:
#         return
#     visited.add(node)
# 
#     # Print the current node (just the local name for clarity)
#     print("  " * depth + node.split('#')[-1])
# 
#     # Namespaces
#     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
#     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# 
#     # Process the triples starting with this node (predicates: rdfs:isDefinedBy, rdfs:member, rdf:value)
#     for _, pred, obj in graph.triples((node, None, None)):
#         if isinstance(obj, URIRef):  # Only process URIRefs (nodes)
#             if pred == RDFS.isDefinedBy:
#                 # Special handling for isDefinedBy predicate: process defined nodes
#                 traverse(graph, obj, visited, depth + 1)
#             elif pred != RDFS.isDefinedBy:
#                 # Handle other predicates: rdfs:member, rdf:value
#                 traverse(graph, obj, visited, depth + 1)
# 
# # Build RDF graph
# g = Graph()
# g.parse(data='''
# @prefix ABC: <http://example.org/ABC#> .
# @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
#
# ABC: xsd:integer ABC:Int ;
#     xsd:string ABC:S .
#
# ABC:Ab rdfs:member ABC:A .
#
# ABC:B a ABC:Class ;
#     rdfs:isDefinedBy ABC:K,
#                      ABC:L .
#
# ABC:Int rdf:value ABC:A .
#
# ABC:K rdfs:member ABC:ABC .
#
# ABC:L rdfs:member ABC:ABC .
#
# ABC:S rdf:value ABC:B .
#
# ABC:A rdfs:member ABC:ABC .
#
# ABC:ABC a ABC:Class .
# ''', format='turtle')
#
# # Start traversal
# start = URIRef("http://example.org/ABC#ABC")
# traverse(g, start)
#
#
#
# # from rdflib import Graph, URIRef, Namespace
# #
# # def traverse(graph, node, visited=None, depth=0):
# #     if visited is None:
# #         visited = set()
# #
# #     # Skip already visited nodes to avoid cycles
# #     if node in visited:
# #         return
# #     visited.add(node)
# #
# #     # Print the current node (just the local name for clarity)
# #     print("  " * depth + node.split('#')[-1])
# #
# #     # Namespaces
# #     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# #     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# #
# #     # Process the triples starting with this node (predicates: rdfs:isDefinedBy, rdfs:member, rdf:value)
# #     for _, pred, obj in graph.triples((node, None, None)):
# #         if isinstance(obj, URIRef):  # Only process URIRefs (nodes)
# #             if pred == RDFS.isDefinedBy:
# #                 # Special handling for isDefinedBy predicate: process defined nodes
# #                 traverse(graph, obj, visited, depth + 1)
# #             elif pred != RDFS.isDefinedBy:
# #                 # Handle other predicates: rdfs:member, rdf:value
# #                 traverse(graph, obj, visited, depth + 1)
# #
# # # Build RDF graph
# # g = Graph()
# # g.parse(data='''
# # @prefix ABC: <http://example.org/ABC#> .
# # @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# # @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# #
# # ABC: xsd:integer ABC:Int ;
# #     xsd:string ABC:S .
# #
# # ABC:Ab rdfs:member ABC:A .
# #
# # ABC:B a ABC:Class ;
# #     rdfs:isDefinedBy ABC:K,
# #                      ABC:L .
# #
# # ABC:Int rdf:value ABC:A .
# #
# # ABC:K rdfs:member ABC:ABC .
# #
# # ABC:L rdfs:member ABC:ABC .
# #
# # ABC:S rdf:value ABC:B .
# #
# # ABC:A rdfs:member ABC:ABC .
# #
# # ABC:ABC a ABC:Class .
# # ''', format='turtle')
# #
# # # Start traversal
# # start = URIRef("http://example.org/ABC#ABC")
# # traverse(g, start)
# #
# #
# #
# # # from rdflib import Graph, URIRef, Namespace
# # #
# # # def traverse(graph, node, visited=None, depth=0):
# # #     if visited is None:
# # #         visited = set()
# # #
# # #     # Skip already visited nodes to avoid cycles
# # #     if node in visited:
# # #         return
# # #     visited.add(node)
# # #
# # #     # Print the current node (just the local name for clarity)
# # #     print("  " * depth + node.split('#')[-1])
# # #
# # #     # Namespaces
# # #     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# # #     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# # #
# # #     # Process the triples starting with this node (predicates are rdfs:isDefinedBy, rdfs:member, rdf:value)
# # #     for _, pred, obj in graph.triples((node, None, None)):
# # #         if isinstance(obj, URIRef):  # Only process URIRefs (nodes)
# # #             if pred == RDFS.isDefinedBy:
# # #                 # Special handling for isDefinedBy predicate: handle it recursively
# # #                 traverse(graph, obj, visited, depth + 1)
# # #             elif pred != RDFS.isDefinedBy:
# # #                 # Handle other predicates: rdfs:member, rdf:value
# # #                 traverse(graph, obj, visited, depth + 1)
# # #
# # # # Build RDF graph
# # # g = Graph()
# # # g.parse(data='''
# # # @prefix ABC: <http://example.org/ABC#> .
# # # @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# # # @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# # # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# # #
# # # ABC: xsd:integer ABC:Int ;
# # #     xsd:string ABC:S .
# # #
# # # ABC:Ab rdfs:member ABC:A .
# # #
# # # ABC:B a ABC:Class ;
# # #     rdfs:isDefinedBy ABC:K,
# # #                      ABC:L .
# # #
# # # ABC:Int rdf:value ABC:A .
# # #
# # # ABC:K rdfs:member ABC:ABC .
# # #
# # # ABC:L rdfs:member ABC:ABC .
# # #
# # # ABC:S rdf:value ABC:B .
# # #
# # # ABC:A rdfs:member ABC:ABC .
# # #
# # # ABC:ABC a ABC:Class .
# # # ''', format='turtle')
# # #
# # # # Start traversal
# # # start = URIRef("http://example.org/ABC#ABC")
# # # traverse(g, start)
# # #
# # #
# # #
# # #
# # # # from rdflib import Graph, URIRef, Namespace
# # # #
# # # # def traverse(graph, node, visited=None, depth=0):
# # # #     if visited is None:
# # # #         visited = set()
# # # #
# # # #     # Skip already visited nodes to avoid cycles
# # # #     if node in visited:
# # # #         return
# # # #     visited.add(node)
# # # #
# # # #     # Print the current node (just the local name for clarity)
# # # #     print("  " * depth + node.split('#')[-1])
# # # #
# # # #     # Namespaces
# # # #     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# # # #     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# # # #
# # # #     # Process the triples starting with this node
# # # #     for _, pred, obj in graph.triples((node, None, None)):
# # # #         if isinstance(obj, URIRef):  # Only process URIRefs (nodes)
# # # #             if pred == RDFS.isDefinedBy:
# # # #                 # Special handling for isDefinedBy predicate
# # # #                 traverse(graph, obj, visited, depth + 1)
# # # #
# # # #             if pred != RDFS.isDefinedBy:
# # # #                 traverse(graph, obj, visited, depth + 1)
# # # #
# # # # # Build RDF graph
# # # # g = Graph()
# # # # g.parse(data='''
# # # # @prefix ABC: <http://example.org/ABC#> .
# # # # @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# # # # @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# # # # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# # # #
# # # # ABC: xsd:integer ABC:Int ;
# # # #     xsd:string ABC:S .
# # # #
# # # # ABC:Ab rdfs:member ABC:A .
# # # #
# # # # ABC:B a ABC:Class ;
# # # #     rdfs:isDefinedBy ABC:K,
# # # #                      ABC:L .
# # # #
# # # # ABC:Int rdf:value ABC:A .
# # # #
# # # # ABC:K rdfs:member ABC:ABC .
# # # #
# # # # ABC:L rdfs:member ABC:ABC .
# # # #
# # # # ABC:S rdf:value ABC:B .
# # # #
# # # # ABC:A rdfs:member ABC:ABC .
# # # #
# # # # ABC:ABC a ABC:Class .
# # # # ''', format='turtle')
# # # #
# # # # # Start traversal
# # # # start = URIRef("http://example.org/ABC#ABC")
# # # # traverse(g, start)
# # # #
# # # #
# # # # # from rdflib import Graph, URIRef, Namespace
# # # # #
# # # # #
# # # # # def traverse(graph, node, path=None, visited_isDefinedBy=None, depth=0):
# # # # #     if path is None:
# # # # #         path = set()
# # # # #     if visited_isDefinedBy is None:
# # # # #         visited_isDefinedBy = set()
# # # # #
# # # # #     # If already in path, skip to avoid loops
# # # # #     if node in path:
# # # # #         return
# # # # #
# # # # #     path = path.copy()
# # # # #     path.add(node)
# # # # #
# # # # #     print("  " * depth + node.split('#')[-1])
# # # # #
# # # # #     # Namespaces
# # # # #     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# # # # #     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# # # # #
# # # # #     # Forward predicates to follow
# # # # #     forward_preds = [RDFS.member, RDF.value, RDFS.isDefinedBy]
# # # # #
# # # # #     # Traverse each of the nodes as needed
# # # # #     for pred in forward_preds:
# # # # #         for _, _, obj in graph.triples((node, pred, None)):
# # # # #             if isinstance(obj, URIRef):
# # # # #                 # If traversing isDefinedBy, only traverse once
# # # # #                 if pred == RDFS.isDefinedBy and obj not in visited_isDefinedBy:
# # # # #                     visited_isDefinedBy.add(obj)  # Mark `isDefinedBy` as visited
# # # # #                     traverse(graph, obj, path, visited_isDefinedBy, depth + 1)
# # # # #                 elif pred != RDFS.isDefinedBy:
# # # # #                     traverse(graph, obj, path, visited_isDefinedBy, depth + 1)
# # # # #
# # # # #     # Reverse traversal (subj → node)
# # # # #     for pred in forward_preds:
# # # # #         for subj, _, _ in graph.triples((None, pred, node)):
# # # # #             if isinstance(subj, URIRef):
# # # # #                 traverse(graph, subj, path, visited_isDefinedBy, depth + 1)
# # # # #
# # # # #
# # # # # # Build RDF graph
# # # # # g = Graph()
# # # # # g.parse(data='''
# # # # # @prefix ABC: <http://example.org/ABC#> .
# # # # # @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# # # # # @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# # # # # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# # # # #
# # # # # ABC: xsd:integer ABC:Int ;
# # # # #     xsd:string ABC:S .
# # # # #
# # # # # ABC:Ab rdfs:member ABC:A .
# # # # #
# # # # # ABC:B a ABC:Class ;
# # # # #     rdfs:isDefinedBy ABC:K,
# # # # #                      ABC:L .
# # # # #
# # # # # ABC:Int rdf:value ABC:A .
# # # # #
# # # # # ABC:K rdfs:member ABC:ABC .
# # # # #
# # # # # ABC:L rdfs:member ABC:ABC .
# # # # #
# # # # # ABC:S rdf:value ABC:B .
# # # # #
# # # # # ABC:A rdfs:member ABC:ABC .
# # # # #
# # # # # ABC:ABC a ABC:Class .
# # # # # ''', format='turtle')
# # # # #
# # # # # # Start traversal
# # # # # start = URIRef("http://example.org/ABC#ABC")
# # # # # traverse(g, start)
# # # # #
# # # # # # from rdflib import Graph, URIRef, Namespace
# # # # # #
# # # # # #
# # # # # # def traverse(graph, node, path=None, visited_isDefinedBy=None, depth=0, parent=None):
# # # # # #     if path is None:
# # # # # #         path = set()
# # # # # #     if visited_isDefinedBy is None:
# # # # # #         visited_isDefinedBy = set()
# # # # # #
# # # # # #     # If already in path, skip to avoid loops
# # # # # #     if node in path:
# # # # # #         return
# # # # # #
# # # # # #     path = path.copy()
# # # # # #     path.add(node)
# # # # # #
# # # # # #     print("  " * depth + node.split('#')[-1])
# # # # # #
# # # # # #     # Namespaces
# # # # # #     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# # # # # #     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# # # # # #
# # # # # #     # Forward predicates to follow
# # # # # #     forward_preds = [RDFS.member, RDF.value, RDFS.isDefinedBy]
# # # # # #
# # # # # #     for pred in forward_preds:
# # # # # #         for _, _, obj in graph.triples((node, pred, None)):
# # # # # #             if isinstance(obj, URIRef):
# # # # # #                 # If we are traversing `rdfs:isDefinedBy`, make sure we don't traverse it multiple times.
# # # # # #                 if pred == RDFS.isDefinedBy and obj not in visited_isDefinedBy:
# # # # # #                     visited_isDefinedBy.add(obj)  # Mark `isDefinedBy` as visited
# # # # # #                     traverse(graph, obj, path, visited_isDefinedBy, depth + 1, node)
# # # # # #                 elif pred != RDFS.isDefinedBy:
# # # # # #                     traverse(graph, obj, path, visited_isDefinedBy, depth + 1, node)
# # # # # #
# # # # # #     # Reverse traversal (subj → node) - only under certain conditions
# # # # # #     for pred in forward_preds:
# # # # # #         for subj, _, _ in graph.triples((None, pred, node)):
# # # # # #             if isinstance(subj, URIRef):
# # # # # #                 # Only proceed with reverse traversal if parent is valid
# # # # # #                 if parent != subj:  # Avoid revisiting parent
# # # # # #                     traverse(graph, subj, path, visited_isDefinedBy, depth + 1, parent)
# # # # # #
# # # # # #
# # # # # # # Build RDF graph
# # # # # # g = Graph()
# # # # # # g.parse(data='''
# # # # # # @prefix ABC: <http://example.org/ABC#> .
# # # # # # @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# # # # # # @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# # # # # # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# # # # # #
# # # # # # ABC: xsd:integer ABC:Int ;
# # # # # #     xsd:string ABC:S .
# # # # # #
# # # # # # ABC:Ab rdfs:member ABC:A .
# # # # # #
# # # # # # ABC:B a ABC:Class ;
# # # # # #     rdfs:isDefinedBy ABC:K,
# # # # # #                      ABC:L .
# # # # # #
# # # # # # ABC:Int rdf:value ABC:A .
# # # # # #
# # # # # # ABC:K rdfs:member ABC:ABC .
# # # # # #
# # # # # # ABC:L rdfs:member ABC:ABC .
# # # # # #
# # # # # # ABC:S rdf:value ABC:B .
# # # # # #
# # # # # # ABC:A rdfs:member ABC:ABC .
# # # # # #
# # # # # # ABC:ABC a ABC:Class .
# # # # # # ''', format='turtle')
# # # # # #
# # # # # # # Start traversal
# # # # # # start = URIRef("http://example.org/ABC#ABC")
# # # # # # traverse(g, start)
# # # # # #
# # # # # # # from rdflib import Graph, URIRef, Namespace
# # # # # # #
# # # # # # #
# # # # # # # def traverse(graph, node, path=None, visited_isDefinedBy=None, depth=0):
# # # # # # #     if path is None:
# # # # # # #         path = set()
# # # # # # #     if visited_isDefinedBy is None:
# # # # # # #         visited_isDefinedBy = set()
# # # # # # #
# # # # # # #     # If already in path, skip to avoid loops
# # # # # # #     if node in path:
# # # # # # #         return
# # # # # # #
# # # # # # #     path = path.copy()
# # # # # # #     path.add(node)
# # # # # # #
# # # # # # #     print("  " * depth + node.split('#')[-1])
# # # # # # #
# # # # # # #     # Namespaces
# # # # # # #     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# # # # # # #     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# # # # # # #
# # # # # # #     # Forward predicates to follow
# # # # # # #     forward_preds = [RDFS.member, RDF.value, RDFS.isDefinedBy]
# # # # # # #
# # # # # # #     for pred in forward_preds:
# # # # # # #         for _, _, obj in graph.triples((node, pred, None)):
# # # # # # #             if isinstance(obj, URIRef):
# # # # # # #                 # If we are traversing `rdfs:isDefinedBy`, make sure we don't traverse it multiple times.
# # # # # # #                 if pred == RDFS.isDefinedBy and obj not in visited_isDefinedBy:
# # # # # # #                     visited_isDefinedBy.add(obj)  # Mark `isDefinedBy` as visited
# # # # # # #                     traverse(graph, obj, path, visited_isDefinedBy, depth + 1)
# # # # # # #                 elif pred != RDFS.isDefinedBy:
# # # # # # #                     traverse(graph, obj, path, visited_isDefinedBy, depth + 1)
# # # # # # #
# # # # # # #     # Reverse traversal (subj → node)
# # # # # # #     for pred in forward_preds:
# # # # # # #         for subj, _, _ in graph.triples((None, pred, node)):
# # # # # # #             if isinstance(subj, URIRef):
# # # # # # #                 traverse(graph, subj, path, visited_isDefinedBy, depth + 1)
# # # # # # #
# # # # # # #
# # # # # # # # Build RDF graph
# # # # # # # g = Graph()
# # # # # # # g.parse(data='''
# # # # # # # @prefix ABC: <http://example.org/ABC#> .
# # # # # # # @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# # # # # # # @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# # # # # # # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# # # # # # #
# # # # # # # ABC: xsd:integer ABC:Int ;
# # # # # # #     xsd:string ABC:S .
# # # # # # #
# # # # # # # ABC:Ab rdfs:member ABC:A .
# # # # # # #
# # # # # # # ABC:B a ABC:Class ;
# # # # # # #     rdfs:isDefinedBy ABC:K,
# # # # # # #                      ABC:L .
# # # # # # #
# # # # # # # ABC:Int rdf:value ABC:A .
# # # # # # #
# # # # # # # ABC:K rdfs:member ABC:ABC .
# # # # # # #
# # # # # # # ABC:L rdfs:member ABC:ABC .
# # # # # # #
# # # # # # # ABC:S rdf:value ABC:B .
# # # # # # #
# # # # # # # ABC:A rdfs:member ABC:ABC .
# # # # # # #
# # # # # # # ABC:ABC a ABC:Class .
# # # # # # # ''', format='turtle')
# # # # # # #
# # # # # # # # Start traversal
# # # # # # # start = URIRef("http://example.org/ABC#ABC")
# # # # # # # traverse(g, start)
# # # # # # #
# # # # # # # # from rdflib import Graph, URIRef, Namespace
# # # # # # # #
# # # # # # # # def traverse(graph, node, path=None, depth=0):
# # # # # # # #     if path is None:
# # # # # # # #         path = set()
# # # # # # # #
# # # # # # # #     if node in path:
# # # # # # # #         return
# # # # # # # #     path = path.copy()
# # # # # # # #     path.add(node)
# # # # # # # #
# # # # # # # #     print("  " * depth + node.split('#')[-1])
# # # # # # # #
# # # # # # # #     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# # # # # # # #     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# # # # # # # #
# # # # # # # #     predicates = [RDFS.member, RDF.value, RDFS.isDefinedBy]
# # # # # # # #
# # # # # # # #     # Forward traversal (node → obj)
# # # # # # # #     for pred in predicates:
# # # # # # # #         for _, _, obj in graph.triples((node, pred, None)):
# # # # # # # #             if isinstance(obj, URIRef):
# # # # # # # #                 traverse(graph, obj, path, depth + 1)
# # # # # # # #
# # # # # # # #     # Reverse traversal (subj → node)
# # # # # # # #     for pred in predicates:
# # # # # # # #         for subj, _, _ in graph.triples((None, pred, node)):
# # # # # # # #             if isinstance(subj, URIRef):
# # # # # # # #                 traverse(graph, subj, path, depth + 1)
# # # # # # # #
# # # # # # # # # Build RDF graph
# # # # # # # # g = Graph()
# # # # # # # # g.parse(data='''
# # # # # # # # @prefix ABC: <http://example.org/ABC#> .
# # # # # # # # @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# # # # # # # # @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# # # # # # # # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# # # # # # # #
# # # # # # # # ABC: xsd:integer ABC:Int ;
# # # # # # # #     xsd:string ABC:S .
# # # # # # # #
# # # # # # # # ABC:Ab rdfs:member ABC:A .
# # # # # # # #
# # # # # # # # ABC:B a ABC:Class ;
# # # # # # # #     rdfs:isDefinedBy ABC:K,
# # # # # # # #                      ABC:L .
# # # # # # # #
# # # # # # # # ABC:Int rdf:value ABC:A .
# # # # # # # #
# # # # # # # # ABC:K rdfs:member ABC:ABC .
# # # # # # # #
# # # # # # # # ABC:L rdfs:member ABC:ABC .
# # # # # # # #
# # # # # # # # ABC:S rdf:value ABC:B .
# # # # # # # #
# # # # # # # # ABC:A rdfs:member ABC:ABC .
# # # # # # # #
# # # # # # # # ABC:ABC a ABC:Class .
# # # # # # # # ''', format='turtle')
# # # # # # # #
# # # # # # # # # Start traversal
# # # # # # # # start = URIRef("http://example.org/ABC#ABC")
# # # # # # # # traverse(g, start)
# # # # # # # #
# # # # # # # #
# # # # # # # # # from rdflib import Graph, URIRef, Namespace
# # # # # # # # #
# # # # # # # # # # Traversal function
# # # # # # # # # def traverse(graph, node, path=None, depth=0):
# # # # # # # # #     if path is None:
# # # # # # # # #         path = set()
# # # # # # # # #
# # # # # # # # #     if node in path:
# # # # # # # # #         return  # Prevent cycles
# # # # # # # # #     path = path.copy()
# # # # # # # # #     path.add(node)
# # # # # # # # #
# # # # # # # # #     print("  " * depth + node.split('#')[-1])
# # # # # # # # #
# # # # # # # # #     # Namespaces
# # # # # # # # #     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# # # # # # # # #     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# # # # # # # # #
# # # # # # # # #     # Forward predicates to follow
# # # # # # # # #     forward_preds = [RDFS.member, RDF.value, RDFS.isDefinedBy]
# # # # # # # # #
# # # # # # # # #     for pred in forward_preds:
# # # # # # # # #         for _, _, obj in graph.triples((node, pred, None)):
# # # # # # # # #             if isinstance(obj, URIRef):
# # # # # # # # #                 traverse(graph, obj, path, depth + 1)
# # # # # # # # #
# # # # # # # # # # RDF data
# # # # # # # # # g = Graph()
# # # # # # # # # g.parse(data='''
# # # # # # # # # @prefix ABC: <http://example.org/ABC#> .
# # # # # # # # # @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# # # # # # # # # @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# # # # # # # # # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# # # # # # # # #
# # # # # # # # # ABC: xsd:integer ABC:Int ;
# # # # # # # # #     xsd:string ABC:S .
# # # # # # # # #
# # # # # # # # # ABC:Ab rdfs:member ABC:A .
# # # # # # # # #
# # # # # # # # # ABC:B a ABC:Class ;
# # # # # # # # #     rdfs:isDefinedBy ABC:K,
# # # # # # # # #                      ABC:L .
# # # # # # # # #
# # # # # # # # # ABC:Int rdf:value ABC:A .
# # # # # # # # #
# # # # # # # # # ABC:K rdfs:member ABC:ABC .
# # # # # # # # #
# # # # # # # # # ABC:L rdfs:member ABC:ABC .
# # # # # # # # #
# # # # # # # # # ABC:S rdf:value ABC:B .
# # # # # # # # #
# # # # # # # # # ABC:A rdfs:member ABC:ABC .
# # # # # # # # #
# # # # # # # # # ABC:ABC a ABC:Class .
# # # # # # # # # ''', format='turtle')
# # # # # # # # #
# # # # # # # # # # Start traversal
# # # # # # # # # start = URIRef("http://example.org/ABC#ABC")
# # # # # # # # # traverse(g, start)
# # # # # # # # #
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # # from rdflib import Graph, URIRef, Namespace
# # # # # # # # # #
# # # # # # # # # # def traverse(graph, node, path=None, depth=0):
# # # # # # # # # #     if path is None:
# # # # # # # # # #         path = set()
# # # # # # # # # #
# # # # # # # # # #     if node in path:
# # # # # # # # # #         return
# # # # # # # # # #     path = path.copy()
# # # # # # # # # #     path.add(node)
# # # # # # # # # #
# # # # # # # # # #     print("  " * depth + node.split('#')[-1])
# # # # # # # # # #
# # # # # # # # # #     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# # # # # # # # # #     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# # # # # # # # # #
# # # # # # # # # #     predicates = [RDFS.member, RDF.value, RDFS.isDefinedBy]
# # # # # # # # # #
# # # # # # # # # #     # Forward traversal
# # # # # # # # # #     for pred in predicates:
# # # # # # # # # #         for _, _, obj in graph.triples((node, pred, None)):
# # # # # # # # # #             if isinstance(obj, URIRef):
# # # # # # # # # #                 traverse(graph, obj, path, depth + 1)
# # # # # # # # # #
# # # # # # # # # #     # Reverse traversal
# # # # # # # # # #     for pred in predicates:
# # # # # # # # # #         for subj, _, _ in graph.triples((None, pred, node)):
# # # # # # # # # #             if isinstance(subj, URIRef):
# # # # # # # # # #                 traverse(graph, subj, path, depth + 1)
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # # # from rdflib import Graph, URIRef, Namespace
# # # # # # # # # # #
# # # # # # # # # # # def traverse(graph, node, visited=None, depth=0):
# # # # # # # # # # #     if visited is None:
# # # # # # # # # # #         visited = set()
# # # # # # # # # # #
# # # # # # # # # # #     if node in visited:
# # # # # # # # # # #         return
# # # # # # # # # # #     visited.add(node)
# # # # # # # # # # #
# # # # # # # # # # #     print("  " * depth + node.split('#')[-1])
# # # # # # # # # # #
# # # # # # # # # # #     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# # # # # # # # # # #     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# # # # # # # # # # #
# # # # # # # # # # #     predicates = [RDFS.member, RDF.value, RDFS.isDefinedBy]
# # # # # # # # # # #
# # # # # # # # # # #     # Traverse forward
# # # # # # # # # # #     for pred in predicates:
# # # # # # # # # # #         for _, _, obj in graph.triples((node, pred, None)):
# # # # # # # # # # #             if isinstance(obj, URIRef):
# # # # # # # # # # #                 traverse(graph, obj, visited, depth + 1)
# # # # # # # # # # #
# # # # # # # # # # #     # Traverse reverse
# # # # # # # # # # #     for pred in predicates:
# # # # # # # # # # #         for subj, _, _ in graph.triples((None, pred, node)):
# # # # # # # # # # #             if isinstance(subj, URIRef):
# # # # # # # # # # #                 traverse(graph, subj, visited, depth + 1)
# # # # # # # # # # #
# # # # # # # # # # # # === RDF Data ===
# # # # # # # # # # # g = Graph()
# # # # # # # # # # # g.parse(data='''
# # # # # # # # # # # @prefix ABC: <http://example.org/ABC#> .
# # # # # # # # # # # @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# # # # # # # # # # # @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# # # # # # # # # # # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# # # # # # # # # # #
# # # # # # # # # # # ABC: xsd:integer ABC:Int ;
# # # # # # # # # # #     xsd:string ABC:S .
# # # # # # # # # # #
# # # # # # # # # # # ABC:Ab rdfs:member ABC:A .
# # # # # # # # # # #
# # # # # # # # # # # ABC:B a ABC:Class ;
# # # # # # # # # # #     rdfs:isDefinedBy ABC:K,
# # # # # # # # # # #         ABC:L .
# # # # # # # # # # #
# # # # # # # # # # # ABC:Int rdf:value ABC:A .
# # # # # # # # # # #
# # # # # # # # # # # ABC:K rdfs:member ABC:ABC .
# # # # # # # # # # #
# # # # # # # # # # # ABC:L rdfs:member ABC:ABC .
# # # # # # # # # # #
# # # # # # # # # # # ABC:S rdf:value ABC:B .
# # # # # # # # # # #
# # # # # # # # # # # ABC:A rdfs:member ABC:ABC .
# # # # # # # # # # #
# # # # # # # # # # # ABC:ABC a ABC:Class .
# # # # # # # # # # # ''', format='turtle')
# # # # # # # # # # #
# # # # # # # # # # # # === Traverse starting from ABC:ABC ===
# # # # # # # # # # # start = URIRef("http://example.org/ABC#ABC")
# # # # # # # # # # # traverse(g, start)
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # from rdflib import Graph, URIRef, Namespace
# # # # # # # # # # # #
# # # # # # # # # # # # def traverse(graph, node, path=None, depth=0):
# # # # # # # # # # # #     if path is None:
# # # # # # # # # # # #         path = set()
# # # # # # # # # # # #     path = path.copy()
# # # # # # # # # # # #     path.add(node)
# # # # # # # # # # # #
# # # # # # # # # # # #     print("  " * depth + node.split('#')[-1])
# # # # # # # # # # # #
# # # # # # # # # # # #     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# # # # # # # # # # # #     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# # # # # # # # # # # #
# # # # # # # # # # # #     predicates = [RDFS.member, RDF.value, RDFS.isDefinedBy]
# # # # # # # # # # # #
# # # # # # # # # # # #     # forward predicates
# # # # # # # # # # # #     for pred in predicates:
# # # # # # # # # # # #         for _, _, obj in graph.triples((node, pred, None)):
# # # # # # # # # # # #             if isinstance(obj, URIRef) and obj not in path:
# # # # # # # # # # # #                 traverse(graph, obj, path, depth + 1)
# # # # # # # # # # # #
# # # # # # # # # # # #     # reverse rdfs:member
# # # # # # # # # # # #     for subj, _, _ in graph.triples((None, RDFS.member, node)):
# # # # # # # # # # # #         if subj not in path:
# # # # # # # # # # # #             traverse(graph, subj, path, depth + 1)
# # # # # # # # # # # #
# # # # # # # # # # # #     # reverse rdf:value
# # # # # # # # # # # #     for subj, _, _ in graph.triples((None, RDF.value, node)):
# # # # # # # # # # # #         if subj not in path:
# # # # # # # # # # # #             traverse(graph, subj, path, depth + 1)
# # # # # # # # # # # #
# # # # # # # # # # # #     # reverse rdfs:isDefinedBy
# # # # # # # # # # # #     for subj, _, _ in graph.triples((None, RDFS.isDefinedBy, node)):
# # # # # # # # # # # #         if subj not in path:
# # # # # # # # # # # #             traverse(graph, subj, path, depth + 1)
# # # # # # # # # # # #
# # # # # # # # # # # #
# # # # # # # # # # # #
# # # # # # # # # # # # # from rdflib import Graph, URIRef, Namespace
# # # # # # # # # # # # #
# # # # # # # # # # # # # def traverse(graph, node, path=None, depth=0):
# # # # # # # # # # # # #     if path is None:
# # # # # # # # # # # # #         path = set()
# # # # # # # # # # # # #     path = path.copy()
# # # # # # # # # # # # #     path.add(node)
# # # # # # # # # # # # #
# # # # # # # # # # # # #     print("  " * depth + node.split('#')[-1])
# # # # # # # # # # # # #
# # # # # # # # # # # # #     RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# # # # # # # # # # # # #     RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# # # # # # # # # # # # #
# # # # # # # # # # # # #     predicates = [RDFS.member, RDF.value, RDFS.isDefinedBy]
# # # # # # # # # # # # #
# # # # # # # # # # # # #     for pred in predicates:
# # # # # # # # # # # # #         for _, _, obj in graph.triples((node, pred, None)):
# # # # # # # # # # # # #             if isinstance(obj, URIRef) and obj not in path:
# # # # # # # # # # # # #                 traverse(graph, obj, path, depth + 1)
# # # # # # # # # # # # #
# # # # # # # # # # # # #     # NEW: follow reverse rdfs:member (e.g., ?child rdfs:member ABC:ABC)
# # # # # # # # # # # # #     for subj, _, _ in graph.triples((None, RDFS.member, node)):
# # # # # # # # # # # # #         if subj not in path:
# # # # # # # # # # # # #             traverse(graph, subj, path, depth + 1)
# # # # # # # # # # # # #
# # # # # # # # # # # # # # === Parse the data ===
# # # # # # # # # # # # # g = Graph()
# # # # # # # # # # # # # g.parse(data='''
# # # # # # # # # # # # # @prefix ABC: <http://example.org/ABC#> .
# # # # # # # # # # # # # @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# # # # # # # # # # # # # @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# # # # # # # # # # # # # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# # # # # # # # # # # # #
# # # # # # # # # # # # # ABC: xsd:integer ABC:Int ;
# # # # # # # # # # # # #     xsd:string ABC:S .
# # # # # # # # # # # # #
# # # # # # # # # # # # # ABC:Ab rdfs:member ABC:A .
# # # # # # # # # # # # #
# # # # # # # # # # # # # ABC:B a ABC:Class ;
# # # # # # # # # # # # #     rdfs:isDefinedBy ABC:K,
# # # # # # # # # # # # #         ABC:L .
# # # # # # # # # # # # #
# # # # # # # # # # # # # ABC:Int rdf:value ABC:A .
# # # # # # # # # # # # #
# # # # # # # # # # # # # ABC:K rdfs:member ABC:ABC .
# # # # # # # # # # # # #
# # # # # # # # # # # # # ABC:L rdfs:member ABC:ABC .
# # # # # # # # # # # # #
# # # # # # # # # # # # # ABC:S rdf:value ABC:B .
# # # # # # # # # # # # #
# # # # # # # # # # # # # ABC:A rdfs:member ABC:ABC .
# # # # # # # # # # # # #
# # # # # # # # # # # # # ABC:ABC a ABC:Class .
# # # # # # # # # # # # # ''', format='turtle')
# # # # # # # # # # # # #
# # # # # # # # # # # # # # === Traverse from ABC:ABC ===
# # # # # # # # # # # # # start = URIRef("http://example.org/ABC#ABC")
# # # # # # # # # # # # # traverse(g, start)
# # # # # # # # # # # # #
# # # # # # # # # # # # #
# # # # # # # # # # # # #
# # # # # # # # # # # # # # from rdflib import Graph, URIRef
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # def traverse(graph, node, path=None, depth=0):
# # # # # # # # # # # # # #     if path is None:
# # # # # # # # # # # # # #         path = set()
# # # # # # # # # # # # # #     path = path.copy()  # Keep path local to this branch
# # # # # # # # # # # # # #     path.add(node)
# # # # # # # # # # # # # #
# # # # # # # # # # # # # #     print("  " * depth + node.split('#')[-1])
# # # # # # # # # # # # # #
# # # # # # # # # # # # # #     predicates = [
# # # # # # # # # # # # # #         URIRef("http://www.w3.org/2000/01/rdf-schema#member"),
# # # # # # # # # # # # # #         URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#value"),
# # # # # # # # # # # # # #         URIRef("http://www.w3.org/2000/01/rdf-schema#isDefinedBy"),
# # # # # # # # # # # # # #     ]
# # # # # # # # # # # # # #
# # # # # # # # # # # # # #     for pred in predicates:
# # # # # # # # # # # # # #         for _, _, obj in graph.triples((node, pred, None)):
# # # # # # # # # # # # # #             if isinstance(obj, URIRef) and obj not in path:
# # # # # # # # # # # # # #                 traverse(graph, obj, path, depth + 1)
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # # Load the RDF graph in Turtle format
# # # # # # # # # # # # # # g = Graph()
# # # # # # # # # # # # # # g.parse(data='''
# # # # # # # # # # # # # # @prefix ABC: <http://example.org/ABC#> .
# # # # # # # # # # # # # # @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# # # # # # # # # # # # # # @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# # # # # # # # # # # # # # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # ABC: xsd:integer ABC:Int ;
# # # # # # # # # # # # # #     xsd:string ABC:S .
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # ABC:Ab rdfs:member ABC:A .
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # ABC:B a ABC:Class ;
# # # # # # # # # # # # # #     rdfs:isDefinedBy ABC:K,
# # # # # # # # # # # # # #         ABC:L .
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # ABC:Int rdf:value ABC:A .
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # ABC:K rdfs:member ABC:ABC .
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # ABC:L rdfs:member ABC:ABC .
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # ABC:S rdf:value ABC:B .
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # ABC:A rdfs:member ABC:ABC .
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # ABC:ABC a ABC:Class .
# # # # # # # # # # # # # # ''', format='turtle')
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # # Start traversal from ABC:ABC
# # # # # # # # # # # # # # start_node = URIRef("http://example.org/ABC#ABC")
# # # # # # # # # # # # # # traverse(g, start_node)
