import copy
from pandas import read_excel
import globals

class Player:
    """
    Class to define the player object. It has information about the player
    """
    def __init__(self, playerNumber=None):
        self.firm_name = "Unnamed firm"
        self.firm_motto = ""
        self.money = 1000 #MNOK
        self.plants = []                                    # A list of plant objects
        self.plantsIndex = 0
        self.playerNumber = playerNumber                    # Should be set by the host
        self.bids = []                                      # List of bids
        self.bidsIndex = 0
        self.status = "Not ready"                           # used by host only
        self.conn = None                                    # The connection object used for communicating with the host on the socket
        self.tcpClient = None                               # The socket object used to communicate
        self.statistics = Statistics()                      # Class that holds information about the players results

    def getName(self):
        return self.firm_name

    def getMotto(self):
        return self.firm_motto

    def getMoney(self):
        return self.money

    def getPlants(self):
        return self.plants

    def getPlant(self, n):
        return self.plants[n]

    def getBids(self):
        return self.bids

    def getPlantBids(self, plant):
        """
        This method inputs a specific plant and returns all bids associated with that plant
        """
        bids = []
        for bid in self.bids:
            if bid.getPlantIdentifier() == plant.identifier:
                bids.append(bid)
        return bids

    def getPlantName(self, identifier):
        for plant in self.plants:
            if plant.identifier == identifier:
                return plant.name

    def accumulatedPlantProduction(self, plant):
        """
        Calculates the planned production for one plant. A plant can not produce more than its capacity
        """
        plantBids = self.getPlantBids(plant)
        production = 0
        for bid in plantBids:
            production += bid.amount
        return production

    def setName(self, firm_name):
        self.firm_name = firm_name

    def setMotto(self, firm_motto):
        self.firm_motto = firm_motto

    def setMoney(self, money):
        self.money = money

    def setPlayerNumber(self, playerNumber):
        self.playerNumber = playerNumber

    def appendBid(self, bid):
        """
        Makes a deep copy of the bid and appends to the players list.
        """
        newBid = copy.deepcopy(bid)
        self.bids.append(newBid)

    def appendPlant(self, plant):
        """
        The method does a deep copy of a plant (to avoid copying reference only) and then appends that new copy to the plant list
        """
        newPlant = copy.deepcopy(plant)
        #newPlant.setIdentifier(self.plantsIndex)
        self.plantsIndex = self.plantsIndex + 1
        self.plants.append(newPlant)

    def appendPlants(self, plants):
        newPlants = copy.deepcopy(plants)
        self.plants.extend(newPlants)

    def pay(self, price):
        self.money = self.money - price

    def editBid(self, n, amount, price):
        self.bids[n].setAmount(amount)
        self.bids[n].setPrice(price)

    def removeBid(self, n, plant):
        """
        Finds the plant and pops it from the list
        """
        for element, bid in enumerate(self.bids):
            if bid.number == n and bid.plant == plant:
                self.bids.pop(element)

    def clearBids(self):
        self.bids.clear()

    def getNumber(self):
        return self.playerNumber

    def setBids(self, bids):
        self.bids = bids

    def getStatus(self):
        return self.status

    def setStatus(self, status):
        self.status = status

    def notReady(self):
        return self.status == "Not ready"

    def getTotalCapacity(self):
        total_capacity = 0
        for plant in self.plants:
            total_capacity += plant.capacity
        return total_capacity

class Simple_Player:
    """
    Class for player informaton sharing among players
    """
    def __init__(self, firm_name, firm_motto, playerNumber):
        self.firm_name = firm_name
        self.firm_motto = firm_motto
        self.playerNumber = playerNumber # playerNumber is used to keep track of which player is which

