# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

#import os
import pandas as pd
#import pyodbc
import math
import geopy.distance
from random import randrange
import copy
def improvement(Network):

    base_cost=Network.totalDistance()
    iteration = 1
    sub_iteration = 1

    emergency_counter=0
    resultNetwork=Network.CopyNetwork()
    while(iteration<4 and emergency_counter<400):
        emergency_counter+=1
        network2=resultNetwork.CopyNetwork()
        random_vehicle1,random_vehicle2=network2.getRandomVehicle()
        random_node1=random_vehicle1.getRandomNode()
        capacity_F=random_vehicle1.remaining_capacity()+random_node1.demand
        checkIs,random_node2=random_vehicle2.getRandomNodeWCapacity(capacity_F)

        if(checkIs):
            print("Iteration ", iteration, ".", sub_iteration)
            random_vehicle1.removeNode(random_node1.name)
            random_vehicle2.removeNode(random_node2.name)
            random_vehicle1.smart_add_node(random_node2)
            random_vehicle2.smart_add_node(random_node1)
            new_cost=network2.totalDistance()


            if(new_cost<base_cost and random_vehicle1.current_load<=60 and random_vehicle2.current_load<=60):
                print("Improvement found. Changed ",random_node1.name," from Vehicle ",random_vehicle1.name," with ",random_node2.name," from Vehicle",random_vehicle2.name)
                network2.Print()
                resultNetwork = network2.CopyNetwork()
                iteration+=1
                sub_iteration=1
                base_cost=new_cost

            else:
                #print("This was not a Improvement")
                sub_iteration +=1






def get_distance(node1,node2):
    node_1_coordinate = (node1.x, node1.y)
    node_2_coordinate = (node2.x, node2.y)
    return    geopy.distance.geodesic(node_1_coordinate, node_2_coordinate).km

def calculate_route_length(route):
    distance = get_distance(depot, route[0])
    for i in range(len(route) - 1):
        distance += get_distance(route[i], route[i + 1])
    distance += get_distance(route[-1], depot)
    return distance


    return geopy.distance.geodesic(node_1_coordinate, node_2_coordinate).km

class Vehicle:
    def __init__(self,depot,capacity,time_window):
        self.time_window=time_window
        self.capacity=capacity
        self.current_load=0
        self.depot=depot
        self.route=[]
        self.penalty=0
        self.name=0

    def getNode(self,name):
        return next((x for x in self.route if x.name == name), None)

    def Print(self):
        String="Vehicle "+str(self.name)+" : "
        for node in self.route:
            String+=" "+str(node.name)
        String+=" Current Load: "+str(self.current_load)+" Penalty: "+str(self.penalty)+" Route Lenght: "+str(self.calculate_route_length())+ " Original Time Window: "+ str(self.time_window)

        print(String)

    def removeNode(self,name):
        self.route = list(filter(lambda x: x.name != name, self.route))
        count_false_window=sum(p.time_window != self.time_window for p in self.route)
        self.penalty=10*count_false_window
        total_demand=0
        for node in self.route:
            total_demand+=node.demand
        self.current_load=total_demand


    def remaining_capacity(self):
        return self.capacity-self.current_load

    def add_node(self,node):
        self.current_load += node.demand

        self.route.append(node)
    #def calculate
    def smart_add_node(self,node):
        min_distance = 100000
        min_index = 0
        for i in range(len(self.route)):
            if (get_distance(self.route[i], node) < min_distance):
                min_distance_node = node
                min_index = i

        if (min_index == len(self.route) - 1):
            self.route.append(node)
        else:
            self.route.insert(min_index + 1, node)
        self.current_load += node.demand

    def calculate_route_length(self):

        return calculate_route_length(self.route)

    def try_add(self,new_node):
        current_distance=self.calculate_route_length()
        min_distance=100000
        new_routing=copy.deepcopy(self.route)
        min_index=0
        for i in range(len(self.route)):
            if(get_distance(self.route[i],new_node)<min_distance):
                min_distance_node=self.route[i]
                min_index=i
        if(min_index==len(self.route)-1):
            new_routing.append(new_node)
        else:
            new_routing.insert(min_index+1,new_node)
        return calculate_route_length(new_routing) - current_distance

    def getRandomNode(self):
        return self.route[randrange(0, len(self.route))]

    def getRandomNodeWCapacity(self,Capacity):
        CapacityNodes = list(filter(lambda x: x.demand <= Capacity, self.route))
        if(len(CapacityNodes)>0):
            return True, CapacityNodes[randrange(0, len(CapacityNodes))]
        else:
            return False,-1

