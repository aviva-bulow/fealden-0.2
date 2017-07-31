#! /bin/bash

# A script to install unafold

cd fealden
#unpack unafold, a fealden dependancy
tar -xzf unafold-3.8.tar.gz
#install unafold
cd unafold-3.8
./configure
make
make install


#format output
echo 
echo
echo "If you recieved an error message, you may need to run this script as root."
echo "If that doesn't work try the more detailed installation instructions in README."
