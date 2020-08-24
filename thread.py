"""
Network has to run on separate threads so that the GUI is not blocked while network codes are run
Explaination: code is evaluated on a per line basis so if one line is held up the other code can not run. The GUI is
running on one line while the player does not exit the window so this meanas other code can not be run in the background.
Code run one a own thread is independant on the other thread so code can be run at the same time.
"""
from time import sleep
import datetime
import socket
from threading import Thread
import globals
from json import loads as json_loads
from Resources.classes import Plant, Bid, Simple_Player

#config.init()

class ServerNetwork(Thread):
    """
    Defines the host network class. It opens a connection on the port and allows connections. A thread is started per
    connection ie. player joining the game
    """
    def __init__(self,window):
        Thread.__init__(self)
        self.window=window

    def run(self):
        # Run a while loop until the socket can be bound to port
        while True:
            #
            sleep(0.2)
            # IP inputed by host
            if self.window.game_obj.getIp() != "":
                # Store IP
                TCP_IP = self.window.game_obj.getIp()
                TCP_PORT = globals.port
                # Create socket and set settings
                self.window.game_obj.host.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.window.game_obj.host.tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # Try to bind server to port
                try:
                    self.window.game_obj.host.tcpServer.bind((TCP_IP, TCP_PORT))
                    self.window.game_obj.host_status = "valid ip"
                    break
                # The IP is probably not valid so let host try again
                except:
                    self.window.game_obj.host_status = "invalid ip"
                    self.window.game_obj.ip = ""
        self.threads = []
        self.window.game_obj.host.tcpServer.listen(4)
        playerNumber = 0
        while self.window.game_obj.host.isJoinable():
            if globals.DEBUGGING:
                print("Waiting for players...")
            (conn, (ip, port)) = self.window.game_obj.host.tcpServer.accept()
            if self.window.game_obj.host.isJoinable():
                # Connection accepted, storing the connection object
                # Add player to list of players
                self.window.game_obj.host.addPlayer(playerNumber)
                self.window.game_obj.host.setConn(conn, playerNumber)
                # Starting a new thread for that connection
                newthread = ClientThread(ip, port, playerNumber, self.window)
                newthread.start()
                self.threads.append(newthread)
                self.onConnection()
                playerNumber += 1
        if globals.DEBUGGING:
            print("The game is not joinable anymore")
        for t in self.threads:
            t.join()

    def onConnection(self):
        """
        Host should sent initial information to the player like playernumber, settings for the game, and the starting plants
        """
        self.window.game_obj.host_status = "valid ip"
        # if globals.DEBUGGING:
        #     print("Player {} connected..".format(playerNumber))
        # data = self.window.createData("settings")
        # self.window.send(data, playerNumber)


    def stop(self):
        # How to kill threads?
        #  - Stop connections
        #  - Stop threads
        # Close all the connections
        for player in self.window.game_obj.host.players:
            player.conn.close()
            del player.conn
        # Stop the threads
        for thread in self.threads:
            del thread
            self.threads.clear()
        # Close the server thread
        self.window.game_obj.host.tcpServer.close()
        del self.window.game_obj.host.tcpServer