class Network:
    def __init__(self,depot):
        self.total_penalty=0
        self.depot = depot
        self.list_vehicle = []
        self.before_noon_nodes=[]
        self.afternoon_nodes=[]
        self.maxVehicle=0

    def Print(self):
        print( "Total Penalty: ", self.total_penalty, " Total Cost: ",self.totalDistance())
        for Vehicle in self.list_vehicle:
            Vehicle.Print()

    def CopyNetwork(self):
        network = Network(self.depot)
        network.total_penalty=self.total_penalty
        network.list_vehicle=copy.deepcopy(self.list_vehicle)
        network.before_noon_nodes = copy.deepcopy(self.before_noon_nodes)
        network.afternoon_nodes = copy.deepcopy(self.afternoon_nodes)
        return network

    def add_vehicle(self,vehicle):
        self.maxVehicle+=1
        vehicle.name=self.maxVehicle
        self.list_vehicle.append(vehicle)

    def add_node(self,node):
      if(node.time_window=='afternoon'):
          self.afternoon_nodes.append(node)
      else:
          self.before_noon_nodes.append(node)

    def getRandomVehicle(self):
        FirstVehicleNo= randrange(0, len(self.list_vehicle))
        SecondVehicleNo=FirstVehicleNo
        while(SecondVehicleNo==FirstVehicleNo):
            SecondVehicleNo=randrange(0, len(self.list_vehicle))

        return self.list_vehicle[FirstVehicleNo],self.list_vehicle[SecondVehicleNo]

    def get_sorted_afternoon(self):
        return sorted(self.afternoon_nodes, key=Node.get_angle)

    def get_sorted_before_noon(self):
        return sorted(self.before_noon_nodes, key=Node.get_angle)

    def totalDistance(self):
        totalDistance=0
        for v in self.list_vehicle:
            totalDistance+=v.calculate_route_length()
        return totalDistance+self.total_penalty

    def sweep(self,sorted_list):
        clusters = []
        capacity = 60
        cluster = []
        remaining_nodes = copy.deepcopy(sorted_list)

        while len(remaining_nodes) > 0:
            node = remaining_nodes[0]

            if capacity - node.demand > 0:
                capacity -= node.demand
                cluster.append(node)
                remaining_nodes.pop(0)
            else:
                clusters.append(cluster)
                cluster = []
                capacity = 60

        return clusters

    def cfrs_routing(self,cluster,time_window):
        vehicle = Vehicle(self.depot, 60,time_window)
        for node in cluster:
            vehicle.add_node(node)

        self.add_vehicle(vehicle)

        return vehicle.calculate_route_length()

    def beforenoon_insertion(self,nodes,nodes2,penalty):
        vehicle = Vehicle(self.depot, 60,"before noon")

        vehicle.add_node(nodes[0])
        self.add_vehicle(vehicle)

        for i in range(1,len(nodes)):
            current_node=nodes[i]
            default_distance=2*current_node.get_distance_depot()
            min_distance=default_distance
            use_default=True
            min_index=0
            for j in range(len(self.list_vehicle)):
                current_vehicle=self.list_vehicle[j]
                dist_difference=current_vehicle.try_add(current_node)
                if(dist_difference<min_distance and current_vehicle.remaining_capacity() >= current_node.demand ):
                    min_distance=dist_difference
                    use_default = False
                    min_index=j
            if(use_default):
                    new_vehicle = Vehicle(self.depot, 60,"before noon")

                    new_vehicle.add_node(current_node)
                    self.add_vehicle(new_vehicle)
            else:
                self.list_vehicle[min_index].smart_add_node(current_node)

        new_node2_list=[]
        for i in range(0, len(nodes2)):
            current_node = nodes2[i]
            default_distance = 2 * current_node.get_distance_depot()
            min_distance = default_distance
            use_default = True
            min_index = 0
            for j in range(len(self.list_vehicle)):
                current_vehicle = self.list_vehicle[j]
                dist_difference = current_vehicle.try_add(current_node)
                if (dist_difference + penalty < min_distance and current_vehicle.remaining_capacity() >= current_node.demand):
                    min_distance = dist_difference+ penalty
                    use_default = False
                    min_index = j
            if (use_default):
                new_node2_list.append(current_node)
            else:
                self.list_vehicle[min_index].smart_add_node(current_node)
                self.total_penalty += penalty
        return new_node2_list

    def beforenoon_insertion_OLD(self,nodes):
        vehicle = Vehicle(self.depot, 60,"before noon")

        vehicle.add_node(nodes[0])
        self.add_vehicle(vehicle)

        for i in range(1,len(nodes)):
            current_node=nodes[i]
            default_distance=2*current_node.get_distance_depot()
            min_distance=default_distance
            use_default=True
            min_index=0
            for j in range(len(self.list_vehicle)):
                current_vehicle=self.list_vehicle[j]
                dist_difference=current_vehicle.try_add(current_node)
                if(dist_difference<min_distance and current_vehicle.remaining_capacity() >= current_node.demand ):
                    min_distance=dist_difference
                    use_default = False
                    min_index=j
            if(use_default):
                    new_vehicle = Vehicle(self.depot, 60,"before noon")

                    new_vehicle.add_node(current_node)
                    self.add_vehicle(new_vehicle)
            else:
                self.list_vehicle[min_index].smart_add_node(current_node)

    def afternoon_insertion(self,nodes):
        vehicle = Vehicle(self.depot, 60,"afternoon")

        vehicle.add_node(nodes[0])
        self.add_vehicle(vehicle)

        for i in range(1,len(nodes)):
            current_node=nodes[i]

            default_distance=2*current_node.get_distance_depot()
            min_distance=default_distance
            use_default=True
            min_index=0
            for j in range(len(self.list_vehicle)):
                current_vehicle=self.list_vehicle[j]
                if not(current_vehicle.time_window=="before noon"):
                  dist_difference=current_vehicle.try_add(current_node)
                  if(dist_difference<min_distance and current_vehicle.remaining_capacity() >= current_node.demand ):
                     min_distance=dist_difference
                     use_default = False
                     min_index=j
            if(use_default):
                    new_vehicle = Vehicle(self.depot, 60,"afternoon")

                    new_vehicle.add_node(current_node)
                    self.add_vehicle(new_vehicle)
            else:
                self.list_vehicle[min_index].smart_add_node(current_node)



