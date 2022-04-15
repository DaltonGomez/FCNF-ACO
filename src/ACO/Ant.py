from src.Network.FlowNetwork import FlowNetwork


class Ant:
    """Class that defines an Ant object, representing a single agent exploring the flow network space"""

    # =========================================
    # ============== CONSTRUCTOR ==============
    # =========================================
    def __init__(self, network: FlowNetwork, minTargetFlow: float):
        """Constructor of an Ant instance"""
        self.network = network
        self.minTargetFlow = minTargetFlow
