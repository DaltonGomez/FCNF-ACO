from src.ACO.Colony import Colony
from src.Network.FlowNetwork import FlowNetwork

# Load Network
networkFile = "basic.p"
network = FlowNetwork()
network = network.loadNetwork(networkFile)

# Test Colony
antColony = Colony(network, 20, 1, 2)
soln = antColony.solveNetwork()

# Visualize final solution
# vis = SolutionVisualizer(soln)
# vis.drawGraphWithLabels()
print("ACO stopped!")
