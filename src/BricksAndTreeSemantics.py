from rdflib import Namespace
from rdflib import RDF
from rdflib import URIRef
from rdflib import XSD
from rdflib import namespace

# https://www.w3.org/TR/rdf12-concepts/#dfn-rdf-dataset
# https://www.w3.org/TR/rdf-schema/#ch_resource
# https://www.w3.org/TR/vocab-dcat-3/#Property:resource_identifier

RDFS = namespace.RDFS
BASE = "http://example.org"
ITEM_SEPARATOR = "#"
CLASS_SEPARATOR = "/"
CLASS_IDENTIFIERS = BASE + CLASS_SEPARATOR
ITEM_IDENTIFIERS = BASE + CLASS_SEPARATOR + "%s" + ITEM_SEPARATOR
ITEM_IDENTIFIERS_COUNTED = BASE + CLASS_SEPARATOR + "%s_%s" + ITEM_SEPARATOR

# ONTOLOGY_REPOSITORY = "../ontologyRepository"
ONTOLOGY_REPOSITORY = "../../PeriConto-Ontologies"

FILE_FORMAT = "trig"
FILE_FORMAT_ = "json-ld"

IDENTIFIER_predicate = URIRef(BASE + ITEM_SEPARATOR + "identifier")

RDFSTerms = {
        "class"        : RDFS.Class,
        "is_class"     : RDF.type,  # was "is_type"
        "is_member"    : RDFS.member,
        "is_defined_by": RDFS.isDefinedBy,
        "value"        : RDF.value,
        "data_type"    : RDFS.Datatype,
        "comment"      : RDFS.comment,
        "integer"      : XSD.integer,
        "string"       : XSD.string,
        "decimal"      : XSD.decimal,
        "uri"          : XSD.anyURI,
        "label"        : RDFS.label,
        "boolean"      : XSD.boolean,
        "identifier"   : IDENTIFIER_predicate,
        }

RULES = {
        "is_class"     : "Class",
        "is_member"    : "is_member",
        "member"    : "is_member",         # tree graph
        "is_defined_by": "is_defined_by",
        "isDefinedBy"  : "is_defined_by",  # tree graph
        "value"        : "value",
        "identifier"   : "identifier",
        "string"       : "string",
        "integer"      : "integer",
        "decimal"      : "decimal",
        "uri"          : "uri",
        "boolean"      : "boolean",
        "comment"      : "comment",
        }

MYTerms = {v: k for k, v in RDFSTerms.items()}

PRIMITIVES = ["integer",
              "comment",
              "decimal",
              "string",
              "uri",
              "boolean"]

RDF_PRIMITIVES = [RDFSTerms[i] for i in PRIMITIVES]

ADD_ELUCIDATIONS = ["class", "is_member", "value"]

DIRECTION = {
        "is_member"    : 1,
        "is_defined_by": 1,
        "value"        : -1,
        "comment"      : -1,
        "integer"      : -1,
        "string"       : -1,
        # "type"            : -1,
        }


def makeClassURI(name):
  ns = Namespace(CLASS_IDENTIFIERS + name)
  ns = Namespace(ITEM_IDENTIFIERS % (name) + name)
  return ns


def makeItemURI(brick, name):
  ns = Namespace(ITEM_IDENTIFIERS % (brick) + name)
  return ns


def makeBrickNameSpace(brick, counter):
  ns = Namespace(ITEM_IDENTIFIERS_COUNTED % (brick, counter))
  return ns


def extractNameFromIRI(iri):
  s_iri = str(iri)
  if ITEM_SEPARATOR in s_iri:
    return extract_item_name(s_iri)
  else:
    return extract_class_name(s_iri)


def extract_item_name(uri):
  return uri.split(ITEM_SEPARATOR)[-1]


def extract_class_name(uri):
  return uri.split(CLASS_SEPARATOR)[-1]