class ClientThread(Thread):
    """
    This class belongs to the HOST
    One of these client threads are started for each player joining the game.
    It acts as a thread to communicate with a specific player
    """
    def __init__(self,ip,port, playerNumber, window):
        Thread.__init__(self)
        self.window=window
        self.ip = ip
        self.port = port
        self.playerNumber = playerNumber

    def run(self):
        """
        Incoming packets for HOST
        """
        while True:
            ## Må dette også inn i en try?
            try:
                packet = self.window.game_obj.host.getConn(self.playerNumber).recv(globals.BUFFER_SIZE)
            except:
                # Lost connection to host
                break
            serialized_data = packet.decode()
            try:
                data = json_loads(serialized_data)
            except:
                # Unable to receive data from player
                break
            if globals.DEBUGGING:
                print("Packet {} was received from player {}".format(data["header"], self.playerNumber))
            # Do something with the package..
            if data["header"] == "info":
                name = data["name"]
                motto = data["motto"]
                occurrences = self.window.findNameCollisions(name)
                self.window.game_obj.host.used_player_names.append(name)
                if occurrences > 1:
                    name = name +"_"+str(occurrences)
                    self.window.game_obj.host.setPlayerData(self.playerNumber, name, motto)
                    data = self.window.createData("nameCollision", occurrences)
                    self.window.send(data, self.playerNumber)
                else:
                    self.window.game_obj.host.setPlayerData(self.playerNumber, name, motto)
                # Create simple player and add to list
                player = Simple_Player(name, motto, self.playerNumber)
                self.window.game_obj.simple_players.append(player)
            elif data["header"] == "status":
                status = data["status"]
                self.window.game_obj.host.setPlayerStatus(self.playerNumber, status)
                if self.window.stackedWidget_inner.currentIndex() == 1:
                    self.window.player_status_changed = True
                if self.window.game_obj.host.allPlayersReady():
                    if globals.DEBUGGING:
                        print("handle_all_players_ready() called because host received status packet")
                    self.window.handle_all_players_ready()
            elif data["header"] == "plantBought":
                self.window.game_obj.host_status = "update demand"
                plant = self.window.game_obj.getStorePlant(data["plantIdentifier"])
                index = self.window.game_obj.host.getPlayerIndex(self.playerNumber)
                self.window.game_obj.host.players[index].appendPlant(plant)
                if plant.source == "PV":
                    self.window.game_obj.host.total_capacity += plant.capacity*plant.efficiency
                else:
                    self.window.game_obj.host.total_capacity += plant.capacity
                self.window.game_obj.calculate_demand_slope()
                self.window.create_expected_demand()
                data = self.window.createData("demand")
                self.window.sendAll(data)
            elif data["header"] == "bids":
                playerBids = []
                for index in range(len(data["bids"])):
                    # Going through the data and creating a bid it adds to the list of bids.
                    identifier = data["bids"][index]["plantIdentifier"]
                    plant = self.window.game_obj.getStorePlant(identifier)
                    amount = data["bids"][index]["amount"]
                    price = data["bids"][index]["price"]
                    bid = Bid(self.playerNumber, plant, amount, price)
                    playerBids.append(bid)
                self.window.game_obj.host.appendBids(playerBids)
                self.window.game_obj.host.setPlayerStatus(self.playerNumber, "Ready")
                if self.window.game_obj.host.allPlayersReady():
                    if globals.DEBUGGING:
                        print("handle_all_players_ready() called because host received bids packet")
                    self.window.handle_all_players_ready()
                    #self.window.changePhase()
            elif data["header"] == "end game":
                self.window.game_obj.host.end_results[self.playerNumber] = data["profits"]
                self.window.game_obj.host.setPlayerStatus(self.playerNumber, "Ready")
                if self.window.game_obj.host.allPlayersReady():
                    self.window.endGame()
            elif data["header"] == "quit":
                self.window.removePlayer(data["playerNumber"], notify=False)
                break
        if globals.DEBUGGING:
            print("Player disconnected.")
        self.window.removePlayer(self.playerNumber, notify=False)


