import numpy as np

from src.ACO.Colony import Colony
from src.Network.FlowNetwork import FlowNetwork
from src.Network.SolutionVisualizer import SolutionVisualizer
from src.Solvers.MILPsolverCPLEX import MILPsolverCPLEX
from src.Solvers.RelaxedLPSolverPDLP import RelaxedLPSolverPDLP

# Load Network
networkFile = "medium.p"
network = FlowNetwork()
network = network.loadNetwork(networkFile)
targetFlow = 1000

# Test Colony
antColony = Colony(network, targetFlow, 25, 25)
antSoln = antColony.solveNetwork(drawing=False)
antSoln.saveSolution()
antVisualizer = SolutionVisualizer(antSoln)
antVisualizer.drawUnlabeledGraph()

# Solve Exactly
milpSolver = MILPsolverCPLEX(network, targetFlow, isOneArcPerEdge=False)
milpSolver.buildModel()
milpSolver.solveModel()
milpSolver.printSolverOverview()
exactSoln = milpSolver.writeSolution()
exactVisualizer = SolutionVisualizer(exactSoln)
exactVisualizer.drawUnlabeledGraph()

# Solve with Naive LP Relaxation
lpSolver = RelaxedLPSolverPDLP(network, targetFlow)
alphaValues = np.full((network.numEdges, network.numArcCaps), 1.0)
lpSolver.updateObjectiveFunction(alphaValues)
lpSolver.solveModel()
lpSolver.printSolverOverview()
relaxedSoln = lpSolver.writeSolution()
relaxedVisualizer = SolutionVisualizer(relaxedSoln)
relaxedVisualizer.drawUnlabeledGraph()
