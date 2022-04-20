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
targetFlow = 600

# Test Colony
antColony = Colony(network, targetFlow, 25, 25)
antSoln = antColony.solveNetwork(drawing=True)
antSoln.saveSolution()

# Solve Exactly
milpSolver = MILPsolverCPLEX(network, targetFlow, isOneArcPerEdge=False)
milpSolver.buildModel()
milpSolver.solveModel()
exactSoln = milpSolver.writeSolution()
exactVisualizer = SolutionVisualizer(exactSoln)
exactVisualizer.drawGraphWithLabels()

# Solve with Naive LP Relaxation
lpSolver = RelaxedLPSolverPDLP(network, targetFlow)
alphaValues = np.full((network.numEdges, network.numArcCaps), 1.0)
lpSolver.updateObjectiveFunction(alphaValues)
lpSolver.solveModel()
relaxedSoln = lpSolver.writeSolution()
relaxedVisualizer = SolutionVisualizer(relaxedSoln)
relaxedVisualizer.drawGraphWithLabels()