class Host:
    def __init__(self):
        self.bids = []                              # list of dicts{playerNumber, plant, amount, }
        #self.player_statistics = []
        self.demand = [0, 0]                        # demand is D = a + bx (ie. 100-2x)
        self.total_capacity = 0
        self.players = []                           # list of players?
        self.database = Database(globals.datafile)
        self.newPlants = []                         # List of new plants not currently sent to the players.
        self.joinable = True
        self.tcpServer = None                       # The server object ie. the socket on the network card
        self.end_results = {}
        self.used_player_names = []
        self.host_statistics = Statistics()

    def input_data(self):
        # get data from host instead
        gas, coal, co2_tax, demand = self.database.input_data()
        gas_cost_fixed = gas["cost_constant"]
        gas_cost_variable = gas["cost_variable"]
        coal_cost_fixed = coal["cost_constant"]
        coal_cost_variable = coal["cost_variable"]
        self.demand[0] = demand["demand_fixed"]
        self.demand[1] = demand["demand_variable"]
        return gas_cost_fixed, gas_cost_variable, coal_cost_fixed, coal_cost_variable, co2_tax

    def setBids(self, bids):
        """
        Input is a list of bids from all players
        """
        self.bids = bids

    def appendBids(self, bids):
        """"
        Input is a list of bids from one player
        """
        self.bids.extend(bids)

    def getBids(self):
        return self.bids

    def getPlayerBids(self, playerNumber):
        result = []
        for bid in self.bids:
            if bid.getPlayerNumber() == playerNumber:
                result.append(bid)
        return result

    def setDemand(self, a, b):
        """
        This should be read from file
        :param a: the initial price when the demand is zero
        :param b: the slope of the demand curve
        todo: should it be defined as a dictionary instead?
        """
        self.demand[0] = a
        self.demand[1] = b

    def getDemand(self):
        return self.demand

    def calculate_player_multiplier(self):
        #Removed
        pass

    def addPlayer(self, playerNumber):
        player = Player(playerNumber)
        self.players.append(player)

    def getPlayer(self, playerNumber):
        for player in self.players:
            if player.playerNumber == playerNumber:
                return player

    def getPlayerIndex(self, playerNumber):
        for index, player in enumerate(self.players):
            if player.playerNumber == playerNumber:
                return index
        # Playernumber does not exist
        return -1

    def setPlayerData(self, playerNumber, name, motto):
        for player in self.players:
            if player.getNumber() == playerNumber:
                player.setName(name)
                player.setMotto(motto)
                return
        print("Error: tried to change data for a player which is not in the players list")

    def setPlayerBids(self, playerNumber, playerBids):
        """
        :param playerNumber: int
        :param playerBids: list of bids
        """
        for index, player in enumerate(self.players):
            if player.playerNumber == playerNumber:
                self.players[index].bids = playerBids
                return
            index += 1

    def removePlayer(self, playerNumber):
        for index, player in enumerate(self.players):
            if player.playerNumber == playerNumber:
                self.players[index].conn.close()
                self.players.pop(index)

    def getPlayers(self):
        return self.players

    def set_player_placement(self):
        """
        Sets placement of all players
        """

    def calculate_placements(self):
        """
        Find the placement of all players and store it
        """
        # Create dictionary of playernumbers and profits
        local_data = {}
        for player in self.players:
            local_data[player.playerNumber] = player.statistics.profits
        sorted_results = sorted(local_data, key=local_data.get, reverse=True)
        for index, key in enumerate(sorted_results):
            playerNumber = key
            placement = index + 1
            self.getPlayer(playerNumber).statistics.placement = placement


    def get_players_by_placement(self):
        """
        Returns a list of all players sorted by placement
        """
        num_players = len(self.players)
        sorted_players = []
        for placement in range(1, num_players+1):
            for player in self.players:
                if player.statistics.placement == placement:
                    sorted_players.append(player)
        return sorted_players

    def setPlayerStatus(self, playerNumber, status):
        for index, player in enumerate(self.players):
            if player.playerNumber == playerNumber:
                self.players[index].status = status

    def allPlayersReady(self):
        for player in self.players:
            if player.notReady():
                return False
        return True

    def setAllPlayesReady(self):
        for playerNumber in range(len(self.players)):
            self.players[playerNumber].setStatus("Ready")

    def setAllPlayersNotReady(self):
        for playerNumber in range(0, len(self.players)):
            self.players[playerNumber].setStatus("Not ready")

    def isJoinable(self):
        return self.joinable

    def setJoinable(self, input):
        self.joinable = input

    def setConn(self, conn, playerNumber):
        # Find player in playerlist and set the conn object for that player
        for index, player in enumerate(self.players):
            if player.playerNumber == playerNumber:
                self.players[index].conn = conn

    def getConn(self, playerNumber):
        # Find player in playerlist and return its conn object
        for index, player in enumerate(self.players):
            if player.playerNumber == playerNumber:
                return self.players[index].conn
