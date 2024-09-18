##########::Instructions to use PERICONTO 0.2::####

Authors:
    Heinz A Preisig
    Vinay Gautam



A brief note about the name: The name PERICONTO has two parts: PERI+ CONTO. 
PERI stands for a term related to Indian Yellow, 
a mysterious transluscnet paint ingredient used untill 19th century (https://en.wikipedia.org/wiki/Indian_yellow).
CONTO stands for coating ontologies.




# how to use PERICONTO_generic_0.1 
    The program is built on pyqt6 and python 3 

    1. make a project directory
    2. change to project directory
    3. create and activate a virtual invironment as following 
        $ python3 -m venv .venv
        $ source .venv/bin/activate
    4. Install dependencies (there was an unresolvable error with the package PyQtWebEngine,tested in Python 3.6)
        $ pip3 install -r requirements.txt ()
    5. launch the PeriConto's GUI
        $ python3 PeriConto.py


# Information about directories




        periconto_0.1
        ├── ontologyRepository  -- quatruple stores and pdf figures of the generated graph
        ├── README.md
        └── src
            ├── attic -- not used
            ├── resources
            ├── PeriConto.py
            ├── PeriConto_gui.py
            ├── PeriConto_gui.ui
            └── requirements.txt




# What one can do with the periconto?

    Currently it allows:
         1. load an existing ontlogy (<name>.trig)
            or create a new ontology -- it will ask for file <name>
            starts a new tree with the root named root
         2. chose an existing sample ontology. 
            asks for input file
         3. one can:
                . add items to a class
                . link a class to an item in a class
                    . either define a new class
                    . or choose an existing class
                . add a primitive to a class or a subclass
                    . primitives are integer, string, comment, decimal, uri
                . items and primitives can be renamed (double click on name)
                . unlink items from a class
                . remove items, primitives and unused classes

    Not (yet) implented:
        1. renaming classes
        2. handling of elucidations