from src.Experiments.ResultsExperiment import ResultsExperiment

numAnts = 50
numEpisodes = 15
networkList = [
    "25-1-1",
    "25-1-5",
    "25-1-10",
    "50-1-1",
    "50-1-5",
    "50-1-10",
    "100-1-1",
    "100-1-5",
    "100-1-10",
    "500-1-1",
    "500-1-5",
    "500-1-10",
    "1000-1-1",
    "1000-1-5",
    "1000-1-10"
]

experiment = ResultsExperiment(networkList, numAnts, numEpisodes)
experiment.runExperiment()
