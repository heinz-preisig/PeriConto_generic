##########::Instructions to use PERICONTO 1.0::####

Authors:
    Heinz A Preisig
    Vinay Gautam



A brief note about the name: The name PERICONTO has two parts: PERI + CONTO. PERI stands for a term related to Indian Yellow, 
a mysterious transluscnet paint ingredient used untill 19th century (https://en.wikipedia.org/wiki/Indian_yellow). CONTO stands for coating ontologies.


# how to use PERICONTO_generic_0.1 
    The program is built on pyqt6 and python 3 and PDM
    
    1. make a project directory
    2. change to project directory
    3. clone PeriConto_generic
    4. add infrastructure from terminal in the PeriConto directory
        4.1 change to the new PeriConto directory
        4.2 init to generate the infrastructure
        4.3 pdm python install 3.12
        4.4 pdm sync to install all requirements
    5. Issus with icons -- .svg did not show --> install
       sudo apt-get install python3-pyqt6.qtsvg
    6. add model repository
        6.1 return to project directory
        6.2 make new directory with the name PeriConto-Ontologies
            the current version uses a fixed location and name.
        6.3 clone PeriConto-Ontologies to get started
    8. The two tasks are found in PeriConto's scr directory
        BricksSchemata.py
        TreeSchemata.py


# Information about directories




        periconto_1.0
        ├── PeriConto-Ontologies  -- quatruple stores and pdf figures of the generated graph
        └── PeriConto├── README.md
                     ├── pdm.lock
                     ├── pdm.toml
                     ├── requirements.txt (not needed)
                     └── src
                         ├── resources
                         ├── tests  (not used)
                         ├── BrickSchemata.py -- the brick editor
                         ├── TreeSchemata.py  -- the application tree editor
                         ├── ...
                    ├── attic -- not used
                    ├── notes -- not used




# What one can do with the periconto?

    Currently it allows:
        Bricks
         . load an existing brick set (<name>.trig)
            or create a new brick set -- it will ask for file <name>
         . add define a new brick
         . add items to a brick recursively
         . add primitives
         . rename bricks, items and primitives
         . make a graph plot
         . save or save with new name
         . delete bricks, items recursively, primitives

        Application trees:
         . define a new tree base on a selected brick
         . link a brick to an enabled link (an open-ended item leave)
         . add a new item to establich a new link point
         . rename a selected tree
         . copy a selected tree --> give name
         . instantiate primitives
         . reduce instantiated tree --> contains only those paths from root to instantiated primitives
        
