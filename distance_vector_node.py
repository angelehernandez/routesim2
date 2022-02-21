import math
import time
from simulator.node import Node
import json
import copy



class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.cost = {}
        self.distVec = {}
        self.NVecs = {}
        self.neighbors = []
        self.knownNodes = []

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function

    def update_dist_vec(self):
        #print("Dist vec before: " + str(self.distVec))
        #print("KNOWN NODES: " + str(self.knownNodes))
        for item in self.knownNodes:
            if item != self.id:
                #print("Examining Node " + str(item))
                min = 100000
                minHop = None
                for n in self.cost:
                    #print("Through Neighbor: " + str(n))
                    
                    if n in self.NVecs and item in self.NVecs[n]:
                        #print("it costs " + str(self.cost[n]) + " to get to neighbor " + str(n) + ". It costs " + str(self.NVecs[n][item][0]) + " to get from there to the destination " + str(item))
                        tempCost = self.cost[n] + self.NVecs[n][item][0]
                        if tempCost < min:
                            if self.NVecs[n][item][2]:
                                if self.id not in self.NVecs[n][item][2]:
                                    #print(str(tempCost) + " is less than our minimum of " + str(min))
                                    min = tempCost
                                    minHop = n
                                    #print("our new minhop is " + str(minHop))
                            else:
                                #print(str(tempCost) + " is less than our minimum of " + str(min))
                                min = tempCost
                                minHop = n
                                #print("our new minhop is " + str(minHop))
                                

                if min != 100000 and minHop != None:
                    if self.NVecs[minHop][item][2]:
                        print(self.NVecs[minHop][item][2])
                        temp = copy.deepcopy(self.NVecs[minHop][item][2])
                        temp.append(minHop)
                        temp.append(self.id)
                        self.distVec[item] = [min, minHop, temp]

                    else:
                        self.distVec[item] = [min, minHop, [minHop]]
        #print("Dist vec after: " + str(self.distVec))

    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        print("Da ID: " + str(self.id))
        if latency == -1:
            print("DELETE")
            del self.cost[neighbor]
            self.distVec[neighbor] = [math.inf, None, []]
            self.neighbors.remove(neighbor)
            print(self.distVec)
            self.update_dist_vec()
            print(self.distVec)
            mess = json.dumps([self.id, self.distVec])
            for n in self.neighbors:
                self.send_to_neighbor(n, mess)
            time.sleep(1)
            return

        if self.id not in self.knownNodes:
            self.distVec[self.id] = [0,self.id,[self.id]]
            self.knownNodes.append(self.id)
        
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
            self.knownNodes.append(neighbor)
            #WILL NEED TO UPDATE THIS NEW NODE
        self.cost[neighbor] = latency
        self.distVec[neighbor] = [latency, neighbor, [neighbor]]
        copyVec = copy.deepcopy(self.distVec)
        #self.update_dist_vec()

        mess = json.dumps([self.id, self.distVec])
        for n in self.neighbors:
            self.send_to_neighbor(n, mess)


    # Fill in this function
    def process_incoming_routing_message(self, m):
        
        mess = json.loads(m)
        sender = mess[0]
        recvDistVec = mess[1]

        print("ID: " + str(self.id))
        #print("sender: " + str(sender))
        #print("Their DV: " + str(recvDistVec))
        #print("OUR DV: " + str(self.distVec))
        #print("NEIGHBOR DV: " + str(self.NVecs))
        #print(self.knownNodes)
        newbie = {}
        for item in recvDistVec:
            #print("item")
            #print(recvDistVec[item])
            tempItem = int(item)
            newbie[tempItem] = recvDistVec[item]
        if sender in self.neighbors:
            self.NVecs[sender] = newbie
        
        for item in self.NVecs:
            for dest in self.NVecs[item]:
                dest = int(dest)
                if dest not in self.knownNodes:
                    self.knownNodes.append(dest)
        print(self.NVecs)
        copyVec = copy.deepcopy(self.distVec)
        self.update_dist_vec()
        if self.distVec != copyVec:
            for n in self.neighbors:
                mess = json.dumps([self.id, self.distVec])
                self.send_to_neighbor(n, mess)

        
        
            



    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        hop = self.distVec[destination][1]
        while hop not in self.neighbors:
            hop = self.distVec[hop][1]
        return hop


class destination():
    def __init__(self, _cost, _next_hop):
        self.latency = _cost
        self.next_hop = _next_hop
    

