from src.Experiments.TuningExperiment import TuningExperiment
from src.Network.FlowNetwork import FlowNetwork

networkFile = "basic.p"
network = FlowNetwork()
network = network.loadNetwork(networkFile)
targetFlow = 120

tuner = TuningExperiment(network, targetFlow)
tuner.runExperiment()
