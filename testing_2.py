import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import globals

from Resources.classes import Bid

# Working principle showing sequences on separate linse
"""
demand = [3000, 5]
demand_x_list = [0, demand[0]/demand[1]]
demand_y_list = [demand[0], 0]

fig, ax = plt.subplots()
fig.set_facecolor(globals.darkmode_light_dark_color)
other_sequence_list_amount = [[0, 100], [200, 200, 200, 300], [300, 300, 300, 400]]
other_sequence_list_price = [[800, 800], [1000, 1200, 1200, 1200], [1200, 1500, 1500, 1500]]
own_sequence_list_amount = [[100, 100, 100, 200]]
own_sequence_list_price = [[800, 1000, 1000, 1000]]
#ax.plot([0, 100], [800, 800], color="tab:blue") # ie. others
#ax.plot([100, 100, 100, 200], [800, 1000, 1000, 1000], color="tab:orange") # ie. player
#ax.plot([200, 200, 200, 300], [1000, 1200, 1200, 1200], color="tab:blue") # ie. others
#ax.plot([300, 300, 300, 400], [1200, 1500, 1500, 1500], color="tab:blue") # ie. others
ax.plot(demand_x_list, demand_y_list, color="tab:orange")
for index in range( len(other_sequence_list_amount) ):
    ax.plot(other_sequence_list_amount[index], other_sequence_list_price[index], color="tab:blue")
for index in range( len(own_sequence_list_amount)):
    ax.plot(own_sequence_list_amount[index], own_sequence_list_price[index], color="tab:green")
ax.set_facecolor(globals.darkmode_light_dark_color)
ax.spines['bottom'].set_color(globals.darkmode_color_white)
ax.spines['top'].set_color(globals.darkmode_light_dark_color)
ax.spines['right'].set_color(globals.darkmode_light_dark_color)
ax.spines['left'].set_color(globals.darkmode_color_white)
ax.tick_params(axis='x', colors=globals.darkmode_color_white)
ax.tick_params(axis='y', colors=globals.darkmode_color_white)
ax.set_ylim(0,3000)
plt.show()
"""
#

from Resources.AuxillaryMethods import format_number
class Test:
    def __init__(self, bids):
        self.bids = bids
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
                #  Skip all the equal bids to save computational time (for the first time in this for while for for method..)
                index = last_index + 1
            else:
                #  The next bid is not equal so go to the next bid
                index += 1
        return bids

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
"""
    def shareEqualBids(self):
        
        #  The bids are sorted so that equal bids are found easily
        bids = sorted(self.bids, key=lambda i: i.price)
        for bid in bids:
            print(bid.price)
        index = 0
        #  Go through all the bids
        for unused in bids:
            first_index = index
            last_index = index
            #  check if the bid has the same price as the next bid
            while self.equalNeighbour(bids, last_index):
                # Match so increment last_index
                last_index += 1
            #  Next bid has a different price. Check if last_index was incremented or not
            if last_index != first_index:
                # Multiple bids has the same price so share their amounts
                print("Found equal bid")
                amount_bid = 0
                amount_sold = 0
                # Calculate the accumulated amount between the bids
                for equals_index in range(first_index, last_index + 1):
                    print("Bid being shared has price {}".format(bid.price))
                    amount_sold += bids[equals_index].sold_amount
                    amount_bid += bids[equals_index].amount
                # Share the accumulated amount between the bids
                for equals_index in range(first_index, last_index + 1):
                    bids[equals_index].sold_amount = format_number(amount_sold * (bids[
                                                                                           equals_index].amount / amount_bid))  # The shared amount times the ratio the bid should get
                #  Skip all the equal bids to save computational time (for the first time in this for while for for method..)
                index = last_index + 1
            else:
                #  The next bid is not equal so go to the next bid
                index += 1
        return bids


    def equalNeighbour(self, bids, i):
        
        try:
            print("Checking neighbours: {} vs {}".format(bids[i+1].price, bids[i].price))
            if bids[i].price == bids[i + 1].price:
                print("This bid is equal")
                return True
        except:  # Exception is raised if i+1 is outside the indices of the list but this exception is excepted and should be ignored
            pass
        return False
"""

from Resources.classes import Bid, Host, Plant
from Resources.optimization import Optimization
from game_client import Game_client
pv = Plant("PV", "test", 1500, 10000, 17, 1000000, 10000000, 0, 0)
gas = Plant("Gas", "test2", 1000, 0, 30, 0, 0 ,0, 1)
bid0 = Bid(0, gas, 400, 200)
bid1 = Bid(1, gas, 400, 500)
bid2 = Bid(0, pv, 400, 200)
bid3 = Bid(1, gas, 500, 100)
bid4 = Bid(1, gas, 500, 100)

game_obj = Game_client("host")
game_obj.host.demand[0] = 10000
game_obj.host.demand[1] = 13.3
#bids = [bid0, bid1, bid2, bid3, bid4]
bids = [bid0, bid1]
bids = [bid0, bid1, bid2]
opt = Optimization(game_obj)
# add bids and demand (note that bids is sliced so that a copy of the bids is passed instead of the references
opt.add_data(bids[:], game_obj)
# Start the optimization
opt.start_optimization()
test = Test(bids)

fixed_bids = test.shareEqualBids()
print(opt.demand)
sum = 0
for i, bid in enumerate(fixed_bids):
    print("Bid {}: amount is {}/{} for price {}".format(i, bid.sold_amount, bid.amount, bid.price))
    sum += bid.sold_amount
print("Sum is: {}".format(sum))

some_string = "kickbutton_1"
test = some_string.replace("kickbutton_", "")
print(int(test))