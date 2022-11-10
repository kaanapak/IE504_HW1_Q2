# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

#import os
import pandas as pd
#import pyodbc
import math
import geopy.distance

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
    def __init__(self,depot,capacity):
        self.time_window="not defined"
        self.capacity=capacity
        self.current_load=0
        self.depot=depot
        self.route=[]
        self.penalty=0

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

    def calculate_route_length(self):

        return calculate_route_length(self.route)

    def try_add(self,new_node):
        current_distance=self.calculate_route_length()
        min_distance=100000
        new_routing=self.route.copy()
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


class Network:
    def __init__(self,depot):
        self.total_penalty=0
        self.depot = depot
        self.list_vehicle = []
        self.before_noon_nodes=[]
        self.afternoon_nodes=[]

    def add_vehicle(self,vehicle):
        self.list_vehicle.append(vehicle)

    def add_node(self,node):
      if(node.time_window=='afternoon'):
          self.afternoon_nodes.append(node)
      else:
          self.before_noon_nodes.append(node)

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
        remaining_nodes = sorted_list.copy()

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

    def cfrs_routing(self,cluster):
        vehicle = Vehicle(self.depot, 60)
        for node in cluster:
            vehicle.add_node(node)
        self.add_vehicle(vehicle)

        return vehicle.calculate_route_length()

    def beforenoon_insertion(self,nodes,nodes2,penalty):
        vehicle = Vehicle(self.depot, 60)
        vehicle.time_window="before noon"
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
                    new_vehicle = Vehicle(self.depot, capacity)
                    new_vehicle.time_window = "before noon"
                    new_vehicle.add_node(current_node)
                    self.add_vehicle(vehicle)
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


    def afternoon_insertion(self,nodes):
        vehicle = Vehicle(self.depot, 60)
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
                    new_vehicle = Vehicle(self.depot, capacity)
                    new_vehicle.add_node(current_node)
                    self.add_vehicle(vehicle)
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
        c1 +=network.cfrs_routing(cluster)

    for cluster in beforenoon_clusters:
        c2 +=network.cfrs_routing(cluster)
    print(c1 + c2)
    penalty=0
    new_afternoonlist=network2.beforenoon_insertion(list_sorted_beforenoon,list_sorted_beforenoon,penalty)
    if(len(new_afternoonlist)>0):
     network2.afternoon_insertion(new_afternoonlist)

    print(network2.totalDistance())

