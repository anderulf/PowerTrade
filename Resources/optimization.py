from pyomo.environ import Param, Set, ConcreteModel, Objective, Constraint, Var, maximize, NonNegativeReals
from pyomo.opt import SolverFactory
from Resources.AuxillaryMethods import format_number
import globals


from Resources.classes import Bid

class Optimization:
    """
    Class for optimization. Contains all relevant data to calculate the results of the optimization aswell.
    Instructions: create a Optimization object. Run start_optimization(). Get results for player with create_results(playerNumber, year, round)
    """
    def __init__(self, game_obj):
        self.data = None                        # The input data
        self.bids = None                        # All the bids
        self.game_obj = game_obj
        self.host = game_obj.host               # The host object is a member of the game client class and stores information about the players
        self.system_price = 0
        #  Initializing imported values (see input_data())
        self.coal_cost_fixed = 0
        self.coal_cost_variable = 0
        self.gas_cost_fixed = 0
        self.gas_cost_variable = 0
        self.co2_tax = 0
        #self.input_data()
        # market dependant variables
        self.gas_fuel = 0
        self.coal_fuel = 0
        self.total_gas_production = 0
        self.total_coal_production = 0
        self.total_pv_production = 0
        self.gas_price = 0
        self.coal_price = 0
        self.demand = 0
        self.players = [] # unused?
        self.hours_per_year = 8760
        self.hours_for_bidround = self.hours_per_year / self.game_obj.bidRounds
        self.accepted_bids_count = 0
        self.rationing_price = 3000 # todo consider moving rationing price to input data

    """
    def input_data(self):
        # get data from host instead
        gas, coal, self.co2_tax, demand = self.host.database.input_data()
        self.gas_cost_fixed = gas["cost_constant"]
        self.gas_cost_variable = gas["cost_variable"]
        self.coal_cost_fixed = coal["cost_constant"]
        self.coal_cost_variable = coal["cost_variable"]
    """
    def add_data(self, bids, game_obj):
        self.bids = bids  # All the bids
        self.game_obj = game_obj
        self.host = game_obj.host
        self.co2_tax = self.game_obj.co2_tax
        self.gas_cost_fixed = self.game_obj.gas_cost_fixed
        self.gas_cost_variable = self.game_obj.gas_cost_variable
        self.coal_cost_fixed = self.game_obj.coal_cost_fixed
        self.coal_cost_variable = self.game_obj.coal_cost_variable
        self.host.bids.clear()  # Clearing the bids so that new ones can be added later

    def createData(self):
        indices = []
        prices = []
        amounts = []
        # Add shadow bid so that the market is always cleared (it is never sold due to it's high price). It should be removed after optimizing
        shadowBid = Bid(-1, None, self.host.demand[0]/self.host.demand[1], self.rationing_price)
        self.bids.insert(0, shadowBid)
        for index, bid in enumerate(self.bids):
            indices.append(index)
            prices.append(bid.price)
            amounts.append(bid.amount)
        self.data = dict(indices=indices, price=prices, amount=amounts)

    def optimization_model(self):
        """
        The optimization model for solving pool trading is set up and solved here
        input: data should edit to supply and demand for example
        """

        model = ConcreteModel()

        # Declare set
        model.blocks = Set(ordered=True, initialize=self.data["indices"])  # Simply a indexing of all the bids

        # Parameters
        model.demand_fixed = Param(initialize=self.host.demand[0])
        model.demand_variable = Param(initialize=self.host.demand[1])
        def init_price(model,block):
            return self.data["price"][block]

        model.bid_price = Param(model.blocks, initialize=init_price, mutable=True)
        def init_maxAmount(model, block):
            return self.data["amount"][block]

        model.bid_maxAmount = Param(model.blocks, initialize=init_maxAmount, mutable=True)

        # variables
        model.bid_amount = Var(model.blocks, within=NonNegativeReals)  # Treated as var because a bid does not have to be fully used
        model.demand = Var(within=NonNegativeReals)  # p = a-b*D, D - demand
        model.system_price = Var(within=NonNegativeReals)

        # Objective function
        def objective_function(model):
            """
            Objective: maximize total surplus
            The first term is the consumer surplus (half of the area demand_fixed - systemprice * demand)
            The second and third term is the producer surplus
            """
            return 0.5*model.demand_variable*model.demand**2 + model.demand_fixed*model.demand - model.demand_variable*model.demand**2 - sum(model.bid_price[block] * model.bid_amount[block] for block in model.blocks)

        model.obj = Objective(rule=objective_function, sense=maximize)

        # Constraints

        # supply == demand
        def powerEquality(model):
            return sum(model.bid_amount[block] for block in model.blocks) == model.demand

        model.constraint_powerBalance = Constraint(rule=powerEquality)

        # Maximum dispatch for each bid (cannot be higher than bid amount)
        def maxAmount(model, block):
            return model.bid_amount[block] <= model.bid_maxAmount[block]

        model.constraint_maxProd = Constraint(model.blocks, rule=maxAmount)

        # Maximum demand
        def maxDemand(model):
            return model.demand <= model.demand_fixed/model.demand_variable # if p = a-bx then p=0 gives x = a/b for maximum demand


        model.constraint_maxDemand = Constraint(rule=maxDemand)
        # demand function met
        def demand_function(model):
            return model.system_price == model.demand_fixed - model.demand_variable*model.demand

        model.constraint_demand_function = Constraint(rule=demand_function)

        return model

    def start_optimization(self):
        """
        Make the necessary steps for optimizing
        """
        self.createData()
        self.model = self.optimization_model()  # The optimization model
        if globals.DEBUGGING:
            print("Optimization was done")
        self.solveOptimization()
        if globals.DEBUGGING:
            print("Solving was completed")
        self.post_analysis()

    def solveOptimization(self):
        try:
            solver = SolverFactory("gurobi")
            result = solver.solve(self.model)
            # The model is now solved and contains information about demand, system price and sold amounts
            self.demand = format_number(self.model.demand.value)
            self.system_price = format_number(self.model.system_price.value)
            for i in self.model.blocks:
                self.bids[i].sold_amount = format_number(self.model.bid_amount[i].value)
            # Remove the shadow bid from the list (it has now served its purpose of clearing the market)
            self.bids.pop(0)
            if globals.DEBUGGING:
                print("Bids in solveOpt {}".format(self.bids))
        except Exception as e:
            print("Exception raised when solving optimization problem")
            print(e)

    def post_analysis(self):
        self.shareEqualBids()
        self.fuelProduction()
        self.calculate_fuel_costs()
        for player in self.host.players:
            self.add_player_bids(player.playerNumber)


    def shareEqualBids(self):
        """
        Method shares the actual bid amounts for bids with the same price so that all players are treated equally.
        Each bid is allocated a percentage of the total accumulated sold amount based on their amount compared to the total amount
        """
        #  The bids are sorted so that equal bids are found easily
        self.bids = sorted(self.bids, key=lambda i: i.price)
        index = 0
        #  Go through all the bids
        for unused in self.bids:
            first_index = index
            last_index = index
            #  check if the bid has the same price as the next bid
            while self.equalNeighbour(last_index):
                # Match so increment last_index
                last_index += 1
            #  Next bid has a different price. Check if last_index was incremented or not
            if last_index != first_index:
                # Multiple bids has the same price so share their amounts
                amount_bid = 0
                amount_sold = 0
                # Calculate the accumulated amount between the bids
                for equals_index in range(first_index, last_index + 1):
                    amount_sold += self.bids[equals_index].sold_amount
                    amount_bid += self.bids[equals_index].amount
                # Share the accumulated amount between the bids
                for equals_index in range(first_index, last_index + 1):
                    self.bids[equals_index].sold_amount = format_number(amount_sold*(self.bids[equals_index].amount/amount_bid))  # The shared amount times the ratio the bid should get
                index = last_index + 1
            else:
                #  The next bid is not equal so go to the next bid
                index += 1

    def equalNeighbour(self, i):
        """
        The method simply compares the price of two neighboring bids handling exceptions so that the other method does not raise exceptions
        """
        try:
            if self.bids[i].price == self.bids[i + 1].price:
                return True
        except:  # Exception is raised if i+1 is outside the indices of the list but this exception is excepted and should be ignored
            pass
        return False

    def fuelProduction(self):
        """
        Inputs evaluated bids and returns the total gas and coal production
        The fuel demand is dependant on the plants efficiency ie. a gas plant with 50% efficiency requires two MW for each MW
        """
        try:
            for bid in self.bids:
                if bid.plant.source == "Gas":
                    self.gas_fuel += bid.sold_amount * self.hours_for_bidround / bid.plant.efficiency
                    self.total_gas_production += bid.sold_amount * self.hours_for_bidround
                elif bid.plant.source == "Coal":
                    self.coal_fuel += bid.sold_amount * self.hours_for_bidround / bid.plant.efficiency
                    self.total_coal_production += bid.sold_amount*self.hours_for_bidround
                elif bid.plant.source == "PV":
                    self.total_pv_production += bid.sold_amount * self.hours_for_bidround
        except Exception as e:
            print("Exception in fuelProduction()")
            print(e)

    def calculate_fuel_costs(self):
        """
        Source is a string input. bids is the full list of bids for one plant after optimization (evaluated)
        """
        self.coal_price = self.coal_cost_fixed + self.coal_cost_variable*self.coal_fuel
        self.gas_price= self.gas_cost_fixed+self.gas_cost_variable*self.gas_fuel

    def add_player_bids(self, playerNumber):
        player_bids = []
        # Find the correct player
        index = self.host.getPlayerIndex(playerNumber)
        # Find the players bids and add them to the player
        for bid in self.bids:
            if bid.playerNumber == playerNumber:
                player_bids.append(bid)
        self.host.players[index].bids = player_bids

    def playerPlantCosts(self, plant, playerNumber):
        try:
            player = self.host.getPlayer(playerNumber)
            plant_bids = player.getPlantBids(plant)
        except:
            return 0
        # Set correct fuel price
        if plant.source == "Gas":
            fuel_cost = self.gas_price
        elif plant.source == "Coal":
            fuel_cost = self.coal_price
        else:
            fuel_cost = 0
        accumulated_power = 0
        for bid in plant_bids:
            accumulated_power += bid.sold_amount
        return plant.annualCost/self.game_obj.bidRounds + (plant.variableCost+fuel_cost)*accumulated_power*self.hours_for_bidround

    def playerPlantEmissions(self, plant, playerNumber):
        try:
            player = self.host.getPlayer(playerNumber)
            plant_bids = player.getPlantBids(plant)
        except:
            return 0
        accumulated_power = 0
        for bid in plant_bids:
            accumulated_power += bid.sold_amount
        return accumulated_power * self.hours_for_bidround * plant.emissions

    def bid_costs(self, playerNumber, bid):
        number_of_bids_for_plant = self.get_number_of_bids_for_plant(playerNumber, bid.plant)
        fuel_cost = self.get_fuel_cost(bid.plant)
        fixed_costs = 0 # We want the operational costs of the bid
        #fixed_costs = bid.plant.annualCost/self.game_obj.bidRounds/number_of_bids_for_plant
        variable_costs = (bid.plant.variableCost + fuel_cost) *bid.sold_amount*self.hours_for_bidround
        return fixed_costs + variable_costs

    def get_number_of_bids_for_plant(self, playerNumber, plant):
        """
        Return the number of bids for plant owned by playerNumber
        """
        player_index = self.host.getPlayerIndex(playerNumber)
        player_bids = self.host.players[player_index].bids
        number_of_bids = 0
        for bid in player_bids:
            if bid.plant == plant:
                number_of_bids += 1
        return number_of_bids

    def get_fuel_cost(self, plant):
        if plant.source == "Gas":
            return self.gas_price
        elif plant.source == "Coal":
            return self.coal_price
        elif plant.source == "PV":
            return 0
        else:
            print("Warning in optimization.get_fuel_cost: source {} is not defined".format(plant.source))

    def bid_emissions(self, bid):
        """
        Return the emissions caused by a bid
        """
        return bid.plant.emissions * self.hours_for_bidround * bid.sold_amount # [kg CO2 eq] (kg/MWh * h * MW)

    def player_source_production(self, playerNumber):
        player_pv_production = 0
        player_gas_production = 0
        player_coal_production = 0
        player_index = self.host.getPlayerIndex(playerNumber)
        player_bids = self.host.players[player_index].bids
        for bid in player_bids:
            if bid.plant.source == "PV":
                player_pv_production += bid.sold_amount * self.hours_for_bidround
            elif bid.plant.source == "Gas":
                player_gas_production += bid.sold_amount * self.hours_for_bidround
            elif bid.plant.source == "Coal":
                player_coal_production += bid.sold_amount * self.hours_for_bidround
        return player_pv_production, player_gas_production, player_coal_production

    def playerTotalCosts(self, playerNumber):
        # Get the total player costs by looking at the players plants
        cost = 0
        for plant in self.host.getPlayer(playerNumber).getPlants():
            cost += self.playerPlantCosts(plant, playerNumber)
        return cost

    def playerResults(self, playerNumber):
        try:
            revenue = 0
            emissions = 0
            player_index = self.host.getPlayerIndex(playerNumber)
            player_bids = self.host.players[player_index].bids
            for bid in player_bids:
                if bid.sold_amount > 0:
                    revenue += bid.sold_amount*self.system_price*self.hours_for_bidround # amount*price*hours per bid round
                    emissions += bid.sold_amount*bid.plant.emissions*self.hours_for_bidround
                    self.accepted_bids_count += 1
            return revenue, emissions
        except Exception as e:
            print("Exception raised in playerResults()")
            print(e)

    def store_host_round_results(self):
        # Where to store this data? It should have year, bidround + all the data but not be linked to any player.
        # Use the statistics class, but make this side of it accessable by the host, and ignored by the players?
        # Store the fields
        # year
        # round
        # bids_accepted
        # number_of_bids
        # hours_for_bid_round
        # system_price
        # demand
        # production
        # co2_tax
        # pv_production
        # gas_price
        # gas_production
        # coal_price
        # coal_production
        data = {
            "year": self.game_obj.year,
            "round": self.game_obj.bidRound,
            "bids_accepted": self.accepted_bids_count,
            "number_of_bids": len(self.bids),
            "hours_for_bid_round": self.hours_for_bidround,
            "system_price": self.system_price,
            "demand": self.demand,
            "production": self.total_pv_production + self.total_gas_production + self.total_coal_production,
            "co2_tax": self.co2_tax,
            "pv_production": self.total_pv_production,
            "gas_price": self.gas_price,
            "gas_production": self.total_gas_production,
            "coal_price": self.coal_price,
            "coal_production": self.total_coal_production
        }
        self.game_obj.host.host_statistics.create_host_round_results(data)

    def create_results(self, playerNumber, year, round):
        try:
            if globals.DEBUGGING:
                # Print demand
                print("Demand: {}-{}*demand".format(self.host.demand[0], self.host.demand[1]))
                print("bids list {}".format(self.bids))
            revenue, emissions = self.playerResults(playerNumber)
            if globals.DEBUGGING:
                print("Emissions: {}".format(emissions))
            cost = self.playerTotalCosts(playerNumber)
            tax = emissions * self.co2_tax
            own_plants = []
            own_actual_amounts = []
            own_bid_producer_surpluses = []
            own_bid_revenues = []
            own_bid_operational_costs = []
            own_bid_taxes = []
            own_bid_emissions = []
            own_bid_prices = []
            own_bid_amounts = []
            own_bid_playerNumbers = []
            other_bid_amounts = []
            other_bid_prices = []
            other_bid_playerNumbers = []
            own_bid_amount = 0
            own_sold_amount = 0
            for index, bid in enumerate(self.bids):
                if bid.playerNumber == playerNumber:
                    # Give detailed information about the players own bids
                    own_bid_amount += bid.amount
                    own_sold_amount += bid.sold_amount
                    own_plants.append(bid.plant.identifier)
                    own_bid_amounts.append(bid.amount)
                    own_bid_prices.append(bid.price)
                    own_bid_playerNumbers.append(playerNumber)
                    own_actual_amounts.append(bid.sold_amount)
                    own_bid_revenue = self.system_price * bid.sold_amount * self.hours_for_bidround  # (self.system_price - bid.price) * bid.sold_amount*self.hours_for_bidround
                    own_bid_operational_cost = self.bid_costs(playerNumber, bid)
                    own_bid_emission = self.bid_emissions(bid)
                    own_bid_tax = self.co2_tax * own_bid_emission
                    # Add bid information to lists
                    own_bid_producer_surpluses.append(own_bid_revenue - own_bid_operational_cost - own_bid_tax)
                    own_bid_revenues.append(own_bid_revenue)
                    own_bid_operational_costs.append(own_bid_operational_cost)
                    own_bid_taxes.append(own_bid_tax)
                    own_bid_emissions.append(own_bid_emission)
                else:
                    # Give limited information about the other players bids
                    other_bid_playerNumbers.append(bid.playerNumber)
                    other_bid_prices.append(bid.price)
                    other_bid_amounts.append(bid.sold_amount)
            # Add all lists to bids dictionary
            own_bids = dict(playerNumber=own_bid_playerNumbers, plant=own_plants, amount=own_bid_amounts, price=own_bid_prices, actual_amount=own_actual_amounts, producer_surplus=own_bid_producer_surpluses,
                            revenues=own_bid_revenues, operational_costs=own_bid_operational_costs,
                            taxes=own_bid_taxes, emissions=own_bid_emissions)
            other_bids = dict(playerNumber=other_bid_playerNumbers, price=other_bid_prices, amount=other_bid_amounts, actual_amount=other_bid_amounts)
            player_pv_production, player_gas_production, player_coal_production = self.player_source_production(
                playerNumber)
            data = {
                "year": year,
                "round": round,
                "demand": self.demand,
                "demand_curve_fixed": self.host.demand[0],
                "demand_curve_variable": self.host.demand[1],
                "system_price": self.system_price,
                "gas_price": self.gas_price,
                "coal_price": self.coal_price,
                "profits": revenue - cost - tax,
                "revenue": revenue,
                "cost": cost,
                "operational_cost": sum(own_bid_operational_costs),
                "administrative_cost": cost - sum(own_bid_operational_costs),
                "taxes": tax,
                "emissions": emissions,
                "own_bids": own_bids, # The player's bids
                "other_bids": other_bids, # the other player's bids
                "bid_amount": own_bid_amount,
                "sold_amount": own_sold_amount,
                "demand": self.demand,
                "gas_fuel": self.gas_fuel, # note that gas fuel is not equal to the gas production because of the efficiency
                "player_gas_production": player_gas_production,
                "coal_fuel": self.coal_fuel,
                "player_coal_production": player_coal_production,
                "player_pv_production": player_pv_production,
                "total_pv_production": self.total_pv_production,
                "total_gas_production": self.total_gas_production,
                "total_coal_production": self.total_coal_production
            }
            # Store statistics to host
            player = self.game_obj.host.getPlayer(playerNumber)
            player.statistics.create_round_results(data)
            player.statistics.profit_list.append(revenue-cost-tax)
            player.statistics.revenue_list.append(revenue)
            player.statistics.cost_list.append(cost)
            player.statistics.emission_list.append(emissions)
            return data
        except Exception as e:
            print("Exception raised in create_results()")
            print(e)

    def clear_values(self):
        """
        Clears values for next optimization.
        Constant values are not altered
        """
        self.total_pv_production = 0
        self.total_gas_production = 0
        self.total_coal_production = 0
        self.gas_fuel = 0
        self.coal_fuel = 0