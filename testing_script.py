import random

import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from PyQt5 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

"""
string = "hei"
index = 0
for char in string:
    type(char)
    print(char)
    print(index)
    index = index +1
"""

"""
someInt = 5
print("name{}".format(someInt))
"""

"""
list = []
list.append("test")
print(list[0])
"""
"""
list = []
print(None == list)
"""
"""
from Resources.classes import Player, Plant
from game_client import Game_client

plant = Plant("PV", "NA", "Premadez", 500, 10000, 0.3, 10000, 0, 0)
game_obj = Game_client(10000, plant)
plant.setName("FUCKER")
game_obj.removePlant(0)
print(game_obj.getStorePlants())
"""
"""
try:
    x
except:
    print("someList does not exist")
print("It ran through..")
"""
"""
header = "settings"
dict = {
    "years": 3,
    "bidRounds": 2,
    "intMoney": 100000,
    "startPlant": "PV"
}

data = [header, dict]
# data[0] is the header of the data
# data[1] is the dictionary data
if header == "settings":
    years = data[1]["years"]
    bidRounds = data[1]["bidRounds"]
    intMoney = data[1]["intMoney"]
    startPlant = data[1]["startPlant"]

print(years)
print(bidRounds)
print(intMoney)
print(startPlant)
"""
"""
import json


dict = {
    "header": "plants",
    "plants": 3,
    "Name": ["Basic PV", "Basic coal", "Basic gas"]
}

str = json.dumps(dict)
data = json.loads(str)
for plant in range(0, len(data["Name"])):
    print(data["Name"][plant])
"""
"""
WIP timer. Format is not ideal but it is quite promising for the future. Using local time is a valid approach
because it means time can be more or less synchronized. It does however mean that some users can cheat by changing
the time on their computer but that is not likely. The host should be able to force end a phase. 
"""
"""
import time

info = time.localtime()
# Get time information
hour = info[3]
min = info[4]
sec = info[5]
print(hour, min, sec)
# convert to seconds.
sec += min*60
sec += min*3600

timer = 5 # sec
end_sec = sec + timer
print(end_sec)

while end_sec > sec:
    time.sleep(1)
    sec +=1
    print(sec)
print("Finished")

def end_time(minutes):
    info = time.localtime()
    hour = info[3]
    min = info[4]
    sec = info[5]
    # and so on
"""
"""
# This proves that both lists and dicts can be checked with True/False statements
list = []
list.append(False)

dict = {
    "some key": "some val"
}

if list:
    print("List is True")

if dict:
    print("Dict is True")

list.clear()

if list:
    print("List is True")
else:
    print("List is False")

dict.clear()

if dict:
    print("Dict is True")
else:
    print("Dict is False")
"""
"""
list = []
list.append("test")
list.append("test2")
list.append("test3")
list.append("test4")
list.append("test5")
list.append("test6")
list.append("test7")
list.append("test8")
list.append("test9")
list.append("test10")

index = list.index("test6")
print(index)
"""
"""


bids = []
bid = {
    "plant": 2,
    "amount": 200,
    "price": 500
}
bids.append(bid)
bid2 = {
    "plant": 3,
    "amount": 500,
    "price": 200
}
bids.append(bid2)
bid3 = {
    "plant": 3,
    "amount": 100,
    "price": 50
}
bids.append(bid3)

data = {
    "player": 3,
    "bids" : bids
}

"""
"""
list = []

dict = {
    "playerNumber": 1,
    "bid": "some bid"
}
list.append(dict)

dict = {
    "playerNumber": 2,
    "bid": "another bid"
}
list.append(dict)

print(list[0]["bid"])
"""
"""
bids = []
playerBids = {
    "playerNumber": 0,
    "bids": []
}

bids.append(playerBids)
"""
"""
from Resources.classes import Player
from game_client import Game_client

game_obj = Game_client("host")


class someClass:
    def __init__(self, host):
        self.host = host
    def doSomething(self):
        # Lagres utenfor dvs. optimization kan ta inn objektet og modifisere den.
        self.host.joinable = False

someClass = someClass(game_obj.host)
someClass.doSomething()
#doSomething(game_obj.host)
print(game_obj.host.joinable)
"""
"""
print(list(range(3)))
"""
"""
from pyomo import environ as pyo
from pyomo.opt import SolverFactory


bids_set = ["Bid 1", "Bid 2", "Bid 3"]
bids_max_amount = [200, 50, 100]
bids_price = [500, 400, 300]
demand_fixed = 400
demand_variable = 5

model = pyo.ConcreteModel()

# Declare set
model.blocks = pyo.Set(ordered=True, initialize=bids_set)  # Each block is a bid

# Parameters
model.demand_fixed = pyo.Param(initialize=demand_fixed)
model.demand_variable = pyo.Param(initialize=demand_variable)
model.bid_price = pyo.Param(model.blocks, initialize=bids_price,
                            mutable=True)
model.bid_maxAmount = pyo.Param(model.blocks, initialize=bids_max_amount,
                                mutable=True)

# variables
model.bid_amount = pyo.Var(model.blocks, within=pyo.NonNegativeReals)  # Treated as var because a bid does not have to be fully used
model.demand = pyo.Var(within=pyo.NonNegativeReals)  # p = a-b*D, D - demand
model.system_price = pyo.Var(within=pyo.NonNegativeReals)

# Objective function
def objective_function(model):

    return model.demand_fixed * model.demand - model.demand_variable * model.demand * model.demand - sum(
        model.bid_price[block] * model.bid_amount[block] for block in model.blocks)


model.obj = pyo.Objective(rule=objective_function, sense=pyo.maximize)

# Constraints

# supply == demand
def powerEquality(model):
    return sum(model.bid_amount[block] for block in model.blocks) == model.demand

model.constraint_powerBalance = pyo.Constraint(rule=powerEquality)

# Maximum production for each bid (cannot be higher than bid amount)
def maxProduction(model, block):
    return model.bid_amount[block] <= model.bid_maxAmount[block]

model.constraint_maxProd = pyo.Constraint(model.blocks, rule=maxProduction)




# Maximum demand
def maxDemand(model):
    return model.demand <= model.demand_fixed / model.demand_variable  # if p = a-bx then p=0 gives x = a/b for maximum demand


model.constraint_maxDemand = pyo.Constraint(model.blocks, rule=maxDemand)





# Set the solver for this
#opt = SolverFactory("glpk")
opt         = SolverFactory('gurobi',solver_io="python")


# Enable dual variable reading -> important for dual values of results
model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)

# Solve the problem
results = opt.solve(model, load_solutions=True)

# Write result on performance
results.write(num=1)
"""
"""
dict = {
    "first": 1,
    "second": 2
}

print(dict)

dict.pop("first")
print(dict)
"""
"""
print("Starting")

from Resources.classes import Bid

bid = Bid(0, None, 50, 150)
bid2 = Bid(0, None, 100, 150)
bid3 = Bid(0, None, 150, 150)
bid4 = Bid(0, None, 200, 250)
bids = [bid, bid2, bid3, bid4]

newlist = sorted(bids, key=lambda i: i.price)
print(newlist)
for bid in newlist:
    print(bid.price)

def shareEqualBids(bids):
    bids = sorted(bids, key=lambda i: i.price)
    index = 0
    for bid in bids:
        print("index {}".format(index))
        # check if the bid has the same price as the next bid
        first_index = index
        last_index = index
        while equalNeighbour(bids, last_index):
            print("Found match between {} and {}".format(last_index, last_index+1))
            last_index += 1
        print("last index is now {}. First index is {}".format(last_index, first_index))
        if last_index != first_index:
            equals = len(range(first_index, last_index+1))
            amount = 0
            for equals_index in range(first_index, last_index+1):
                amount += bids[equals_index].amount
            shared_amount = amount/equals
            for equals_index in range(first_index, last_index+1):
                bids[equals_index].amount = shared_amount
            print("Finished looking through index: next index is {}".format(last_index+1))
            index = last_index+1
        else: index += 1
    return bids


def equalNeighbour(bids, i):
    try:
        if bids[i].price == bids[i + 1].price:
            return True
    except:
        pass
    return False

newbids = shareEqualBids(bids)
print(newbids)
for bid in newbids:
    print(bid.amount)

"""
"""
import pandas

#dataFrame = pandas.read_excel("Resources/data.xlsx")
colName = "Type"
filter = "Huge"
df_map = pandas.read_excel("Resources/data.xlsx", sheet_name=None)
print(df_map)
filtered = df_map["plants"].loc[df_map["plants"][colName] == filter]
print(filtered)
"""
"""
from Resources.classes import Database

db = Database("Resources/data.xlsx")
plants = db.get_plants("Type", "Initial", 0)

db.input_data()
"""
"""
from Resources.classes import Bid, Plant, Player
from Resources.optimization import Optimization
from game_client import Game_client

plant = Plant("Gas", "Testplant", 500, 10000, 0.7, 1000, 1, 10, 0)
bid = Bid(0, plant, 100, 700)
bid2 = Bid(0, plant, 75, 700)
bid3 = Bid(0, plant, 25, 700)
bid4 = Bid(0, plant, 60, 900)
bids = [bid, bid2, bid3, bid4]
game_obj = Game_client("host")
player = Player(0)
game_obj.host.addPlayer(0)
game_obj.host.players[0].appendPlant(plant)
game_obj.host.appendBids(bids)

opt = Optimization(bids, game_obj)
opt.start_optimization()
results = opt.create_results(0, 1, 1)


#opt.start_optimization()
#results = opt.create_results(0, 1, 1)
"""
"""
from Resources.classes import Player
def removePlayer(players, playerNumber):
    for index, player in enumerate(players):
        if player.playerNumber == playerNumber:
            players.pop(index)
    return players

p1 = Player(1)
p1.firm_name = "SIEMENS"
p2 = Player(2)
p2.firm_name = "ABB"
p3 = Player(3)
p3.firm_name = "EQUINOR"

players = [p1, p2, p3]

for p in players:
    print(p.firm_name)

removePlayer(players, 2)
for p in players:
    print(p.firm_name)
"""

