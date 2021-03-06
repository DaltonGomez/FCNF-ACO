import csv
from datetime import datetime

import numpy as np

from src.ACO.Colony import Colony
from src.Network.FlowNetwork import FlowNetwork
from src.Solvers.MILPsolverCPLEX import MILPsolverCPLEX
from src.Solvers.RelaxedLPSolverPDLP import RelaxedLPSolverPDLP


class TuningExperiment:
    """Class that defines a Tuning Experiment object, used for finding the optimal hyperparameters of the ACO"""

    # =========================================
    # ============== CONSTRUCTOR ==============
    # =========================================
    def __init__(self, network: FlowNetwork, minTargetFlow: float):
        """Constructor of a Tuning Experiment instance"""
        # Input Attributes
        self.network = network
        self.minTargetFlow = minTargetFlow

        # Hyperparameter Attributes (Defines the Grid Search Space)
        self.numEpisodes = [15]
        self.numAnts = [10, 25, 50]
        self.initialPheromoneConcentration = [1, 10000, 1000000]
        self.evaporationRate = [0.05, 0.50, 0.75]
        self.alpha = [1, 3, 10]
        self.beta = [1, 3, 10]
        self.Q = [1, 5, 20]

        # Mathematical Programming Solvers
        self.relaxedSolver = RelaxedLPSolverPDLP(network, minTargetFlow)
        self.relaxedCost, self.relaxedSoln = self.findRelaxedSolution()
        self.exactSolver = MILPsolverCPLEX(network, minTargetFlow, isOneArcPerEdge=False)
        self.exactCost, self.exactSoln = self.findExactSolution()
        print("Mathematical programming solvers executed...")

        # ACO Approach
        self.aco = Colony(network, minTargetFlow, self.numAnts[0], self.numEpisodes[0])

        # Tuning Results
        self.outputBlock = []
        self.buildOutputHeader()

    def runExperiment(self) -> None:
        """Runs a grid search hyperparameter tuning experiment"""
        for ants in self.numAnts:
            for initialPheromone in self.initialPheromoneConcentration:
                for evaporation in self.evaporationRate:
                    for alphaValue in self.alpha:
                        for betaValue in self.beta:
                            for qValue in self.Q:
                                # Set this batch of hyperparameters
                                self.setAntColonyHyperparameters(ants, initialPheromone, evaporation, alphaValue,
                                                                 betaValue, qValue)
                                # Solve the network
                                currSoln = self.aco.solveNetwork(drawing=False)
                                # Output data
                                outputRow = [ants, initialPheromone, evaporation, alphaValue, betaValue, qValue,
                                             currSoln.trueCost]
                                for ep in range(self.aco.numEpisodes):
                                    outputRow.append(self.aco.convergenceData[ep])
                                print("\nSolved:")
                                print(outputRow)
                                self.outputBlock.append(outputRow)
        self.writeOutputBlock()
        print("\nTUNING EXPERIMENT COMPLETE!")

    def setAntColonyHyperparameters(self, numAnts: int, initialPheromone: float, evaporation: float, alpha: float,
                                    beta: float, Q: float) -> None:
        """Sets the hyperparameters of the ACO object"""
        self.aco = Colony(self.network, self.minTargetFlow, numAnts, self.numEpisodes[0])  # Reset the ACO object
        self.aco.numAnts = numAnts
        self.aco.initialPheromoneConcentration = initialPheromone
        self.aco.evaporationRate = evaporation
        self.aco.alpha = alpha
        self.aco.beta = beta
        self.aco.Q = Q

    def findRelaxedSolution(self) -> tuple:
        """Computes the LP relaxed solution"""
        alphaValues = np.full((self.network.numEdges, self.network.numArcCaps), 1.0)
        self.relaxedSolver.updateObjectiveFunction(alphaValues)
        self.relaxedSolver.solveModel()
        # self.relaxedSolver.printSolverOverview()
        relaxedSoln = self.relaxedSolver.writeSolution()
        return self.relaxedSolver.trueCost, relaxedSoln

    def findExactSolution(self) -> tuple:
        """Computes the MILP exact solution"""
        self.exactSolver.buildModel()
        self.exactSolver.solveModel()
        # self.exactSolver.printSolverOverview()
        exactSoln = self.exactSolver.writeSolution()
        return self.exactSolver.model.solution.get_objective_value(), exactSoln

    def writeOutputBlock(self) -> None:
        """Writes the output block to a csv file"""
        now = datetime.now()
        uniqueID = now.strftime("%d_%m_%Y_%H_%M")
        fileName = "Tuning_" + uniqueID + ".csv"
        print("Writing output block to: " + fileName)
        file = open(fileName, "w+", newline="")
        with file:
            write = csv.writer(file)
            write.writerows(self.outputBlock)

    def buildOutputHeader(self) -> None:
        """Builds the header of the output block"""
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        self.outputBlock.append(["Tuning Experiment Output", timestamp])
        self.outputBlock.append(["Network", self.network.name])
        self.outputBlock.append(["Min Target Flow", self.minTargetFlow])
        self.outputBlock.append(["Exact Cost", self.exactCost])
        self.outputBlock.append(["Relaxed Cost", self.relaxedCost])
        self.outputBlock.append(["TUNING EXPERIMENT OUTPUT"])
        self.outputBlock.append(
            ["Num. Ants", "Initial Pheromone", "Evap. Rate", "Alpha", "Beta", "Q", "Best Cost", "Convergence"])
