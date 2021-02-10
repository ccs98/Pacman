# -*- coding: cp1252 -*-
# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters
import time
import os.path as path
from wekaI import Weka

cadena = ""

class NullGraphics:
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent:
    
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        #for index, inf in enumerate(self.inferenceModules):
        #    if not self.firstMove and self.elapseTimeEnable:
        #        inf.elapseTime(gameState)
        #    self.firstMove = False
        #    if self.observeEnable:
        #        inf.observeState(gameState)
        #    self.ghostBeliefs[index] = inf.getBeliefDistribution()
        #self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."
    cadena = ""
    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)
    
    def printLineData(self, gameState):
        file = open('test_othermaps_keyboard.arff', 'a')#crea el archivo si no existe y lo abre para escribir
        if(self.cadena != ""):file.write(self.cadena +", "+ str(gameState.getScore())+ "\n")
        posicion_pacman = (str(gameState.getPacmanPosition()[0])+", "+str(gameState.getPacmanPosition()[1])+", ")
        posiciones_legales = gameState.getLegalPacmanActions()
        cantidad = len(posiciones_legales)
        string_pos_legales = ', '.join(str(p) for p in posiciones_legales) + ", "
        for i in range(cantidad, 5):
            string_pos_legales += "None, "
        Numero_de_fantasmas = str(gameState.getNumAgents() - 1)+", "
        Fantasmas_vivos = gameState.getLivingGhosts()
        string_fantasmas_vivos = ', '.join(str(p) for p in Fantasmas_vivos) + ", "
        Posicion_fantasmas = gameState.getGhostPositions()
        string_posicion_fantasmas = ', '.join(str(p) for p in Posicion_fantasmas) + ", "
        string_posicion_fantasmas = string_posicion_fantasmas.replace("(","")
        string_posicion_fantasmas = string_posicion_fantasmas.replace(")","")
        Direcciones_fantasmas = (gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1))
        String_direcciones = ', '.join(str(p) for p in Direcciones_fantasmas) + ", "
        Distancias_fantasmas = gameState.data.ghostDistances
        String_distancias = str(Distancias_fantasmas)+", "
        String_distancias = String_distancias.replace("]","")
        String_distancias = String_distancias.replace("[","")
        String_distancias = String_distancias.replace("None","9999")
        Comida = str(gameState.getNumFood())+", "
        Comida = Comida.replace("None","9999")
        Distancia_comida = str(gameState.getDistanceNearestFood())+", "
        Distancia_comida = Distancia_comida.replace("None","9999")
        Direccion_pacman = str(gameState.data.agentStates[0].getDirection()) + ", "
        Puntuacion = str(gameState.getScore())
        self.cadena = posicion_pacman + string_pos_legales + Numero_de_fantasmas + string_fantasmas_vivos + string_posicion_fantasmas + String_direcciones + String_distancias + Comida + Distancia_comida + Direccion_pacman + Puntuacion
        if(Fantasmas_vivos[0] == "False")and(Fantasmas_vivos[1] == "False")and(Fantasmas_vivos[2] == "False")and(Fantasmas_vivos[3] == "False")and(Fantasmas_vivos[4] == "False"):file.write(self.cadena +", "+ Puntuacion+300)
        file.close()


from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table
        
    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move
        
class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST

