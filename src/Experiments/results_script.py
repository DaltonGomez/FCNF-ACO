from src.Experiments.ResultsExperiment import ResultsExperiment

numAnts = 50
numEpisodes = 15
networkList = [
    "25-1-1",
    "25-1-5",
    "25-1-10",
]

experiment = ResultsExperiment(networkList, numAnts, numEpisodes)
experiment.runExperiment()
