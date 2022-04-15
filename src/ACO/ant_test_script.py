from src.ACO.Colony import Colony
from src.Network.FlowNetwork import FlowNetwork

# Load Network
networkFile = "basic.p"
network = FlowNetwork()
network = network.loadNetwork(networkFile)

# Test Colony
antColony = Colony(network, 120, 20, 4)
antColony.solveNetwork()
