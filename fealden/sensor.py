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

import fold as f

''' ---------------------------------------------------------------
    Sensor is a structure to hold and interpret the results from 
    a unafold query, along with some other information. A Sensor 
    object has a sequence, a recognition sequence and 
    its location in the overall sequence, a list of Folds,
    a tagging location, the desired state of the recognition
    sequence, the name of the seed graph that gave rise to
    this sensor, and an overall score. 
-----------------------------------------------------------------'''


class Sensor:
    '''
        This is the constructor for Sensor. 
        Parameters: 
                    dataFile <- a File object (this should be the .ct
                                               returned from a unafold query)
                    recSeq   <- a dict of the form {'start': n, 'end': p}, where n,p are
                                integers and represent, respectively, the starting and
                                ending location of the recognition sequence within the
                                overall sensor's sequence.
                    respSeq <- a dict of the form {'start': n, 'end': p}, where n,p are
                                integers and represent, respectively, the starting and
                                ending location of the recognition response sequence
                                within the overall sensor's sequence. n and p are both -1
                                if the recognition sequence is single stranded.
                    desRecSeqState <- An integer, either 0 or 1, representing the state in
                                which the recognition sequence binds to the target.
                                0 represents double stranded, 1 represents single stranded.
                    seedName <- An integer, this is a simple tag to represent which
                                graph gave rise to this sensor. 
    '''
    def __init__(self,  dataFile,
                        recSeq,
                        respSeq,
                        desRecSeqState,
                        seedName):
        self.seedName = seedName
        self.recSeq = recSeq
        self.respSeq = respSeq
        self.desRecSeqState= desRecSeqState
        (self.seq, self.folds) = self.interpret_data(dataFile.readlines())
        self.onConc = 0
        self.offConc = 0
        self.noiseConc = 0
        self.onToOffDist = 0
        (self.tagLoc, self.score) = self.get_tag_and_score()

    '''
        interpret_data takes data from a the .ct file which has 
        been parsed into a list of lines. It returns a tuple. 
        The first value is the sequence, represented as a string
        of lowercase letters. The second value is a list of Folds.

        Parameters:
            lines   <-- A list of lines from the .ct file output by unafold.
        Returns:
            (seq, folds) <-- the tuple described above.

    '''
    def interpret_data(self, lines):
        (seq, structureData) = self.simplify_input(lines)
        folds = []      
        
        for i, v in enumerate(structureData):
            fold = f.Fold(v['bps'], v['deltaG'], self.recSeq)
            folds.append(fold)
        
        return (seq, folds)

        
    '''
        simplify_input takes the .ct file, represented as as list
        of lines, and distills from it the information we care 
        about into a usable form. The information returned is 
        a tuple. The first value is the sequence represented as 
        a string. The second value is a list of dictionaries. 
        The list consists of all the folds in the data file. The 
        dictionary contains all the relevant information we have
        about each fold up to this point. See the following example
        for clarification.
    
        ('attcgtgcatggtcaatcttacgttacgacggcccattcaaa' ,
         [{'deltaG': -13.4 ,        <- The delta G for the first fold in the list
          'bps'   : [[1, 0],    <- base pair 1 is bound to nothing
                     [2, 0],
                     [3, 22],   <- Base pair 3 is bound to base pair 22
                     .
                     .
                     .
                     [44, 30]]
          }
          {'deltaG': -12.3 ,    <- The second fold in the list has a delta G of -12.3
           'bps'   : [[1, 23],  <- base pair 1 is bound to base pair 23
                     .
                     .
                     .
                     [44, 0]]   <- Base pair 44 is not bound
          } 
          . 
          .
          .
         ]
        )


        Parameters:
            lines <-- a list of lines from the .ct file
        Returns:
            (sequence, stuructureData) -- the tuple described above
    '''
    def simplify_input(self, lines):
        structureData = []  
        foldIndex = -1
        foldSize = int(lines[0].split()[0])
        sequence = []   
    
        for i, v in enumerate(lines):
            if i%(foldSize + 1) == 0:
            #This line holds a deltaG value for a new structure 
                deltaG = float(v.split()[3])
                structureData.append({"deltaG" : deltaG, "bps" : []})
                foldIndex +=1;
            else:
            #This line holds information about the structure we're currently working on
                temp = v.split()
                strlist = temp[0:1] + temp[4:5]
                structureData[foldIndex]["bps"].append([int(x) for x in strlist])
                #we've just appended the base pair number, and the number of the
                #base pair it is bound to
                if i< foldSize +1:
                    sequence.append(temp[1])
        return ("".join(sequence).lower(), structureData)

    '''
        get_tag_and_score returns a number for the sensor, based on an arbitrary fitness
        scale, this serves as a proxy for our estimation of how well the sensor
        will work. The greater the number, the higher the estimation of the
        probability for success. When the value -1 is returned, the sensor was
        determined to be invalid entirely.

        Parameters:
            None
        Returns:
            A tuple, (x,y). x is an integer, the location on the sensor's sequence upon
            upon which the tag should be placed. y is a floating point number, the score
            of the sensor. 
    '''

    def get_tag_and_score(self):
        #print 'in get_score()' 
        DELTA_G_MAX_DIFFERENCE = 5
        if len(self.folds) <= 1:
            #print 'Only one fold'
            return (0, float('-inf'))
        if self.folds[1].deltaG-DELTA_G_MAX_DIFFERENCE > self.folds[0].deltaG:
            #print "First two folds have delta Gs which are too disparate."
            return (0, float('-inf'))
        if len(self.folds) >2 and self.folds[2].deltaG-DELTA_G_MAX_DIFFERENCE  > self.folds[1].deltaG:
            #print "Delta Gs of 2nd and 3rd folds are disparate."
            if self.folds[0].recSeqState == self.folds[1].recSeqState:
                #print "Recognition sequence is in the same state in the first two folds."
                return (0, float('-inf'))
            if self.folds[0].recSeqState != self.desRecSeqState and \
               self.folds[1].recSeqState != self.desRecSeqState:
                #print "In neither of the first two folds is the recognition sequence in the desired state."
                return (0, float('-inf'))
        if self.folds[0].deltaG > -2 or self.folds[0].deltaG < -50:
            #print "The first has a delta G which is out of range."
            return (0, float('-inf'))
        #sensor has passed triage criteria
        #compute validity based on criteria requiring distance
        scoreData = self.get_tagging_information()
        
        if scoreData == (0):
            return (0, float('-inf'))
        (self.tagLoc, self.onConc, self.offConc,\
         self.noiseConc, self.wrongConc, self.fuzzyConc, \
         self.onToOffDist) = scoreData
        #if sensor is valid, get optimal tagging scenario
        #score sensor based on optimal tagging scenario
        return (self.tagLoc, (1-abs(self.onConc - self.offConc)/(self.onConc + self.offConc))*self.onToOffDist)
 
    '''
        get_tagging_information() finds the optimal tagging situation, and returns some
        information with which it is associated. The information returned is labeled in
        the "Returns:" section below and should be interpreted as follows:
            position               -- the location, expressed as an integer, of the base
                                      to be tagged
            onConc                 -- the (relative) concentration of sensor that's 'on.'
            offConc                -- the (relative) concentration of sensor that's 'off.'
            noiseConc              -- the (relative) concentration of sensors that are
                                      'wrong' or 'fuzzy.'
            concWrong              -- the relative concentration of sensor that is on/off
                                      when it should be the opposite. (ie it's in the
                                      wrong state.)
            concFuzzy              -- the relative concentration of sensor in which the
                                      tags are neither close enough to be 'on' nor far
                                      enough away from the 'on' states to be truly 'off.'
            weightedAvgOnToOffDist -- the average distance of the on states
                                      less the average distance of the off states.
                                      All averages are weighted based on the
                                      concentrations of the various on and off states. 

        
        Parameters:
            None

        Returns:
            (position, onConc, offConc, noiseConc, concWrong, concFuzzy, weightedAvgOnToOffDist)
    '''

    def get_tagging_information(self):
        #print  "In get_tagging_information()"
        MAX_ON_DIST    = 12
        MIN_OFF_CHANGE = 10
        
        tagLocs = []
        #get potential tagging locations and their distances in all the various folds
        for i, v in enumerate(self.seq): 
            if v.lower() == 't' and \
            (i+1<self.recSeq['start']  or i+1 >self.recSeq['end']) and \
            (i+1<self.respSeq['start'] or i+1 > self.respSeq['end']):
                distances = [f.get_distance(1, i+1) for f in self.folds]
                smallestDist = min(distances)
                if smallestDist <= MAX_ON_DIST and \
                   max(distances) - smallestDist >= MIN_OFF_CHANGE:
                    tagLocs.append((i+1, distances))
        scoreData = (0)
        maxAvgDeltaOnToOff = 0
        #determine if this would make a good sensor if tagged in each possible location
        for t in tagLocs:   
            onConc        = 0
            offConc       = 0
            noiseConc     = 0
            concWrong     = 0
            concFuzzy     = 0

            #position == the location of the tag
            #distances == the physical distance between the tag
            #             and the first position in each fold
            (position, distances) = t
            
            onStateInfo  = []
            offStateInfo = []
            for i, d in enumerate(distances):
                currFold = self.folds[i]#the fold to which this distance is referring
                #distance is less than or equal to on dist (ie this is a on fold)
                if MAX_ON_DIST-d >= 0:
                    if (self.desRecSeqState == currFold.recSeqState):
                        #This is a on position and the sensor will bind the target
                        onStateInfo.append((d, currFold.conc))
                    else: #this is sending the opposite of the desired signal
                        concWrong += currFold.conc
                        #this is only to speed it up when we don't want any noise
                        break
                        

            if onStateInfo == []: # no on states
                continue

            #total concentration of all the on states
            onConc              = sum([j for (i,j) in onStateInfo])
            #
            weightedAvgOnDist   = sum([i*(j/onConc) for (i,j) in onStateInfo])
            
            for i,d in enumerate(distances):
                currFold = self.folds[i]
                if   MAX_ON_DIST-d >= 0:
                    continue #we've already dealt with these folds
                elif MIN_OFF_CHANGE <= d-weightedAvgOnDist :
                    if (self.desRecSeqState  != currFold.recSeqState):
                        #This is a off position and the sensor will not bind the target
                        offStateInfo.append((d, currFold.conc))
                    else: #this is sending the wrong signal
                        concWrong += currFold.conc
                        #this is only to speed it up when we don't want any noise
                        break
                else:# the tag distance is not close enough to be on nor far enough to be off
                    concFuzzy += currFold.conc
                    #this is only to speed it up when we don't want any noise
                    break

            #print "Fuzzy: " + str(concFuzzy)
            #print "Wrong: " + str(concWrong)
            noiseConc = concFuzzy + concWrong
            
            if offStateInfo ==[]: #no off states
                continue

            #the concentration of all the off states
            offConc = sum([j for (i,j) in offStateInfo])


            '''
            if noiseConc*10 > offConc + onConc or\
               concWrong*10 > offConc or\
               concWrong*10 > onConc or\
            '''
            if noiseConc > 0 or\
               offConc*10 < onConc or\
               onConc*10 < offConc:
                #print "too much noise, too many are wrong, or ratios are off" 
                continue
            #
            weightedAvgOnToOffDist = sum([(i-weightedAvgOnDist)*(j/offConc) \
                                            for (i,j) in offStateInfo])
            #print weightedAvgOnToOffDist
            #CHANGE to check for best overall score
            if maxAvgDeltaOnToOff < weightedAvgOnToOffDist:
                scoreData = (position, onConc, offConc, noiseConc,\
                            concWrong, concFuzzy, weightedAvgOnToOffDist)

        
        #print tagLocs
        #print scoreData
        return scoreData

    '''
        __repr__() generates the string representation of a sensor. It is essentially all
        the information one might want to know about a sensor.


        Parameters:
            None
        Returns:
            A string, the string representation of a sensor. 
    '''

    def __repr__(self):
        return str("\n\nSequence: " + self.seq +\
                   "\nScore: " + str(self.score) + \
                   "\nSeed Name: " + self.seedName + \
                   "\nTag Location: " + str(self.tagLoc) +\
                   "\nConc On: " + str(self.onConc) +\
                   "\nConc Off: " + str(self.offConc) + \
                   "\nConc Noise: " +  str(self.noiseConc) + \
                   "\nConc Wrong: " + str(self.wrongConc) + \
                   "\nConc Fuzzy: " + str(self.fuzzyConc) + \
                   "\nOn to Off Dist: " + str(self.onToOffDist) +\
                   "\nLength: " + str(len(self.seq))+ \
                   "\nNum Folds: " + str(len(self.folds)))


    '''
        __cmp__() allows a sensor to be compared to other sensors. The comparison used
        is based upon the sensors scores, and is very self explanatory. 

        Parameters:
            other   <-- another sensor, the one being compared to 'self'
        Returns:
            An integer, -1, 0, or 1. 
    '''
    def __cmp__(self, other):
        if self.score < other.score:
            return -1
        elif self.score == other.score:
            return 0
        else:
            return 1

