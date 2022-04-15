from src.ACO.Colony import Colony
from src.Network.FlowNetwork import FlowNetwork
from src.Network.SolutionVisualizer import SolutionVisualizer

# Load Network
networkFile = "basic.p"
network = FlowNetwork()
network = network.loadNetwork(networkFile)

# Test Colony
antColony = Colony(network, 120, 20, 5)
soln = antColony.solveNetwork()

vis = SolutionVisualizer(soln)
vis.drawGraphWithLabels()
print("ACO stopped!")
