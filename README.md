# Fealden-0.2

Biosensors constructed from DNA and an electrochemical tag can be tailored to detect the presence of a "target" substance which binds to DNA in a sequence and motif specific manner. Fealden automates the design of such biosensors for simple binding motifs. 

## Getting Started


If you're running linux, simply grab the latest version of fealden:

```
$ git clone https://github.com/aviva-bulow/fealden-0.2.git
```
Fealden depends on a program called unafold, which you'll have to install. 
The easist way to do that is to run the install script:

```
$ cd fealden-0.2
$ sudo ./install.sh
```
If this doesn't work for you, navigate to fealden-0.2/fealden/unafold-3.8 and follow the instructions in the INSTALL file there.
You may need to extract unafold-3.8.tar.gz first.
```
$ cd fealden 
$ tar -xzf unafold-3.8.tar.gz ; cd unafold-3.8
$ gedit INSTALL
```
### Prerequisites

Python 2.x or 3.x
Make
gcc

## Running Fealden

Navigate to the fealden-0.2/fealden directory. 

```
$ cd fealden-0.2/fealden
```

If your target binds to a single stranded region of DNA with the signature "ATTCGACC"
you would enter:
```
$ python fealden.py attcgacc 1
```
If your target binds to a double stranded region of DNA with the signature "ATTCGACC"
you would enter:
```
$ python fealden.py attcgacc 0
```
To see all possible options enter:

```
$ python fealden.py -h
```

## Authors

* **Aviva Bulow** 
* **Andrew Bonham** 

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the GNU General Public License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* This work was inspired by earlier work done by Jody Stephens. 
* This work depends on the program unafold-3.8, written by Nicholas R. Markham and Michael Zuker