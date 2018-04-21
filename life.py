import Tkinter as tk
import time
import random

from timeit import default_timer as timer

import numpy as np
import matplotlib.pyplot as plt

class CellCreature(object):
    """
    base class for cell creatures
    """
    def tick(self, cell):
        pass

    def getDecision(self):
        if self.type == 'obstacle':
            return None
        else:
            if self.timeWithoutOffspring == self.offspringTimeLimit:
                self.timeWithoutOffspring = 0
                makeOffspring = 1
            else:
                makeOffspring = 0
            return (random.randint(-1, 1), random.randint(-1, 1), self, makeOffspring)

class Predator(CellCreature):
    def __init__(self, offspringTimeLimit, hungerLimit):
        self.type = 'predator'
        self.color = "#990033"
        self.lifeTime = 0
        self.timeWithoutFood = 0
        self.timeWithoutOffspring = 0
        self.offspringTimeLimit = offspringTimeLimit
        self.hungerLimit = hungerLimit

    def setNotHungry(self):
        self.timeWithoutFood = 0

    def tick(self, cell):
        self.lifeTime = self.lifeTime + 1
        self.timeWithoutFood = self.timeWithoutFood + 1
        self.timeWithoutOffspring = self.timeWithoutOffspring + 1

        if self.timeWithoutFood == self.hungerLimit:
            cell.removeCreature()
    pass

class Prey(CellCreature):
    def __init__(self, offspringTimeLimit):
        self.type = 'prey'
        self.color = "#00991A"
        self.timeWithoutOffspring = 0
        self.offspringTimeLimit = offspringTimeLimit

    def tick(self, cell):
        self.timeWithoutOffspring = self.timeWithoutOffspring + 1

class Obstacle(CellCreature):
    def __init__(self):
        self.type = 'obstacle'
        self.color = "black"

