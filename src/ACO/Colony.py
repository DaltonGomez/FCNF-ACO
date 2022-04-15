import sys

from src.ACO.Ant import Ant
from src.Network.FlowNetwork import FlowNetwork
from src.Network.Solution import Solution
from src.Network.SolutionVisualizer import SolutionVisualizer


class Colony:
    """Class that defines a Colony object, representing an entire ant colony in the ACO approach"""

    # =========================================
    # ============== CONSTRUCTOR ==============
    # =========================================
    def __init__(self, network: FlowNetwork, minTargetFlow: float, numEpisodes: int, numAnts: int):
        """Constructor of a Colony instance"""
        # Input Attributes
        self.network = network
        self.minTargetFlow = minTargetFlow

        # Hyperparameters
        self.numEpisodes = numEpisodes  # One episode = All the ants completing one tour (i.e. creating a valid solution) each
        self.numAnts = numAnts  # Number of tours completed per episode
        self.evaporationRate = 0.50  # rho = Rate at which pheromone is lost (NOTE: 1 = complete loss/episode; 0 = no loss/episode)
        self.alpha = 1  # alpha = Relative importance to the ant of pheromone over "goodness" of arc
        self.beta = 1  # beta = Relative importance to the ant of "goodness" of arc over pheromone
        self.Q = 5  # Q = Proportionality scalar of best solution, which scales how much pheromone the best solution deposits

        # Colony Attributes
        self.population = self.initializePopulation()  # Contains the population of ants
        self.pheromoneDict = self.initializePheromoneDict()  # Dictionary indexed on key (fromNode, toNode, cap) with value (pheromone deposited)
        self.goodnessDict = self.initializeGoodnessOfArcDict()  # Dictionary indexed on key (fromNode, toNode, cap) with value (eta) (i.e. the "goodness" of taking that arc)
        self.bestKnownCost = None  # Stores the lowest cost solution found so far
        self.bestKnownSolution = None  # Stores the global best solution found so far
        self.visual = None  # Object used to view the best solutions of the episode over time

    def solveNetwork(self) -> Solution:
        """Main loop that solves the Flow Network instance with the ACO"""
        # EPISODE LOOP
        for episode in range(self.numEpisodes):
            print("\nStarting Episode " + str(episode) + "...")
            # INDIVIDUAL ANT EXPLORATION LOOP
            for antIndex in range(self.numAnts):
                print("Solving ant " + str(antIndex) + "...")
                self.population[antIndex].findSolution(self.pheromoneDict,
                                                       self.goodnessDict)  # In series, each ant solves individually
            # POST-EXPLORATION DAEMON UPDATES
            print("Doing post-exploration updates...")
            self.updateBestSolution()  # Updates the best solution only if this population contains it
            self.evaporatePheromone()  # Reduces the pheromone across the entire dictionary based on rho
            self.depositPheromone()  # Deposits new pheromone on the arcs in the best known solution
            self.resetAllAnts()  # Clears the tour/solution attributes of every ant in the population for the next episode
            self.visual = SolutionVisualizer(self.bestKnownSolution)  # Instantiate a visualizer
            self.visual.drawGraphWithLabels(leadingText="Ep." + str(episode) + "_")  # Draw graph
        return self.bestKnownSolution  # Should return the best solution found at the end

    def updateBestSolution(self) -> None:
        """Finds the best solution in the current population and updates the global best if necessary"""
        currentBestCost = sys.maxsize
        currentBestAnt = None
        # Iterate over the current population to find current best
        for ant in self.population:
            if ant.trueCost < currentBestCost:
                currentBestCost = ant.trueCost
                currentBestAnt = ant
        # Compare current best to global best
        if self.bestKnownCost is None:
            self.bestKnownCost = currentBestCost
            self.bestKnownSolution = currentBestAnt.writeSolution()
        elif self.bestKnownCost > currentBestCost:
            self.bestKnownCost = currentBestCost
            self.bestKnownSolution = currentBestAnt.writeSolution()

    def evaporatePheromone(self) -> None:
        """Evaporates pheromone using (1-rho)*pheromone across the entire dictionary"""
        for arc in self.pheromoneDict.keys():
            self.pheromoneDict[arc] = self.pheromoneDict[arc] * (1 - self.evaporationRate)

    def depositPheromone(self) -> None:
        """Deposits new pheromone on the arcs contained in the best known solution so far"""
        for edgeIndex in range(self.network.numEdges):
            for capIndex in range(self.network.numArcCaps):
                edge = self.network.edgesArray[edgeIndex]
                cap = self.network.possibleArcCapsArray[capIndex]
                arcFlow = self.bestKnownSolution.arcFlows[(edgeIndex, capIndex)]
                if arcFlow > 0.0:
                    self.pheromoneDict[(edge[0], edge[1], cap)] = self.Q / self.bestKnownCost
                    # TODO - Update deposit pheromone if needed (Currently based on the concave cost NFP paper)
                    # TODO - Deposit pheromone proportional to the amount of flow on the arc, not just if it was opened?

    def initializePopulation(self) -> list:
        """Initializes the population with ants objects"""
        population = []
        for n in range(self.numAnts):
            thisAnt = Ant(self.network, self.minTargetFlow, self.alpha, self.beta)
            population.append(thisAnt)
        return population

    def initializePheromoneDict(self) -> dict:
        """Adds all possible arcs and supersource/sink as keys to the pheromone dictionary with a value of 1.0"""
        pheromoneDict = {}
        # For all edge, cap pairs, initialize with one
        for edge in self.network.edgesArray:
            for cap in self.network.possibleArcCapsArray:
                pheromoneDict[(edge[0], edge[1], cap)] = 1.0
        # For all supersource -> source and visa versa, initialize with zero
        for srcIndex in range(self.network.numSources):
            source = self.network.sourcesArray[srcIndex]
            cap = self.network.sourceCapsArray[srcIndex]
            pheromoneDict[(-1, source, cap)] = 1.0
            pheromoneDict[(source, -1, -1)] = 1.0
        # For all supersink -> sink, initialize with zero (NOTE: You can't go back from a supersink)
        for sinkIndex in range(self.network.numSinks):
            sink = self.network.sinksArray[sinkIndex]
            cap = self.network.sinkCapsArray[sinkIndex]
            pheromoneDict[(sink, -2, cap)] = 1.0
        return pheromoneDict

    def initializeGoodnessOfArcDict(self) -> dict:
        """Adds all possible arcs and supersource/sink as keys to the pheromone dictionary with a value of 1/(FixedCost + VariableCost)"""
        # TODO - Determine if there is a better metric for "goodness" of arc (Currently based on the concave cost NFP paper)
        arcGoodnessDict = {}
        # For all edge, cap pairs, initialize with one
        for edge in self.network.edgesArray:
            for cap in self.network.possibleArcCapsArray:
                arcObj = self.network.arcsDict[(edge[0], edge[1], cap)]
                arcGoodness = 1 / (arcObj.fixedCost + arcObj.variableCost)
                arcGoodnessDict[(edge[0], edge[1], cap)] = arcGoodness
        # For all supersource -> source and visa versa, initialize with zero
        for srcIndex in range(self.network.numSources):
            source = self.network.sourcesArray[srcIndex]
            cap = self.network.sourceCapsArray[srcIndex]
            variableCost = self.network.sourceVariableCostsArray[srcIndex]
            # srcGoodness = 1/variableCost
            srcGoodness = 1 / (
                        variableCost ** 2)  # NOTE: SQUARING THE SOURCES VARIABLE COST TO MAKE MOVING BACK TO THE SOURCE SEEM REALLY NOT GOOD
            # TODO - Understand how the "goodness" influences source and sink super-edges as we want to be moving away from sources and towards sinks when they are adjacent
            arcGoodnessDict[(-1, source, cap)] = srcGoodness
            # TODO - Determine how to weight the "goodness" of the edges that go back to a supersource as these should only be taken when they have to be
            arcGoodnessDict[(source, -1, -1)] = 0.0001
        # For all supersink -> sink, initialize with zero (NOTE: You can't go back from a supersink)
        for sinkIndex in range(self.network.numSinks):
            sink = self.network.sinksArray[sinkIndex]
            cap = self.network.sinkCapsArray[sinkIndex]
            variableCost = self.network.sinkVariableCostsArray[sinkIndex]
            sinkGoodness = 100 / variableCost  # NOTE: PUTTING 100 IN THE NUMERATOR TO CREDIT THAT WE WANT TO MOVE TOWARDS SINKS IF WE ARE CLOSE
            # TODO - Understand how the "goodness" influences source and sink super-edges as we want to be moving away from sources and towards sinks when they are adjacent
            arcGoodnessDict[(sink, -2, cap)] = sinkGoodness
        return arcGoodnessDict

    def resetAllAnts(self) -> None:
        """Resets the tour/solution attributes for all the ants in the population"""
        for ant in self.population:
            ant.resetTourAndSolutionAttributes()
