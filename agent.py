from mesa import Agent
import numpy as np
import random



class VacuumAgent(Agent):
    def __init__(self,id, x, y, model):
        super().__init__(id,model)
        self.id = id
        self.coords = x,y
        self.model = model
        self.next_pos = None
        self.total_steps = 0
        self.desc = "Vacuum"
    
    def step(self):
        need_to_clean = any([isinstance(agent,DirtAgent) and not agent.is_clean for agent in self.model.grid.iter_neighbors(self.coords, False, True, 0)])
        if not need_to_clean:
            valid_neighborhood = [cell for cell in self.model.grid.iter_neighborhood(self.coords,True,False,1)]
            # insert current coords to replace unreachable space
            valid_neighborhood.extend([self.coords for _ in range(8-len(valid_neighborhood))])
            
            choices = valid_neighborhood
            # choose next position
            self.next_pos =choices[np.random.choice(len(choices))]
        else:
            self.next_pos = self.coords
    def advance(self):
        if self.next_pos != self.coords:
            self.total_steps = self.total_steps + 1
        self.coords = self.next_pos
        self.model.grid.move_agent(self,self.coords)

class DirtAgent(Agent):
    def __init__(self,id, x, y, model):
        super().__init__(id, model)
        self.id = id
        self.coords = x, y
        self.model = model
        self.next_state = None
        self.is_clean = False
        self.desc = "Dirt"
        
    def step(self):
        # if there are any vacuum agents in the same cell next state is clean
        if not self.is_clean:
            self.next_state = any([isinstance(agent,VacuumAgent) for agent in self.model.grid.iter_neighbors(self.coords, False, True, 0)])
            if self.next_state == True:
                self.model.dirt_amount = self.model.dirt_amount-1
                self.model.kill_agents.append(self)
        
                
        
    def advance(self):
        self.is_clean = self.is_clean or self.next_state