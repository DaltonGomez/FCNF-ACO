from src.ACO.Colony import Colony
from src.Network.FlowNetwork import FlowNetwork

networkFile = "smallTest.p"

network = FlowNetwork()
network = network.loadNetwork(networkFile)

antColony = Colony(network, 100)