class Node:

    def __init__(self,name,time_window,demand,x,y,depot_x,depot_y):
        self.name = name
        self.time_window = time_window
        self.demand = demand
        self.x = x
        self.y = y
        self.depot_x = depot_x
        self.depot_y = depot_y

    def __str__(self):
        return self.name
    # time wind
    def set_demand(self,demand):
        self.demand = demand

    def get_angle(self):
        angle = math.atan2(self.y - self.depot_y,self.x - self.depot_y) * 180 / math.pi
        if angle < 0:
            return angle + 360
        else:
            return angle

    def get_distance_depot(self):
        return get_distance(self,depot)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    #DataPrep
    data = pd.read_excel('HW1_instances.xlsx')
    row_depot=data[data['Type']=='Depot']
    depot = Node(row_depot['Type'], row_depot['Time window'].iloc[0], row_depot['Demand (boxes)'].iloc[0], row_depot['Latitude'].iloc[0], row_depot['Longitude'].iloc[0],row_depot['Latitude'].iloc[0], row_depot['Longitude'].iloc[0])
    data_nodes = data[data['Type'] != 'Depot']

    network=Network(depot)
    network2 = Network(depot)

    for index, row in data_nodes.iterrows():
        current_node=Node(row['Type'], row['Time window'], row['Demand (boxes)'], row['Latitude'], row['Longitude'],row_depot['Latitude'].iloc[0], row_depot['Longitude'].iloc[0])
        network.add_node(current_node)
        network2.add_node(current_node)

    list_sorted_afternoon = network.get_sorted_afternoon()
    list_sorted_beforenoon = network.get_sorted_before_noon()

    #Q1
    afternoon_clusters = network.sweep(list_sorted_afternoon)
    beforenoon_clusters = network.sweep(list_sorted_beforenoon)

    c1 = 0
    c2 = 0

    for cluster in afternoon_clusters:
        c1 +=network.cfrs_routing(cluster,"afternoon")

    for cluster in beforenoon_clusters:
        c2 +=network.cfrs_routing(cluster,"before noon")
    print(c1 + c2)
    penalty=10

    #network2.beforenoon_insertion_OLD(list_sorted_beforenoon)

    new_afternoonlist=network2.beforenoon_insertion(list_sorted_beforenoon,list_sorted_afternoon,penalty)
    if(len(new_afternoonlist)>0):
      network2.afternoon_insertion(new_afternoonlist)
    network.Print()
    print('---- Improve-----')
    improvement(network)
    print('-----')
    print(network2.totalDistance())
    network2.Print()
    print('---- Improve-----')
    improvement(network2)