"""
# Noe svada til kraftsystemer

import pandas

lines_df = pandas.read_excel("input_file.exl", sheet_name="lines")
nodes_df = pandas.read_excel("input_file.exl", sheet_name="nodes")

class Bus():
    def __init__(self, bus_type, number):
        self.number = number
        self.bus_class = None
        if bus_type == "PV":
            self.bus_class = PV()
        elif bus_type == "PQ":
            self.bus_class = PQ()
        elif bus_type == "Slack":
            self.bus_class = Slack()

class PV():
    def __init(self, P, V):
        self.P = P
        self.V = V

class PQ():
    def __int__(self, P, Q):
        self.P = P
        self.Q = Q
class Slack():
    def __int__(self, V, delta):
        self.V = V
        self.delta = delta


class Node():
    def __init__(self, from_node, to_node, R, X):
        self.from_node = from_node
        self.to_node = to_node
        self.R = R
        self.X = X

    def some_function(self):
        pass

"""
"""
import time
from Resources.AuxillaryMethods import getSec, get_sec, endTime
#from datetime import datetime, timedelta
import datetime
from datetime import timedelta
def dummy_endTime(timeString):
    m, s = timeString.split(":")
    current_time = datetime.datetime.now()
    end_time = current_time + datetime.timedelta(minutes=int(m), seconds=int(s))
    #return "{}:{}".format(end_time.minute, end_time.second)
    return end_time

def dummy_endTime_to_seconds(end_time):
    now = datetime.datetime.now()
    seconds = (timedelta(hours=24) - (now - now.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second))).total_seconds() % (24 * 3600)
    return seconds

# 2 mm:ss to time
tidsgrense = "55:00"
end_time = dummy_endTime(tidsgrense)
print(end_time)
dummy_time = datetime
dummy_time.hour = end_time.hour
print(dummy_time.hour)
# 3 time to seconds
sec = dummy_endTime_to_seconds(end_time)
print(sec)

# 4 seconds to mm:ss
remain = time.strftime("%M:%S", time.gmtime(sec))
print(remain)
"""