class Cell(object):
    """
    holds operations for one cell of the field:
    rules of objects interaction etc.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.creature = None
        self.nextState = {}

        self.rect = None

    def getState(self):
        """
        returns string representation of cell creature type
        """
        if self.creature == None:
            return 'empty'
        else:
            return self.creature.type

    def initCreature(self, creature):
        """
        init creature in cell by type
        """
        if self.creature == None:
            self.creature = creature
            return True
        else:
            return False

    def removeCreature(self):
        self.creature = None

    def setNewcomer(self, newcomer):
        """
        a creature is trying to come to cell
        returns bool representing whether it is possible
        """
        if self.creature != None and self.creature.type == 'obstacle':
            return False
        elif newcomer.type in ('predator', 'prey'):
            if (self.creature != None and newcomer.type == self.creature.type) or newcomer.type in self.nextState:
                return False
            else:
                self.nextState[newcomer.type] = newcomer
                return True

        return False

    def discardAction(self):
        """
        the action was incorrect so the cell creature stays
        """
        self.nextState[self.creature.type] = self.creature

    def getDecision(self):
        """
        returns a tuple which represents the action that cell creature runs
        """
        if self.creature == None:
            return None
        else:
            action = self.creature.getDecision()
            if action == None:
                self.nextState[self.creature.type] = self.creature
            return action

    def getColor(self):
        """
        returns cell color depending on cell creature
        """
        if self.creature == None:
            return "#0047D6"
        else:
            return self.creature.color;

    def update(self):
        """
        updates cell creature depending on what creatures came to the cell
        """
        if self.getState() != 'obstacle':
            if 'predator' in self.nextState:
                self.creature = self.nextState['predator']
                if 'prey' in self.nextState:
                    self.creature.setNotHungry()
            elif 'prey' in self.nextState:
                self.creature = self.nextState['prey']
            else:
                self.creature = None
            self.nextState = {}

        if self.creature != None:
            self.creature.tick(self)

    def paint(self, canvas, cellSize):
        if not self.rect:
            self.rect = canvas.create_rectangle(
                self.x * cellSize[0] + 1,
                self.y * cellSize[1] + 1,
                (self.x + 1) * cellSize[0] + 1,
                (self.y + 1) * cellSize[1] + 1,
                fill=self.getColor(),
                outline=self.getColor(),
            )
            print "created rect"
        color = self.getColor()
        canvas.itemconfig(self.rect, fill=color, outline=color)
        

class Field(object):
    """
    holds field of cells, interacts them, paints them
    """
    def __init__(self, objectNumbers, cellNumbers, cellSize, limits, iterations):
        self.limits = limits
        self.iterations = iterations

        self.objectsNumbers = objectNumbers
        self.cellNumbers = cellNumbers
        self.cellSize = cellSize
        self.cells = [[Cell(x,y) for y in xrange(cellNumbers[0])] for x in xrange(cellNumbers[1])]
        self.predatorNumber = self.objectsNumbers[0]
        self.preyNumber = self.objectsNumbers[1]

        self.step = 0

        self.randomInitCellsWith('predator', objectNumbers[0])
        self.randomInitCellsWith('prey', objectNumbers[1])
        self.randomInitCellsWith('obstacle', objectNumbers[2])

    def createCreatureByType(self, type):
        if type == 'predator':
            return Predator(self.limits['predatorOffspringTimeLimit'], self.limits['predatorHungerLimit'])
        elif type == 'prey':
            return Prey(self.limits['preyOffspringTimeLimit'])
        elif type == 'obstacle':
            return Obstacle()

    def randomInitCellsWith(self, type, number):
        """
        fills the field with randomly positioned @number of creatures of @type
        """
        for i in xrange(number):
            success = False
            creature = self.createCreatureByType(type)
            while not success:
                objectX = random.randint(0, self.cellNumbers[0] - 1)
                objectY = random.randint(0, self.cellNumbers[1] - 1)
                if self.cells[objectY][objectX].initCreature(creature):
                    success = True

    def getFieldSize(self):
        """
        get height & width in pixels for the field
        result is counted basing on cells number & size
        """
        return map(lambda x, y: x * y, self.cellNumbers, self.cellSize)

    def tick(self):
        """
        goes through all field objects & analizes their decisions
        """
        start = timer()
        for row,elements in enumerate(self.cells):
            for column,element in enumerate(elements):
                action = element.getDecision()
                if action != None:
                    destination = self.cells[(row + action[0]) % len(self.cells)][(column + action[1]) % len(elements)]
                    if action[3] == 1:
                        newcomer = self.createCreatureByType(action[2].type)
                        element.discardAction()
                        destination.setNewcomer(newcomer)
                    else:
                        newcomer = action[2]
                        if (not destination.setNewcomer(newcomer)):
                            element.discardAction()

                oldstate = element.getState()
                element.update()
                newstate = element.getState()

                if oldstate != newstate:
                    if oldstate == 'predator':
                        self.predatorNumber = self.predatorNumber - 1
                    if newstate == 'predator':
                        self.predatorNumber = self.predatorNumber + 1
                    if oldstate == 'prey':
                        self.preyNumber = self.preyNumber - 1
                    if newstate == 'prey':
                        self.preyNumber = self.preyNumber + 1

                

        #print("tick took: %f" % (timer() - start))
        self.step = self.step + 1

    def isTimeToFinish(self):
        """
        @return bool - whether it is time to Finish The Game

        """
        return self.step >= self.iterations or self.predatorNumber <= 0 or self.preyNumber <= 0

    def paint(self, canvas):
        """
        update objects states after tick & paint them
        also updates stats
        """
        #canvas.delete("all")
        start = timer()
        for elements in self.cells:
            for element in elements:           
                element.paint(canvas, self.cellSize)
        #print("paint took: %f" % (timer() - start))


    def getStatus(self):
        """
        @return string stats for field state
        """
        if not self.isTimeToFinish():
            return (
                "step #" + str(self.step) + "\n" +
                "predator number: " + str(self.predatorNumber) + "\n" +
                "prey number: " + str(self.preyNumber)
            )
        else:
            if self.predatorNumber != 0 and self.preyNumber != 0:
                return "DRAW"
            elif self.predatorNumber > self.preyNumber:
                return "PREDATORS WIN"
            else:
                return "PREY WINS"


class App(object):
    """
    holds & runs base objects: display widgets, main form, field object
    """
    def __init__(self):
        self.field = self.readFieldFromFile("life_config.txt")
        fieldSize = self.field.getFieldSize()

        self.isRunning = True

        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.label = tk.Label(self.frame, width=20, text="")
        self.canvas = tk.Canvas(self.frame, height=fieldSize[0], width=fieldSize[1], bg="#008099")
        self.restartButton = tk.Button(self.frame, text="Restart", command=self.restartSimulation)
        self.plot1Button = tk.Button(self.frame, text="Plot N(t)", command=self.plot_N_t)
        self.plot2Button = tk.Button(self.frame, text="Plot PreyN(PredatorN)", command=self.plot_PreyN_PredatorN)
        self.frame.pack()
        self.label.pack(side=tk.RIGHT)
        self.canvas.pack()
        self.restartButton.pack()
        self.plot1Button.pack()
        self.plot2Button.pack()



        self.simulation_delay_scale = tk.Scale(self.frame, from_=0, to=5000, orient=tk.HORIZONTAL, label="отрисовка каждые, мс")
        self.simulation_delay_scale.set(0)
        self.simulation_delay_scale.pack(side=tk.RIGHT)


        # plots
        self.fig_N_t = None
        self.fig_PreyN_PredatorN = None

        self.plot_x = []
        self.plot_y_predators = []
        self.plot_y_prey = []

        #plt.axis([0, 10, 0, 1])

        self.last_time_tick = 0        
        self.tick()

        

        while True:
            try:
                #start = timer()
                self.root.update()
                #self.root.update_idletasks()    
                #print("tk update took: %f" % (timer() - start))           
            
                if self.isRunning and not self.field.isTimeToFinish():
                    self.tick()                    

                    self.plot_x.append(self.field.step)
                    self.plot_y_prey.append(self.field.preyNumber)
                    self.plot_y_predators.append(self.field.predatorNumber)                            
                
            except Exception as e:
                print "Exception: %s" % str(e)
                break

    def tick(self):
        start = timer()

        # update field logic
        self.field.tick()

        # paint 
        if time.time() - self.last_time_tick > float(self.simulation_delay_scale.get())/1000:            
            self.field.paint(self.canvas)
            self.last_time_tick = time.time()
        
        self.label.configure(text=self.field.getStatus())
       
    def restartSimulation(self):
        self.canvas.delete('all')
        self.field = self.readFieldFromFile("life_config.txt")

        self.plot_x = []
        self.plot_y_predators = []
        self.plot_y_prey = []
    

    def plot_PreyN_PredatorN(self):
        if not self.fig_PreyN_PredatorN:
            self.fig_PreyN_PredatorN = plt.gcf()
            self.fig_PreyN_PredatorN.show()
            self.fig_PreyN_PredatorN.canvas.draw()

        # switch to fig      
        plt.figure(self.fig_PreyN_PredatorN.number)

        self.fig_PreyN_PredatorN.clf()
        plt.plot(self.plot_y_prey, self.plot_y_predators, c="b")        
        self.fig_PreyN_PredatorN.canvas.draw()
        plt.hold(True)

    def plot_N_t(self):
        if not self.fig_N_t:                  
            self.fig_N_t = plt.gcf()
            self.fig_N_t.show()
            self.fig_N_t.canvas.draw()

        # switch to fig      
        plt.figure(self.fig_N_t.number)

        self.fig_N_t.clf()
        plt.plot(self.plot_x, self.plot_y_prey, c="g")
        plt.plot(self.plot_x, self.plot_y_predators, c="r")
        self.fig_N_t.canvas.draw()
        plt.hold(True)

        

    def changeRunningState(self):
        self.isRunning = not self.isRunning
        if self.isRunning:
            self.tick()

    def readFieldFromFile(self, fileName):
        file = open(fileName)
        lines = file.readlines()
        config = {}
        for line in lines:
            equation = line.rstrip('\n').split('=')
            config[equation[0]] = int(equation[1])

        objectNumbers = (config['predatorNumber'], config['preyNumber'], config['obstacleNumber'])
        cellNumbers = (config['cellNumberWidth'], config['cellNumberHeight'])
        cellSize = (config['cellWidth'], config['cellHeight'])
        limits = {}
        limits['predatorOffspringTimeLimit'] = config['predatorOffspringTimeLimit']
        limits['predatorHungerLimit'] = config['predatorHungerLimit']
        limits['preyOffspringTimeLimit'] = config['preyOffspringTimeLimit']
        iterations = config['iterations']
        file.close()
        return Field(objectNumbers, cellNumbers, cellSize, limits, iterations)

app = App()