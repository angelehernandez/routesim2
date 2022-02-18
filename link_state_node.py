import math
import time
import random

from torch import minimum, ne
from simulator.node import Node
import json
import copy
import uuid


class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.routeTable = {}
        self.costTable = {}
        self.recentlySeenSeq = {}


    # Return a string
    def __str__(self):
        return "ID:" + str(self.id)

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
            for key in self.costTable:
                lKey = list(key)
                message = [lKey[0], lKey[1], self.costTable[key][0], self.costTable[key][1], self.id]
                message = json.dumps(message)
                self.send_to_neighbor(neighbor, message)
        #print("self: " + str(self.id) + "Neightbors: " + str(self.neighbors)) 
            #self.seq = self.seq + 1
        if frozenset([self.id, neighbor]) in self.costTable:
            seq = self.costTable[frozenset([self.id, neighbor])][1]
            seq += 1
        else:
            seq = 0
        self.costTable[frozenset([self.id, neighbor])] = [latency, seq]
        # if(neighbor == 6 and self.id == 4) or ((neighbor == 6 and self.id == 4)):
        #     print("We got it! sending it to our neighbors now")
        #     print(self.neighbors)
        message = [self.id, neighbor, latency, seq, self.id]
        message = json.dumps(message)
        for n in self.neighbors:
            self.send_to_neighbor(n, message)
            if((self.id == 4 and neighbor == 6) or (self.id == 6 and neighbor == 4)):
                print("JKLM")
                print(self.neighbors)



    # Fill in this function
    def process_incoming_routing_message(self, m):
        mess = json.loads(m)
        source = mess[0]
        dest = mess[1]
        cost = mess[2]
        seq = mess[3]
        og = mess[4]
        
        print("CURRENT ID: " + str(self.id))
        print("source: " + str(source) + " destination: " + str(dest) + " seq: " + str(seq))
        print(self.costTable)
        if(dest == 6 and source == 4) or ((source == 6 and dest == 4)):
            print("GOT IT: " + str(self.id))
            print("New Sequence " + str(seq))
            if frozenset([source, dest]) in self.costTable:
                print("WE KNOW ABOUT IT ALREADY")
                print("Sequence Number we Have: " + str(self.costTable[frozenset([source, dest])]))
            print("These are our neighbors: ")
            print(self.neighbors)
        if frozenset([source, dest]) in self.costTable:
            seq2 = self.costTable[frozenset([source, dest])][1]
            print(seq2)
        else:
            seq2 = seq
        #print("received seq " + str(seq2) + " for the link of " + str(source) + "  " + str(dest))
        #print("I am " + str(self.id))
        #print("source: " + str(source) + " destination: " + str(dest) + " seq: " + str(seq))
        #print("current sequence: " + str(self.recentlySeenSeq))
        if frozenset([source, dest]) in self.costTable:
            print('we know about this link already')
            if seq2 < seq:
                print('The seq number ' + str(seq) + ' is greater than ' + str(seq2))
                key = frozenset([source,dest])
                self.costTable[key] = [cost, seq2]
                message = [source, dest, cost, seq2, self.id]
                message = json.dumps(message)
                print("Sending to these neighbors now")
                print(self.neighbors)
                for n in self.neighbors:
                    if n != og:
                        print("Sending information about " + str(dest) + " " + str(source) + " to " + str(n))
                        self.send_to_neighbor(n, message)
            elif seq2 > seq:
                print("recieved older sequence")
                message = [source, dest, cost, seq, self.id]
                message = json.dumps(message)
                self.send_to_neighbor(og, message)
        else:
            print("this is a new link")
            key = frozenset([source,dest])
            self.costTable[key] = [cost, seq2]
            message = [source, dest, cost, seq2, self.id]
            message = json.dumps(message)
            for n in self.neighbors:
                if n != og:
                    print("Sending information about " + str(dest) + " " + str(source) + " to " + str(n))
                    self.send_to_neighbor(n, message)
        #time.sleep(1)

        



            #print("GOT IN")
            #print("currently updating " + str(self.id)+ " to know about " + str(dest) + str(source))
            #print(self.costTable[key])
            
            #print("sending info about : " + str(source) + " " + str(dest))
            #print(self.neighbors)
        

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        print(self.id)
        print(self.costTable)
        #print("Costs before running")
        #print(self.costTable)
        D = self.dijRun()
        #print(D)
        currPrev = D[destination][1]
        if currPrev == self.id:
            return destination
        #print("destination " + str(destination))
        while currPrev not in self.neighbors:
            #print("Curr prev: " + str(currPrev))
            #print(self.neighbors)
            #print(currPrev)
            #print(D)
            currPrev = D[currPrev][1]
        print("RETURNED" + str(currPrev))
        return currPrev

            


    def dijRun(self):
        
        #print(self.id)
        #print(self.neighbors)
        print(self.costTable)
        D = {}
        #print(self.neighbors)
        N = [self.id]
        #print("COST TABLE AT START OF DIJ")
        #print('id: ' + str(self.id))
        #print(self.costTable)
        for keys in self.costTable:
            tempKeys = list(keys)
            #print("CURRENT KEY LOOKING AT " + str(tempKeys))
            if self.id in tempKeys:
                #print("this is a neighbor")
                if tempKeys[0] == self.id:
                    source = tempKeys[0]
                    dest = tempKeys[1]
                else:
                    source = tempKeys[1]
                    dest = tempKeys[0]
                #print("source " + str(source))
                #print("dest: " + str(dest))
                #print(D.keys())
                #print("in here")
                D[dest] = [self.costTable[keys][0], self.id]  
            else:
                #print("part 1")
                #print(list(D.keys()))
                if tempKeys[0] not in list(D.keys()):
                    #print("part 2")
                    D[tempKeys[0]] = [math.inf, None]
                elif tempKeys[1] not in list(D.keys()):
                    D[tempKeys[1]] = [math.inf, None]

        #print(len(self.costTable))
        while len(N) < len(self.costTable):
            minimum = math.inf
            #print(self.costTable)
            for item in D:
                if D[item][0] < minimum and item not in N:
                    w = item
                    minimum = D[item][0]
            N.append(w)
            #print(N)
            for keys in self.costTable:
                tempKeys = list(keys)
                if w in tempKeys:
                    if tempKeys[0] == w:
                        source = tempKeys[0]
                        dest = tempKeys[1]
                    else:
                        source = tempKeys[1]
                        dest = tempKeys[0]
                    #print("source " + str(source))
                    #print("dest: " + str(dest))
                    if dest == self.id:
                        continue
                    
                    chk = copy.deepcopy(D[dest][0])
                    D[dest][0] = min(D[dest][0], D[w][0]+self.costTable[keys][0])
                    if D[dest][0] != chk:
                        D[dest][1] = source


        return D