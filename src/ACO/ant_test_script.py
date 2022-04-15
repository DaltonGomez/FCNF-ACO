from src.ACO.Ant import Ant
from src.Network.FlowNetwork import FlowNetwork

networkFile = "basic.p"

network = FlowNetwork()
network = network.loadNetwork(networkFile)

singleAnt = Ant(network, 20.0)
singleAnt.findSolution()