class Plant:
    """
    Class to define the plant object.
    """
    def __init__(self, source, name, capacity, investmentCost, efficiency, annualCost, variableCost, emissions, identifier = 0):
        self.source = source
        # Should classification be removed??
        self.classification = ""
        self.name = name
        self.capacity = capacity
        self.investmentCost = investmentCost
        self.efficiency = efficiency
        self.annualCost = annualCost
        # Should it be a marginal cost here?? and emissions
        self.emissions = emissions
        self.variableCost = variableCost
        self.identifier = identifier

    def __eq__(self, other):
        """
        Operator "==" overloading for plant objects
        """
        if (self.identifier == other.identifier):
            return True
        else:
            return False

    def getSource(self):
        return self.source

    def getClassification(self):
        return self.classification

    def getName(self):
        return self.name

    def getCapacity(self):
        return self.capacity

    def getInvestmentCost(self):
        return self.investmentCost

    def getEfficiency(self):
        return self.efficiency

    def getAnnualCost(self):
        return self.annualCost

    def getIdentifier(self):
        return self.identifier

    def getVariableCost(self):
        return self.variableCost

    def getEmissions(self):
        return self.emissions

    def setName(self, name):
        self.name = name

    def setSource(self, source):
        self.source = source

    def setClassification(self, classification):
        self.classification = classification

    def setCapacity(self, capacity):
        self.capacity = capacity

    def setInvestmentCost(self, investmentCost):
        self.investmentCost = investmentCost

    def setEfficiency(self, efficiency):
        self.efficiency = efficiency

    def setAnnualCost(self, annualCost):
        self.annualCost = annualCost

    def setIdentifier(self, identifier):
        self.identifier = identifier

    def setVariableCost(self, variableCost):
        self.variableCost = variableCost

    def setEmissions(self, emissions):
        self.emissions = emissions

    def isDispatchable(self):
        """
        A check if the plant is dispatchable. A dispatchable plant is a fuel driven plant which is able to produce its capacity
        A non dispatchable unit is a plant dependant on externalities like wind, sun, rain etc.
        :return:
        """
        if self.source == "Gas" or self.source == "Coal":
            return True
        else:
            return False


    def getActualCapacity(self, weather_effect):
        if self.isDispatchable():
            return self.capacity
        else:
            return self.capacity * self.efficiency * weather_effect[self.source]
class Phase:
    """
    TODO: delete class
    Phases:
    Strategy phase
    Bidding phase
    """
    def __init__(self):
        self.phase = "Strategy phase"
        self.bidRound = 1
        self.strategyTime = 0
        self.bidTime = 0
        self.endTime = ""                                   # mm:ss format string for the end time for the current phase based on the stratTime and bidTime set by clients or host local time.
    def transition(self):
        if self.phase == "Bidding phase":
            self.phase = "Strategy phase"
            self.bidRound = 1
        elif self.phase == "Strategy phase":
            self.phase = "Bidding phase"

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

class Bid:
    def __init__(self, playerNumber, plant, amount, price):
        """
        A bid is linked to a specific plant and has a amount and price. It is also given a number so that the
        the market window is able to see if a bid is new or edited.
        """
        self.playerNumber = playerNumber
        self.plant = plant
        self.amount = amount
        self.price = price
        self.number = 0
        self.sold_amount = 0

    def getPlayerNumber(self):
        return self.playerNumber

    def getPlant(self):
        return self.plant

    def getPlantIdentifier(self):
        return self.plant.getIdentifier()

    def getPlantSource(self):
        return self.plant.source

    def getAmount(self):
        return self.amount

    def getPrice(self):
        return self.price

    def getNumber(self):
        return self.number

    def setAmount(self, amount):
        self.amount = amount

    def setPrice(self, price):
        self.price = price

    def setNumber(self, number):
        self.number = number

    def setPlayerNumber(self, playerNumber):
        self.playerNumber = playerNumber

