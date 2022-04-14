class Ant:
    """Class that defines an Ant object, representing a single agent exploring the flow network space"""

    # =========================================
    # ============== CONSTRUCTOR ==============
    # =========================================
    def __init__(self, minTargetFlow: float):
        """Constructor of an Ant instance"""
        self.minTargetFlow = minTargetFlow
