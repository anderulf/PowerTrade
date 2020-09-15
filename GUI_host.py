
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QCoreApplication, QTimer
from Main_Window_Host import Ui_MainWindow_Host
from dialog_newPlant import Ui_dialog_newPlant
from dialog_setDemand import Ui_dialog_setDemand
from Resources.optimization import Optimization
from Resources.classes import Plant
from Resources.AuxillaryMethods import endTime, endTime_to_seconds, number_to_string, create_plot_lists
from game_client import Game_client
import json
import time
from thread import ServerNetwork
from matplotlib.backends.qt_compat import is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import random

# for testing purposes
from Resources.classes import Player


import globals


# The functions of the window classes are implemented here (do not edit Main_Window_Player)
class startWindow_host(QtWidgets.QMainWindow, Ui_MainWindow_Host):
    """
    This is the main class. It acts as a platform for the other game mechanics ie. main window and game components
    All methods that change the GUI must be implemented here
    """
    def __init__(self, *args, **kwargs):
        super(startWindow_host, self).__init__(*args, **kwargs)
        # Initialize the game object (containing all relevant data for the game
        self.game_obj = Game_client("host")
        # Initialize the optimization object running later
        self.opt = Optimization(self.game_obj)

    def setUpSlots(self):
        self.create_button_next.clicked.connect(self.create_handle_button_next)

        #self.settings_button_start.clicked.connect(self.settings_handle_button_start)
        #test
        self.settings_button_start.clicked.connect(self.settings_handle_button_create)
        self.button_main.clicked.connect(self.handle_button_main)
        self.button_players.clicked.connect(self.handle_button_players)
        self.button_statistics.clicked.connect(self.handle_button_statistics)
        self.host_main_quitButton.clicked.connect(QCoreApplication.instance().quit)

        self.lobby_button_start.clicked.connect(self.lobby_handle_button_start)

        self.main_button_add_plant.clicked.connect(self.main_handle_button_add_next_plant)
        self.main_button_create_plant.clicked.connect(self.main_handle_button_newPlant)
        self.main_button_set_demand.clicked.connect(self.main_handle_button_set_demand)

        self.statistics_combobox_players.currentIndexChanged.connect(self.statistics_handle_comboBox)
        self.statistics_performance_tabWidget.currentChanged.connect(self.plot_statistics_performance_graphs)
        self.statistics_comboBox_round_results.currentIndexChanged.connect(self.statistics_round_results_handle_comboBox)
        self.statistics_tabWidget_general_plots.currentChanged.connect(self.statistics_round_results_handle_general_plots)

        self.transition_button_next.clicked.connect(self.transition_handle_button_next)

        self.optimize_button_optimize.clicked.connect(self.initialize_optimization)

    def setUpValidators(self):
        """
        The validators are used to limit input data into certain fields
        """
        # Create validator for IP-address
        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"                                                           # ipRange is: 0 to 199 and 200 to 249 and 250 to 255 ie. 0 to 255
        ip_regex = QtCore.QRegExp(
            "^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")                                  # Regular expression defined as xxx.xxx.xxx.xxx
        ip_validator = QtGui.QRegExpValidator(ip_regex)                                                                 # Creating a validator from the regular expression
        self.create_lineEdit_hostIp.setValidator(ip_validator)
        # integer regex (for settings)
        int_regex = QtCore.QRegExp("[1234567890]+")  # Integers only (might be a easier way to do this
        int_validator = QtGui.QRegExpValidator(int_regex)
        # float regex for numbers above zero (used in dialog windows)
        float_positive_regex = QtCore.QRegExp("^[0-9]+(?:\.[0-9]+)?$")
        self.float_positive_validator = QtGui.QRegExpValidator(float_positive_regex)
        # float regex for percentages ie. between 0 and 100
        float_positive_percentage_regex = QtCore.QRegExp("^([0-9](?:\.[0-9]+)?|[1-9][0-9](?:\.[0-9]+)?|100(?:\.[0]+)?)$") # Accepts only 0.0 to 99.99999.. and 100.0 or integers. No negative numbers.
        self.float_positive_percentage_valdidator = QtGui.QRegExpValidator(float_positive_percentage_regex)
        # Enable valikdators
        self.settings_lineEdit_rounds.setValidator(int_validator)
        self.settings_lineEdit_bidRounds.setValidator(int_validator)
        self.settings_lineEdit_initialMoney.setValidator(int_validator)

    def setUpMisc(self):
        self.stackedWidget.setCurrentIndex(1)
        self.stackedWidget_inner.setCurrentIndex(0)
        self.statistics_tabWidget.setCurrentIndex(0)
        self.statistics_performance_tabWidget.setCurrentIndex(0)
        self.statistics_tabWidget_round_results.setCurrentIndex(0)
        self.settings_lineEdit_rounds.setPlaceholderText(str(globals.default_years))
        self.settings_lineEdit_bidRounds.setPlaceholderText(str(globals.default_rounds))
        self.settings_lineEdit_initialMoney.setPlaceholderText(str(globals.default_money))
        # Empty warning labels
        self.create_label_warning.setText("")
        self.lobby_label_warning.setText("")
        self.main_label_warning.setText("")
        self.players_label_warning.setText("")
        # Repeaters
        self.end_game_counter = 0 # quick fix getting rid of host sending a bunch of packages
        # Define flags
        self.countdown_stop_flag = False
        self.player_removed = None
        self.round_results_drawn = False
        self.player_status_changed = False
        # Create timer object
        self.lobby_refresh_timer = QTimer(self)
        self.player_refresh_timer = QTimer(self)
        self.countdown = QTimer(self)
        self.countdown.timeout.connect(self.update_countdown)
        self.warnTimer = QTimer(self)
        self.warnTimer.timeout.connect(self.warningCountdownFinished)  # Trigger method when the timer times out
        self.warnTimer.setSingleShot(True)  # A single shot timer executes the timeout method only once
        self.background_counter = QTimer(self)
        self.background_counter.timeout.connect(self.background_flag_check)
        self.background_counter.start(100) # connected method is run every 100 ms (input value given in ms)
        # Set up alignments (this is done in designer but must be redone here to fix bug on MAC OSx)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout.setFormAlignment((QtCore.Qt.AlignLeft))
        self.formLayout_2.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_2.setFormAlignment((QtCore.Qt.AlignLeft))
        self.formLayout_3.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_3.setFormAlignment((QtCore.Qt.AlignLeft))
        self.formLayout_4.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_4.setFormAlignment((QtCore.Qt.AlignLeft))
        self.formLayout_5.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_5.setFormAlignment((QtCore.Qt.AlignLeft))
        self.formLayout_6.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_6.setFormAlignment(QtCore.Qt.AlignLeft)
        # Input data from excel
        gas_cost_fixed, gas_cost_variable, coal_cost_fixed, coal_cost_variable, co2_tax = self.game_obj.host.input_data()
        self.game_obj.gas_cost_fixed = gas_cost_fixed
        self.game_obj.gas_cost_variable = gas_cost_variable
        self.game_obj.coal_cost_fixed = coal_cost_fixed
        self.game_obj.coal_cost_variable = coal_cost_variable
        self.game_obj.co2_tax = co2_tax
        self.statistics_comboBox_round_results.setEnabled(False)
        self.statistics_tabWidget_general_plots.setEnabled(False)
        self.statistics_tabWidget_round_results.setEnabled(False)
        self.static_canvas_statistics_performance = None
        self._static_ax_statistics_performance = None
        self._static_ax = None
        self._static_ax_statistics_round_results_players = None
        self.static_canvas = None
        self.static_canvas_statistics_round_results_players = None
        self.statistics_tabWidget_general_plots_currentIndex = None
        self.sec_remaining = 0


    def background_flag_check(self):
        """
        The method runs a timer which runs in the background and checks for flags and then runs events triggered by these flags
        """
        if self.player_removed is not None:
            if globals.DEBUGGING:
                print(self.player_removed)
            self.warningCountdown("kick", self.player_removed)
            self.player_removed = None
        if self.game_obj.host_status:
            if self.game_obj.host_status == "update demand":
                self.game_obj.host_status = ""
                self.main_label_demand.setText(
                    number_to_string(self.game_obj.host.demand[0]) + "-" + number_to_string(
                        self.game_obj.host.demand[1]) + "Q")
            elif self.game_obj.host_status == "valid ip":
                self.game_obj.host_status = ""
                data = self.createData("settings")
                self.sendAll(data)
                if self.stackedWidget.currentIndex() == 1:
                    self.stackedWidget.setCurrentIndex(2)
            elif self.game_obj.host_status == "invalid ip":
                self.game_obj.host_status = ""
                self.warningCountdown("invalid ip")


    def create_handle_button_next(self):
        # Set up and start the network thread
        self.serverThread = ServerNetwork(self)
        self.serverThread.start()
        ip = self.create_lineEdit_hostIp.text()
        if (not ip.strip()) or ip.count(".") != 3:                                        # Checks that field is nonempty (also for whitespaces) and that that IP-address has correct format (three dots)
            # Show error message
            print("Some error message")
        else:
            self.game_obj.setIp(ip)
            #self.stackedWidget.setCurrentIndex(2)
        # Set number of players to zero
        self.num_players = 0
        # Connect to slot method
        self.lobby_refresh_timer.timeout.connect(self.automatic_lobby_refresh)
        # Start  the timer
        self.lobby_refresh_timer.start(100)  # argument is update frequency in ms

    def settings_handle_button_create(self):
        years = self.settings_lineEdit_rounds.text()
        bidRounds = self.settings_lineEdit_bidRounds.text()
        money = self.settings_lineEdit_initialMoney.text()
        stratTime = self.strategy_timeEdit.text()
        bidTime = self.bid_timeEdit.text()
        self.initial_plants()
        # Only use inputed values if they are edited. Else use default values defined in globals.py initialized in Game_client.py
        if bool(years.strip()):
            self.game_obj.years = int(years)
        if bool(bidRounds.strip()):
            self.game_obj.bidRounds = int(bidRounds)
        if bool(money.strip()):
            self.game_obj.initialMoney = int(money)*1000000
        self.game_obj.setStrategyTime(stratTime)
        self.game_obj.setBidTime(bidTime)
        # Send settings to players
        data = self.createData("settings")
        self.sendAll(data)
        self.label_time.setText(self.game_obj.getStrategyTime()) # initial time remaining in the game window
        # Change page
        #self.game_obj.host.setJoinable(True)  # Should now be True
        # Draw the lobby initially
        self.drawLobby()
        self.stackedWidget.setCurrentIndex(3)

    def automatic_lobby_refresh(self):
        """
        Lobby refreshes automatically in given intervalls. The refreshing is started when the host enters the setting page because players can be in the lobby at the same time
        """
        if self.stackedWidget.currentIndex() == 3:
            # Redraw the lobby
            self.clearLobby()
            self.drawLobby()
        # A new player has joined since the last time the method was run
        if self.num_players != len(self.game_obj.simple_players):
            self.num_players = len(self.game_obj.simple_players)
            # Share new information to all players
            data = self.createData("players")
            self.sendAll(data)

    def lobby_handle_button_start(self):
        if self.game_obj.host.allPlayersReady():
            # Reset status of players to "not ready"
            self.game_obj.host.setAllPlayersNotReady()
            # Make the game not joinable
            self.game_obj.host.setJoinable(False)
            # Send playerNumbers to all players
            for player in self.game_obj.host.players:
                data = self.createData("playerNumber", player.playerNumber)
                self.send(data, player.playerNumber)
            # Calculate the time of the end of the round
            self.game_obj.setEndTime(endTime(self.game_obj.getStrategyTime()))
            # Send data about time of the end of the round
            data = self.createData("endTime")
            self.sendAll(data)
            # Send initial plants
            data = self.createData("plants")
            self.sendAll(data)
            for player in self.game_obj.host.players:
                self.statistics_combobox_players.addItem(player.firm_name)
            # Send expected demand
            self.create_expected_demand()
            data = self.createData("demand")
            self.sendAll(data)
            # Set correct labels
            self.label_year.setText("Year: {}/{}".format(self.game_obj.year, self.game_obj.years))
            self.main_label_number_new_plants.setText(str(len(self.game_obj.host.newPlants)))
            self.main_label_next_plant_name.setText(self.game_obj.host.database.get_name_of_next_plant())
            # Stop lobby refresh
            self.lobby_refresh_timer.stop()
            # Start the round countdown
            if globals.DEBUGGING:
                print(self.countdown_stop_flag)
            self.startCountdown()
            # Change window to main window
            self.stackedWidget.setCurrentIndex(4)
        else:
            self.warningCountdown("notAllPlayersReady")

    def create_expected_demand(self):
        """
        The expected demand is somewhat different from the actual demand which means the players cannot really know
        what happens in the market which is also true for realistic cases
        """
        self.game_obj.expected_demand_fixed = random.uniform(0.75, 1.25) * self.game_obj.host.demand[0]
        self.game_obj.expected_demand_variable = random.uniform(0.75, 1.25) * self.game_obj.host.demand[1]

    def handle_button_main(self):
        self.uncheck_buttons()
        self.button_main.setChecked(True)
        self.clear_page()

        # Set correct labels
        self.main_label_demand.setText("{}-{}Q".format(round(self.game_obj.host.demand[0],1), round(self.game_obj.host.demand[1],1)))
        self.stackedWidget_inner.setCurrentIndex(0)

    def handle_button_players(self):
        try:
            self.uncheck_buttons()
            self.button_players.setChecked(True)
            if self.stackedWidget_inner.currentIndex() == 1:
                return
            self.clear_page()
            self.drawPlayers()
            self.player_refresh_timer.timeout.connect(self.automatic_player_refresh)
            # Start  the timer
            self.player_refresh_timer.start(100)  # argument is update frequency in ms
            self.stackedWidget_inner.setCurrentIndex(1)
        except Exception as e:
            print(e)

    def handle_button_statistics(self):
        self.uncheck_buttons()
        self.button_statistics.setChecked(True)
        self.clear_page()
        self.draw_statistics_leaderboards()
        # Force update player specific data
        self.statistics_handle_comboBox()
        # Make performance plot
        self.plot_statistics_performance_graphs()
        self.stackedWidget_inner.setCurrentIndex(2)


    def main_handle_button_add_next_plant(self):
        """
        Called when button "Add next plant in list" is clicked
        The plant shown in label should be taken from the database and added to the hosts list of new plants to be added to players store
        """
        next_plant = self.game_obj.host.database.get_next_plant_in_list(len(self.game_obj.storePlants) + len(self.game_obj.host.newPlants))
        if next_plant:
            self.game_obj.host.newPlants.append(next_plant)
            self.warningCountdown("next_plant_added", next_plant.name)
            self.main_label_next_plant_name.setText(self.game_obj.host.database.get_name_of_next_plant())
            self.main_label_number_new_plants.setText(str(len(self.game_obj.host.newPlants)))
        else:
            self.warningCountdown("next_plant_failed")

    def main_handle_button_newPlant(self):
        # Initialize dialog window
        self.dialog_new_plant = QtWidgets.QDialog()
        # Set GUI wrapper
        self.dialog_new_plant.ui = Ui_dialog_newPlant()
        # Initialize the design onto the dialog using the wrapper
        self.dialog_new_plant.ui.setupUi(self.dialog_new_plant)
        # Set up slots for the input
        self.dialog_new_plant.ui.dialog_addPlant_buttonBox.accepted.connect(self.addPlant_dialog_accepted)
        self.dialog_new_plant.ui.dialog_addPlant_buttonBox.rejected.connect(self.close_dialog_new_plant_window)
        # Set up validators
        self.dialog_new_plant.ui.addPlant_lineEdit_capacity.setValidator(self.float_positive_validator)
        self.dialog_new_plant.ui.addPlant_lineEdit_investmentCost.setValidator(self.float_positive_validator)
        self.dialog_new_plant.ui.addPlant_lineEdit_annualCost.setValidator(self.float_positive_validator)
        self.dialog_new_plant.ui.addPlant_lineEdit_variableCost.setValidator(self.float_positive_validator)
        self.dialog_new_plant.ui.addPlant_lineEdit_emissions.setValidator(self.float_positive_validator)
        self.dialog_new_plant.ui.addPlant_lineEdit_efficiency.setValidator(self.float_positive_percentage_valdidator)
        # Make it so that only the dialog window can be used when it is open
        self.dialog_new_plant.setModal(True)
        # Show the dialog window
        self.dialog_new_plant.show()
        self.dialog_new_plant.exec_()



    def addPlant_dialog_accepted(self):
        """
        Method is called when the "OK" button is clicked in the addPlant dialog window as it is a standard acceptance button
        """
        name = self.dialog_new_plant.ui.addPlant_lineEdit_name.text()
        source = self.dialog_new_plant.ui.addPlant_comboBox_source.currentText()
        try:
            capacity = float(self.dialog_new_plant.ui.addPlant_lineEdit_capacity.text())
            efficiency = float(self.dialog_new_plant.ui.addPlant_lineEdit_efficiency.text())/100 # division by 100 because efficiency uses decimal numbers for efficiency
            investment_cost = float(self.dialog_new_plant.ui.addPlant_lineEdit_investmentCost.text()) * 10**6
            annual_cost = float(self.dialog_new_plant.ui.addPlant_lineEdit_annualCost.text()) *10**6
            variable_cost = float(self.dialog_new_plant.ui.addPlant_lineEdit_variableCost.text())
            emissions = float(self.dialog_new_plant.ui.addPlant_lineEdit_emissions.text())
            # Create plant from input values
            new_plant = Plant(source, name, capacity, investment_cost, efficiency, annual_cost, variable_cost,
                              emissions)
            # Add plant to vector of new plants to be added to the next round.
            self.game_obj.host.newPlants.append(new_plant)
            # Set label
            self.main_label_number_new_plants.setText(str(len(self.game_obj.host.newPlants)))
            self.warningCountdown("new_plant_success")
        except:
            self.warningCountdown("new_plant_failed")
        # Close window
        self.dialog_new_plant.close()


    def close_dialog_new_plant_window(self):
        """
        The method is called when "Cancel" is clicked as it is a standard rejection button
        This method should simply close the dialog window without saving
        """
        print("Closing dialog window")
        self.dialog_new_plant.close()

    def main_handle_button_set_demand(self):
        """
        Set the event triggered by button click. Open dialog window showing demand setting.
        """
        # Initialize dialog window
        self.dialog_set_demand = QtWidgets.QDialog()
        # Set GUI wrapper
        self.dialog_set_demand.ui = Ui_dialog_setDemand()
        # Initialize the design onto the dialog using the wrapper
        self.dialog_set_demand.ui.setupUi(self.dialog_set_demand)
        # Set up slots for the input
        self.dialog_set_demand.ui.dialog_setDemand_plotButton.clicked.connect(self.dialog_set_demand_handle_button_plot)
        self.dialog_set_demand.ui.dialog_setDemand_buttonBox.accepted.connect(self.set_demand_dialog_accepted)
        self.dialog_set_demand.ui.dialog_setDemand_buttonBox.rejected.connect(self.close_dialog_set_demand_window)
        # Enable validators for input fields
        self.dialog_set_demand.ui.dialog_setDemand_fixed_lineEdit.setValidator(self.float_positive_validator)
        self.dialog_set_demand.ui.dialog_setDemand_variable_lineEdit.setValidator(self.float_positive_validator)
        # Make it so that only the dialog window can be used when it is open
        self.dialog_set_demand.setModal(True)
        # Plot the demand and previous bids if they exist
        self.plot_inside_window(self.dialog_set_demand.ui.demand_dialog_verticalLayout)
        # Show the dialog window
        self.dialog_set_demand.show()
        self.dialog_set_demand.exec_()

    def dialog_set_demand_handle_button_plot(self):
        # Clear the plot if it already exists
        try:
            self.dialog_set_demand.ui.demand_dialog_verticalLayout.removeWidget(self.static_canvas)
            self.static_canvas.deleteLater()
            self.static_canvas = None
        except:
            pass # plot does not exist so ignore the exception
        try:
            second_demand_fixed = float(self.dialog_set_demand.ui.dialog_setDemand_fixed_lineEdit.text())
            second_demand_variable = float(self.dialog_set_demand.ui.dialog_setDemand_variable_lineEdit.text())
            self.plot_inside_window(self.dialog_set_demand.ui.demand_dialog_verticalLayout, second_demand_fixed_optional=second_demand_fixed, second_demand_variable_optional=second_demand_variable)
        except:
            # Plot only the existing demand
            self.plot_inside_window(self.dialog_set_demand.ui.demand_dialog_verticalLayout)
            # Show some error message
            pass

    def set_demand_dialog_accepted(self):
        # Save inputted values if valid
        try:
            self.game_obj.host.demand[0] = float(self.dialog_set_demand.ui.dialog_setDemand_fixed_lineEdit.text())
            self.game_obj.host.demand[1] = float(self.dialog_set_demand.ui.dialog_setDemand_variable_lineEdit.text())
            # Change label
            self.main_label_demand.setText("{}-{}Q".format(round(self.game_obj.host.demand[0],1), round(self.game_obj.host.demand[1],1)))
            # show sucess message
            self.warningCountdown("set_demand_accepted")
        except:
            # show some error
            self.warningCountdown("set_demand_rejected")
            pass
        # Clear plot
        self.clear_set_demand_dialog_plot()
        # Close window
        self.dialog_set_demand.close()

    def close_dialog_set_demand_window(self):
        # Clear plot
        self.clear_set_demand_dialog_plot()
        # Close window
        self.dialog_set_demand.close()



    def uncheck_buttons(self):
        if self.stackedWidget_inner.currentIndex()==0:
            self.button_main.setChecked(False)
        elif self.stackedWidget_inner.currentIndex()==1:
            self.button_players.setChecked(False)
        elif self.stackedWidget_inner.currentIndex()==2:
            self.button_statistics.setChecked(False)


    def transition_handle_button_next(self):
        """
        Check current phase and make the correct transition
        """
        self.countdown_stop_flag = False
        self.game_obj.host.calculate_placements()
        if self.game_obj.phase == "End game":
            self.drawLeaderboard()
            self.stackedWidget.setCurrentIndex(7)
            return
        elif self.game_obj.phase == "Strategy phase":
            # Create endTime
            self.game_obj.endTime = endTime(self.game_obj.strategyTime)
        elif self.game_obj.phase == "Bidding phase":
            self.game_obj.endTime = endTime(self.game_obj.bidTime)
        self.clear_transition_results()
        data = self.createData("endTime")
        self.sendAll(data)
        print(len(self.game_obj.host.host_statistics.host_round_results))
        if len(self.game_obj.host.host_statistics.host_round_results) > 0:
            print("Adding item to combobox")
            self.statistics_comboBox_round_results.addItem(
                "Year {} round {}".format(self.game_obj.host.host_statistics.host_round_results[-1]["year"],
                                          self.game_obj.host.host_statistics.host_round_results[-1]["round"]))
        self.startCountdown()
        self.stackedWidget.setCurrentIndex(4)
        self.handle_button_main()
        self.statistics_tabWidget.setCurrentIndex(0)
        if self.game_obj.host.host_statistics.host_round_results:
            self.statistics_comboBox_round_results.setEnabled(True)
            self.statistics_tabWidget_general_plots.setEnabled(True)
            self.statistics_tabWidget_round_results.setEnabled(True)


    def drawLobby(self):
        try:
            self.lobby_label_ip.setText(self.game_obj.getIp())
            # Define font to be applied to new widgets
            font = QtGui.QFont()
            font.setPointSize(18)
            # Get players from list
            players = self.game_obj.host.players
            # Go through every plant in list of plants and create a widget for every element
            elements = len(players)
            if elements == 0:
                self.lobby_empty = QtWidgets.QLabel(self.page_lobby)
                self.lobby_empty.setFont(font)
                self.lobby_layout_emptyList.addWidget(self.lobby_empty)
                self.lobby_empty.setText("Connected players will show up here..")
                return
            # Creating empty lists for every variable in the plant class.
            self.lobby_widget_name = [None] * elements
            self.lobby_widget_ready = [None] * elements
            self.lobby_widget_kick = [None] * elements
            for row, player in enumerate(players):
                # Name
                self.lobby_widget_name[row] = QtWidgets.QLabel(self.page_lobby)
                self.lobby_widget_name[row].setFont(font)
                self.lobby_gridLayout.addWidget(self.lobby_widget_name[row], row + 1, 0, 1, 1)
                self.lobby_widget_name[row].setText(player.getName())
                # motto?
                # Status
                self.lobby_widget_ready[row] = QtWidgets.QLabel(self.page_lobby)
                self.lobby_widget_ready[row].setFont(font)
                self.lobby_gridLayout.addWidget(self.lobby_widget_ready[row], row + 1, 1, 1, 1)
                self.lobby_widget_ready[row].setText(player.status)
                # Kick button
                #self.lobby_widget_kick[row] = QtWidgets.QPushButton(self.page_lobby)
                self.lobby_widget_kick[row] = QtWidgets.QPushButton("Kick", self)
                self.lobby_widget_kick[row].setFont(font)
                self.lobby_widget_kick[row].setObjectName("kickbutton_" + str(player.playerNumber))
                self.lobby_gridLayout.addWidget(self.lobby_widget_kick[row], row+1, 2, 1, 1)
                #self.lobby_widget_kick[row].setText("Kick")
                #self.lobby_widget_kick[row].clicked.connect(self.handle_button_kick(player.playerNumber))
                #self.lobby_widget_kick[row].clicked.connect(lambda: self.handle_button_kick(player.playerNumber))
                self.lobby_widget_kick[row].clicked.connect(self.handle_button_kick)
        except Exception as e:
            print("Exception called in drawLobby():")
            print(e)

    #def handle_button_kick(self, playerNumber):
    #    # This method is used to allow input values in the connected event (the actual handler does not take input values)
    #    def handler():
    #        if globals.DEBUGGING:
    #            print("Kicking player")
    #        self.removePlayer(playerNumber, notify=True)
    #    return handler


    #def handle_button_kick(self, playerNumber):
    def handle_button_kick(self):
        # The sender has information about the player associated with the button so extract that information
        sender = self.sender()
        playerNumber = int(sender.objectName().replace("kickbutton_", ""))
        self.removePlayer(playerNumber, notify=True)

    def statistics_handle_comboBox(self):
        try:
            n = self.statistics_combobox_players.currentIndex()
            # Update labels for player
            if n == -1: # this output means the player was not found
                self.statistics_label_money.setText("-")
                self.statistics_label_profits.setText("-")
                self.statistics_label_emissions.setText("-")
                self.statistics_label_co2tax.setText("-")
                self.statistics_label_plants.setText("-")
            else:
                player = self.game_obj.host.getPlayer(n)
                self.statistics_label_money.setText(number_to_string(player.money, "MNOK"))
                self.statistics_label_profits.setText(number_to_string(player.statistics.profits, "MNOK"))
                self.statistics_label_emissions.setText(
                    number_to_string(player.statistics.emissions, "TON CO<sub>2</sub>eq"))
                self.statistics_label_co2tax.setText(number_to_string(player.statistics.taxes, "MNOK"))
                self.statistics_label_plants.setText(str(len(player.getPlants())))
        except Exception as e:
            print("Exception in statistics_handle_comboBox")
            print(e)

    def clearLobby(self):
        # Checks if the list exist and if it does, goes through it
        try:
            # Iterating through all rows and deleting contents
            for row in range(0, len(self.lobby_widget_name)):
                # Name
                self.lobby_gridLayout.removeWidget(self.lobby_widget_name[row])
                self.lobby_widget_name[row].deleteLater()
                self.lobby_widget_name[row] = None
                # Ready
                self.lobby_gridLayout.removeWidget(self.lobby_widget_ready[row])
                self.lobby_widget_ready[row].deleteLater()
                self.lobby_widget_ready[row] = None
                # Kick button
                self.lobby_gridLayout.removeWidget(self.lobby_widget_kick[row])
                self.lobby_widget_kick[row].deleteLater()
                self.lobby_widget_kick[row] = None
        except:
            self.lobby_layout_emptyList.removeWidget(self.lobby_empty)
            self.lobby_empty.deleteLater()
            self.lobby_empty = None

    def automatic_player_refresh(self):
        """
        Player list refreshes automatically in given interval if a flag is set
        """
        # A new player has joined since the last time the method was run
        if self.player_status_changed:
            self.player_status_changed = False
            self.clearPlayers()
            self.drawPlayers()

    def drawPlayers(self):
        """
        This method draws the players in the player tab of the main window.
        It reads this from the players list in the host class
        """
        # Define font to be applied to new widgets
        font = QtGui.QFont()
        font.setPointSize(18)
        # Get player list
        players = self.game_obj.host.players
        # Go through every plant in list of plants and create a widget for every element
        elements = len(players)
        if elements == 0:
            self.players_empty = QtWidgets.QLabel(self.page_players)
            self.players_empty.setFont(font)
            self.players_verticalLayout_emptyList.addWidget(self.players_empty)
            self.players_empty.setText("There are no players in the game!")
            return
        # Creating empty lists for every variable in the plant class.
        self.players_widget_name = [None] * elements
        self.players_widget_motto = [None] * elements
        self.players_widget_profits = [None] * elements
        self.players_widget_emissions = [None] * elements
        self.players_widget_status = [None] * elements
        self.players_widget_kick = [None] * elements
        # Looping through plants in order to draw information in window
        try:
            for row, player in enumerate(players):
                # Name
                self.players_widget_name[row] = QtWidgets.QLabel(self.page_players)
                self.players_widget_name[row].setFont(font)
                self.players_gridLayout.addWidget(self.players_widget_name[row], row + 1, 0, 1,
                                                 1)  # Drawing at row+1 because information is drawn in row 0
                self.players_widget_name[row].setText(player.firm_name)
                # Motto
                self.players_widget_motto[row] = QtWidgets.QLabel(self.page_players)
                self.players_widget_motto[row].setFont(font)
                self.players_gridLayout.addWidget(self.players_widget_motto[row], row + 1, 1, 1, 1)
                self.players_widget_motto[row].setText(player.firm_motto)
                # profits
                self.players_widget_profits[row] = QtWidgets.QLabel(self.page_players)
                self.players_widget_profits[row].setFont(font)
                self.players_gridLayout.addWidget(self.players_widget_profits[row], row + 1, 2, 1, 1)
                self.players_widget_profits[row].setText(number_to_string(player.statistics.profits, "MNOK"))
                # emissions
                self.players_widget_emissions[row] = QtWidgets.QLabel(self.page_players)
                self.players_widget_emissions[row].setFont(font)
                self.players_gridLayout.addWidget(self.players_widget_emissions[row], row + 1, 3, 1, 1)
                self.players_widget_emissions[row].setText(number_to_string(player.statistics.emissions, "TON CO<sub>2</sub>eq" ))
                # status
                self.players_widget_status[row] = QtWidgets.QLabel(self.page_players)
                self.players_widget_status[row].setFont(font)
                self.players_gridLayout.addWidget(self.players_widget_status[row], row + 1, 4, 1, 1)
                self.players_widget_status[row].setText(player.status)
                # kick
                self.players_widget_kick[row] = QtWidgets.QPushButton("Kick player", self)
                self.lobby_widget_kick[row].setObjectName("kickbutton_" + str(player.playerNumber))
                self.players_widget_kick[row].setFont(font)
                self.players_gridLayout.addWidget(self.players_widget_kick[row], row + 1, 5, 1, 1)
                #self.players_widget_kick[row].clicked.connect(lambda: self.handle_button_kick(player.playerNumber))
                self.players_widget_kick[row].clicked.connect(self.handle_button_kick)
                #self.players_widget_kick[row].clicked.connect(self.handle_button_kick(player.playerNumber))
        except Exception as e:
            print("Exception in drawPlayers(): ")
            print(e)

    def draw_transition_results(self):
        """
        Creates labels for the transition window after bid rounds and shows results from this round.
        """
        font = QtGui.QFont()
        font.setPointSize(24)
        try:
            self.transition_formlayout.setLabelAlignment(QtCore.Qt.AlignLeft)
            self.transition_formlayout.setFormAlignment(QtCore.Qt.AlignLeft)
            # Bids
            self.transition_label_bids = QtWidgets.QLabel(self.page_transition)
            self.transition_label_bids.setFont(font)
            self.transition_label_bids.setText("Bids accepted:")
            self.transition_formlayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.transition_label_bids)
            self.transition_widget_bids= QtWidgets.QLabel(self.page_transition)
            self.transition_widget_bids.setFont(font)
            try:
                self.transition_widget_bids.setText(str(self.opt.accepted_bids_count) + "/" + str(len(self.opt.bids)))
            except:
                self.transition_widget_bids.setText("-/-")
            self.transition_formlayout.setWidget(0, QtWidgets.QFormLayout.FieldRole,
                                                 self.transition_widget_bids)
            # Hours
            self.transition_label_hours= QtWidgets.QLabel(self.page_transition)
            self.transition_label_hours.setFont(font)
            self.transition_label_hours.setText("Hours for bid round:")
            self.transition_formlayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.transition_label_hours)
            self.transition_widget_hours = QtWidgets.QLabel(self.page_transition)
            self.transition_widget_hours .setFont(font)
            self.transition_widget_hours.setText(str(self.opt.hours_for_bidround) + " hours")
            self.transition_formlayout.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                                 self.transition_widget_hours)
            # System price
            self.transition_label_system_price = QtWidgets.QLabel(self.page_transition)
            self.transition_label_system_price.setFont(font)
            self.transition_label_system_price.setText("System price:")
            self.transition_formlayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.transition_label_system_price)
            self.transition_widget_system_price = QtWidgets.QLabel(self.page_transition)
            self.transition_widget_system_price.setFont(font)
            self.transition_widget_system_price.setText(number_to_string(self.opt.system_price, "NOK/MWh"))
            self.transition_formlayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.transition_widget_system_price)
            # Demand
            self.transition_label_demand = QtWidgets.QLabel(self.page_transition)
            self.transition_label_demand.setFont(font)
            self.transition_label_demand.setText("Demand:")
            self.transition_formlayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.transition_label_demand)
            self.transition_widget_demand= QtWidgets.QLabel(self.page_transition)
            self.transition_widget_demand.setFont(font)
            self.transition_widget_demand.setText(number_to_string(self.opt.demand*self.opt.hours_for_bidround,"GWh"))
            self.transition_formlayout.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                                 self.transition_widget_demand)
            # CO2 tax
            self.transition_label_co2_tax = QtWidgets.QLabel(self.page_transition)
            self.transition_label_co2_tax.setFont(font)
            self.transition_label_co2_tax.setText("CO<sub>2</sub> tax:")
            self.transition_formlayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.transition_label_co2_tax)
            self.transition_widget_co2_tax= QtWidgets.QLabel(self.page_transition)
            self.transition_widget_co2_tax.setFont(font)
            self.transition_widget_co2_tax.setText(number_to_string(self.opt.co2_tax, "NOK/(kg CO<sub>2</sub>eq)"))
            self.transition_formlayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                                 self.transition_widget_co2_tax)
            # Gas price
            self.transition_label_gas_price= QtWidgets.QLabel(self.page_transition)
            self.transition_label_gas_price.setFont(font)
            self.transition_label_gas_price.setText("Gas price:")
            self.transition_formlayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.transition_label_gas_price)
            self.transition_widget_gas_price = QtWidgets.QLabel(self.page_transition)
            self.transition_widget_gas_price.setFont(font)
            self.transition_widget_gas_price.setText(number_to_string(self.opt.gas_price, "NOK/MWh"))
            self.transition_formlayout.setWidget(5, QtWidgets.QFormLayout.FieldRole,
                                                 self.transition_widget_gas_price)
            # Coal price
            self.transition_label_coal_price = QtWidgets.QLabel(self.page_transition)
            self.transition_label_coal_price.setFont(font)
            self.transition_label_coal_price.setText("Coal price:")
            self.transition_formlayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.transition_label_coal_price)
            self.transition_widget_coal_price = QtWidgets.QLabel(self.page_transition)
            self.transition_widget_coal_price.setFont(font)
            self.transition_widget_coal_price.setText(number_to_string(self.opt.coal_price, "NOK/MWh"))
            self.transition_formlayout.setWidget(6, QtWidgets.QFormLayout.FieldRole,
                                                 self.transition_widget_coal_price)
            # gas production
            self.transition_label_gas_production = QtWidgets.QLabel(self.page_transition)
            self.transition_label_gas_production.setFont(font)
            self.transition_label_gas_production.setText("Gas production:")
            self.transition_formlayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.transition_label_gas_production)
            self.transition_widget_gas_production = QtWidgets.QLabel(self.page_transition)
            self.transition_widget_gas_production.setFont(font)
            self.transition_widget_gas_production.setText(number_to_string(self.opt.total_gas_production, "GWh"))
            self.transition_formlayout.setWidget(7, QtWidgets.QFormLayout.FieldRole,
                                                 self.transition_widget_gas_production)
            # Coal production
            self.transition_label_coal_production = QtWidgets.QLabel(self.page_transition)
            self.transition_label_coal_production.setFont(font)
            self.transition_label_coal_production.setText("Coal production:")
            self.transition_formlayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.transition_label_coal_production)
            self.transition_widget_coal_production= QtWidgets.QLabel(self.page_transition)
            self.transition_widget_coal_production.setFont(font)
            self.transition_widget_coal_production.setText(number_to_string(self.opt.total_coal_production, "GWh"))
            self.transition_formlayout.setWidget(8, QtWidgets.QFormLayout.FieldRole,
                                                 self.transition_widget_coal_production)

        except Exception as e:
            print("Exception in draw_transition_results:")
            print(e)

    def draw_statistics_leaderboards(self):
        # Define font to be applied to new widgets
        font = QtGui.QFont()
        font.setPointSize(13)
        # Get sorted player list and store it temporarily in case someone leaves game before the statistics tab is left
        # Sliced list copy is used so that players_temp is not changed during operation
        self.players_temp = self.game_obj.host.get_players_by_placement()[:]
        elements = len(self.players_temp)
        if elements == 0:
            self.players_empty = QtWidgets.QLabel(self.page_statistics)
            self.players_empty.setFont(font)
            self.statistics_verticalLayout_leaderboards.addWidget(self.players_empty)
            self.players_empty.setText("There are no players in the game!")
            return
        # Creating empty lists for every variable in the plant class.
        self.players_widget_placement = [None] * elements
        self.players_widget_name = [None] * elements
        self.players_widget_profits = [None] * elements
        # Looping through plants in order to draw information in window
        try:
            for row, player in enumerate(self.players_temp):
                # Placement
                self.players_widget_placement[row] = QtWidgets.QLabel(self.page_statistics)
                self.players_widget_placement[row].setFont(font)
                self.statistics_gridLayout.addWidget(self.players_widget_placement[row], row + 1, 0, 1,
                                                 1)  # Drawing at row+1 because information is drawn in row 0
                self.players_widget_placement[row].setText(str(player.statistics.placement))
                # Name
                self.players_widget_name[row] = QtWidgets.QLabel(self.page_statistics)
                self.players_widget_name[row].setFont(font)
                self.statistics_gridLayout.addWidget(self.players_widget_name[row], row + 1, 1, 1,
                                                     1)  # Drawing at row+1 because information is drawn in row 0
                self.players_widget_name[row].setText(player.firm_name)
                # Profits
                self.players_widget_profits[row] = QtWidgets.QLabel(self.page_statistics)
                self.players_widget_profits[row].setFont(font)
                self.statistics_gridLayout.addWidget(self.players_widget_profits[row], row + 1, 2, 1,
                                                     1)  # Drawing at row+1 because information is drawn in row 0
                self.players_widget_profits[row].setText(number_to_string(player.statistics.profits, "MNOK"))
        except Exception as e:
            print("Exception in draw_statistics_leaderboard")
            print(e)

    def clear_statistics_leaderboards(self):
        # Checks if the list exist and if it does, goes through it
        try:
            # If the empty widget exists remove it
            self.statistics_verticalLayout_leaderboards.removeWidget(self.players_empty)
            self.players_empty.deleteLater()
            self.players_empty = None
        except:
            # If it does not it means there are players so remove them instead
            for row in range(len(self.players_temp)):
                # Placement
                self.statistics_gridLayout.removeWidget(self.players_widget_placement[row])
                self.players_widget_placement[row].deleteLater()
                self.players_widget_placement[row] = None
                # Name
                self.statistics_gridLayout.removeWidget(self.players_widget_name[row])
                self.players_widget_name[row].deleteLater()
                self.players_widget_name[row] = None
                # Profits
                self.statistics_gridLayout.removeWidget(self.players_widget_profits[row])
                self.players_widget_profits[row].deleteLater()
                self.players_widget_profits[row] = None


    def clear_transition_results(self):
        try:
            #bids
            self.transition_widget_bids.deleteLater()
            self.transition_widget_bids = None
            self.transition_label_bids.deleteLater()
            self.transition_label_bids = None
            # hours
            self.transition_widget_hours.deleteLater()
            self.transition_widget_hours = None
            self.transition_label_hours.deleteLater()
            self.transition_label_hours = None
            # Systemprice
            self.transition_widget_system_price.deleteLater()
            self.transition_widget_system_price = None
            self.transition_label_system_price.deleteLater()
            self.transition_label_system_price = None
            # demand
            self.transition_widget_demand.deleteLater()
            self.transition_widget_demand= None
            self.transition_label_demand.deleteLater()
            self.transition_label_demand= None
            # co2 tax
            self.transition_widget_co2_tax.deleteLater()
            self.transition_widget_co2_tax= None
            self.transition_label_co2_tax.deleteLater()
            self.transition_label_co2_tax= None
            # gas price
            self.transition_widget_gas_price.deleteLater()
            self.transition_widget_gas_price= None
            self.transition_label_gas_price.deleteLater()
            self.transition_label_gas_price= None
            # coal price
            self.transition_widget_coal_price.deleteLater()
            self.transition_widget_coal_price= None
            self.transition_label_coal_price.deleteLater()
            self.transition_label_coal_price= None
            # gas production
            self.transition_widget_gas_production.deleteLater()
            self.transition_widget_gas_production= None
            self.transition_label_gas_production.deleteLater()
            self.transition_label_gas_production = None
            # coal production
            self.transition_widget_coal_production.deleteLater()
            self.transition_widget_coal_production= None
            self.transition_label_coal_production.deleteLater()
            self.transition_label_coal_production= None

        except:
            pass # Results were not drawn so ignore the clearing

    def statistics_round_results_handle_comboBox(self):
        """
        Triggered by a change in the current index of the combobox for the bid results
        Triggers:   player enters another item in the combobox
                    player enters info tab
        """
        try:
            # Clear the current round results but only if some round result has been written
            if self.round_results_drawn:
                self.clear_statistics_round_results()
                self.round_results_drawn = False
            # Draw the round results
            self.draw_statistics_round_results()  # round_results_drawn flag set if drawing is successful
        except Exception as e:
            print("Exception in statistics_round_results_handle_comboBox()")
            print(e)

    def draw_statistics_round_results(self):
        # bids accepted
        # hours for bid round
        # system price
        # demand
        # production
        # co2 tax
        # gas price
        # gas production
        # coal price
        # coal production

        # demand/player plot

        # pv production
        # pv market share
        # gas production
        # gas market share
        # coal production
        # coal market share

        font = QtGui.QFont()
        font.setPointSize(12)
        try:
            n = self.statistics_comboBox_round_results.currentIndex()
            result = self.game_obj.host.host_statistics.host_round_results[n]
            # Set labels
            #    for general
            self.statistics_round_results_label_bids_accepted.setText(str(result["bids_accepted"]) + "/" + str(result["number_of_bids"]))
            self.statistics_round_results_label_hours_for_bid_round.setText(number_to_string(result["hours_for_bid_round"], "hours"))
            self.statistics_round_results_label_system_price.setText(number_to_string(result["system_price"], "NOK/MW"))
            self.statistics_round_results_label_demand.setText(number_to_string(result["demand"], "MW"))
            self.statistics_round_results_label_production.setText(number_to_string(result["production"], "GWh"))
            self.statistics_label_co2tax.setText(number_to_string(result["co2_tax"], "NOK/(CO<sub>2</sub>eq)"))
            self.statistics_round_results_label_pv_production.setText(number_to_string(result["pv_production"], "GWh"))
            self.statistics_round_results_label_gas_price.setText(number_to_string(result["gas_price"], "NOK/MWh"))
            self.statistics_round_results_label_gas_production.setText(number_to_string(result["gas_production"], "GWh"))
            self.statistics_round_results_label_coal_price.setText(number_to_string(result["coal_price"], "NOK/MWh"))
            self.statistics_round_results_label_coal_production.setText(number_to_string(result["coal_production"], "GWh"))
            #    labels for sources
            # Calculate the source market shares
            if result["production"] == 0:
                self.pv_market_share = 0
                self.gas_market_share = 0
                self.coal_market_share = 0
            else:
                if result["pv_production"] == 0:
                    self.pv_market_share = 0
                else:
                    self.pv_market_share = result["pv_production"] / result["production"]
                if result["gas_production"] == 0:
                    self.gas_market_share = 0
                else:
                    self.gas_market_share = result["gas_production"] / result["production"]
                if result["coal_production"] == 0:
                    self.coal_market_share = 0
                else:
                    self.coal_market_share = result["coal_production"] / result["production"]

            # Set production labels
            self.statistics_round_results__sources_label_pv_production.setText(number_to_string(result["pv_production"], "GWh"))
            self.statistics_round_results_sources_label_gas_production.setText(
                number_to_string(result["gas_production"], "GWh"))
            self.statistics_round_results_sources_label_coal_production.setText(
                number_to_string(result["coal_production"], "GWh"))
            # Set source market share label
            self.statistics_round_results_sources_label_pv_market_share.setText(number_to_string(self.pv_market_share, "%"))
            self.statistics_round_results_sources_label_gas_market_share.setText(number_to_string(self.gas_market_share, "%"))
            self.statistics_round_results_sources_label_coal_market_share.setText(number_to_string(self.coal_market_share, "%"))
            # Draw the demand plot or the players plot for the general tab
            # Draw the pie chart for the sources tab
            self.plot_statistics_round_results_sources_graph()
            self.statistics_tabWidget_round_results.setCurrentIndex(0)
            self.statistics_tabWidget_general_plots.setCurrentIndex(0)
            self.round_results_drawn = True
        except Exception as e:
            print("Exception in draw_statistics_round_results(): ")
            print(e)

    def clear_statistics_round_results(self):
        # What needs clearing? demand or players plot, sources plot
        self.clear_statistics_round_results_general_graphs()

    def clearPlayers(self):
        # Checks if the list exist and if it does, goes through it
        try:
            # Iterating through all rows and deleting contents
            for row in range(0, len(self.players_widget_name)):
                # Name
                self.players_gridLayout.removeWidget(self.players_widget_name[row])
                self.players_widget_name[row].deleteLater()
                self.players_widget_name[row] = None
                # Motto
                self.players_gridLayout.removeWidget(self.players_widget_motto[row])
                self.players_widget_motto[row].deleteLater()
                self.players_widget_motto[row] = None
                # Profits
                self.players_gridLayout.removeWidget(self.players_widget_profits[row])
                self.players_widget_profits[row].deleteLater()
                self.players_widget_profits[row] = None
                # Emissions
                self.players_gridLayout.removeWidget(self.players_widget_emissions[row])
                self.players_widget_emissions[row].deleteLater()
                self.players_widget_emissions[row] = None
                # Status
                self.players_gridLayout.removeWidget(self.players_widget_status[row])
                self.players_widget_status[row].deleteLater()
                self.players_widget_status[row] = None
                # Kick button
                self.players_gridLayout.removeWidget(self.players_widget_kick[row])
                self.players_widget_kick[row].deleteLater()
                self.players_widget_kick[row] = None
        except:
            self.players_verticalLayout_emptyList.removeWidget(self.players_empty)
            self.players_empty.deleteLater()
            self.players_empty = None

    def clear_page(self):
        try:
            if self.stackedWidget_inner.currentIndex() == 1:
                self.clearPlayers()
                self.player_refresh_timer.stop()
            if self.stackedWidget_inner.currentIndex() == 2:
                self.clear_statistics_leaderboards()
                self.statistics_tabWidget.setCurrentIndex(0)
                self.statistics_performance_tabWidget.setCurrentIndex(0)
                self.statistics_tabWidget_round_results.setCurrentIndex(0)
                self.statistics_tabWidget_general_plots.setCurrentIndex(0)
        except Exception as e:
            print(e)

    def initial_plants(self):
        """
        Take value from the settings combobox and add the correct plant(s) to the storePlants by reading from file then send it
        WIP
        """
        startPlant = self.settings_combobox_startingPlant.currentText()
        # Create storePlants from initial plant
        if startPlant == "None" or startPlant == "Free choice":
            self.game_obj.host.newPlants = self.game_obj.host.database.get_plants("Type", "Initial", identifier_offset=0)
        elif startPlant == "Coal" or startPlant == "Gas" or startPlant == "PV":
            self.game_obj.host.newPlants = self.game_obj.host.database.get_plants("Type", "Initial", identifier_offset=0, optional_colName="Source", optional_filter=startPlant)
            # TODO: also add some plants to the store?

    def startCountdown(self):
        """
        Calculate seconds until the calculated end time of the phase
        Start the timer
        Update it once to smoothen it out
        """
        self.sec_remaining = endTime_to_seconds(self.game_obj.endTime)
        self.countdown.start(100) # argument is update frequency in ms
        self.update_countdown()

    def update_countdown(self):
        """
        Method is triggered when the timer times out ie. every 100ms or so
        Note that the host controls the timeout so that all the players are timed out at the same time
        """
        self.sec_remaining = endTime_to_seconds(self.game_obj.endTime)
        timeString = time.strftime("%M:%S", time.gmtime(self.sec_remaining))
        self.label_time.setText(timeString)
        if self.countdown_stop_flag == True:
            self.countdown_stop_flag = False
            self.countdown.stop()
            self.label_time.setText("00:00")
        elif self.sec_remaining <= 0:
            # Stop the timer
            self.countdown.stop()
            if globals.DEBUGGING:
                print("Time ran out..")
            #self.label_time.setText("00:00")
            # Force all players to be ready because time ran out
            #self.game_obj.host.setAllPlayesReady()
            self.handle_all_players_ready() # Note that countdown_stop_flag is set here so the countdown is stopped when the time runs out

    def warningCountdown(self, filter, optional_filter=""):
        try:
            self.warnTimer.stop()
        except:  # counter not active, do nothing
            pass
        # Start timer
        self.warnTimer.start(globals.warningTimer*1000)                 # input is ms so globals.warningTimer is multiplied with 1000
        # self.warning is used to notify the finish method which label is showing a warning, so that it can remove that warning message
        self.warning = None
        if filter == "invalid ip":
            self.warning = self.create_label_warning
            self.warning.setText("Could not create a lobby. Are you sure the IP address is correct?")
        elif filter == "kick":
            if self.stackedWidget.currentIndex() == 3:
                self.warning = self.lobby_label_warning
            elif self.stackedWidget.currentIndex() == 4 and self.stackedWidget_inner.currentIndex() == 0:
                self.warning = self.main_label_warning
            else:
                self.warning = self.players_label_warning
            self.warning.setText("Player \"{}\" has been removed from the game".format(optional_filter))
        elif filter == "notAllPlayersReady":
            self.warning = self.lobby_label_warning
            self.warning.setText("Not all players are ready")
        # TODO: add elif for "next plant added" and "next plant not added" and label on main as was done for player window
        elif filter == "next_plant_added":
            self.warning = self.main_label_warning
            self.warning.setText("The plant \"{}\" was successfully added to the queue and will be active the next strategy round".format(optional_filter))
        elif filter == "next_plant_failed":
            self.warning = self.main_label_warning
            self.warning.setText("Failed to add a new plant")
        elif filter == "new_plant_success":
            self.warning = self.main_label_warning
            self.warning.setText("A new plant was successfully created and will be active the next strategy round")
        elif filter == "new_plant_failed":
            self.warning = self.main_label_warning
            self.warning.setText("Failed to create plant. One or more input values are not accepted")
        elif filter == "set_demand_accepted":
            self.warning = self.main_label_warning
            self.warning.setText("The demand was successfully set")
        elif filter == "set_demand_rejected":
            self.warning = self.main_label_warning
            self.warning.setText("Demand was not set. One or both input values are not valid")
        else:
            pass

    def warningCountdownFinished(self):
        """
        Clear the warning text when the countdown finishes.
        """
        self.warning.setText("")

    def changePhase(self):
        """
        Initiate a new round. Calculate bids if it's a end of bid round. Send data to player.
        Phase transitions are:
        - Strategy phase to bid phase
        - Bid phase to bid phase
        - Bid phase to strategy phase
        - Bid phase to endgame
        Any phase transition will open the transition window. Here some results should be shown
        """
        # New labels should be set when the packet is received.
        previousPhase = self.game_obj.phase
        self.game_obj.transition()
        newPhase = self.game_obj.phase
        if newPhase == "Bidding phase":
            self.label_phase.setText(newPhase + " {}/{}".format(self.game_obj.bidRound, self.game_obj.bidRounds))
        else:
            self.label_phase.setText(newPhase)
        #try:
        if True:
            if newPhase == "Strategy phase":
                """
                print("Warning: simple plant addition is active in changePhase()")
                # todo: TEMPORARY PROGRESSION SOLUTION UNDERNEATH. TRY BETTER SOLUTION FOR THIS
                if self.game_obj.year == 2:
                    temp_plants = self.game_obj.host.database.get_plants("Type", "Beginner", (len(self.game_obj.storePlants) + len(self.game_obj.host.newPlants)))
                    print(type(temp_plants))
                    print(self.game_obj.host.newPlants)
                    self.game_obj.host.newPlants.extend(temp_plants)
                    print(self.game_obj.host.newPlants)
                    data = self.createData("plants")
                    self.sendAll(data)
                if self.game_obj.year == 4:
                    temp_plants = self.game_obj.host.database.get_plants("Type", "Advanced", (len(self.game_obj.storePlants) + len(self.game_obj.host.newPlants)))
                    self.game_obj.host.newPlants.extend(temp_plants)
                    data = self.createData("plants")
                    self.sendAll(data)
                """
                # Send new plants to players if there are any
                if self.game_obj.host.newPlants:
                    data = self.createData("plants")
                    self.sendAll(data)
                # Create and send expected demand
                self.create_expected_demand()
                data = self.createData("demand")
                self.sendAll(data)
                # Set labels
                self.label_year.setText("Year: {}/{}".format(self.game_obj.year, self.game_obj.years))
                self.transition_label_info.setText("The bidding phase has ended. Strategy phase starting when \"next\" is clicked.")
                # send data about plants, weather and event.
                #data = self.createData("plants")
                #self.sendAll(data)
                data = self.createData("start strategy phase")
            elif previousPhase == "Strategy phase" and newPhase == "Bidding phase":
                self.transition_label_info.setText("The strategy phase has ended. Bidding phase starting when \"next\" is clicked.")
                data = self.createData("start bid phase")
            elif previousPhase == "Bidding phase" and newPhase == "Bidding phase":
                self.transition_label_info.setText("The bidding round has ended. New bid round coming up.")
                data = self.createData("new bid round")
            elif newPhase == "End game":
                if self.end_game_counter >=1:
                    # Just assuring that end game does not start multiple times
                    return
                self.end_game_counter +=1
                #self.endGame() # This should be triggered when all packages are received from players
                data = self.createData("end game")
            else:
                print("Error in changePhase(): Phase {} is not recognized".format(self.game_obj.phase))
            self.sendAll(data)
            self.stackedWidget.setCurrentIndex(5)
            self.game_obj.host.setAllPlayersNotReady()

    def endGame(self):
        """
        When all players have sent their results the player will calculate who won and send it to the player.
        """
        player_list = []
        motto_list = []
        profits_list = []
        placement_list = []
        for player in self.game_obj.host.get_players_by_placement():
            player_list.append(player.firm_name)
            motto_list.append(player.firm_motto)
            profits_list.append(player.statistics.profits)
            placement_list.append(player.statistics.placement)
        data = dict(header="placement", placements=placement_list)
        data["result_dict"] = dict(players=player_list, mottos=motto_list, profits=profits_list)
        self.sendAll(data)
        try:
            self.background_counter.stop()
        except:
            pass

    def drawLeaderboard(self):
        try:
            font = QtGui.QFont()
            font.setPointSize(13)
            elements = len(self.game_obj.host.get_players_by_placement())
            self.leaderboard_widget_placement = [None] * elements
            self.leaderboard_widget_name = [None] * elements
            self.leaderboard_widget_motto = [None] * elements
            self.leaderboard_widget_profit = [None] * elements
            self.leaderboard_widget_emission = [None] * elements
        except Exception as e:
            print(e)

        try:
            for row, player in enumerate(self.game_obj.host.get_players_by_placement()):
                # Placement
                self.leaderboard_widget_placement[row] = QtWidgets.QLabel(self.page_leaderboard)
                self.leaderboard_widget_placement[row].setFont(font)
                self.leaderboards_gridLayout.addWidget(self.leaderboard_widget_placement[row], row + 1, 0, 1, 1)
                self.leaderboard_widget_placement[row].setText(str(player.statistics.placement))
                # Name
                self.leaderboard_widget_name[row] = QtWidgets.QLabel(self.page_leaderboard)
                self.leaderboard_widget_name[row].setFont(font)
                self.leaderboards_gridLayout.addWidget(self.leaderboard_widget_name[row], row + 1, 1, 1, 1)
                self.leaderboard_widget_name[row].setText(player.firm_name)
                # Motto
                self.leaderboard_widget_motto[row] = QtWidgets.QLabel(self.page_leaderboard)
                self.leaderboard_widget_motto[row].setFont(font)
                self.leaderboards_gridLayout.addWidget(self.leaderboard_widget_motto[row], row + 1, 2, 1, 1)
                self.leaderboard_widget_motto[row].setText(player.firm_motto)
                # Profits
                self.leaderboard_widget_profit[row] = QtWidgets.QLabel(self.page_leaderboard)
                self.leaderboard_widget_profit[row].setFont(font)
                self.leaderboards_gridLayout.addWidget(self.leaderboard_widget_profit[row], row + 1, 3, 1, 1)
                self.leaderboard_widget_profit[row].setText(number_to_string(player.statistics.profits, "MNOK"))
                # Emissions
                self.leaderboard_widget_emission[row] = QtWidgets.QLabel(self.page_leaderboard)
                self.leaderboard_widget_emission[row].setFont(font)
                self.leaderboards_gridLayout.addWidget(self.leaderboard_widget_emission[row], row + 1, 4, 1, 1)
                self.leaderboard_widget_emission[row].setText(number_to_string(player.statistics.emissions, "TON CO<sub>2</sub>-eq" ))

        except Exception as e:
            print("Exception raised in drawLeaderboard()")
            print(e)

    def handle_all_players_ready(self):
        """
        Is called when 1. All players are ready ie. their status == "Ready" or 2. the countdown has timed out
        Make the proper handling of phases, status

        This is a intermediate step before changePhase() is called as optimization should happen before the new round.
        """
        if self.stackedWidget.currentIndex() == 3:
            # Lobby so wait until host clicks start
            return
        # If countdown has not stopped already, stop it (ie. if all players clicked ready before time ran out)
        if self.game_obj.host.allPlayersReady() and self.sec_remaining > 0:
            self.countdown_stop_flag = True
        if self.game_obj.phase == "Strategy phase":
            self.changePhase()
        elif self.game_obj.phase == "Bidding phase":
            # todo: consider changing it so that the host is notified but not forced to continue ie. incase host is changing some setting
            if globals.DEBUGGING:
                print("Setting up optimization..")
            data = self.createData("status")
            # Changing player status so that looping is prevented
            self.game_obj.host.setAllPlayersNotReady()
            self.sendAll(data)
            self.optimize_label_bidsCount.setText(
                "Bids received: {}".format(len(self.game_obj.host.bids)))
            self.stackedWidget.setCurrentIndex(6)  # page optimize
    """
    Network methods
    """
    def createData(self, header, optional_data=None):
        """
        Header (string) input should be one of:
        playerNumber
        settings
        plants
        demand
        status
        players
        endTime
        start bid round
        start strategy phase
        end game
        kick
        nameCollision
        Returns ready to send data with header readable by receiver to find out how to treat data
        """
        try:
            data = {} # dictionary
            if header == "playerNumber":
                data["header"] = "playerNumber"
                data["playerNumber"] = optional_data # optional data should contain the playerNumber
            elif header == "settings":
                data["header"] = "settings"
                data["years"] = self.game_obj.years
                data["bidRounds"] = self.game_obj.bidRounds
                data["initialMoney"] = self.game_obj.initialMoney
                data["startPlant"] = self.settings_combobox_startingPlant.currentText()
                data["stratTime"] = self.game_obj.getStrategyTime()
                data["bidTime"] = self.game_obj.getBidTime()
                data["co2_tax"] = self.game_obj.co2_tax
                data["gas_fixed_cost"] = self.game_obj.gas_cost_fixed
                data["gas_variable_cost"] = self.game_obj.gas_cost_variable
                data["coal_fixed_cost"] = self.game_obj.coal_cost_fixed
                data["coal_variable_cost"] = self.game_obj.coal_cost_variable
            elif header == "plants":
                data["header"] = header
                # Initiate lists
                data["name"] = []
                data["source"] = []
                data["capacity"] = []
                data["efficiency"] = []
                data["annualCost"] = []
                data["investmentCost"] = []
                data["variableCost"] = []
                data["emissions"] = []
                data["identifier"] = []
                # Get data from newPlants
                for plant in self.game_obj.host.newPlants:
                    data["name"].append(plant.getName())
                    data["source"].append(plant.getSource())
                    data["capacity"].append(plant.getCapacity())
                    data["efficiency"].append(plant.getEfficiency())
                    data["annualCost"].append(plant.getAnnualCost())
                    data["investmentCost"].append(plant.getInvestmentCost())
                    data["variableCost"].append(plant.getVariableCost())
                    data["emissions"].append(plant.getEmissions())
                    data["identifier"].append(plant.getIdentifier())
                self.game_obj.storePlants.extend(self.game_obj.host.newPlants)
                self.game_obj.host.newPlants.clear()
            elif header == "demand":
                data["header"] = "demand"
                # Add expected demand
                data["demand"] = [self.game_obj.expected_demand_fixed, self.game_obj.expected_demand_variable]
            elif header == "status":
                data["header"] = header
                if self.game_obj.phase == "Bidding phase" or self.stackedWidget.currentIndex()==6: # note currentIndex 6 is the waiting page, but it should still be a biding round
                    data["status"] = "clearing market"
                else: data["status"] = None
            elif header == "players":
                data["header"] = "players"
                data["name"] = []
                data["motto"] = []
                data["playerNumber"] = []
                for player in self.game_obj.simple_players:
                    data["name"].append(player.firm_name)
                    data["motto"].append(player.firm_motto)
                    data["playerNumber"].append(player.playerNumber)
            elif header == "endTime":
                data["header"] = header
                data["year"] = self.game_obj.endTime.year
                data["month"] = self.game_obj.endTime.month
                data["day"] = self.game_obj.endTime.day
                data["hour"] = self.game_obj.endTime.hour
                data["minute"] = self.game_obj.endTime.minute
                data["second"] = self.game_obj.endTime.second
            elif header == "start bid phase":
                data["header"] = header
                #data["event"]
                #data["weather"]
            elif header == "new bid round":
                data["header"] = header
            elif header == "start strategy phase":
                data["header"] = header
                # Add new plants
                # Initiate lists
                plants = {}
                plants["name"] = []
                plants["source"] = []
                plants["capacity"] = []
                plants["efficiency"] = []
                plants["annualCost"] = []
                plants["investmentCost"] = []
                plants["variableCost"] = []
                plants["emissions"] = []
                plants["identifier"] = []
                # Get data from newPlants
                for plant in self.game_obj.host.newPlants:
                    plants["name"].append(plant.getName())
                    plants["source"].append(plant.getSource())
                    plants["capacity"].append(plant.getCapacity())
                    plants["efficiency"].append(plant.getEfficiency())
                    plants["annualCost"].append(plant.getAnnualCost())
                    plants["investmentCost"].append(plant.getInvestmentCost())
                    plants["variableCost"].append(plant.getVariableCost())
                    plants["emissions"].append(plant.getEmissions())
                    plants["identifier"].append(plant.getIdentifier())
                self.game_obj.storePlants.extend(self.game_obj.host.newPlants)
                self.game_obj.host.newPlants.clear()
                # add plants to data
                data["plants"] = plants
            elif header == "end game":
                data["header"] = header
            elif header == "kick":
                data["header"] = header
            elif header == "nameCollision":
                data["header"] = header
                data["index"] = optional_data
            else:
                print("Error: the header type: {} is not defined..".format(header))
                # TODO: all the headers without any other data can be treated equally in an else to clean up the code
            return data
        except Exception as e:
            print("Exception in createData:")
            print(e)
    def send(self, data, playerNumber):
        """
        Create a package from the data and send it to a specific number given by their playerNumber. Also sleeps after sending
        to avoid stacking up packages.
        """
        # Serialize data with json
        serialized_data = json.dumps(data)
        # send data
        try:
            self.game_obj.host.getConn(playerNumber).send(serialized_data.encode())
            if globals.DEBUGGING:
                print("Packet {} was sent to player {}".format(data["header"], playerNumber))
        except Exception as e:
            print(e)
            self.game_obj.host.removePlayer(playerNumber)
        finally: time.sleep(0.1) # Sleep a little to avoid stacking packages

    def sendAll(self, data):
        for player in self.game_obj.host.players:
            self.send(data, player.playerNumber)

    def removePlayer(self, playerNumber, notify):
        try:
            player = self.game_obj.host.getPlayer(playerNumber)
            # Find index in combobox in statistics tab by looking for the firm name
            n = self.statistics_combobox_players.findText(player.firm_name)
            # Remove the index from the combobox
            self.statistics_combobox_players.removeItem(n)
            if self.stackedWidget_inner.currentIndex() == 1:
                self.player_status_changed = True
            if notify:
                data = self.createData("kick")
                self.send(data, playerNumber)
            self.game_obj.host.removePlayer(playerNumber)
            self.game_obj.removeSimplePlayer(playerNumber)
            # Set player removd to playerNumber to flag the removal for the background counter
            if globals.DEBUGGING:
                print("Player removed flag set to {}".format(playerNumber))
            if player.firm_name == "Unnamed firm":
                self.player_removed = playerNumber
            else:
                self.player_removed = player.firm_name
            #self.warningCountdown("kick", playerNumber)
            self.game_obj.host.calculate_player_multiplier()
        except Exception as e:
            print(e)

    def findNameCollisions(self, firm_name):
        """
        Look for name collisions in player list and return the number of occurrences. ie. if one collision the last player is called [firm_name]_2 etc.
        """
        occurrences = 1
        for used_name in self.game_obj.host.used_player_names:
            if used_name == firm_name:
                occurrences += 1
        return occurrences

    def initialize_optimization(self):
        try:
            #self.countdown.stop() # set stop flag
            self.countdown_stop_flag = True
        except:
            pass
        self.opt.accepted_bids_count = 0
        bids = self.game_obj.host.getBids()
        # add bids and demand (note that bids is sliced so that a copy of the bids is passed instead of the references
        self.opt.add_data(bids[:], self.game_obj)
        # Start the optimization
        self.opt.start_optimization()
        # Get players results and send to player
        for player in self.game_obj.host.players:
            data = self.opt.create_results(player.playerNumber, self.game_obj.year, self.game_obj.bidRound)
            data["header"] = "optimization"
            self.send(data, player.playerNumber)
            # Store data in host
            player.statistics.profits += data["profits"]
            player.money += data["profits"]
            player.statistics.revenue += data["revenue"]
            player.statistics.cost += data["cost"]
            player.statistics.taxes += data["taxes"]
            player.statistics.emissions += data["emissions"]
        self.opt.store_host_round_results()
        self.game_obj.host.calculate_placements()
        self.draw_transition_results()
        #  Optimization is finished so start new round
        self.changePhase()
        self.opt.clear_values()

    """
    Plotting
    """

    def plot_inside_window(self, layout, bids=None, second_demand_fixed_optional=None, second_demand_variable_optional=None):  # data, flag
        if bids:
            amount_list, price_list = create_plot_lists(bids)
        demand_x_list = [0, self.game_obj.host.demand[0] / self.game_obj.host.demand[1]]
        demand_y_list = [self.game_obj.host.demand[0], 0]
        if second_demand_fixed_optional and second_demand_variable_optional:
            second_demand_x_list = [0, second_demand_fixed_optional / second_demand_variable_optional]
            second_demand_y_list = [second_demand_fixed_optional, 0]
        # Get the demand ie slope and fixed variable
        self.static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.insertWidget(0, self.static_canvas) # Inserted at index = 0 ie. the beginning
        self.addToolBar(NavigationToolbar(self.static_canvas, self))

        self._static_ax = self.static_canvas.figure.subplots()
        if second_demand_fixed_optional and bids:
            self._static_ax.plot(amount_list, price_list, demand_x_list, demand_y_list, second_demand_x_list, second_demand_y_list)
        elif second_demand_fixed_optional and not bids:
            self._static_ax.plot(demand_x_list, demand_y_list, second_demand_x_list, second_demand_y_list)
        elif bids and not second_demand_fixed_optional:
            self._static_ax.plot(amount_list, price_list, demand_x_list, demand_y_list)
        else:
            self._static_ax.plot(demand_x_list, demand_y_list)
        self._static_ax.spines['top'].set_color("white")
        self._static_ax.spines['right'].set_color("white")
        self._static_ax.set_xlabel("MW")
        self._static_ax.set_ylabel("MNOK")
        self._static_ax.set_ylim(0, 3010)

    def statistics_round_results_handle_general_plots(self):
        if not self.game_obj.host.host_statistics.host_round_results:
            return
        self.statistics_tabWidget_general_plots.setEnabled(True)
        self.clear_statistics_round_results_general_graphs()
        if self.statistics_tabWidget_general_plots.currentIndex() == 0: # demand
            self.statistics_tabWidget_general_plots_currentIndex = 0
            self.plot_statistics_round_results_general_demand()
        elif self.statistics_tabWidget_general_plots.currentIndex() == 1: # players
            self.statistics_tabWidget_general_plots_currentIndex = 1
            self.plot_statistics_round_results_general_players_results()

    def plot_statistics_round_results_general_demand(self):
        n = self.statistics_comboBox_round_results.currentIndex()
        layout = self.statistics_round_results_horizontalLayout_demand
        #self.static_canvas_statistics_round_results_demand = FigureCanvas(Figure(figsize=(5, 3)))
        #self.addToolBar(NavigationToolbar(self.static_canvas_statistics_round_results_demand, self))
        #layout.addWidget(self.static_canvas_statistics_round_results_demand)
        #self._static_ax_statistics_round_results_demand = None
        self.plot_inside_window(layout)

    def plot_statistics_round_results_general_players_results(self):
        n = self.statistics_comboBox_round_results.currentIndex()
        layout = self.statistics_round_results_horizontalLayout_players
        self.static_canvas_statistics_round_results_players = FigureCanvas(Figure(figsize=(5, 3)))
        self.addToolBar(NavigationToolbar(self.static_canvas_statistics_round_results_players, self))
        layout.addWidget(self.static_canvas_statistics_round_results_players)
        profits_list = []
        firm_name_list = []
        for player in self.game_obj.host.players:
            profits_list.append(player.statistics.round_results[n]["profits"]/1000000) # mnok
            firm_name_list.append(player.firm_name)
        self._static_ax_statistics_round_results_players = self.static_canvas_statistics_round_results_players.figure.subplots()
        barlist = self._static_ax_statistics_round_results_players.bar(firm_name_list, profits_list, width=0.6)
        self._static_ax_statistics_round_results_players.set_ylabel("Profit [MNOK]")
        for i, bar in enumerate(barlist):
            bar.set_color(globals.standard_color_scheme[i])


    def plot_statistics_performance_graphs(self):
        if len(self.game_obj.host.host_statistics.host_round_results) < 2:
            # No rounds have been played so do not plot
            self.statistics_performance_tabWidget.setEnabled(False)
            return
        self.statistics_performance_tabWidget.setEnabled(True)
        # Clear old plot if it has been drawn
        self.clear_statistics_performance_graphs()
        rounds_list = []
        legend_labels = []
        legend_elements = []
        for round_result in self.game_obj.host.players[0].statistics.round_results:
            rounds_list.append("Year {} b{}".format(round_result["year"], round_result["round"]))
        # Create the canvas
        self.static_canvas_statistics_performance = FigureCanvas(Figure(figsize=(5, 3)))
        self.addToolBar(NavigationToolbar(self.static_canvas_statistics_performance, self))
        # Store the current index to be able to delete the correct plot later
        self.statistics_performance_tabWidget_currentIndex = self.statistics_performance_tabWidget.currentIndex()
        # Get the right layout depending on which tab is selected
        if self.statistics_performance_tabWidget.currentIndex() == 0: # profit
            layout = self.statistics_performance_horizontalLayout_profit
        elif self.statistics_performance_tabWidget.currentIndex() == 1: # Revenue
            layout = self.statistics_performance_horizontalLayout_revenue
        elif self.statistics_performance_tabWidget.currentIndex() == 2: # Cost
            layout = self.statistics_performance_horizontalLayout_cost
        elif self.statistics_performance_tabWidget.currentIndex() == 3: # Emission
            layout = self.statistics_performance_horizontalLayout_emission
        # Add the canvas to the layout
        layout.addWidget(self.static_canvas_statistics_performance)
        self._static_ax_statistics_performance = self.static_canvas_statistics_performance.figure.subplots()
        for player in self.game_obj.host.players:
            legend_labels.append(player.firm_name)
            if self.statistics_performance_tabWidget.currentIndex() == 0:  # profit
                y_list = player.statistics.profit_list
                y_list = [y / 1000000 for y in y_list] # to mnok
                self._static_ax_statistics_performance.set_ylabel("Profit [MNOK]")
            elif self.statistics_performance_tabWidget.currentIndex() == 1:  # Revenue
                y_list = player.statistics.revenue_list
                y_list = [y / 1000000 for y in y_list]  # to mnok
                self._static_ax_statistics_performance.set_ylabel("Revenue [MNOK]")
            elif self.statistics_performance_tabWidget.currentIndex() == 2:  # Cost
                y_list = player.statistics.cost_list
                y_list = [y / 1000000 for y in y_list]  # to mnok
                self._static_ax_statistics_performance.set_ylabel("Cost incl. taxes [MNOK]")
            elif self.statistics_performance_tabWidget.currentIndex() == 3:  # Emission
                y_list = player.statistics.emission_list
                y_list = [y / 1000000 for y in y_list]  # to 1000 ton
                self._static_ax_statistics_performance.set_ylabel("Emission [1000 TON CO2 eq]")
            self._static_ax_statistics_performance.plot(rounds_list, y_list)
            legend_elements.append(Line2D([0], [0], lw=1))
        self._static_ax_statistics_performance.legend(legend_elements, legend_labels, loc="upper right")
        self._static_ax_statistics_performance.spines['bottom'].set_position('zero')
        self._static_ax_statistics_performance.spines['left'].set_position('zero')
        self._static_ax_statistics_performance.spines['top'].set_color("white")
        self._static_ax_statistics_performance.spines['right'].set_color("white")

    #def plot_statistics_round_results_general_graphs(self):
    #    self.statistics_tabWidget_general_plots_currentIndex = self.statistics_tabWidget_general_plots.currentIndex()
    #    if self.statistics_tabWidget_general_plots.currentIndex() == 0: # demand
    #        layout = self.statistics_round_results_horizontalLayout_demand
    #    elif self.statistics_tabWidget_general_plots.currentIndex() == 1: # players
    #        layout = self.statistics_round_results_horizontalLayout_players

    def plot_statistics_round_results_sources_graph(self):
        try:
            market_shares = [self.pv_market_share, self.gas_market_share, self.coal_market_share]
            source_labels = ["PV", "Gas", "Coal"]
            zero_shares = []
            for i, share in enumerate(market_shares):
                if share == 0:
                    zero_shares.append(i)
            for i in zero_shares[::-1]:
                market_shares.pop(i)
                source_labels.pop(i)
            explode_list = [0.05 for i in range(len(source_labels))]
            # Create the canvas
            self.static_canvas_round_results_sources = FigureCanvas(Figure(figsize=(5, 3)))
            self.addToolBar(NavigationToolbar(self.static_canvas_round_results_sources, self))
            # Add canvas to the layout
            self.statistics_round_results_sources_horizontalLayout.addWidget(self.static_canvas_round_results_sources)
            self._static_ax_round_results_sources = self.static_canvas_round_results_sources.figure.subplots()
            self._static_ax_round_results_sources.pie(market_shares, explode=explode_list, labels=source_labels,
                                        autopct="%1.1f%%", shadow=True, startangle=180)
            self._static_ax_round_results_sources.axis("equal")
        except Exception as e:
            print("Exception in plot_info_round_results_sources_graphs:")
            print(e)

    def clear_set_demand_dialog_plot(self):
        """
        Clears the plot created in the set demand dialog window by deleting the canvas widget
        Checks if it exists first
        """
        if self._static_ax:
            self.dialog_set_demand.ui.demand_dialog_verticalLayout.removeWidget(self.static_canvas)
            self.static_canvas.deleteLater()
            self.static_canvas = None
        else:
            pass

    def clear_statistics_performance_graphs(self):
        if self._static_ax_statistics_performance:
            if self.statistics_performance_tabWidget_currentIndex == 0:
                self.statistics_performance_horizontalLayout_profit.removeWidget(self.static_canvas_statistics_performance)
            elif self.statistics_performance_tabWidget_currentIndex == 1:
                self.statistics_performance_horizontalLayout_revenue.removeWidget(self.static_canvas_statistics_performance)
            elif self.statistics_performance_tabWidget_currentIndex == 2:
                self.statistics_performance_horizontalLayout_cost.removeWidget(self.static_canvas_statistics_performance)
            elif self.statistics_performance_tabWidget_currentIndex == 3:
                self.statistics_performance_horizontalLayout_emission.removeWidget(self.static_canvas_statistics_performance)
            self.static_canvas_statistics_performance.deleteLater()
            self.static_canvas_statistics_performance= None
        else:
            pass

    def clear_statistics_round_results_general_graphs(self):
        print("Tab current index is {}".format(self.statistics_tabWidget_general_plots_currentIndex))
        if self.statistics_tabWidget_general_plots_currentIndex == 0:
            print("Clearing demand")
            self.statistics_round_results_horizontalLayout_demand.removeWidget(self.static_canvas)
            self.static_canvas.deleteLater()
            self.static_canvas= None
            self.statistics_tabWidget_general_plots_currentIndex = None
        elif self.statistics_tabWidget_general_plots_currentIndex == 1:
            print("Clearing players")
            self.statistics_round_results_horizontalLayout_players.removeWidget(self.static_canvas_statistics_round_results_players)
            self.static_canvas_statistics_round_results_players.deleteLater()
            self.static_canvas_statistics_round_results_players = None
            self.statistics_tabWidget_general_plots_currentIndex = None
        else: return

    def clear_statistics_round_results_sources_graph(self):
        if self._static_ax_round_results_sources:
            self.statistics_round_results_sources_horizontalLayout.removeWidget(self.static_canvas_round_results_sources)
            self.static_canvas_round_results_sources.deleteLater()
            self.static_canvas_round_results_sources = None