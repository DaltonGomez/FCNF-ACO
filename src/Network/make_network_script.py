from src.Network.GraphMaker import GraphMaker

name = "25-1-10"
numNodes = 25
numSources = 10
numSinks = 10

graphMaker = GraphMaker(name, numNodes, numSources, numSinks)
# Uncomment to tune how the network generates costs and to turn on generalizations
graphMaker.setCostDeterminingHyperparameters(possibleArcCaps=[100])
graphMaker.setSourceSinkGeneralizations(True, True)

generatedNetwork = graphMaker.generateNetwork()
generatedNetwork.drawNetworkTriangulation()
generatedNetwork.saveNetwork()
