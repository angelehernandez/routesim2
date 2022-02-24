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
        for item in self.knownNodes:
            if item != self.id:
                min = 100000
                minHop = None
                for n in self.cost:
                    
                    if n in self.NVecs and item in self.NVecs[n]:
                        tempCost = self.cost[n] + self.NVecs[n][item][0]
                        if tempCost < min:
                            if self.NVecs[n][item][2]:
                                if self.id not in self.NVecs[n][item][2]:
                                    min = tempCost
                                    minHop = n
                            else:
                                min = tempCost
                                minHop = n
                                

                if min != 100000 and minHop != None:
                    if self.NVecs[minHop][item][2]:
                        temp = copy.deepcopy(self.NVecs[minHop][item][2])
                        temp.append(minHop)
                        temp.append(self.id)
                        self.distVec[item] = [min, minHop, temp]

                    else:
                        self.distVec[item] = [min, minHop, [minHop]]

    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        if latency == -1:
            del self.cost[neighbor]
            self.distVec[neighbor] = [math.inf, None, []]
            self.neighbors.remove(neighbor)
            self.update_dist_vec()
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

        newbie = {}
        for item in recvDistVec:
            tempItem = int(item)
            newbie[tempItem] = recvDistVec[item]
        if sender in self.neighbors:
            self.NVecs[sender] = newbie
        
        for item in self.NVecs:
            for dest in self.NVecs[item]:
                dest = int(dest)
                if dest not in self.knownNodes:
                    self.knownNodes.append(dest)
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
            if hop is None:
                return None
            print(f"hop: {hop}")
            print(f"distVec: {self.distVec}")
            hop = self.distVec[hop][1]
        return hop


class destination():
    def __init__(self, _cost, _next_hop):
        self.latency = _cost
        self.next_hop = _next_hop
    

