from src.ACO.Colony import Colony
from src.Network.FlowNetwork import FlowNetwork
from src.Network.SolutionVisualizer import SolutionVisualizer
from src.Solvers.MILPsolverCPLEX import MILPsolverCPLEX

# Load Network
networkFile = "basic.p"
network = FlowNetwork()
network = network.loadNetwork(networkFile)
targetFlow = 120

# Test Colony
antColony = Colony(network, targetFlow, 5, 5)
antSoln = antColony.solveNetwork(drawing=True)
antSoln.saveSolution()

# Solve Exactly
milpSolver = MILPsolverCPLEX(network, targetFlow, isOneArcPerEdge=False)
milpSolver.buildModel()
milpSolver.solveModel()
exactSoln = milpSolver.writeSolution()
solnVisualizer = SolutionVisualizer(exactSoln)
solnVisualizer.drawGraphWithLabels()