"""
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import globals

from Resources.classes import Bid

def create_plot_lists(bids):
    amount_list = []
    price_list = []
    accumulated_amount = 0
    for bid in bids:
        amount_list.extend([accumulated_amount, accumulated_amount + bid.amount])
        price_list.extend([bid.price, bid.price])
        accumulated_amount += bid.amount
    return amount_list, price_list

demand = [3000, 5]
demand_x_list = [0, demand[0]/demand[1]]
demand_y_list = [demand[0], 0]

bid0 = Bid(0, None, 100, 500)
bid1 = Bid(0, None, 80, 1550)
bid2 = Bid(0, None, 200, 1700)
bid3 = Bid(0, None, 100, 1810)


bids = [bid0, bid1, bid2, bid3]

fig, ax = plt.subplots()
fig.set_facecolor(globals.darkmode_light_dark_color)
amount_list, price_list = create_plot_lists(bids)
ax.plot(amount_list, price_list, demand_x_list, demand_y_list)
ax.set_facecolor(globals.darkmode_light_dark_color)
ax.spines['bottom'].set_color(globals.darkmode_color_white)
ax.spines['top'].set_color(globals.darkmode_light_dark_color)
ax.spines['right'].set_color(globals.darkmode_light_dark_color)
ax.spines['left'].set_color(globals.darkmode_color_white)
ax.tick_params(axis='x', colors="red")
ax.tick_params(axis='y', colors=globals.darkmode_color_white)
plt.show()

"""
"""
from PyQt5 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


import random

import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

import globals

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QVBoxLayout(self._main)
        self.plot_info_graphs_handle()


    def plot_info_graphs_handle(self):
        # rounds_list = []
        # Create the canvas
        # self.static_canvas_info = FigureCanvas(Figure(figsize=(5, 3)))
        # self.addToolBar(NavigationToolbar(self.static_canvas_info, self))
        # Add to correct layout based on current index
        # rounds_list = ["year 1 b1", "year 1 b2", "year 2 b1", "year 2 b2"]
        # profits_list = [100, 200, 500, 300]
        # self.layout.addWidget(self.static_canvas_info)
        # self._static_ax_info = self.static_canvas_info.figure.subplots()
        # self._static_ax_info.bar(rounds_list, profits_list, width=0.8)
        # self._static_ax_info.set_xlabel("Rounds")
        # self._static_ax_info.set_ylabel("MNOK")

        # Create the canvas
        self.static_canvas_sources = FigureCanvas(Figure(figsize=(5, 3)))
        self.addToolBar(NavigationToolbar(self.static_canvas_sources, self))
        # Add canvas to the layout
        self.layout.addWidget(self.static_canvas_sources)
        self._static_ax_sources = self.static_canvas_sources.figure.subplots()
        self.static_canvas_sources.figure.set_facecolor(globals.darkmode_background_color)
        market_shares = [15, 35, 50]
        self._static_ax_sources.pie(market_shares, explode=[0.05,0.05,0.05], labels=["PV", "Gas", "Coal"], autopct="%1.1f%%", shadow=True, startangle=180)
        self._static_ax_sources.axis("equal")

if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    toolbar = app.findChild(QtWidgets.QToolBar)
    toolbar.setVisible(False)
    app.show()
    qapp.exec_()
"""

import globals
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QVBoxLayout(self._main)
        self.plot_info_graphs_handle()


    def plot_info_graphs_handle(self):
        from Resources.classes import Host, Statistics
        profits_list = [200, 1000, 300, 500, 100]
        firm_name_list = ["111", "222", "333", "444", "555"]
        # Create the canvas
        self.static_canvas_sources = FigureCanvas(Figure(figsize=(5, 3)))
        self.addToolBar(NavigationToolbar(self.static_canvas_sources, self))
        # Add canvas to the layout
        self.layout.addWidget(self.static_canvas_sources)
        self._static_ax_sources = self.static_canvas_sources.figure.subplots()
        barlist = self._static_ax_sources.bar(firm_name_list, profits_list)
        for i, bar in enumerate(barlist):
            bar.set_color(globals.standard_color_scheme[i])
if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    toolbar = app.findChild(QtWidgets.QToolBar)
    toolbar.setVisible(False)
    app.show()
    qapp.exec_()
