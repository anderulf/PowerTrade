from time import localtime
from datetime import timedelta
from datetime import datetime
from Resources.classes import Bid

def isNumber(input):
    """
    Evaluates string type inputs
    """
    try:
        float(input)
        return True
    except:
        return False

def isPositive(input):
    """
    Evaluates string type inputs
    """
    try:
        float(input)
        return float(input)>= 0
    except:
        return False

def get_sec(time_str):
    m, s = time_str.split(':')
    return int(m) * 60 + int(s)

def endTime(timeString):
    # Returns a endtime in mm:ss from a timeString in mm:ss using the local time.
    m, s = timeString.split(":")
    current_time = datetime.now()
    end_time = current_time + timedelta(minutes=int(m), seconds=int(s))
    return end_time

def endTime_to_seconds(end_time):
    now = datetime.now()
    seconds = (timedelta(hours=24) - (now - now.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second))).total_seconds() % (24 * 3600)
    return seconds

def getSec(endTime):
    """
    Takes a end time in format str(mm:ss) and returns the remaining time in secondsseconds
    """
    end_m, end_s = endTime.split(":")
    local_m = localtime()[4]
    local_s = localtime()[5]
    m = int(end_m) - local_m
    if m < 0:
        m = 60 - m
    s = int(end_s) - local_s
    if s < 0:
        s += 60
        m -=1
    return m*60+s

def format_number(floaty):
    return float("{0:.1f}".format(floaty))

def number_to_string(number, postfix=None):
    """
    This number to string method is less efficient than the locale version but locale is not guaranteed to be
    supported by all systems to this one should work better.
    It takes a number, convertes it to a string with one decimal. Separates the integer part and the decimal part
    and adds seperators

    The postfix shows the unit of the number

    NOTE:
        the method handles units automatically so the developer should not worry about this
        Basic units for the game are:
        MW, MWh, kg CO2eq, NOK, hours
        Thus TON is given by dividing kg by 1000, GWh is given by dividing MWh by 1000, MNOK is given by dividing NOK by 1 000 000
    """
    # Alter the number based on the postfix
    if postfix == "%":
        number *= 100 # to percent
    elif postfix == "MNOK" or postfix == "MNOK/year":
        number /= 1000000 # to MNOK
    elif postfix == "TON CO<sub>2</sub>eq" or postfix == "GWh":
        number /= 1000 # to TON or GWh
    # Extract data from the number
    number_string = "{0:.1f}".format(number)
    int, dec = number_string.split(".")
    final_int = ""
    index = 0
    for num in int[::-1]:
        final_int = num + final_int
        index += 1
        if index == 3:
            final_int = " " + final_int
            index = 0
    output_string =  final_int + "." + dec
    #if output_string == "0.0":
    #    return "-"
    if postfix == None:
        return output_string
    elif postfix == "%":
        return output_string + postfix
    else:
        return output_string + " " + postfix

def create_plot_lists(bids, playerNumber):
    """
    Input a list of bids and decouple it into amounts and prices for all segments
    in the plot

    returns four lists, two lists for amounts and prices for own bids, and two lists for amounts and prices for other bids
    """
    if not bids:
        return [], [], [], []
    # sort by price first using lambda operator
    bids.sort(key=lambda bid: bid.price)
    # Initialize lists
    # Because own bids are located at random positions inbetween other bids, the other bids needs to be separated into smaller sequences
    own_sequence_list_amount = []
    own_sequence_list_price = []
    other_sequence_list_amount = []
    other_sequence_list_price = []
    # Set initial values
    accumulated_amount = 0
    own_sequence_list_index = 0
    other_sequence_list_index = 0
    bids_index = 0
    last_price = bids[0].price # set last bid price to the price of the first bid
    # Add first element to sequence lists (they are lists of lists). So: own_sequences_list_amount[0] should exist
    own_sequence_list_amount.append([])
    own_sequence_list_price.append([])
    other_sequence_list_amount.append([])
    other_sequence_list_price.append([])
    # Initialize boolean player/other control variable
    if bids[0].playerNumber == playerNumber:
        last_bid_own_bid = True
    else:
        last_bid_own_bid = False
    # Go through all the bids
    for bid in bids:
        # Determine if bid is set by player
        if bid.playerNumber == playerNumber:
            # Check if the last bid belonged to other players
            if not last_bid_own_bid: # if last bid belong to other players
                # Increase the index to be filled by the other_sequence_list
                own_sequence_list_index += 1 # start new sequence
                # Add new empty list to sequence list
                own_sequence_list_amount.append([])
                own_sequence_list_price.append([])
            # Add connecting line from last bid to new bid (and add to players list of for correct coloring)
            own_sequence_list_amount[own_sequence_list_index].extend([accumulated_amount, accumulated_amount])
            own_sequence_list_price[own_sequence_list_index].extend([last_price, bid.price])
            # Add line for current bid
            own_sequence_list_amount[own_sequence_list_index].extend([accumulated_amount, accumulated_amount + bid.amount])
            own_sequence_list_price[own_sequence_list_index].extend([bid.price, bid.price]) # horizontal line
            last_bid_own_bid = True
        # Or bid is set by other players
        else:
            if last_bid_own_bid: # if last bid belonged to player
                # Increase the index to be filled by the other_sequence_list
                other_sequence_list_index += 1  # start new sequence
                # Add new empty list to sequence list
                other_sequence_list_amount.append([])
                other_sequence_list_price.append([])
            # Add connecting line from last bid to new bid (and add to players list of for correct coloring)
            other_sequence_list_amount[other_sequence_list_index].extend([accumulated_amount, accumulated_amount])
            other_sequence_list_price[other_sequence_list_index].extend([last_price, bid.price])
            # Add line for current bid
            other_sequence_list_amount[other_sequence_list_index].extend([accumulated_amount, accumulated_amount + bid.amount])
            other_sequence_list_price[other_sequence_list_index].extend([bid.price, bid.price])  # horizontal line
            last_bid_own_bid = False
        # Do for all bids
        accumulated_amount += bid.amount
        last_price = bid.price
        bids_index += 1
    # Remove first element if it is empty
    if not other_sequence_list_amount[0]:
        other_sequence_list_amount.pop(0)
        other_sequence_list_price.pop(0)
    if not own_sequence_list_amount[0]:
        own_sequence_list_amount.pop(0)
        own_sequence_list_price.pop(0)
    return own_sequence_list_amount, own_sequence_list_price, other_sequence_list_amount, other_sequence_list_price

def dict_bids_to_bids_object_list(dict_bids_list):
    bids = []
    for index in range(len(dict_bids_list["amount"])):
        bid = Bid(dict_bids_list["playerNumber"][index], None, dict_bids_list["amount"][index], dict_bids_list["price"][index])
        bids.append(bid)
    return bids