class BasicAgentAA(BustersAgent):
    cadena = ""
    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        #print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def printInfo(self, gameState):
        print "---------------- TICK ", self.countActions, " --------------------------"
        # Dimensiones del mapa
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print "Width: ", width, " Height: ", height
        # Posicion del Pacman
        print "Pacman position: ", gameState.getPacmanPosition()
        # Acciones legales de pacman en la posicion actual
        print "Legal actions: ", gameState.getLegalPacmanActions()
        # Direccion de pacman
        print "Pacman direction: ", gameState.data.agentStates[0].getDirection()
        # Numero de fantasmas
        print "Number of ghosts: ", gameState.getNumAgents() - 1
        # Fantasmas que estan vivos (el indice 0 del array que se devuelve corresponde a pacman y siempre es false)
        print "Living ghosts: ", gameState.getLivingGhosts()
        # Posicion de los fantasmas
        print "Ghosts positions: ", gameState.getGhostPositions()
        # Direciones de los fantasmas
        print "Ghosts directions: ", [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)]
        # Distancia de manhattan a los fantasmas
        print "Ghosts distances: ", gameState.data.ghostDistances
        # Puntos de comida restantes
        print "Pac dots: ", gameState.getNumFood()
        # Distancia de manhattan a la comida mas cercada
        print "Distance nearest pac dots: ", gameState.getDistanceNearestFood()
        # Paredes del mapa
        print "Map:  \n", gameState.getWalls()
        # Puntuacion
        print "Score: ", gameState.getScore()


    def printLineData(self, gameState):
        file = open('datosRelevantes.txt', 'a')#crea el archivo si no existe y lo abre para escribir
        file.write("Pacman position: " + str(gameState.getPacmanPosition()))
        file.write(" , Legal actions: " + str(gameState.getLegalPacmanActions()))
        file.write(" , Living ghosts: " + str(gameState.getLivingGhosts()))
        file.write(" , Ghosts positions: " + str(gameState.getGhostPositions()))
        file.write(" , Ghosts distances: " + str(gameState.data.ghostDistances))
        file.write(" , Score: " + str(gameState.getScore()) + '\n')
        file.close()
        
    def chooseAction(self, gameState):
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
        move = Directions.STOP
        legal = gameState.getLegalActions(0)
        tup = [0,0,'Stop','Stop','Stop','Stop','Stop',0,'False','False','False','False','False',0,0,0,0,0,0,0,0,'Stop','Stop','Stop','Stop',0,0,0,0,0,0,0,0]
        posicionPacman = gameState.getPacmanPosition()
        tup[0] = posicionPacman[0]
        tup[1] = posicionPacman[1]
        posiciones_legales = gameState.getLegalPacmanActions()
        cantidad = len(posiciones_legales)
        for i in range(cantidad, 5):
            if (posiciones_legales[i]!='North')and(posiciones_legales[i]!='South')and(posiciones_legales[i]!='West')and(posiciones_legales[i]!='East')and(posiciones_legales[i]!='Stop'):posiciones_legales[i] = 'None'
        tup[2] = posiciones_legales[0]
        tup[3] = posiciones_legales[1]
        tup[4] = posiciones_legales[2]
        tup[5] = posiciones_legales[3]
        tup[6] = posiciones_legales[4]
        numfantasmas = str(gameState.getNumAgents() - 1)
        tup[7] = numfantasmas
        livingGhosts = gameState.getLivingGhosts()
        tup[8] = livingGhosts[0]
        tup[9] = livingGhosts[1]
        tup[10] = livingGhosts[2]
        tup[11] = livingGhosts[3]
        Posiciones_fantasmas = gameState.getGhostPositions()
        tup[12] = Posiciones_fantasmas[0][0]
        tup[13] = Posiciones_fantasmas[0][1]
        tup[14] = Posiciones_fantasmas[1][0]
        tup[15] = Posiciones_fantasmas[1][1]
        tup[16] = Posiciones_fantasmas[2][0]
        tup[17] = Posiciones_fantasmas[2][1]
        tup[18] = Posiciones_fantasmas[3][0]
        tup[19] = Posiciones_fantasmas[3][1]
        tup[20] = Posiciones_fantasmas[4][0]
        tup[21] = Posiciones_fantasmas[4][1]
        Direcciones_fantasmas = [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)]
        Direcciones_fantasmas_Final = ['Stop', 'Stop', 'Stop', 'Stop']
        for i in range(len(Direcciones_fantasmas)):
            Direcciones_fantasmas_Final[i] = Direcciones_fantasmas[i]
        tup[22] = ghostsDirectionsFinal[0]
        tup[23] = ghostsDirectionsFinal[1]
        tup[24] = ghostsDirectionsFinal[2]
        tup[25] = ghostsDirectionsFinal[3]
        Distancia_fantasmas = gameState.data.ghostDistances
        tup[26] = Distancia_fantasmas[0]
        tup[27] = Distancia_fantasmas[1]
        tup[28] = Distancia_fantasmas[2]
        tup[29] = Distancia_fantasmas[3]
        Comida = gameState.getNumFood()
        tup[30] = Comida
        Distancia_comida = gameState.getDistanceNearestFood()
        tup[31] = Distancia_comida
        Puntuacion = gameState.getScore()
        tup[32] = Puntuacion
        pacManLegalActions = gameState.getLegalPacmanActions()
        if(self.countActions < 2):
            return 'Stop'
        else:
            print(tup)
            a = self.weka.predict("./RandomForest.model", tup, "./Training_set.arff")
            for i in pacManLegalActions:
                if(a == i):
                    return a
            return 'Stop'
        


    def printLineData(self, gameState):
        file = open('test_othermaps_tutorial.arff', 'a')#crea el archivo si no existe y lo abre para escribir
        if(self.cadena != ""):file.write(self.cadena +", "+ str(gameState.getScore())+ "\n")
        posicion_pacman = (str(gameState.getPacmanPosition()[0])+", "+str(gameState.getPacmanPosition()[1])+", ")
        posiciones_legales = gameState.getLegalPacmanActions()
        cantidad = len(posiciones_legales)
        string_pos_legales = ', '.join(str(p) for p in posiciones_legales) + ", "
        for i in range(cantidad, 5):
            string_pos_legales += "None, "
        Numero_de_fantasmas = str(gameState.getNumAgents() - 1)+", "
        Fantasmas_vivos = gameState.getLivingGhosts()
        string_fantasmas_vivos = ', '.join(str(p) for p in Fantasmas_vivos) + ", "
        Posicion_fantasmas = gameState.getGhostPositions()
        string_posicion_fantasmas = ', '.join(str(p) for p in Posicion_fantasmas) + ", "
        string_posicion_fantasmas = string_posicion_fantasmas.replace("(","")
        string_posicion_fantasmas = string_posicion_fantasmas.replace(")","")
        Direcciones_fantasmas = (gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1))
        String_direcciones = ', '.join(str(p) for p in Direcciones_fantasmas) + ", "
        Distancias_fantasmas = gameState.data.ghostDistances
        String_distancias = str(Distancias_fantasmas)+", "
        String_distancias = String_distancias.replace("]","")
        String_distancias = String_distancias.replace("[","")
        String_distancias = String_distancias.replace("None","9999")
        Comida = str(gameState.getNumFood())+", "
        Comida = Comida.replace("None","9999")
        Distancia_comida = str(gameState.getDistanceNearestFood())+", "
        Distancia_comida = Distancia_comida.replace("None","9999")
        Direccion_pacman = str(gameState.data.agentStates[0].getDirection()) + ", "
        Puntuacion = str(gameState.getScore())
        self.cadena = posicion_pacman + string_pos_legales + Numero_de_fantasmas + string_fantasmas_vivos + string_posicion_fantasmas + String_direcciones + String_distancias + Comida + Distancia_comida + Direccion_pacman + Puntuacion
        if(Fantasmas_vivos[0] == "False")and(Fantasmas_vivos[1] == "False")and(Fantasmas_vivos[2] == "False")and(Fantasmas_vivos[3] == "False")and(Fantasmas_vivos[4] == "False"):file.write(self.cadena +", "+ Puntuacion+300)
        file.close()
    
        
