import numpy as np
import agentpy as ap
import matplotlib.pyplot as plt
import seaborn as sns
import IPython
import json

class Vehicle(ap.Agent):
    def setup(self):
        self.grid = self.model.grid
        self.pos = [0, 0]
        self.road = 1
        self.side = [1, 0]
        self.speed = 1
        self.crossed = False
        self.id = 0
        self.posDict = []

    def direction(self):
        self.pos = self.grid.positions[self]
        if self.pos[1] == 0:
            self.side = [0, 1]

    def movement(self):
        self.direction()
        new_Dict = {}
        new_Dict["id"] = self.id
        new_Dict["x"] = self.pos[0]
        new_Dict["y"] = 0
        new_Dict["z"] = self.pos[1]
        self.posDict.append(new_Dict)
        return (self.speed * self.side[0], self.speed * self.side[1])

    def add_position(self):
        new_Dict = {}
        new_Dict["id"] = self.id
        new_Dict["x"] = self.pos[0]
        new_Dict["y"] = 0
        new_Dict["z"] = self.pos[1]
        self.posDict.append(new_Dict)

    def route(self):
        self.pos = self.grid.positions[self]
        if self.pos[1] == 0:
            return 'Horizontal'
        return 'Vertical'

class StopSign(ap.Agent):
    def setup(self):
        self.status = 1
        self.road = 3
        self.grid = self.model.grid
        self.pos = [0, 0]
        self.route=''
        self.id = 0
        self.statusDict = []

    def positions(self):
        self.pos = self.grid.positions[self]

    def change_state(self):
        self.positions()
        tGrid = self.p['Grid']
        self.status = 2
        self.road=2
        if self.model.n_cars_1 > self.model.n_cars_2:
            if self.pos[0] == int((tGrid/2)+1):
                self.status = 0
                self.road=4
        elif self.model.n_cars_1 < self.model.n_cars_2:
            if self.pos[1] == int((tGrid/2)+1):
                self.status = 0
                self.road=4
        else:
            if self.pos[1] == int((tGrid/2)+1):
                self.status = 0
                self.road=4
        new_Dict = {}
        new_Dict["idSS"] = self.id
        new_Dict["state"] = self.status
        self.statusDict.append(new_Dict)

class Roads(ap.Agent):
    def setup(self):
        self.road = 1
        self.condition = 1

class IntersectionModel(ap.Model):
    def setup(self):
        self.con=0
        tGrid = self.p['Grid']
        self.grid = ap.Grid(self, [tGrid] * 2, torus=True,track_empty=True)

        self.n_cars_1 = 0
        self.n_cars_2 = 0

        n_vehicles = self.p['Vehicles']
        n_roads = tGrid*2

        self.vehicles = ap.AgentList(self, n_vehicles, Vehicle)

        self.road = ap.AgentList(self, n_roads, Roads)
        self.stop_sign = ap.AgentList(self, 2, StopSign)

        self.vehicles.grid = self.grid

        contador = 0
        for vehicle in self.vehicles:
            vehicle.id = contador
            contador+=1
            
        self.grid.add_agents(self.stop_sign, positions=[(int((tGrid/2)-1), int((tGrid/2)+1)), (int((tGrid/2)+1), int((tGrid/2)-1))])
        stop_lights = self.stop_sign
        contadorS = 0
        for semaforo in stop_lights:
            if self.grid.positions[semaforo][1]==0:
                semaforo.route='Vertical'
            else: 
                semaforo.route='Horizontal'
            semaforo.id = contadorS
            contadorS+=1
        vehicles_positions=[]
        for i in range (1,n_vehicles+1):
            if i%2==0:
                vehicles_positions.append((int(tGrid/2), 0))
            else:
                vehicles_positions.append((0,int(tGrid/2)))
        self.contador = 0
        self.jsonCollectData = {}

    def step(self):
        self.contador += 1
        tGrid = self.p['Grid']
        number_vehicles = self.p['Vehicles']
        if self.con==0:
            vehicles_positions=[]
            positions=[(0, int(tGrid/2)), (int(tGrid/2), 0)]
            
            for i in range (number_vehicles):
                random_position = np.random.randint(0, 2)
                vehicles_positions.append(positions[random_position])
            self.grid.add_agents(self.vehicles,vehicles_positions)
            self.con+=1


        movimiento=True
        state=False
        moving_cars_1 = self.vehicles

        for car in moving_cars_1:
            agent_pos=self.grid.positions[car]
            for i in range(1,int((tGrid/2))):
                if (int(tGrid/2) == agent_pos[0])and(int(i) == agent_pos[1]):
                    self.n_cars_1 += 1
                    state=True
                if  (int(tGrid/2) == agent_pos[1])and(int(i) == agent_pos[0]):
                    self.n_cars_2 += 1
                    state=True
        if state:
            stop_light = self.stop_sign
            for semaforo in stop_light:    
                if state:
                    semaforo.change_state()
                else:
                    semaforo.status=1
                    semaforo.road=3

        for agents in self.grid.agents:
            agent_pos=self.grid.positions[agents]
            movimiento=True
            if agents.type == 'Vehicle':
                for neighbor in self.grid.neighbors(agents):
                    if agents.route() == 'Vertical':
                        if self.grid.positions[neighbor][1]==agent_pos[1]+1 and self.grid.positions[neighbor][0]==agent_pos[0]:
                            if   neighbor.type=='Vehicle':    
                                movimiento=False
                                break
                        if self.grid.positions[neighbor][1]==agent_pos[1] and self.grid.positions[neighbor][0]==agent_pos[0]+1:
                            if  neighbor.type=='StopSign':
                                if neighbor.status==2:
                                    movimiento=False
                                    break
                                else:
                                    self.n_cars_1-=1
                                    break
                        
                    if agents.route() == 'Vertical':
                        if self.grid.positions[neighbor][0]==agent_pos[0]+1 and self.grid.positions[neighbor][1]==agent_pos[1]:
                            if  neighbor.type=='Vehicle':
                                movimiento=False
                                break
                        if self.grid.positions[neighbor][0]==agent_pos[0] and self.grid.positions[neighbor][1]==agent_pos[1]+1:
                            if  neighbor.type=='StopSign':
                                if neighbor.status==2:
                                    movimiento=False
                                    break
                                else:
                                    self.n_cars_2-=1
                                    break
                if movimiento:
                    coordinates_move=agents.movement()
                    self.grid.move_by(agents,coordinates_move)
                else:
                    agents.add_position()

        if self.contador == self.p['steps'] - 1:
            IntersectionModel.end(self)

    def end(self):
        jsonCollectData = {}
        vehicles = self.vehicles 
        arregloPos = []
        for car in vehicles:
            arregloPos = np.append(arregloPos, car.posDict)
        stopSigns = self.stop_sign
        arregloSS = []
        for stopSign in stopSigns:
            arregloSS = np.append(arregloSS, stopSign.statusDict)
        print(arregloPos)
        arregloPos = arregloPos.tolist()
        arregloSS = arregloSS.tolist()
        jsonCollectData["data"] = arregloPos
        jsonCollectData["dataStopSign"] = arregloSS
        with open('archivoPosJson.json', 'w') as file:
            json.dump(jsonCollectData, file, indent=4)
        self.jsonCollectData = jsonCollectData

        pass

def runModel():
    parameters = {
        'Vehicles': 15,
        'steps': 500,
        'Grid':25,
    }
    model = IntersectionModel(parameters)
    model.run()
    print(model.jsonCollectData)
    return model.jsonCollectData
    
