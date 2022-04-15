from src.Network.FlowNetwork import FlowNetwork


class Colony:
    """Class that defines a Colony object, representing an entire ant colony in the ACO approach"""

    # =========================================
    # ============== CONSTRUCTOR ==============
    # =========================================
    def __init__(self, network: FlowNetwork, minTargetFlow: float):
        """Constructor of a Colony instance"""
        self.network = network
        self.minTargetFlow = minTargetFlow