class Database:
    """
    Pandas dataFrame extraction class to get data from excel sheet.
    Further work: separate the different sheets in the excel file so that it's easier to go through the data.
    """
    def __init__(self, file):
        try: # TODO: remove this try (it was placed to do debugging)
            # Loading the dataframe. Using sheet_name=None will set self.dataFrame to a dict of dataframes
            self.dataFrame_dict = read_excel(file, sheet_name=None)
        except:
            self.dataFrame_dict = read_excel("data.xlsx")

    def input_data(self):
        data = self.dataFrame_dict["market"]
        dc = data.to_dict()
        gas = dict(cost_constant=dc["Value"][0], cost_variable=dc["Value"][1])
        coal = dict(cost_constant=dc["Value"][2], cost_variable=dc["Value"][3])
        co2_tax = dc["Value"][4]
        demand = dict(demand_fixed=dc["Value"][5], demand_variable=dc["Value"][6])

        return gas, coal, co2_tax, demand

    def get_plants(self, colName, filter, identifier_offset, optional_colName=None, optional_filter = None):
        """
        The method filters out rows in the dataframe based on input settings and returns a list of plants. The extracted rows are removed from the dataframe
        :param colName: Column name ie. Type, Source, Capacity :type: string
        :param filter: what value to look for ie. Initial type, PV source, 500 capacity :type string
        :param identifier_offset: should be equal to len(storePlants) so that the new plants are given the correct identifier :type: int
        :param optional_colName: optional additional colName
        :param optional_filter:  optional additional filter
        :return: a list of plants
        """
        try:
            filtered = self.dataFrame_dict["plants"].loc[self.dataFrame_dict["plants"][colName] == filter]
            if (optional_colName is not None) and (optional_filter is not None):
                filtered = filtered.loc[filtered[optional_colName] == optional_filter]
            dc = filtered.to_dict()
            plants = []
            for i,key in enumerate(dc[colName].keys()):
                plant = Plant(dc["Source"][key], dc["Name"][key], dc["Capacity"][key], dc["InvestmentCost"][key], dc["Efficiency"][key], dc["AnnualCost"][key],dc["VariableCost"][key], dc["Emissions"][key], i+identifier_offset)
                if filter == "Initial" and i == 0:
                    # The initial price value is stored so that the prices can be corrected later
                    globals.initialPlantPrice = dc["InvestmentCost"][key]
                plants.append(plant)
                self.dataFrame_dict["plants"] = self.dataFrame_dict["plants"].drop([key], axis=0)                                        # The dataFrame is restored withouth the extracted row (so that the same plant is not added multiple times)
            return plants
        except Exception as e:
            print(e)

    def get_next_plant_in_list(self, identifier):
        """
        This method extracts the next plant in the list and removes it from the dataframe
        """
        try:
            dc = self.dataFrame_dict["plants"].values[0]
            next_plant = Plant(dc[1], dc[2], dc[3], dc[4], dc[5], dc[6], dc[7], dc[8], identifier)
            # Remove first element from dataframe
            self.dataFrame_dict["plants"].drop(self.dataFrame_dict["plants"].index[:1], inplace=True)
        except:
            next_plant = None
        return next_plant

    def get_name_of_next_plant(self):
        """
        Returns the name of the first plant in the database
        """
        try:
            dc = self.dataFrame_dict["plants"].values[0]
            name = dc[2]
        except:
            # No next plant
            name = "-"
        return name

class Statistics:
    def __init__(self):
        self.profits = 0
        self.revenue = 0
        self.cost = 0
        self.emissions = 0
        self.taxes = 0
        self.installed_capacity = 0
        self.round_results = []
        self.host_round_results = []
        self.placement = 1
        self.leaderboard = None
        self.profit_list = [] # Used by host
        self.revenue_list = []  # Used by host
        self.cost_list = []  # Used by host
        self.emission_list = []  # Used by host


    def create_round_results(self, data):
        """
        data is a dictionary with the following keys
        {
            "year"
            "round"
            "demand_fixed"
            "demand_variable"
            "profits"
            "revenue"
            "cost"
            "taxes"
            "emissions"
            "gas_price"
            "coal_price"
            "gas_production"
            "coal_production"
            "bids": []
        }
        where bids is a list of dictionaries with the following keys
        {
            "plant"
            "bid_amount"
            "actual_amount"
            "profit"
        }
        """
        self.round_results.append(data)

    def get_round_result(self, year, round):
        for round_result in self.round_results:
            if round_result["year"] == year and round_result["round"] == round:
                return round_result

    def create_host_round_results(self, data):
        # Data holds the fields:
        # year
        # round
        # demand_fixed
        # demand_variable
        # bids_accepted
        # number_of_bids
        # hours_for_bid_round
        # system_price
        # demand
        # production
        # co2_tax
        # gas_price
        # gas_production
        # coal_price
        # coal_production
        # pv_production
        print("storing")
        self.host_round_results.append(data)

    def get_host_round_result(self, year, round):
        for round_result in self.host_round_results:
            if round_result["year"] == year and round_result["round"] == round:
                return round_result
"""
    class Host_Statistics:
        def __init__(self, player_list):
            self.players_performance_list = []
            self.rounds_results = []
            self.init_players_performance_list()

        def init_players_performance_list(self, player_list):
            for player in player_list:
                player_dict = {
                    "playerNumber": player.playerNumber,
                    "profit_list": [],
                    "revenue_list": [],
                    "cost_list": [],
                    "emission_list": []
                }
                self.players_performance_list.append(player_dict)
                
        def add_results(self, playerNumber, profit, revenue, cost, emission):
            # Find player
            for player_dict in self.players_performance_list:
                # Add data 
                if player_dict["playerNumber"] == playerNumber:
                    player_dict["profit_list"].append(profit)
                    player_dict["revenue_list"].append(revenue)
                    player_dict["cost_list"].append(cost)
                    player_dict["emission_list"].append(emission)
                    
                    
"""