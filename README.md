# UniversalPetrarch
Language-agnostic political event coding using universal dependencies

##Prerequisites
Python package [NetworkX](https://networkx.github.io/) is required before using UniversalPetrarch. This is a library for storing and manipulating network structures consisting of nodes and edges. 


##Usage
``usage: python petrarch_ud.py batch -i INPUT_FILE -o OUTPUT_FILE -c CONFIG_FILE -d``

Required Arguments:
``-i INPUT_FILE	Filepath for the input XML file. ``
``-o OUTPUT_FILE	Filepath for the output file.``

Optional Arguments:
``-c CONFIG_FILE  Filepath for the PETRARCH configuration file. Defaults to PETR_config.ini``
``-d turn on debug mode``

