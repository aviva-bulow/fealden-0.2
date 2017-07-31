Fealden automates the design of simple biosensors and works with python2.x and python3.x

Fealden depends on a program called unafold. To install unafold:

    Navigate to fealden-0.2, and try: 
      $ sudo ./install
    
    This should install unafold. 
    If that doesn't work, navigate to fealden-0.2/fealden/unafold-3.8 and follow the instructions in the INSTALL file there. 
    You may need to extract unafold-3.8.tar.gz first.



To run fealden:
  Navigate to fealden-0.2/fealden. 
  Into your terminal, type: 

    $ python fealden.py -h 

  This will give you the details on how to enter the fealden parameters properly. 


The resulting sensors will be output to the terminal, they will also be automatically saved in a file labeled "results.txt". This file is re-written whenever you run fealden, so if you want a permanent copy of your results, rename the file after you run fealden.



To introduce a new seed graph:
     Construct your favorite sensor structure.
     Convert it to a seed graph (see "how_to_make_a_seed_graph.pdf" for details).
     Follow the instructions for converting the graph structure into the proper text format listed in the documentation of the functions "parse_seed_file()" in fealden.py and "make_graph()" in the file "seed.py". 
     Append your graph to the proper file. If you're sensor binds to a double stranded region, append it to 1seedGraphs.txt, if it binds to a double stranded region append it to 0seedGraphs.txt. 

If you have any questions, feel free to email me at aviva_bulow@berkeley.edu. I will do my best to help. 
