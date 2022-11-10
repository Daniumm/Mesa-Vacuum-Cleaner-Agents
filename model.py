from mesa import Model
from mesa.time import RandomActivation, SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import time
import numpy as np
import itertools
from agent import DirtAgent, VacuumAgent

def get_grid(model):
    dimensions = model.grid.width, model.grid.height
    grid = np.zeros(dimensions)
    for x, line in enumerate(grid):
        for y, _ in enumerate(line):
            # amount of dirt agents in cell
            dirt = len(list(filter(lambda agent: isinstance(agent,DirtAgent) and not agent.is_clean, model.grid.iter_neighbors((x,y), False, True, 0))))
            #print(f'{x=} {y=} {dirt=}')
            # len of dirt agents in cell
            vacuums = len(list(filter(lambda agent: isinstance(agent,VacuumAgent), model.grid.iter_neighbors((x,y), False, True, 0))))
            #print(f'{vacuums=}')
            if dirt != 0 and vacuums == 0:
                grid[x][y] = -10
            elif dirt == 0 and vacuums != 0:
                grid[x][y] = 10
            elif dirt != 0 and vacuums != 0:
                grid[x][y] = 5
            elif dirt == 0 and vacuums == 0:
                grid[x][y] = 0
        
    return grid

def get_dirt_amount(model):
    return model.dirt_amount

class CleaningModel(Model):
    def __init__(self,M,N,vacuums,dirty_percentage,exec_time):
        self.grid = MultiGrid(M,N,False)
        self.x = M
        self.y = N
        self.schedule = SimultaneousActivation(self)
        self.dirt_amount = int(M*N*(dirty_percentage*100))//100
        self.running = True
        self.exec_time = float(exec_time)
        self.start_time = time.time()
        self.cur_time = 0
        self.kill_agents = []
        
        id = 0
        shuffled_dirt_coords = list(self.grid.coord_iter())
        np.random.shuffle(shuffled_dirt_coords)
        for (content, x, y) in shuffled_dirt_coords[:self.dirt_amount]:
            a = DirtAgent(id, x, y, self)
            self.grid.place_agent(a, (x, y))
            self.schedule.add(a)
            id = id + 1
        
        for _ in itertools.repeat(None,vacuums):
            a = VacuumAgent(id, 1, 1, self)
            self.grid.place_agent(a, (1, 1))
            self.schedule.add(a)
            id = id + 1
    
                
        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid, "Dirt_amount":get_dirt_amount})
    def step(self):
        if time.time() - self.start_time >= self.exec_time:
            self.running = False
            self.datacollector.collect(self)
        if self.running and time.time() - self.start_time < self.exec_time:
            self.datacollector.collect(self)
            self.schedule.step()
            self.cur_time = time.time() - self.start_time 
            if self.dirt_amount == 0:
                self.running = False
        for x in self.kill_agents:
            self.grid.remove_agent(x)
            self.schedule.remove(x)
            self.kill_agents.remove(x)

