'''
Copyright 2016, 2017 Aviva Bulow

This file is part of Fealden.

    Fealden is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Fealden is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Fealden.  If not, see <http://www.gnu.org/licenses/>.

'''



import seed
import sys as system
import multiprocessing, copy, os, timeit, argparse, re, random

BINDING_STATE = {'DS' : 0, 'SS' : 1}

'''
    __main__() begins the program, parses, and validates the command line arguments.
    The program is run by typing "python ./fealden.py STRING INT' where:
        STRING is a string, in quotes, which consists of A, T, C, G, a, c, t, or g
        and which represents the recognition sequence
        INT is an integer, either 0 or 1, which denotes the binding state of the
        recognition sequence. 0 stands for DS, 1 stands for SS.

    Parameters:
        None
    Returns:
        Nothing
''' 
def __main__():
    parser = argparse.ArgumentParser()
    parser.add_argument("recSeq", type=str,\
                        help="The sequenced recognized by your target \
                        represented as a string comprised of the letters 'a', 'A', 't', \
                        'T', 'c', 'C', 'g', and 'G'.")
    parser.add_argument("bindingState", type=int, \
                        help="The state of the sequence when bound to the target.\
                        \n This is 0 if your target binds to a double stranded sequence\
                        and 1 if it binds to a single stranded sequence.")
    parser.add_argument("-ms", "-max_size", type=int, \
                        help = "The maximum number of bases allowed in your sensor.\
                        This number must be greater than 20 and should probably be less \
                        than 50.", \
                        default = 50)
    parser.add_argument("-sps", "-sens_per_seed", type= int, \
                        help = "The minimum number of potential sensors per seed graph \
                        structure. \n This number should be increased if you\
                        are not getting enough results. (Start by increasing it to 2000, \
                        and increase from there if you are still unsatisfied.)",\
                        default = 500)
    #TODO: Binding affinity tuning
    #TODO: Anticipated target concentration tuning
      
    args = parser.parse_args()
    invalidChars = re.compile('[bdefhijklmnopqrsuvwxyz]', re.IGNORECASE)
    if invalidChars.search(args.recSeq):
        print("Invalid recognition sequence.\n You must enter a sequence \
               consisting only of a,c,t,g,A,C,T,G.")
        system.exit(0)
    if args.bindingState != 0 and args.bindingState!=1:
        print("Invalid binding state. Argument must be 0 or 1. See -h for help.")
        system.exit(0)
    if args.ms <= 20:
        print("Maximum sensor size is too low, it must be greater than 20.")
        system.exit(0)
    f = Fealden(args.recSeq, args.bindingState, args.ms, args.sps)

'''
    generate_sensor() generates a number of possible sensors and it returns the a list
    of valid sensors. 

    Parameters:
        seed        <-- an object of the 'Seed' class, the seed graph for the sensor
        recSeq      <-- a String, the recognition sequence
        numPossSen  <-- an integer, the number of possible sensors to be generated
        core        <-- an integer, the ID of the core in which this process is running
        
    Returns:
        sensors     <-- list of objects of the class 'Sensor'
'''
def generate_sensor(seed, recSeq, numPossSen, core):
   
    sensors = []
    version = 0
    minScore = float('-inf')

    
    while version < numPossSen:
        version+=1
        #build sensor from seed copy
        s = copy.deepcopy(seed)
        sen = s.build_sensor(core, version)
        
        #only keep good sensors
        if sen is None:
            continue
        if sen.score > minScore:
            sensors.append(sen)
    #print sorted(sensors)
    return sensors

