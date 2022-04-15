from src.Network.FlowNetwork import FlowNetwork
# Network Test
from src.Network.SolutionVisualizer import SolutionVisualizer
from src.Solvers.MILPsolverCPLEX import MILPsolverCPLEX

name = "basic.p"
flowNetwork = FlowNetwork()
flowNetwork = flowNetwork.loadNetwork(name)
flowNetwork.drawNetworkTriangulation()

# Network Visualization Test
# visualizer = NetworkVisualizer(flowNetwork, directed=True)
# visualizer.drawBidirectionalGraphWithSmoothedLabeledEdges()

# Solver Test
solver = MILPsolverCPLEX(flowNetwork, 80, isOneArcPerEdge=True)
solver.buildModel()
solver.solveModel()
solver.printAllSolverData()

# Solution Test
solution = solver.writeSolution()
solution.saveSolution()

# Solution Visualizer Test
solnVisualizer = SolutionVisualizer(solution)
# solnVisualizer.drawUnlabeledGraph()
solnVisualizer.drawGraphWithLabels()
