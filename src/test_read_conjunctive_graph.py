
import glob
import json
import os
import sys

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, 'resources')])

from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import *
from graphviz import Digraph
from rdflib import ConjunctiveGraph
from rdflib import Graph
from rdflib import Literal
from rdflib import RDF
from rdflib import XSD
from rdflib.namespace import RDFS

# from graphHAP import Graph
from PeriConto_gui import Ui_MainWindow
from resources.pop_up_message_box import makeMessageBox
from resources.resources_icons import roundButton
from resources.ui_string_dialog_impl import UI_String
from resources.ui_single_list_selector_impl import UI_stringSelector

# https://www.w3.org/TR/rdf12-concepts/#dfn-rdf-dataset
# https://www.w3.org/TR/rdf-schema/#ch_resource

RDFSTerms = {
        "class"           : RDFS.Class,
        "is_a_subclass_of": RDFS.subClassOf,
        "link_to_class"   : RDFS.isDefinedBy,
        "value"           : RDF.value,
        "comment"         : RDFS.comment,
        "integer"         : XSD.integer,
        "string"          : XSD.string,
        }

MYTerms = {v: k for k, v in RDFSTerms.items()}

VALUE = "value"
PRIMITIVES = ["integer", "string", "comment"]
ADD_ELUCIDATIONS = ["class", "subclass", VALUE]

COLOURS = {
        "is_a_subclass_of": QtGui.QColor(0, 0, 0, 255),
        "link_to_class"   : QtGui.QColor(255, 100, 5, 255),
        "value"           : QtGui.QColor(155, 155, 255),
        "comment"         : QtGui.QColor(155, 155, 255),
        "integer"         : QtGui.QColor(155, 155, 255),
        "string"          : QtGui.QColor(255, 200, 200, 255),
        "selected"        : QtGui.QColor(252, 248, 192, 255),
        "unselect"        : QtGui.QColor(255, 255, 255, 255),
        }

EDGE_COLOUR = {
        "is_a_subclass_of": "blue",
        "link_to_class"   : "red",
        "value"           : "black",
        "comment"         : "green",
        "integer"         : "darkorange",
        "string"          : "cyan",
        }

QBRUSHES = {"is_a_subclass_of": QtGui.QBrush(COLOURS["is_a_subclass_of"]),
            "link_to_class"   : QtGui.QBrush(COLOURS["link_to_class"]),
            "value"           : QtGui.QBrush(COLOURS["value"]),
            "comment"         : QtGui.QBrush(COLOURS["comment"]),
            "integer"         : QtGui.QBrush(COLOURS["integer"]),
            "string"          : QtGui.QBrush(COLOURS["string"]),
            # "selected"        : QtGui.QBrush(COLOURS["selected"]), # not needed auto-implemented
            # "unselect"        : QtGui.QBrush(COLOURS["unselect"]),
            }

DIRECTION = {
        "is_a_subclass_of": 1,
        "link_to_class"   : 1,
        "value"           : -1,
        "comment"         : -1,
        "integer"         : -1,
        "string"          : -1,
        }

LINK_COLOUR = QtGui.QColor(255, 100, 5, 255)
PRIMITIVE_COLOUR = QtGui.QColor(255, 3, 23, 255)

ONTOLOGY_DIRECTORY = "../ontologyRepository"