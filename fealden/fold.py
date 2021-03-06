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

import node, sys, math

class Fold:
    #the states a sequence can be in
    SEQ_STATE = {"DS" : 0, "SS": 1, "MIXED": 3}
    RT = 8.3144598*(1.0/4184.0)*298.0
    '''
        The constructor for Fold.

        Parameters:
            foldData    <- a list of fold data in the format of the second
                            value of the tuple which is output by simplify_input. 
            deltaG      <- a float, the deltaG of the fold (we got this from unafold)
            recSeq      <- a string, the recognition sequence
                     
    '''
    def __init__(self, foldData, deltaG, recSeq):
        self.head = node.SSNode(None) 
        self.deltaG = deltaG
        self.conc   = math.e**(-self.deltaG/Fold.RT)
        self.foldData = foldData
        self.ptrList = [None]*len(self.foldData) #for bp i, ptrList[i-1]= ptr to node that bp i belongs to
        self.construct_graph_SSNode(self.head, 0)
        self.recSeq = recSeq
        self.recSeqState = self.get_rec_seq_state()

    '''
        construct_graph_SSNode is the algorithm for constructing the 
        fold graph given that the current node is an SSNode. 

        Parameters: 
            currentNode  <- the SSNode we're currently on. 
            currentIndex <- the index in self.graphData which we're currently at.
        Returns:
            Nothing
    '''
    def construct_graph_SSNode(self, currentNode, currentIndex):
        currentNode.set_start(currentIndex +1)
        isLastNode = True
        length = 0
        for i, v in enumerate(self.foldData[currentIndex::]):
            if v[1] == 0:
                self.ptrList[i+currentIndex] = currentNode
                length = i+1 #keep track in case this is the last node
            else:
                #print i
                isLastNode = False
                currentNode.set_length(i)
                nextNode = None
                if self.ptrList[v[1]-1] == None:
                    nextNode = node.DSNode(currentNode)
                    self.construct_graph_DSNode_strand1(nextNode, currentIndex + i)
                else:
                    nextNode = self.ptrList[v[1]-1]
                    self.construct_graph_DSNode_strand2(nextNode, currentIndex + i, currentNode)

                currentNode.set_downstreamDSNode(nextNode)
                break
        if isLastNode:
            currentNode.set_length(length)
    '''
        construct_graph_DSNode_strand1 is the algorithm for building a 
        DSNode into the graph given that the base pairs in the DSNode that
        we're processing are all on the "first" strand of the DSNode. (ie
        the location number of these bps on the strand is less then that 
        of their response bps). 

        Parameters:
            currentNode     <- the DSNode we're currently working on
            currentIndex    <- the index in the self.foldData that we're currently on
        Returns:
            Nothing
    '''
    def construct_graph_DSNode_strand1(self, currentNode, currentIndex):
        currentNode.set_strand1Start(currentIndex +1)
        prevPair = self.foldData[currentIndex][1]+1
        for i, v in enumerate(self.foldData[currentIndex::]):
            if v[1] == prevPair -1:
                self.ptrList[i+currentIndex] = currentNode
                self.ptrList[prevPair-2] = currentNode
                prevPair -=1
            else:
                currentNode.set_length(i)
                nextNode = node.SSNode(currentNode)
                self.construct_graph_SSNode(nextNode, currentIndex + i) 
                currentNode.set_midSSNode1(nextNode)
    
                break
    '''
        construct_graph_DSNode_strand2 is the algorithm for building a 
        DSNode into the graph given that the base pairs in the DSNode that
        we're processing are all on the "second" strand of the DSNode. (ie
        the location number of these bps on the strand is greater then that 
        of their response bps). 

        Parameters:
            currentNode     <- the DSNode we're currently working on
            currentIndex    <- the index in the self.foldData that we're currently on
            prevNode        <- the last SSNode we've worked on
        Returns:
            Nothing
    '''
    def construct_graph_DSNode_strand2(self, currentNode, currentIndex, prevNode):
        currentNode.set_strand2Start(currentIndex +1)
        currentNode.set_midSSNode2(prevNode)
        prevPair = self.foldData[currentIndex][1]+1
        for i, v in enumerate(self.foldData[currentIndex::]):
            if (v[1] == prevPair-1) and (v[1] != 0):
                #self.ptrList[i+currentIndex] = currentNode #already set when building strand 1
                #self.ptrList[prevPair-2] = currentNode #already set when building strand 1
                prevPair -=1
            else:
                nextNode = node.SSNode(currentNode)
                self.construct_graph_SSNode(nextNode, currentIndex +i)
                currentNode.set_downstreamSSNode(nextNode)
                #don't set length, it's already been set while building strand 1
                break

    '''
        get_distance (is a proper distance metric which) captures the approximate spacial
        distance between two base pairs

        Parameters:
            firstIndex  <- an integer, the index of the first bp (the smaller index)
            secondIndex <- an integer, the index of the second bp (the larger index)
        Returns:
            distance   <- an integer, the calculated distance
    '''
    def get_distance(self, index1, index2):
        if index1>index2:
            temp = index1
            index1 = index2
            index2 = index1
    
        node1 = self.ptrList[index1-1]
        node2 = self.ptrList[index2-1]

        if node1 == node2:
            return node1.get_index_distance(index1, index2)
        dist = sys.maxsize
        links = node1.get_links()
        for l in links:
            distToIndex2 = self.get_dist_to_index(index2, [node1], node1, l)
            
            tempDist = distToIndex2 + node1.get_index_to_link_dist(index1, l, 0)
            if tempDist < dist:
                dist = tempDist
        return dist 
    '''
        get_dist_to_index() gets the distance from the start of the current
        node to the base pair at the index referenced.

        Parameters:
            index       <- the target, an integer
            traversed   <- a list of nodes we have previously traversed
                           (To avoid going in circles).
            previous    <- the node most recently traversed
            current     <- the node being traversed
            
    '''
    def get_dist_to_index(self, index, traversed, previous, current):
        if current == None:     #reached end and have not found index
            return sys.maxsize
        if current.contains(index):
            return current.get_index_to_link_dist(index, previous, 1)
        dist = sys.maxsize
        links = current.get_links()     
        traversed.append(current)
        for l in links:
            if l in traversed:
                continue
            tempDist = current.get_distance(previous, l) + \
                       self.get_dist_to_index(index, [j for j in traversed], current, l)
            if tempDist < dist:
                dist = tempDist

        return dist

    '''
        get_rec_seq_state() gets the state (ie DS, SS, or Mixed) into which the recognition
        sequence has folded.

        Parameters:
            none
        Returns:
            the state  <- an item from the Fold.SEQ_STATE list. 
    '''
    def get_rec_seq_state(self):
        recSeqPtrList = self.ptrList[self.recSeq["start"]-1:self.recSeq['end']-1]
        assert recSeqPtrList != []
        startingNode = recSeqPtrList[0]
        recSeqMixed = False;
        for p in recSeqPtrList:
            if p != startingNode:
                recSeqMixed = True
        if recSeqMixed:
            #print "Rec seq mixed"
            return Fold.SEQ_STATE["MIXED"]
        #print "Rec seq " + str(startingNode.get_state())
        return startingNode.get_state()
