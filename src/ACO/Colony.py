from src.Network.FlowNetwork import FlowNetwork
from src.Network.Solution import Solution


class Colony:
    """Class that defines a Colony object, representing an entire ant colony in the ACO approach"""

    # =========================================
    # ============== CONSTRUCTOR ==============
    # =========================================
    def __init__(self, network: FlowNetwork, minTargetFlow: float):
        """Constructor of a Colony instance"""
        # Input Attributes
        self.network = network
        self.minTargetFlow = minTargetFlow

        # Colony Attributes
        self.numEpisodes = 1  # One episode = All the ants creating one valid solution each
        self.numAnts = 1
        self.population = []

    def solve(self) -> Solution:
        """Main loop that solves the Flow Network instance with ACO"""
        for episode in range(self.numEpisodes):
            for ant in self.population:
                pass  # Should call a method where an ant solves the network
            pass  # Should call a method where all ants solutions are evaluated/pheromone is evaporated/applied
        return Solution()  # Should return the best solution found at the end
