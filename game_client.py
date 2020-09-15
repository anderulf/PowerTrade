from copy import deepcopy
from Resources.classes import Player, Phase, Host
import globals


class Game_client:
    """
    The game class for the client (player) and host. Keeps track of key game aspects
    """
    def __init__(self, role):
        self.role = role
        self.year = 1
        self.years = globals.default_years
        self.bidRounds = globals.default_rounds
        self.storePlants = []
        self.phase = Phase()
        self.ip = ""
        self.phase = "Strategy phase"
        self.bidRound = 1
        self.strategyTime = "--:--"
        self.bidTime = "--:--"
        self.endTime = ""
        self.weather_effect = dict(PV=1, wind=1) # no weather effect initially
        self.initialMoney = globals.default_money*1000000
        self.co2_tax = 0
        self.gas_cost_fixed = 0
        self.gas_cost_variable = 0
        self.coal_cost_fixed = 0
        self.coal_cost_variable = 0
        self.expected_demand_fixed = 0
        self.expected_demand_variable = 0
        self.simple_players = []  # list of Simple_Players objects used to show the players who else is in the game.
        self.host_status = "" # Used for the countdown. Sttus from the host is stored here, so that the player can act on these messages from it's own thread


        if role == "player":
            self.player = Player()
        elif role == "host":
            self.host = Host()
        else:
            print("Error creating game object. Role is not recognized")


    def getBidRounds(self):
        return self.bidRounds

    #def setInitialMoney(self, money):
    #    self.initialMoney = money

    def setYear(self, year):
        self.year = year

    def setYears(self, years):
        self.years = years

    def setBidRounds(self, bidRounds):
        self.bidRounds = bidRounds

    def setStartPlant(self, startPlant):
        """
        Input is string, not a plant object
        """
        self.startPlant = startPlant

    def newYear(self):
        self.year = self.year +1

    def getStorePlants(self):
        return self.storePlants

    def getStorePlant(self, identifier):
        for plant in self.storePlants:
            if plant.identifier == identifier:
                return plant

    def clearStorePlants(self):
        self.storePlants.clear()

    def getYear(self):
        return self.year

    def getYears(self):
        return self.years

    def getPlantPrice(self, n):
        return self.storePlants[n].getInvestmentCost()

    def removePlant(self, n):
        self.storePlants.pop(n)

    def addPlant(self, plant):
        newPlant = deepcopy(plant)
        self.storePlants.append(newPlant)

    def addStorePlant(self, plant):
        self.storePlants.append(plant)

    def getIp(self):
        return self.ip

    def setIp(self, ip):
        self.ip = ip

    def transition(self):
        """
        When called it transitions into the correct phase ie. new bidding phase, new strategy phase, endGame
        phases: "strategy phase", "Bidding phase", "End game"
        """
        try:
            # Strategy phase always initiates a bidding phase
            if self.phase == "Strategy phase":
                self.phase = "Bidding phase"
                self.bidRound = 1
            # A bidding phase can initiate strategy phase, bid phase and endGame
            elif self.phase == "Bidding phase":
                self.bidRound += 1
                if self.bidRound > self.bidRounds:
                    self.year += 1
                    if self.year > self.years:
                        self.phase = "End game"
                    else:  # still more years left in game transition to strategy phase
                        self.phase = "Strategy phase"
            if self.role == "host":
                self.host.setAllPlayersNotReady()
            elif self.role == "player":
                self.player.status == "Not ready"
        except Exception as e:
            print(e)

    def getPhase(self):
        return self.phase

    def incrementBidRound(self):
        self.bidRound = self.bidRound + 1

    def getBidRound(self):
        return self.bidRound

    def setStrategyTime(self, sec):
        self.strategyTime = sec

    def getStrategyTime(self):
        return self.strategyTime

    def setBidTime(self, sec):
        self.bidTime = sec

    def getBidTime(self):
        return self.bidTime

    def setEndTime(self, endTime):
        self.endTime = endTime

    def getEndTime(self):
        return self.endTime

    def calculate_demand_slope(self):
        """
        Calculates the demand slope based on the total installed capacity
        """
        # TODO: method needs adjusting. It should also be moved to host??
        self.host.demand[1] = self.host.demand[0]/((0.6+0.05*(self.year-1))*self.host.total_capacity)
        if globals.DEBUGGING:
            print("Debbuging in calculate_demand_slope:")
            print(self.host.total_capacity)
            print(self.host.demand[0])
            print(self.host.demand[1])
            print("Debugging completed")

    def removeSimplePlayer(self, playerNumber):
        for index, player in enumerate(self.simple_players):
            if player.playerNumber == playerNumber:
                if globals.DEBUGGING:
                    print("Removing player {}".format(player.firm_name))
                self.simple_players.pop(index)
                if globals.DEBUGGING:
                    print("Simple players remaining {}".format(self.simple_players))