import random
import sys

from src.Network.FlowNetwork import FlowNetwork


class Ant:
    """Class that defines an Ant object, representing a single agent exploring the flow network space"""

    # =========================================
    # ============== CONSTRUCTOR ==============
    # =========================================
    def __init__(self, network: FlowNetwork, minTargetFlow: float):
        """Constructor of an Ant instance"""
        # Input Attributes
        self.network = network
        self.minTargetFlow = minTargetFlow

        # Hyperparameters
        self.flowCarriedPerTrip = 10.0  # The size of the ant's "backpack"

        # Tour Attributes
        # NOTE: A "tour" is a complete feasible solution that assigns all target flow across the network in a number of trips
        self.time = 0  # Kind of for shits and gigs, incremented every time an arc is traveled (i.e. proportional to the search time of all trips
        self.numTrips = 0  # Number of trips the ant has taken
        self.currentPosition = -1  # Node ID of the ant's position- NOTE: -1 Represents the supersource and -2 represents the supersink
        self.remainingFlowToAssign = self.minTargetFlow  # "Mountain" of flow initially at the supersource that the ant has to move
        self.flowCarriedOnCurrentTrip = 0.0  # Amount of flow in the ant's "backpack" on any given trip
        self.flowDeliveredToSinks = 0.0  # "Mountain" of flow built up over multiple trips until the tour is complete
        self.arcsTraveled = self.initializeArcsTravelFlowAssignDict()  # Dictionary indexed on key (fromNode, toNode, cap) with value (# of times traversed)
        self.assignedFlowDict = self.initializeArcsTravelFlowAssignDict()  # Dictionary indexed on key (fromNode, toNode, cap) with value (cumulative flow assigned)
        self.availableCapacity = self.initializeAvailableCapacityDict()  # Dictionary indexed on key (fromNode, toNode, cap) with value (available capacity until full)

        # Trip Attributes
        # NOTE: A "trip" is a single supersource -> supersink path that assigns only x amount of flow
        self.tripStack = []  # Maintains the arcs traveled on the current trip (NOTE: Should be treated as a true stack- push/pop only!
        self.arcsVisitedThisTrip = set()  # Maintains a set to prevent taking the same arc twice
        # TODO - Originally the set data structure was to prevent cycles, while it prevents continuously going back and forth, it does not prevent cycles

    def findSolution(self) -> dict:
        """Main loop that has the ant explore the graph space until a feasible solution is discovered"""
        # TOUR LOOP
        while self.remainingFlowToAssign > 0.0:  # While all flow is not delivered
            # PRE-TRIP SETUP
            self.resetTripAttributes()  # Start a new trip
            self.currentPosition = -1  # Reset to supersource
            self.flowCarriedOnCurrentTrip = self.flowCarriedPerTrip  # Take flow from mountain and put in backpack
            # TRIP LOOP
            while self.currentPosition != -2:  # Explore until the supersink is found
                options = self.getPossibleNextMoves()  # Get options for next move by checking non-full adjacent edges
                arcChoice = self.decideArcToTraverse(options)  # Probabilistically choose a next arc
                self.printTimeStepData(arcChoice)  # Print action for debugging/QA
                self.travelArc(arcChoice)  # Move the ant across the arc and assign flow
            # POST-TRIP ACCOUNTING
            self.remainingFlowToAssign -= self.flowCarriedOnCurrentTrip  # Deduct remaining flow from "mountain"
            self.flowDeliveredToSinks += self.flowCarriedOnCurrentTrip  # Deposit flow in supersink
            self.numTrips += 1  # Increment trips
            self.printTripData()  # Print trip for debugging/QA
        return self.assignedFlowDict  # Return where flow was assigned (Not really necessary as it is an instance field)

    def getPossibleNextMoves(self) -> list:
        """Returns the possible options the ant could take on their next timestep"""
        options = []
        # Evaluate options if you're at supersource
        if self.currentPosition == -1:
            for srcIndex in range(self.network.numSources):
                source = self.network.sourcesArray[srcIndex]
                cap = self.network.sourceCapsArray[srcIndex]
                arcID = (-1, source, cap)
                # Previous is was: if self.availableCapacity[arcID] > 0.0 and arcID not in self.arcsVisitedThisTrip:
                if self.availableCapacity[arcID] > 0.0:
                    options.append((-1, source, cap))
        # Evaluate options if you're anywhere else
        else:
            nodeObj = self.network.nodesDict[self.currentPosition]
            # Add all arcs that are not at capacity to the options
            for edge in nodeObj.outgoingEdges:
                for cap in self.network.possibleArcCapsArray:
                    arcID = (edge[0], edge[1], cap)
                    # Previous is was: if self.availableCapacity[arcID] > 0.0 and arcID not in self.arcsVisitedThisTrip:
                    if self.availableCapacity[arcID] > 0.0:
                        options.append((edge[0], edge[1], cap))
            # Give the possibility to go back to the supersource if at a source
            if nodeObj.nodeType == 0:
                options.append((nodeObj.nodeID, -1, -1))
            # Give the possibility to go to the supersink if at a sink
            elif nodeObj.nodeType == 1:
                for sinkIndex in range(self.network.numSinks):
                    if nodeObj.nodeID == self.network.sinksArray[sinkIndex]:
                        options.append((nodeObj.nodeID, -2, self.network.sinkCapsArray[sinkIndex]))
        return options

    @staticmethod
    def decideArcToTraverse(options: list) -> tuple:
        """Probabilistically selects the arc the ant will travel on the next timestep"""
        # TODO - Implement based on pheromone/goodness of arc... Currently a random walk until everything else is working
        # TODO - Implementation should strongly discredit backtracks (unless its the only option)
        random.seed()
        arcChoice = random.choice(options)
        return arcChoice

    def travelArc(self, arcChoice: tuple) -> None:
        """Moves the ant across the arc, assigning flow as it goes"""
        # If the move is a back track, then undo the flow assigned on the last step
        if self.isBackTrack(arcChoice) is True:
            self.time += 1  # Increment the timestep
            backArc = self.tripStack.pop(
                -1)  # Pop previous move off trip stack (i.e. get the opposite edge to this one)
            self.currentPosition = arcChoice[1]  # Update position (i.e. move across arc)
            self.assignedFlowDict[
                backArc] -= self.flowCarriedOnCurrentTrip  # Deduct previously assigned flow on opposite arc
            self.availableCapacity[backArc] += self.flowCarriedOnCurrentTrip  # Add flow back to available capacity
            self.arcsTraveled[backArc] -= 1  # Don't count a back tracked arc in the final solution
            self.arcsVisitedThisTrip.add(arcChoice)  # Add to arcs visited this trip set
        else:
            self.time += 1  # Increment the timestep
            self.currentPosition = arcChoice[1]  # Update position (i.e. move across arc)
            self.assignedFlowDict[
                arcChoice] += self.flowCarriedOnCurrentTrip  # Assign carried flow to whatever has already been assigned
            # TODO - What if deducting the flow makes it go negative? Only take what you can and propagate the reduced flow back through the path?
            self.availableCapacity[arcChoice] -= self.flowCarriedOnCurrentTrip  # Deduct flow from available capacity
            self.arcsTraveled[arcChoice] += 1  # Increment this arc's entry in number of times visited
            self.tripStack.append(arcChoice)  # Push the move onto the trip stack
            self.arcsVisitedThisTrip.add(arcChoice)  # Add to arcs visited this trip set

    def isBackTrack(self, arcChoice: tuple) -> bool:
        """Peeks at the top of the trip stack and returns true if the current move undoes the last"""
        # Make sure there is a trip history (i.e. not at the supersource)
        if len(self.tripStack) == 0:
            return False
        else:
            tripStackPeek = self.tripStack[-1]
            # If now's toNode is last's fromNode and last's fromNode is now's toNode
            if arcChoice[0] == tripStackPeek[1] and arcChoice[1] == tripStackPeek[0]:
                return True
            else:
                return False

    def initializeArcsTravelFlowAssignDict(self) -> dict:
        """Adds all possible arcs and supersource/sink as keys to the assigned flow/arcs traveled dictionaries with a value of zero"""
        assignedFlowDict = {}
        # For all edge, cap pairs, initialize with zero
        for edge in self.network.edgesArray:
            for cap in self.network.possibleArcCapsArray:
                assignedFlowDict[(edge[0], edge[1], cap)] = 0
        # For all supersource -> source and visa versa, initialize with zero
        for srcIndex in range(self.network.numSources):
            source = self.network.sourcesArray[srcIndex]
            cap = self.network.sourceCapsArray[srcIndex]
            assignedFlowDict[(-1, source, cap)] = 0
            assignedFlowDict[(source, -1, -1)] = 0
        # For all supersink -> sink, initialize with zero (NOTE: You can't go back from a supersink)
        for sinkIndex in range(self.network.numSinks):
            sink = self.network.sinksArray[sinkIndex]
            cap = self.network.sinkCapsArray[sinkIndex]
            assignedFlowDict[(sink, -2, cap)] = 0
        return assignedFlowDict

    def initializeAvailableCapacityDict(self) -> dict:
        """Adds all possible arcs and supersource/sink as keys to the available capacity dictionary with value capacity"""
        availableCapacity = {}
        # For all edge, cap pairs, initialize with cap
        for edge in self.network.edgesArray:
            for cap in self.network.possibleArcCapsArray:
                availableCapacity[(edge[0], edge[1], cap)] = cap
        # For all supersource -> source initialize with cap, and for visa versa initialize with MAX_INT
        for srcIndex in range(self.network.numSources):
            source = self.network.sourcesArray[srcIndex]
            cap = self.network.sourceCapsArray[srcIndex]
            availableCapacity[(-1, source, cap)] = cap
            availableCapacity[(source, -1, -1)] = sys.maxsize
        # For all supersink -> sink, initialize with zero (NOTE: You can't go back from a supersink)
        for sinkIndex in range(self.network.numSinks):
            sink = self.network.sinksArray[sinkIndex]
            cap = self.network.sinkCapsArray[sinkIndex]
            availableCapacity[(sink, -2, cap)] = cap
        return availableCapacity

    def resetTripAttributes(self) -> None:
        """Resets the trip attributes after going back to the source"""
        self.arcsVisitedThisTrip = set()
        self.tripStack = []

    def printTripData(self) -> None:
        """Prints the data at each time step"""
        print("==================== TRIP ====================")
        print("Trip Number = " + str(self.numTrips))
        print("Trip Stack:")
        print(str(self.tripStack))

    def printTimeStepData(self, arcChoice: tuple) -> None:
        """Prints the data at each time step"""
        print("----------- TIME STEP -----------")
        print("Time = " + str(self.time))
        print("Prev. Node = " + str(arcChoice[0]))
        print("Current Node = " + str(arcChoice[1]))
        print("Is Backtrack? " + str(self.isBackTrack(arcChoice)))
        print("Trip Stack:")
        print(str(self.tripStack))
