import csv
from datetime import datetime

import numpy as np

from src.ACO.Colony import Colony
from src.Network.FlowNetwork import FlowNetwork
from src.Solvers.MILPsolverCPLEX import MILPsolverCPLEX
from src.Solvers.RelaxedLPSolverPDLP import RelaxedLPSolverPDLP


class ResultsExperiment:
    """Class that defines a Results Experiment object, used for comparing the tuned ACO to the optimal value for """

    # =========================================
    # ============== CONSTRUCTOR ==============
    # =========================================
    def __init__(self, networkList: list, numAnts: int, numEpisodes: int):
        """Constructor of a Tuning Experiment instance"""
        # Input Attributes
        self.networkList = networkList
        self.numAnts = numAnts
        self.numEpisodes = numEpisodes

        # Experimental Results
        self.outputBlock = []
        self.buildOutputHeader()

    def runExperiment(self) -> None:
        """Runs a grid search hyperparameter tuning experiment"""
        for networkName in self.networkList:
            print("Solving " + networkName + "...")
            # Initialize output row
            outputRow = []
            # Get network data and build output row input cells
            networkData = networkName.split("-")
            numNode = networkData[0]
            outputRow.append(numNode)
            parallelEdges = networkData[1]
            outputRow.append(parallelEdges)
            numSrcSinks = networkData[2]
            outputRow.append(numSrcSinks)
            minTargetFlow = int(numSrcSinks) * 100
            outputRow.append(minTargetFlow)
            # Load network
            networkFile = networkName + ".p"
            network = FlowNetwork()
            network = network.loadNetwork(networkFile)
            # Find exact solution
            exactSolver = MILPsolverCPLEX(network, minTargetFlow, isOneArcPerEdge=False)
            exactSolver.buildModel()
            exactSolver.solveModel()
            exactValue = exactSolver.model.solution.get_objective_value()
            outputRow.append(exactValue)
            print("Exact solution found...")
            # Find relaxed solution
            relaxedSolver = RelaxedLPSolverPDLP(network, minTargetFlow)
            alphaValues = np.full((network.numEdges, network.numArcCaps), 1.0)
            relaxedSolver.updateObjectiveFunction(alphaValues)
            relaxedSolver.solveModel()
            relaxedSolver.writeSolution()
            outputRow.append(relaxedSolver.trueCost)
            print("Relaxed solution found...")
            # Run ACO trials
            acoTrials = []
            for trial in range(10):
                aco = Colony(network, minTargetFlow, self.numAnts, self.numEpisodes)
                aco.solveNetwork(drawing=False)
                outputRow.append(aco.bestKnownCost)
                acoTrials.append(aco.bestKnownCost)
                print("ACO trial " + str(trial) + " solved...")
            # Find ACO average
            acoAverage = sum(acoTrials) / len(acoTrials)
            outputRow.append(acoAverage)
            # Compute Optimality Gap
            optimalityGap = ((acoAverage / exactValue) - 1) * 100
            outputRow.append(optimalityGap)
            self.outputBlock.append(outputRow)
        self.writeOutputBlock()
        print("\nRESULTS EXPERIMENT COMPLETE!")

    def buildOutputHeader(self) -> None:
        """Builds the header of the output block"""
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        self.outputBlock.append(["EXPERIMENTAL RESULTS OUTPUT", timestamp])
        self.outputBlock.append(
            ["Num. Nodes", "Num. Parallel Edges", "Num. Src/Sinks", "Min. Target Flow", "Optimal MILP Value",
             "Relaxed LP Value", "ACO 1", "ACO 2", "ACO 3", "ACO 4", "ACO 5", "ACO 6", "ACO 7", "ACO 8", "ACO 9",
             "ACO 10", "Avg. ACO Value", "Optimality Gap"])

    def writeOutputBlock(self) -> None:
        """Writes the output block to a csv file"""
        now = datetime.now()
        uniqueID = now.strftime("%d_%m_%Y_%H_%M")
        fileName = "Results_" + uniqueID + ".csv"
        print("Writing output block to: " + fileName)
        file = open(fileName, "w+", newline="")
        with file:
            write = csv.writer(file)
            write.writerows(self.outputBlock)