'''***************************************************************************************
Generating a Fealden object automatically runs all non-interactive parts of the program. 
***************************************************************************************'''
class Fealden:


    '''
        __init__() the constructor for Fealden objects. The time it takes to run the
        program is printed to the standard out.
        To run this method sequentially, uncomment the 8th line in the method body.

        Parameters:
            recSeq         <-- a String, the recognition sequence.
            bindingState   <-- an integer, 0 or 1, representing the binding state of the
                               recognition sequence.
            maxSensorSize  <-- the maximum number of bases the user would like in their
                               sensor.
            minSensPerSeed <-- The minimum number of potential sensors to be generated
                               per seed graph. 
        Returns:
            an object of the class Fealden
    '''
    def __init__(self, recSeq, bindingState, maxSensorSize, minSensPerSeed):
        self.recSeq       = recSeq
        self.bindingState = bindingState
        self.maxSensorSize= maxSensorSize
        f                 = open(os.getcwd() + '/' + str(bindingState) + "seedGraphs.txt")
        seeds             = self.parse_seed_file(f.readlines())
        f.close()
        recommendedSensPerSeed   = 10*len(recSeq)*\
                                   ((50 - maxSensorSize) if (maxSensorSize<40) else (10))
        posSensPerSeed = recommendedSensPerSeed if \
                         recommendedSensPerSeed > minSensPerSeed else minSensPerSeed

        timeZero = timeit.default_timer()
        #'''
        numProcess        = multiprocessing.cpu_count()
        pool              = multiprocessing.Pool(numProcess)
        seedSensPerProcess= posSensPerSeed//numProcess

        tasks = []
        i = 0
        while i < numProcess:
            i+=1
            tasks.extend( [ (s, self.recSeq, seedSensPerProcess, i, ) for s in seeds] )

       
        results = [pool.apply_async( generate_sensor, t, ) for t in tasks]

        f = open(os.getcwd() + "/results.txt", 'w')
        f.write("Here are the results:\n")
        
        sensors = []
        
        for r in results:
            l = r.get()
            for s in l:
                sensors.append(s)
        
        s = sorted(sensors)
        f.write(str(s) + '\n')
        f.close()
        print(s)
        '''
        sens = []
        for s in seeds:
            sens.extend(generate_sensor(s, self.recSeq, posSensPerSeed, 1))
            
        f = open(os.getcwd() + "/results.txt", 'w')
        f.write("Here are the results:\n")
        for s in sens:
            f.write(str(s) + "\n")
        f.close()
        #'''
        print("Time: " + str(timeit.default_timer() - timeZero))

    '''
        parse_seed_file() is a simple method for parsing the seedGraph file.
        A seed graph file looks like this:
            Seed Graph 1:   <- The following information is for the first seed graph
            2               <- The name of the node which will contain the recognition seq
            2 1 3 3 5       
            3 2 2
            5 2 4
            4 5 7 7 0
            7 4 4 
            Seed Graph 2:
            4
            1 0 2
            2 1 3 3 5
            3 2 2
            5 2 4
            4 5 7 7 0
            7 4 4
            .
            .
            .
        See the comment for the "make_graph" method of the seed class for an explanation
        of how the data given correlates to a graph.

        This method breaks the data into chunks, one per seed graph, where each chunk is
        a list containing all the information about that particular graph. Then each list
        is used to generate a new seed graph using the class Seed. A list of Seed objects
        is returned.

        Parameters:
            lines <-- a list of strings, each string is a line in the seed graph data file

        Returns:
            seeds <-- a list of objects of the class "Seed"
    '''
    def parse_seed_file(self, lines):
        seeds = []
        i = 0
        l = lines[i]
        seedNum = 0
        while i < (len(lines)):
            i+=1
            l = lines[i]
            graphData = []
            recNodeName = '-1'
            seedNum +=1
            while i <(len(lines)) and lines[i].split()[0] != "Seed" :
                l = lines[i].strip()
                if len(l) == 1 :
                    recNodeName = l
                    i+=1
                    continue
                graphData.append(l)
                i +=1
            seeds.append(seed.Seed(graphData, recNodeName, self.recSeq, \
                                   self.bindingState, str("Graph " +  str(seedNum)), self.maxSensorSize))
        return seeds

#run the program from the command line        
if __name__ == "__main__":
    __main__()