class ClientNetwork(Thread):
    def __init__(self, window):
        Thread.__init__(self)
        self.window=window

    def run(self):
        trying_to_connect = True
        while trying_to_connect:
            sleep(0.5)
            if self.window.game_obj.getIp() != "":
                # Found network
                break
        self.host = self.window.game_obj.getIp() #socket.gethostname() can also be used but not recommended for joining the correct lobby
        self.port = globals.port
        self.BUFFER_SIZE = globals.BUFFER_SIZE
        self.window.game_obj.player.tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if globals.DEBUGGING:
            print("Trying to connect to server..")
        try:
            self.window.game_obj.player.tcpClient.settimeout(3) # timeout used to check if connection worked.
            self.window.game_obj.player.tcpClient.connect((self.host, self.port))
            # Proceed to next page
            self.window.game_obj.host_status = "connected to host"
            #self.window.stackedWidget.setCurrentIndex(2)
        except socket.timeout: #Exception as e:
            if globals.DEBUGGING:
                print("Unable to connect to host..")
            self.window.game_obj.ip = ""
            # Set some flag for warningCountdown
            self.window.connection_failed_flag = True
            self.run()
        except Exception as e:
            if globals.DEBUGGING:
                print("Connection was refused by the host. The server might not be running properly yet. Please retry the connection")
            self.window.game_obj.ip = ""
            # Set some flag for warningCountdown
            self.window.connection_refused_flag = True
            self.run()
        self.window.game_obj.player.tcpClient.settimeout(None) # timeout removed in order to keep connection alive
        # Infinite loop waiting for packets from server
        while True:
            """
            Incoming packets for PLAYER
            """
            # Packet recieved is just a bytestream
            packet = self.window.game_obj.player.tcpClient.recv(self.BUFFER_SIZE)
            # Convert the packet to a string
            serialized_data = packet.decode()
            # Convert string to dictionary
            try:
                data = json_loads(serialized_data)
            except:
                # Disconnected
                break
            if globals.DEBUGGING:
                print("Packet {} was received from host".format(data["header"]))
            if data["header"] == "playerNumber":
                self.window.game_obj.player.setPlayerNumber(data["playerNumber"])
            elif data["header"] == "settings":
                # set flag
                self.window.settings_received_flag = True
                self.window.game_obj.setYears(data["years"])
                self.window.game_obj.setBidRounds(data["bidRounds"])
                self.window.game_obj.player.setMoney(data["initialMoney"])
                self.window.game_obj.initialMoney = data["initialMoney"]
                self.window.game_obj.setStrategyTime(data["stratTime"])
                self.window.game_obj.setBidTime(data["bidTime"])
                self.window.game_obj.years = data["years"]
                self.window.game_obj.bidRounds = data["bidRounds"]
                self.window.game_obj.startPlant = data["startPlant"]
                self.window.game_obj.strategyTime= data["stratTime"]
                self.window.game_obj.bidTime = data["bidTime"]
                # Open some dialog/window showing game settings?
                # Set market data
                self.window.game_obj.gas_cost_fixed = data["gas_fixed_cost"]
                self.window.game_obj.gas_cost_variable = data["gas_variable_cost"]
                self.window.game_obj.coal_cost_fixed = data["coal_fixed_cost"]
                self.window.game_obj.coal_cost_variable = data["coal_variable_cost"]
                self.window.game_obj.co2_tax = data["co2_tax"]
            elif data["header"] == "players":
                # Initialize empty list of players
                players = []
                for index in range(0, len(data["name"])):
                    # Create simple player object
                    player = Simple_Player(data["name"][index], data["motto"][index], data["playerNumber"][index])
                    # Add player to list
                    players.append(player)
                # Overwrite existing list
                self.window.game_obj.simple_players = players
            elif data["header"] == "plants":
                for index in range(0, len(data["name"])):
                    source = data["source"][index]
                    name = data["name"][index]
                    capacity = data["capacity"][index]
                    investmentCost = data["investmentCost"][index]
                    annualCost = data["annualCost"][index]
                    efficiency = data["efficiency"][index]
                    variableCost = data["variableCost"][index]
                    emissions = data["emissions"][index]
                    identifier = data["identifier"][index]
                    plant = Plant(source, name, capacity, investmentCost, efficiency, annualCost, variableCost, emissions, identifier)
                    self.window.game_obj.addStorePlant(plant)
                    # Open some dialog message to player: "New plants added to the store"
            elif data["header"] == "demand":
                self.window.game_obj.expected_demand_fixed = data["demand"][0]
                self.window.game_obj.expected_demand_variable = data["demand"][1]
            elif data["header"] == "endTime":
                # create a new datetime object
                endTime = datetime
                # add data from packet
                endTime.year = data["year"]
                endTime.month = data["month"]
                endTime.day = data["day"]
                endTime.hour = data["hour"]
                endTime.minute = data["minute"]
                endTime.second = data["second"]
                # store endTime in game_obj
                self.window.game_obj.endTime = endTime
                if self.window.game_obj.year == 1 and self.window.game_obj.phase == "Strategy phase":
                    self.window.game_obj.host_status = "start game"
                    #self.window.stackedWidget.setCurrentIndex(4)
                elif self.window.game_obj.phase != "End game":
                    # Set new round ready flag
                    self.window.game_obj.host_status = "next phase ready"
            elif data["header"] == "status":
                if data["status"] == "clearing market":
                    if globals.DEBUGGING:
                        print("Clearing market status flag added")
                    self.window.game_obj.host_status = "clearing market"
                else: pass
            elif data["header"] == "results":
                # do something
                pass
            elif data["header"] == "start bid phase":
                # Set countdown stop flag
                self.window.countdown_stop_flag = True
                # Set host status flag
                self.window.game_obj.host_status = data["header"]
                if globals.DEBUGGING:
                    print("From host: host_status set to {}".format(data["header"]))
                self.window.game_obj.transition()
            elif data["header"] == "start strategy phase":
                # Stop countdown
                self.window.countdown_stop_flag = True
                # Set host status flag
                self.window.game_obj.host_status = data["header"]
                # Add new plants
                for index in range(0, len(data["plants"]["name"])):
                    source = data["plants"]["source"][index]
                    name = data["plants"]["name"][index]
                    capacity = data["plants"]["capacity"][index]
                    investmentCost = data["plants"]["investmentCost"][index]
                    annualCost = data["plants"]["annualCost"][index]
                    efficiency = data["plants"]["efficiency"][index]
                    variableCost = data["plants"]["variableCost"][index]
                    emissions = data["plants"]["emissions"][index]
                    identifier = data["plants"]["identifier"][index]
                    plant = Plant(source, name, capacity, investmentCost, efficiency, annualCost, variableCost, emissions, identifier)
                    self.window.game_obj.addStorePlant(plant)
                    # Open some dialog message to player: "New plants added to the store"
                # Set correct information for new round
                self.window.game_obj.transition()
            elif data["header"] == "new bid round":
                # stop countdown
                self.window.countdown_stop_flag = True
                # Set host status flag
                self.window.game_obj.host_status = data["header"]
                self.window.game_obj.transition()
            elif data["header"] == "end game":
                # Set host status flag
                self.window.game_obj.host_status = data["header"]
            elif data["header"] == "kick":
                self.window.game_obj.player.tcpClient.close()
                self.window.game_obj.host_status = "kicked"
                #self.window.stackedWidget.setCurrentIndex(9)
            elif data["header"] == "nameCollision":
                self.window.game_obj.player.firm_name += "_" + str(data["index"])
            elif data["header"] == "optimization":
                data.pop("header")
                # save round results
                self.window.game_obj.player.statistics.profits += data["profits"]
                self.window.game_obj.player.money += data["profits"]
                self.window.game_obj.player.statistics.revenue += data["revenue"]
                self.window.game_obj.player.statistics.cost += data["cost"]
                self.window.game_obj.player.statistics.taxes += data["taxes"]
                self.window.game_obj.player.statistics.emissions += data["emissions"]
                # The results contains the actual amounts of the bid, so the player should append it's bid amounts
                # to the bid so that the results can show what was bid, and what was actually sold.
                # Add the round result to the players statistics
                self.window.game_obj.player.statistics.create_round_results(data)
                # Delete the previous bids
                #self.window.game_obj.player.bids.clear() # keep the bids so that they can be changed in the next bid round and later
                self.window.game_obj.host_status = "market cleared"
            elif data["header"] == "placement":
                index = data["result_dict"]["players"].index(self.window.game_obj.player.firm_name)
                self.window.game_obj.player.statistics.placement = data["placements"][index]
                # Treat results
                self.window.game_obj.player.statistics.leaderboard = data["result_dict"]
                self.window.game_obj.host_status = "placement ready"
                #self.window.transition_button_next.setEnabled(True)
            else:
                if globals.DEBUGGING:
                    print("Message header type: {} is not recognized..".format(data["header"]))
                else: pass
        if globals.DEBUGGING:
            print("The host has disconnected.")
        self.stop()
        # Show some page informing the player about what happened

    def stop(self):
        try:
            self.window.game_obj.player.tcpClient.close()
            del self.window.game_obj.player.tcpClient
        except: pass