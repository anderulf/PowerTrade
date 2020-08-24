"""


This function runs defines the GUI windows getting the settings from the GUI class files.
It defines the signals and slots, validators and handler functions.

This is done so that the window classes can be changed in the designer without redoing the above mentioned functions.
It also separates the files so that it is easier to read through.

It seems that this file has to run all other stuff in order to get information to print correct information


"""


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtGui import QPalette, QColor
from Main_Window_Player import Ui_MainWindow_Player
from game_client import Game_client
from Resources.classes import Bid
from Resources.AuxillaryMethods import isPositive, isNumber, endTime_to_seconds, number_to_string, create_plot_lists, dict_bids_to_bids_object_list
from dialog_expected_marginal_cost import Ui_dialog_expected_marginal_cost
from dialog_settings import Ui_dialog_settings
import json
import globals
from matplotlib.backends.qt_compat import is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import time

# The functions of the window classes are implemented here (do not edit Main_Window_Player)
class startWindow_player(QtWidgets.QMainWindow, Ui_MainWindow_Player):
    """
    This is the main class. It acts as a platform for the other game mechanics ie. main window and game components
    All methods that change the GUI must be implemented here
    """
    def __init__(self):
        super(startWindow_player, self).__init__()
        # This subclass inherits from its parent Ui_MainWIndow_Player so that its classes are available for it to use
        # set up the game object for the player based on information from host
        self.game_obj = Game_client("player")
        self.font_setting = "mid"

    def setUpSlots(self):
        """
        Signals and slots. The signals (buttons) are connected to the slots (the handlers) defined in other methods
        """
        self.loadingscreen_begin.clicked.connect(self.loadingscreen_handle_button)
        self.create_next.clicked.connect(self.create_handle_button)
        self.connect_next.clicked.connect(self.connect_handle_button)
        self.lobby_button.clicked.connect(self.lobby_handle_button)
        self.start_button_continue.clicked.connect(self.start_handle_button)
        # Buttons for menu bar
        self.button_main.clicked.connect(self.handle_button_main)
        self.button_plants.clicked.connect(self.handle_button_plants)
        self.button_invest.clicked.connect(self.handle_button_invest)
        self.button_market.clicked.connect(self.handle_button_market)
        self.button_info.clicked.connect(self.handle_button_info)
        self.button_quit.clicked.connect(QCoreApplication.instance().quit)                                              # Should give a dialong window if player really wants to quit. Should also notify host
        # Buttons for page: main
        self.main_button_settings.clicked.connect(self.main_handle_button_settings)
        self.main_button_ready.clicked.connect(self.main_handle_button_ready)
        # Buttons for page: invest
        self.invest_button_purchase.clicked.connect(self.invest_handle_button_purchase)
        # Buttons for page: market
        self.market_comboBox_plants.currentIndexChanged.connect(self.market_handle_comboBox)
        self.market_button_sendBids.clicked.connect(self.market_handle_button_sendBids)
        self.market_button_accept_bid1.clicked.connect(self.market_handle_button_save_bid1)
        self.market_button_accept_bid2.clicked.connect(self.market_handle_button_save_bid2)
        self.market_button_accept_bid3.clicked.connect(self.market_handle_button_save_bid3)
        self.market_button_delete_bid1.clicked.connect(self.market_handle_button_delete_bid1)
        self.market_button_delete_bid2.clicked.connect(self.market_handle_button_delete_bid2)
        self.market_button_delete_bid3.clicked.connect(self.market_handle_button_delete_bid3)
        self.market_button_dialog_expected_marginal_cost.clicked.connect(self.market_handle_button_calculator)
        # Widget for page: info
        self.info_tabWidget_plots.currentChanged.connect(self.plot_info_graphs_handle)
        self.info_comboBox_results.currentIndexChanged.connect(self.info_handle_comboBox)
        # Buttons for page: transition
        self.transition_button_next.clicked.connect(self.transition_handle_button_next)
        # Buttons for page: post round
        self.post_round_button_next.clicked.connect(self.transition_handle_button_next)
        self.post_round_button_show_results.clicked.connect(self.post_round_handle_button_show_results)

    def setUpValidators(self):
        """
        The validators are used to limit input data into certain fields
        """
        # Create validator for IP-address
        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"                                                           # ipRange is: 000 to 199 and 200 to 249 and 250 to 255 ie. 0 to 255
        ip_regex = QtCore.QRegExp(
            "^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")                                  # Regular expression defined as xxx.xxx.xxx.xxx
        ip_validator = QtGui.QRegExpValidator(ip_regex)                                                                 # Creating a validator from the regular expression
        self.ipAddressLineEdit.setValidator(ip_validator)
        # float regex for numbers above zero (used in dialog windows)
        float_positive_regex = QtCore.QRegExp("^[0-9]+(?:\.[0-9]+)?$")
        self.float_positive_validator = QtGui.QRegExpValidator(float_positive_regex)
        # Set float regex for bid table in market tab (price and amount)
        self.market_lineEdit_dispatch_bid1.setValidator(self.float_positive_validator)
        self.market_lineEdit_dispatch_bid2.setValidator(self.float_positive_validator)
        self.market_lineEdit_dispatch_bid3.setValidator(self.float_positive_validator)
        self.market_lineEdit_price_bid1.setValidator(self.float_positive_validator)
        self.market_lineEdit_price_bid2.setValidator(self.float_positive_validator)
        self.market_lineEdit_price_bid3.setValidator(self.float_positive_validator)

    def setUpImages(self):
        """
        Set images to labels in the GUI
        """
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Resources/powertrade_icon.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.connect_logo.setPixmap(QtGui.QPixmap("Resources/logo_test_medium.png"))
        self.create_logo.setPixmap(QtGui.QPixmap("Resources/logo_test_medium.png"))
        self.lobby_logo.setPixmap(QtGui.QPixmap("Resources/logo_test_medium.png"))
        self.loadingscreen_logo.setPixmap(QtGui.QPixmap("Resources/logo_test_huge.png"))

    def setUpTheme(self):
        if globals.darkmode == True:
            globals.app.setStyle("Fusion")
            darkPalette = QPalette();
            darkPalette.setColor(QPalette.Window, QColor(53, 53, 53));
            darkPalette.setColor(QPalette.WindowText, QColor(255, 255, 255));
            darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127));
            darkPalette.setColor(QPalette.Base, QColor(42, 42, 42));
            darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66));
            darkPalette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255));
            darkPalette.setColor(QPalette.ToolTipText, QColor(255, 255, 255));
            darkPalette.setColor(QPalette.Text, QColor(255, 255, 255));
            darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127));
            darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35));
            darkPalette.setColor(QPalette.Light, QColor(80, 80, 80));
            darkPalette.setColor(QPalette.Midlight, QColor(66, 66, 66));
            darkPalette.setColor(QPalette.Mid, QColor(40, 40, 40));
            darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20));
            darkPalette.setColor(QPalette.Button, QColor(53, 53, 53));
            darkPalette.setColor(QPalette.ButtonText, QColor(255, 255, 255));
            darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127));
            darkPalette.setColor(QPalette.BrightText, QColor(124, 10, 2));
            darkPalette.setColor(QPalette.Link, QColor(42, 130, 218));
            darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218));
            darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80));
            darkPalette.setColor(QPalette.HighlightedText, QColor(255, 255, 255));
            darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127));
            globals.app.setPalette(darkPalette)
            self.post_round_scrollArea_general.setStyleSheet(
                "background-color: " + globals.darkmode_light_dark_color_styleSheet + ";")
            self.post_round_scrollArea_bids.setStyleSheet(
                "background-color: " + globals.darkmode_light_dark_color_styleSheet + ";")
            self.market_button_sendBids.setStyleSheet(
                "QPushButton {background-color: " + globals.darkmode_color_green_styleSheet + "}" +
                "QPushButton:disabled {background-color: " + globals.darkmode_color_disabled_green_styleSheet + "}")
            self.market_lineEdit_dispatch_bid1.setStyleSheet(
                "QLineEdit { background-color: " + globals.darkmode_light_styleSheet + "}")  # light
            self.market_lineEdit_dispatch_bid2.setStyleSheet(
                "QLineEdit { background-color: " + globals.darkmode_light_styleSheet + "}")
            self.market_lineEdit_dispatch_bid3.setStyleSheet(
                "QLineEdit { background-color: " + globals.darkmode_light_styleSheet + "}")
            self.market_lineEdit_price_bid1.setStyleSheet(
                "QLineEdit { background-color: " + globals.darkmode_light_styleSheet + "}")
            self.market_lineEdit_price_bid2.setStyleSheet(
                "QLineEdit { background-color: " + globals.darkmode_light_styleSheet + "}")
            self.market_lineEdit_price_bid3.setStyleSheet(
                "QLineEdit { background-color: " + globals.darkmode_light_styleSheet + "}")
            self.scrollArea_3.setStyleSheet("")
            self.scrollArea.setStyleSheet("")
            if self.market_button_accept_bid1.isEnabled() == False:
                self.market_button_accept_bid1.setIcon(QtGui.QIcon("Resources/check_arrow_white"))
                self.market_button_accept_bid2.setIcon(QtGui.QIcon("Resources/check_arrow_white"))
                self.market_button_accept_bid3.setIcon(QtGui.QIcon("Resources/check_arrow_white"))
                self.market_button_delete_bid1.setIcon(QtGui.QIcon("Resources/cross_white"))
                self.market_button_delete_bid2.setIcon(QtGui.QIcon("Resources/cross_white"))
                self.market_button_delete_bid3.setIcon(QtGui.QIcon("Resources/cross_white"))
            else:
                self.market_button_accept_bid1.setIcon(QtGui.QIcon("Resources/check_arrow_white"))
                self.market_button_accept_bid2.setIcon(QtGui.QIcon("Resources/check_arrow_white"))
                self.market_button_accept_bid3.setIcon(QtGui.QIcon("Resources/check_arrow_white"))
                self.market_button_delete_bid1.setIcon(QtGui.QIcon("Resources/cross_white"))
                self.market_button_delete_bid2.setIcon(QtGui.QIcon("Resources/cross_white"))
                self.market_button_delete_bid3.setIcon(QtGui.QIcon("Resources/cross_white"))
        else:
            globals.app.setPalette(globals.standard_palette)
            globals.app.setStyle("QtCurve")
            self.post_round_scrollArea_general.setStyleSheet("")
            self.post_round_scrollArea_bids.setStyleSheet(
                "")
            self.market_button_sendBids.setStyleSheet(
                "")
            self.market_lineEdit_dispatch_bid1.setStyleSheet(
                "")  # light
            self.market_lineEdit_dispatch_bid2.setStyleSheet(
                "")
            self.market_lineEdit_dispatch_bid3.setStyleSheet(
                "")
            self.market_lineEdit_price_bid1.setStyleSheet(
                "")
            self.market_lineEdit_price_bid2.setStyleSheet(
                "")
            self.market_lineEdit_price_bid3.setStyleSheet(
                "")
            self.scrollArea_3.setStyleSheet(
                "QScrollArea { background-color: rgb(255,255,255) }")
            self.scrollArea.setStyleSheet(
                "QScrollArea { background-color: rgb(255,255,255) }")
            if self.market_button_accept_bid1.isEnabled() == False:
                self.market_button_accept_bid1.setIcon(QtGui.QIcon("Resources/check_arrow_white_disabled"))
                self.market_button_accept_bid2.setIcon(QtGui.QIcon("Resources/check_arrow_white_disabled"))
                self.market_button_accept_bid3.setIcon(QtGui.QIcon("Resources/check_arrow_white_disabled"))
                self.market_button_delete_bid1.setIcon(QtGui.QIcon("Resources/cross_disabled"))
                self.market_button_delete_bid2.setIcon(QtGui.QIcon("Resources/cross_disabled"))
                self.market_button_delete_bid3.setIcon(QtGui.QIcon("Resources/cross_disabled"))
            else:
                self.market_button_accept_bid1.setIcon(QtGui.QIcon("Resources/check_arrow_black"))
                self.market_button_accept_bid2.setIcon(QtGui.QIcon("Resources/check_arrow_black"))
                self.market_button_accept_bid3.setIcon(QtGui.QIcon("Resources/check_arrow_black"))
                self.market_button_delete_bid1.setIcon(QtGui.QIcon("Resources/cross_black"))
                self.market_button_delete_bid2.setIcon(QtGui.QIcon("Resources/cross_black"))
                self.market_button_delete_bid3.setIcon(QtGui.QIcon("Resources/cross_black"))

    def setUpFonts(self):
        """
        Sets font setting to all labels
        """
        if self.font_setting == "big":
            self.fonts = globals.fonts["big"]
        elif self.font_setting == "mid":
            self.fonts = globals.fonts["mid"]
        elif self.font_setting == "small":
            self.fonts = globals.fonts["small"]
        # Set font to all labels in the game
        self.connect_logo.setFont(self.fonts["title"])
        self.connect_label_info.setFont(self.fonts["big_text"])
        self.ipAddressLabel.setFont(self.fonts["big_text"])
        self.ipAddressLineEdit.setFont(self.fonts["big_text"])
        self.connect_label_warning.setFont(self.fonts["tiny_text"])
        self.connect_next.setFont(self.fonts["big_text"])
        self.create_logo.setFont(self.fonts["title"])
        self.create_introduction.setFont(self.fonts["big_text"])
        self.create_firmNameLabel.setFont(self.fonts["big_text"])
        self.create_firmNameLineEdit.setFont(self.fonts["big_text"])
        self.create_firmMottoLabel.setFont(self.fonts["big_text"])
        self.create_firmMottoLineEdit.setFont(self.fonts["big_text"])
        self.create_label_warning.setFont(self.fonts["tiny_text"])
        self.create_next.setFont(self.fonts["big_text"])
        self.lobby_logo.setFont(self.fonts["title"])
        self.label_6.setFont(self.fonts["big_text"])
        self.label_10.setFont(self.fonts["big_text"])
        self.lobby_label_years.setFont(self.fonts["big_text"])
        self.label_11.setFont(self.fonts["big_text"])
        self.lobby_label_bidRounds.setFont(self.fonts["big_text"])
        self.label_13.setFont(self.fonts["big_text"])
        self.lobby_label_startMoney.setFont(self.fonts["big_text"])
        self.label_16.setFont(self.fonts["big_text"])
        self.lobby_label_startPlant.setFont(self.fonts["big_text"])
        self.label_18.setFont(self.fonts["big_text"])
        self.lobby_label_timeStrategy.setFont(self.fonts["big_text"])
        self.label_20.setFont(self.fonts["big_text"])
        self.lobby_label_timeBid.setFont(self.fonts["big_text"])
        self.label_8.setFont(self.fonts["big_text"])
        self.lobby_label_warning.setFont(self.fonts["tiny_text"])
        self.lobby_button.setFont(self.fonts["big_text"])
        self.start_logo.setFont(self.fonts["title"])
        self.label_15.setFont(self.fonts["big_text"])
        self.start_button_continue.setFont(self.fonts["big_text"])
        self.label_phase.setFont(self.fonts["title"])
        self.label_time.setFont(self.fonts["title"])
        self.label_companyName.setFont(self.fonts["title"])
        self.label_money.setFont(self.fonts["title"])
        self.button_main.setFont(self.fonts["big_text"])
        self.button_plants.setFont(self.fonts["big_text"])
        self.button_invest.setFont(self.fonts["big_text"])
        self.button_market.setFont(self.fonts["big_text"])
        self.button_info.setFont(self.fonts["big_text"])
        self.button_quit.setFont(self.fonts["big_text"])
        self.label_4.setFont(self.fonts["big_text"])
        self.main_label_motto.setFont(self.fonts["big_text"])
        self.main_label_year.setFont(self.fonts["big_text"])
        self.main_label_info.setFont(self.fonts["big_text"])
        self.main_label_warning.setFont(self.fonts["tiny_text"])
        self.main_button_settings.setFont(self.fonts["big_text"])
        self.main_button_ready.setFont(self.fonts["big_text"])
        self.plants_window_title.setFont(self.fonts["big_text"])
        self.label_47.setFont(self.fonts["small_text"])
        self.label_49.setFont(self.fonts["small_text"])
        self.label_46.setFont(self.fonts["small_text"])
        self.label_48.setFont(self.fonts["small_text"])
        self.label_44.setFont(self.fonts["small_text"])
        self.label_45.setFont(self.fonts["small_text"])
        self.label_50.setFont(self.fonts["small_text"])
        self.label_51.setFont(self.fonts["small_text"])
        self.plants_label_warning.setFont(self.fonts["tiny_text"])
        self.invest_window_title.setFont(self.fonts["big_text"])
        self.label_59.setFont(self.fonts["small_text"])
        self.label_54.setFont(self.fonts["small_text"])
        self.label_56.setFont(self.fonts["small_text"])
        self.label_57.setFont(self.fonts["small_text"])
        self.label_58.setFont(self.fonts["small_text"])
        self.label_60.setFont(self.fonts["small_text"])
        self.label_3.setFont(self.fonts["small_text"])
        self.invest_label_warning.setFont(self.fonts["tiny_text"])
        self.label_72.setFont(self.fonts["big_text"])
        self.invest_lineEdit_setName.setFont(self.fonts["big_text"])
        self.invest_button_purchase.setFont(self.fonts["big_text"])
        self.label_5.setFont(self.fonts["big_text"])
        self.label_26.setFont(self.fonts["small_text"])
        self.market_label_bidRound.setFont(self.fonts["small_text"])
        self.label_66.setFont(self.fonts["small_text"])
        self.market_label_hours.setFont(self.fonts["small_text"])
        self.label_25.setFont(self.fonts["small_text"])
        self.market_label_expectedDemand.setFont(self.fonts["small_text"])
        self.label_24.setFont(self.fonts["small_text"])
        self.market_label_gasPrice.setFont(self.fonts["small_text"])
        self.label_17.setFont(self.fonts["small_text"])
        self.market_label_coalPrice.setFont(self.fonts["small_text"])
        self.label_28.setFont(self.fonts["small_text"])
        self.market_label_co2Tax.setFont(self.fonts["small_text"])
        self.label_7.setFont(self.fonts["big_text"])
        self.market_comboBox_plants.setFont(self.fonts["small_text"])
        self.label_12.setFont(self.fonts["small_text"])
        self.market_label_source.setFont(self.fonts["small_text"])
        self.label_19.setFont(self.fonts["small_text"])
        self.market_label_capacity.setFont(self.fonts["small_text"])
        self.label_53.setFont(self.fonts["small_text"])
        self.market_label_actual_capacity.setFont(self.fonts["small_text"])
        self.label_21.setFont(self.fonts["small_text"])
        self.market_label_efficiency.setFont(self.fonts["small_text"])
        self.label_22.setFont(self.fonts["small_text"])
        self.market_label_annualCosts.setFont(self.fonts["small_text"])
        self.label_14.setFont(self.fonts["small_text"])
        self.market_label_variableCost.setFont(self.fonts["small_text"])
        self.label_27.setFont(self.fonts["small_text"])
        self.market_label_emissions.setFont(self.fonts["small_text"])
        self.label_9.setFont(self.fonts["big_text"])
        self.label_37.setFont(self.fonts["small_text"])
        self.market_label_bidsCount.setFont(self.fonts["small_text"])
        self.label_146.setFont(self.fonts["small_text"])
        self.label_147.setFont(self.fonts["small_text"])
        self.label_149.setFont(self.fonts["small_text"])
        self.market_lineEdit_dispatch_bid1.setFont(self.fonts["small_text"])
        self.market_lineEdit_price_bid1.setFont(self.fonts["small_text"])
        self.label_150.setFont(self.fonts["small_text"])
        self.market_lineEdit_dispatch_bid2.setFont(self.fonts["small_text"])
        self.market_lineEdit_price_bid2.setFont(self.fonts["small_text"])
        self.label_151.setFont(self.fonts["small_text"])
        self.market_lineEdit_dispatch_bid3.setFont(self.fonts["small_text"])
        self.market_lineEdit_price_bid3.setFont(self.fonts["small_text"])
        self.market_label_warning.setFont(self.fonts["tiny_text"])
        self.label_35.setFont(self.fonts["big_text"])
        self.market_label_totalBids.setFont(self.fonts["big_text"])
        self.market_button_dialog_expected_marginal_cost.setFont(self.fonts["big_text"])
        self.market_button_sendBids.setFont(self.fonts["big_text"])
        self.label_29.setFont(self.fonts["big_text"])
        self.info_tabWidget_outer.setFont(self.fonts["small_text"])
        self.label_2.setFont(self.fonts["small_text"])
        self.info_label_profit.setFont(self.fonts["small_text"])
        self.label_30.setFont(self.fonts["small_text"])
        self.info_label_revenue.setFont(self.fonts["small_text"])
        self.label_33.setFont(self.fonts["small_text"])
        self.info_label_costs.setFont(self.fonts["small_text"])
        self.label_55.setFont(self.fonts["small_text"])
        self.info_label_taxes.setFont(self.fonts["small_text"])
        self.label_52.setFont(self.fonts["small_text"])
        self.info_label_emissions.setFont(self.fonts["small_text"])
        self.label_65.setFont(self.fonts["small_text"])
        self.info_label_total_capacity.setFont(self.fonts["small_text"])
        self.info_tabWidget_plots.setFont(self.fonts["tiny_text"])
        self.info_comboBox_results.setFont(self.fonts["small_text"])
        self.info_tabWidget_inner.setFont(self.fonts["tiny_text"])
        self.label_39.setFont(self.fonts["small_text"]) # or tiny
        self.round_results_label_hours_bid_on.setFont(self.fonts["small_text"])
        self.label_71.setFont(self.fonts["small_text"])
        self.round_results_label_demand.setFont(self.fonts["small_text"])
        self.label_68.setFont(self.fonts["small_text"])
        self.round_results_label_system_price.setFont(self.fonts["small_text"])
        self.label_110.setFont(self.fonts["small_text"])
        self.round_results_label_used_capacity.setFont(self.fonts["small_text"])
        self.label_85.setFont(self.fonts["small_text"])
        self.round_results_label_production.setFont(self.fonts["small_text"])
        self.label_84.setFont(self.fonts["small_text"])
        self.round_results_label_profits.setFont(self.fonts["small_text"])
        self.label_87.setFont(self.fonts["small_text"])
        self.round_results_label_revenue.setFont(self.fonts["small_text"])
        self.label_86.setFont(self.fonts["small_text"])
        self.round_results_label_costs.setFont(self.fonts["small_text"])
        self.label.setFont(self.fonts["small_text"])
        self.round_results_label_administrative_costs.setFont(self.fonts["small_text"])
        self.label_148.setFont(self.fonts["small_text"])
        self.round_results_label_operational_costs.setFont(self.fonts["small_text"])
        self.label_106.setFont(self.fonts["small_text"])
        self.round_results_label_taxes.setFont(self.fonts["small_text"])
        self.label_89.setFont(self.fonts["small_text"])
        self.round_results_label_emissions.setFont(self.fonts["small_text"])
        self.label_88.setFont(self.fonts["small_text"])
        self.round_results_label_gas_price.setFont(self.fonts["small_text"])
        self.label_74.setFont(self.fonts["small_text"])
        self.round_results_label_gas_fuel.setFont(self.fonts["small_text"])
        self.label_73.setFont(self.fonts["small_text"])
        self.round_results_label_gas_production.setFont(self.fonts["small_text"])
        self.label_70.setFont(self.fonts["small_text"])
        self.round_results_label_coal_price.setFont(self.fonts["small_text"])
        self.label_114.setFont(self.fonts["small_text"])
        self.round_results_label_coal_fuel.setFont(self.fonts["small_text"])
        self.label_115.setFont(self.fonts["small_text"])
        self.round_results_label_coal_production.setFont(self.fonts["small_text"])
        self.label_40.setFont(self.fonts["small_text"])
        self.label_61.setFont(self.fonts["tiny_text"])
        self.info_sources_label_your_production_pv.setFont(self.fonts["tiny_text"])
        self.label_69.setFont(self.fonts["tiny_text"])
        self.info_sources_label_total_production_pv.setFont(self.fonts["tiny_text"])
        self.label_75.setFont(self.fonts["tiny_text"])
        self.info_sources_label_your_market_share_pv.setFont(self.fonts["tiny_text"])
        self.label_76.setFont(self.fonts["tiny_text"])
        self.info_sources_label_source_market_share_pv.setFont(self.fonts["tiny_text"])
        self.label_93.setFont(self.fonts["small_text"])
        self.label_109.setFont(self.fonts["tiny_text"])
        self.info_sources_label_your_production_gas.setFont(self.fonts["tiny_text"])
        self.label_102.setFont(self.fonts["tiny_text"])
        self.info_sources_label_total_production_gas.setFont(self.fonts["tiny_text"])
        self.label_104.setFont(self.fonts["tiny_text"])
        self.info_sources_label_your_market_share_gas.setFont(self.fonts["tiny_text"])
        self.label_105.setFont(self.fonts["tiny_text"])
        self.info_sources_label_source_market_share_gas.setFont(self.fonts["tiny_text"])
        self.label_112.setFont(self.fonts["small_text"])
        self.label_121.setFont(self.fonts["tiny_text"])
        self.info_sources_label_your_production_coal.setFont(self.fonts["tiny_text"])
        self.label_113.setFont(self.fonts["tiny_text"])
        self.info_sources_label_total_production_coal.setFont(self.fonts["tiny_text"])
        self.label_117.setFont(self.fonts["tiny_text"])
        self.info_sources_label_your_market_share_coal.setFont(self.fonts["tiny_text"])
        self.label_118.setFont(self.fonts["tiny_text"])
        self.info_sources_label_source_market_share_coal.setFont(self.fonts["tiny_text"])
        self.label_77.setFont(self.fonts["small_text"])
        self.label_80.setFont(self.fonts["tiny_text"])
        self.label_153.setFont(self.fonts["tiny_text"])
        self.label_81.setFont(self.fonts["tiny_text"])
        self.label_82.setFont(self.fonts["tiny_text"])
        self.label_83.setFont(self.fonts["tiny_text"])
        self.label_90.setFont(self.fonts["tiny_text"])
        self.label_91.setFont(self.fonts["tiny_text"])
        self.label_92.setFont(self.fonts["tiny_text"])
        self.info_label_warning.setFont(self.fonts["big_text"])
        self.label_34.setFont(self.fonts["title"])
        self.transition_label_info.setFont(self.fonts["big_text"])
        self.transition_button_next.setFont(self.fonts["big_text"])
        self.wait_label_countdown.setFont(self.fonts["giant_text"])
        self.wait_label_info.setFont(self.fonts["big_text"])
        self.label_38.setFont(self.fonts["title"])
        self.label_36.setFont(self.fonts["big_text"])
        self.leaderboards_label_placement.setFont(self.fonts["big_text"])
        self.label_63.setFont(self.fonts["big_text"])
        self.label_62.setFont(self.fonts["big_text"])
        self.label_43.setFont(self.fonts["big_text"])
        self.label_64.setFont(self.fonts["big_text"])
        self.label_42.setFont(self.fonts["big_text"])
        self.label_23.setFont(self.fonts["huge_text"])
        self.label_78.setFont(self.fonts["title"])
        self.post_round_label_info.setFont(self.fonts["big_text"])
        self.post_round_tabWidget.setFont(self.fonts["tiny_text"])
        self.label_94.setFont(self.fonts["small_text"])
        self.post_results_label_hours_bid_on.setFont(self.fonts["small_text"])
        self.label_122.setFont(self.fonts["small_text"])
        self.post_results_label_demand.setFont(self.fonts["small_text"])
        self.label_95.setFont(self.fonts["small_text"])
        self.post_results_label_system_price.setFont(self.fonts["small_text"])
        self.label_111.setFont(self.fonts["small_text"])
        self.post_results_label_used_capacity.setFont(self.fonts["small_text"])
        self.label_96.setFont(self.fonts["small_text"])
        self.post_results_label_production.setFont(self.fonts["small_text"])
        self.label_97.setFont(self.fonts["small_text"])
        self.post_results_label_profits.setFont(self.fonts["small_text"])
        self.label_98.setFont(self.fonts["small_text"])
        self.post_results_label_revenue.setFont(self.fonts["small_text"])
        self.label_99.setFont(self.fonts["small_text"])
        self.post_results_label_costs.setFont(self.fonts["small_text"])
        self.label_152.setFont(self.fonts["small_text"])
        self.post_results_label_administrative_costs.setFont(self.fonts["small_text"])
        self.label_154.setFont(self.fonts["small_text"])
        self.post_results_label_operational_costs.setFont(self.fonts["small_text"])
        self.label_107.setFont(self.fonts["small_text"])
        self.post_results_label_taxes.setFont(self.fonts["small_text"])
        self.label_100.setFont(self.fonts["small_text"])
        self.post_results_label_emissions.setFont(self.fonts["small_text"])
        self.label_101.setFont(self.fonts["small_text"])
        self.post_results_label_gas_price.setFont(self.fonts["small_text"])
        self.label_103.setFont(self.fonts["small_text"])
        self.post_results_label_gas_fuel.setFont(self.fonts["small_text"])
        self.label_108.setFont(self.fonts["small_text"])
        self.post_results_label_gas_production.setFont(self.fonts["small_text"])
        self.label_116.setFont(self.fonts["small_text"])
        self.post_results_label_coal_price.setFont(self.fonts["small_text"])
        self.label_119.setFont(self.fonts["small_text"])
        self.post_results_label_coal_fuel.setFont(self.fonts["small_text"])
        self.label_120.setFont(self.fonts["small_text"])
        self.post_results_label_coal_production.setFont(self.fonts["small_text"])
        self.label_123.setFont(self.fonts["small_text"])
        self.label_127.setFont(self.fonts["tiny_text"])
        self.post_results_label_your_production_pv.setFont(self.fonts["tiny_text"])
        self.label_124.setFont(self.fonts["tiny_text"])
        self.post_results_label_total_production_pv.setFont(self.fonts["tiny_text"])
        self.label_125.setFont(self.fonts["tiny_text"])
        self.post_results_label_your_market_share_pv.setFont(self.fonts["tiny_text"])
        self.label_126.setFont(self.fonts["tiny_text"])
        self.post_results_label_source_market_share_pv.setFont(self.fonts["tiny_text"])
        self.label_128.setFont(self.fonts["small_text"])
        self.label_132.setFont(self.fonts["tiny_text"])
        self.post_results_label_your_production_gas.setFont(self.fonts["tiny_text"])
        self.label_129.setFont(self.fonts["tiny_text"])
        self.post_results_label_total_production_gas.setFont(self.fonts["tiny_text"])
        self.label_130.setFont(self.fonts["tiny_text"])
        self.post_results_label_your_market_share_gas.setFont(self.fonts["tiny_text"])
        self.label_131.setFont(self.fonts["tiny_text"])
        self.post_results_label_source_market_share_gas.setFont(self.fonts["tiny_text"])
        self.label_133.setFont(self.fonts["small_text"])
        self.label_137.setFont(self.fonts["tiny_text"])
        self.post_results_label_your_production_coal.setFont(self.fonts["tiny_text"])
        self.label_134.setFont(self.fonts["tiny_text"])
        self.post_results_label_total_production_coal.setFont(self.fonts["tiny_text"])
        self.label_135.setFont(self.fonts["tiny_text"])
        self.post_results_label_your_market_share_coal.setFont(self.fonts["tiny_text"])
        self.label_136.setFont(self.fonts["tiny_text"])
        self.post_results_label_source_market_share_coal.setFont(self.fonts["tiny_text"])
        self.label_138.setFont(self.fonts["small_text"])
        self.label_144.setFont(self.fonts["tiny_text"])
        self.label_155.setFont(self.fonts["tiny_text"])
        self.label_142.setFont(self.fonts["tiny_text"])
        self.label_143.setFont(self.fonts["tiny_text"])
        self.label_139.setFont(self.fonts["tiny_text"])
        self.label_140.setFont(self.fonts["tiny_text"])
        self.label_141.setFont(self.fonts["tiny_text"])
        self.label_145.setFont(self.fonts["tiny_text"])
        self.post_round_button_show_results.setFont(self.fonts["big_text"])
        self.post_round_button_next.setFont(self.fonts["big_text"])

    def setUpMisc(self):
        # Set correct initial pages
        self.stackedWidget.setCurrentIndex(1)
        self.stackedWidget_inner.setCurrentIndex(0)
        self.info_tabWidget_outer.setCurrentIndex(0)
        self.info_tabWidget_inner.setCurrentIndex(0)
        # Table column titles for the page market is often not shown so here it is forced to
        #self.market_table_bids.horizontalHeader().setVisible(True)
        # The warning labels have initial texts so that they can be seen in the designer, but they should not be initially visible ingame
        self.connect_label_warning.setText("")
        self.create_label_warning.setText("")
        self.lobby_label_warning.setText("")
        self.main_label_warning.setText("")
        self.plants_label_warning.setText("")
        self.invest_label_warning.setText("")
        self.market_label_warning.setText("")
        self.info_label_warning.setText("")
        # Set column width for delete button in market table
        # Empty list in info todo: maybe just do this in designer
        self.info_emptyList = QtWidgets.QLabel(self.page_info)
        self.info_verticalLayout_emptyList.addWidget(self.info_emptyList)
        self.info_emptyList.setText("")
        # Combobox in info tab initially disabled
        self.info_comboBox_results.setEnabled(False)
        # Define flags
        self.settings_received_flag = False
        self.countdown_stop_flag = False
        self.connection_failed_flag = False
        self.connection_refused_flag = False
        self.lobby_refresh_timer = QTimer(self)
        # Connect to slot method
        self.lobby_refresh_timer.timeout.connect(self.automatic_lobby_refresh)
        self.countdown = QTimer(self)
        self.countdown.timeout.connect(self.update_countdown)
        self.warnTimer = QTimer(self)
        self.warnTimer.timeout.connect(self.warningCountdownFinished)
        self.warnTimer.setSingleShot(True)  # A single shot timer executes the timeout method only once
        self.background_counter = QTimer(self)
        self.background_counter.timeout.connect(self.background_flag_check)
        self.background_counter.start(20)  # connected method is run every 20 ms (input value given in ms)
        # Set initial value of the boolean keeping track of the results in the transition window
        self.post_results_shown = False
        # Set intial value of the boolean keeping track of the status of rounds results
        self.round_results_drawn = False
        # Initialize spam avoidance iterators
        self.lobby_button_clicks = 0
        self.main_button_clicks = 0
        # Set the headers for the bid table
        # Set correct alignment (as MAC systems uses another alignement rule for forms)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_2.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_2.setFormAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_3.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_3.setFormAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_4.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_4.setFormAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_5.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_5.setFormAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_6.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_6.setFormAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_7.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_7.setFormAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_9.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_9.setFormAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_10.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_10.setFormAlignment(QtCore.Qt.AlignLeft)
        self.transition_formLayout.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.transition_formLayout.setFormAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_12.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.formLayout_12.setFormAlignment(QtCore.Qt.AlignLeft)
        #print(QtGui.QGuiApplication.primaryScreen().logicalDotsPerInch())
        # Set default buttons (triggered aswell with enter button)
        self.connect_next.setDefault(True)
        # Set colors
        if globals.darkmode:
            self.post_round_scrollArea_general.setStyleSheet("background-color: " + globals.darkmode_light_dark_color_styleSheet + ";")
            self.post_round_scrollArea_bids.setStyleSheet("background-color: " + globals.darkmode_light_dark_color_styleSheet + ";")
            self.market_button_sendBids.setStyleSheet("QPushButton {background-color: " + globals.darkmode_color_green_styleSheet + "}" +
                                            "QPushButton:disabled {background-color: " + globals.darkmode_color_disabled_green_styleSheet + "}")
            self.market_lineEdit_dispatch_bid1.setStyleSheet(
                "QLineEdit { background-color: " + globals.darkmode_light_styleSheet + "}") # light
            self.market_lineEdit_dispatch_bid2.setStyleSheet(
                "QLineEdit { background-color: " + globals.darkmode_light_styleSheet + "}")
            self.market_lineEdit_dispatch_bid3.setStyleSheet(
                "QLineEdit { background-color: " + globals.darkmode_light_styleSheet + "}")
            self.market_lineEdit_price_bid1.setStyleSheet(
                "QLineEdit { background-color: " + globals.darkmode_light_styleSheet + "}")
            self.market_lineEdit_price_bid2.setStyleSheet(
                "QLineEdit { background-color: " + globals.darkmode_light_styleSheet + "}")
            self.market_lineEdit_price_bid3.setStyleSheet(
                "QLineEdit { background-color: " + globals.darkmode_light_styleSheet + "}")
            self.market_button_accept_bid1.setIcon(QtGui.QIcon("Resources/check_arrow_white_disabled"))
            self.market_button_accept_bid2.setIcon(QtGui.QIcon("Resources/check_arrow_white_disabled"))
            self.market_button_accept_bid3.setIcon(QtGui.QIcon("Resources/check_arrow_white_disabled"))
            self.market_button_delete_bid1.setIcon(QtGui.QIcon("Resources/cross_disabled"))
            self.market_button_delete_bid2.setIcon(QtGui.QIcon("Resources/cross_disabled"))
            self.market_button_delete_bid3.setIcon(QtGui.QIcon("Resources/cross_disabled"))
            self._static_ax_post_results = None
            self._static_ax_post_results_sources = None

    def background_flag_check(self):
        """
        The method runs a timer which runs in the background and checks for flags and then runs events triggered by these flags
        """
        try:
            if self.connection_failed_flag:
                if globals.DEBUGGING:
                    print("Connection failed flag check triggered")
                self.warningCountdown("connection failed")
                self.connection_failed_flag = False
            elif self.connection_refused_flag:
                if globals.DEBUGGING:
                    print("Connection refuse flag check triggered")
                self.warningCountdown("connection refused")
                self.connection_refused_flag = False
            elif self.settings_received_flag == True:
                self.settings_received_flag = False
                # Set labels in lobby
                self.lobby_label_years.setText(str(self.game_obj.years))
                self.lobby_label_bidRounds.setText(str(self.game_obj.bidRounds))
                self.lobby_label_startMoney.setText(number_to_string(self.game_obj.initialMoney, "MNOK"))
                self.lobby_label_startPlant.setText(self.game_obj.startPlant)
                self.lobby_label_timeStrategy.setText(self.game_obj.strategyTime)
                self.lobby_label_timeBid.setText(self.game_obj.bidTime)
            elif self.game_obj.host_status:
                if self.game_obj.host_status == "start strategy phase":
                    self.game_obj.host_status = ""
                    # Flag set from incoming host packet but changed here
                    self.label_phase.setText(self.game_obj.phase)
                    self.main_label_year.setText(
                        "Year {}/{}".format(self.game_obj.year, self.game_obj.years))
                    #self.transition_label_info.setText("The bidding phase has ended. Click button to show results. The strategy phase will start shortly.")
                    self.market_button_sendBids.setEnabled(False)
                    self.invest_button_purchase.setEnabled(True)
                    self.post_round_button_show_results.setEnabled(True)
                    self.main_button_ready.setChecked(True)
                    self.market_label_bidsCount.setText("0")
                    self.market_label_totalBids.setText("0")
                    self.label_money.setText(number_to_string(self.game_obj.player.money, "MNOK"))
                    self.clearWindow()
                    self.stackedWidget.setCurrentIndex(10)
                elif self.game_obj.host_status == "start bid phase":
                    self.game_obj.host_status = ""
                    self.label_phase.setText(self.game_obj.phase + " {}/{}".format(self.game_obj.bidRound,
                                                                                                 self.game_obj.bidRounds))
                    #self.transition_label_info.setText("The strategy phase has ended. The bidding round will now start")
                    self.market_button_sendBids.setEnabled(True)
                    self.invest_button_purchase.setEnabled(False)
                    self.main_button_ready.setChecked(True)
                    self.clearWindow()
                    self.stackedWidget.setCurrentIndex(6)
                elif self.game_obj.host_status == "clearing market":
                    self.game_obj.host_status = ""
                    self.game_obj.player.status = "Not ready"
                    self.wait_label_info.setText("Waiting for host to clear market")
                    try:  # Stop the countdown if it hasn't stopped already
                        self.countdown.stop()
                        self.wait_label_countdown.setText("")
                    except:
                        pass
                    finally:
                        self.stackedWidget.setCurrentIndex(7)
                elif self.game_obj.host_status == "market cleared":
                    self.stackedWidget.setCurrentIndex(10)
                    self.post_round_button_show_results.setEnabled(True)
                elif self.game_obj.host_status == "new bid round":
                    self.game_obj.host_status = ""
                    self.label_phase.setText(self.game_obj.phase + " {}/{}".format(self.game_obj.bidRound,
                                                                                                 self.game_obj.bidRounds))
                    #self.transition_label_info.setText("The bidding round has ended. Click button to show results. The next round will start shortly")
                    self.post_round_button_show_results.setEnabled(True)
                    self.main_button_ready.setChecked(True)
                    self.label_money.setText(number_to_string(self.game_obj.player.money, "MNOK"))
                    self.market_label_bidsCount.setText("0")
                    self.market_label_totalBids.setText("0")
                    self.clearWindow()
                    self.stackedWidget.setCurrentIndex(10)
                elif self.game_obj.host_status == "end game":
                    # Players send some data to host and then the host will respons witt placement ready
                    if globals.DEBUGGING:
                        print("end game flag checked")
                    self.game_obj.host_status = ""
                    self.post_round_label_info.setText(
                        "The game has now ended! Click show results to show the results from this round. Click next to show the leaderboards")
                    self.post_round_button_show_results.setEnabled(True)
                    self.post_round_button_next.setEnabled(False)
                    self.clearWindow()
                    #self.stackedWidget.setCurrentIndex(10)
                    self.game_obj.phase = "End game"
                    data = self.createData("end game")
                    self.send(data)
                elif self.game_obj.host_status == "placement ready":
                    self.game_obj.host_status = ""
                    self.transition_button_next.setEnabled(True)
                    self.post_round_button_next.setEnabled(True)
                elif self.game_obj.host_status == "next phase ready":
                    self.game_obj.host_status = ""
                    self.transition_button_next.setEnabled(True)
                    self.post_round_button_next.setEnabled(True)
                elif self.game_obj.host_status == "start game":
                    self.game_obj.host_status = ""
                    self.stackedWidget.setCurrentIndex(4)
                elif self.game_obj.host_status == "kicked":
                    self.stackedWidget.setCurrentIndex(9)
                elif self.game_obj.host_status == "connected to host":
                    self.game_obj.host_status = ""
                    self.stackedWidget.setCurrentIndex(2)
            else: return # no flags set
        except Exception as e:
            print("Exception in background_flag_check()")
            print("Host status for exception is: {}".format(self.game_obj.host_status))
            print(e)

    #### Button handlers ####
    """
    The button handlers are methods that define the action of triggers in the GUI ie. changing the window
    if a button is clicked 
    """
    def loadingscreen_handle_button(self):
        self.stackedWidget.setCurrentIndex(1)

    def connect_handle_button(self):
        ip = self.ipAddressLineEdit.text()
        #port = self.portLineEdit.text()
        #if (not hostIP.strip()) or (not port.strip()) or hostIP.count(".") != 3:                                      # Checks that field is nonempty (also for whitespaces) and that that IP-address has correct format (three dots)
        if (not ip.strip()) or ip.count(".") != 3:
            # Show error message
            self.warningCountdown("invalidIP")
        else: # Inputted IP has valid format
            self.game_obj.setIp(ip)
            self.warningCountdown("connecting")
            #self.stackedWidget.setCurrentIndex(2)

    def create_handle_button(self):
        firm_name = self.create_firmNameLineEdit.text()  # Inputed text in the line edit is exported when the button is clicked by using the member function text()
        firm_motto = self.create_firmMottoLineEdit.text()
        if not firm_name.strip():  # Checks that the field is nonempty (also for whitespaces)
            self.warningCountdown("invalidName")
        elif not firm_motto.strip():
            self.warningCountdown("invalidMotto")
        else:
            self.game_obj.player.setName(firm_name.strip())
            self.game_obj.player.setMotto(firm_motto.strip())
            # Send data to host
            data = self.createData("info")
            self.send(data)
            #self.lobby_name_player.setText(self.game_obj.player.firm_name)
            # Draw the lobby initially
            self.drawLobby()
            # Set number of players to zero
            self.num_players = 0
            # Start  the timer
            self.lobby_refresh_timer.start(100)  # argument is update frequency in ms
            # Check if name was edited due to name collision with other player(s)
            if firm_name != self.game_obj.player.firm_name:
                self.warningCountdown("name collision")
            self.stackedWidget.setCurrentIndex(3)

    def lobby_handle_button(self):
        self.lobby_button_clicks += 1
        if self.lobby_button_clicks > 5:
            self.warningCountdown("lobby button spam")
            self.lobby_button.setEnabled(False)
            self.game_obj.player.status = "Ready"
        elif self.player_widget_status.text() == "Not ready":
            self.game_obj.player.status = "Ready"
            self.warningCountdown("lobby ready")
        elif self.player_widget_status.text() == "Ready":
            self.game_obj.player.status = "Not ready"
            self.warningCountdown("lobby not ready")
        data = self.createData("status")
        self.send(data)
        self.player_widget_status.setText(self.game_obj.player.status)


    def start_handle_button(self):
        # stop lobby refresh
        self.lobby_refresh_timer.stop()
        # Start game timer
        self.startCountdown()
        # Based on initial plant settings
        if self.lobby_label_startPlant.text() == "Gas" or self.lobby_label_startPlant.text() == "PV" or self.lobby_label_startPlant.text() == "Coal":
            self.game_obj.player.appendPlants(self.game_obj.getStorePlants())
            self.game_obj.removePlant(0)
        elif self.lobby_label_startPlant.text() == "Free choice":
            for index in range(0, len(self.game_obj.storePlants)):
                self.game_obj.storePlants[index].setInvestmentCost(0)
        # Set correct data for the labels
        self.label_companyName.setText(self.game_obj.player.getName())
        self.main_label_motto.setText("\"" + self.game_obj.player.getMotto() + "\"")
        self.main_label_year.setText("Year: {}/{}".format(self.game_obj.year, self.game_obj.years))
        self.main_label_info.setText(
            "Some info about the current phase and where to go.")  # TODO: when text is gotten from excel update this
        self.label_phase.setText(self.game_obj.getPhase())
        self.label_money.setText(number_to_string(self.game_obj.initialMoney, "MNOK"))
        self.market_label_hours.setText(number_to_string(8760/self.game_obj.bidRounds, "hours"))
        self.market_label_co2Tax.setText(number_to_string(self.game_obj.co2_tax, "NOK/(kg CO<sub>2</sub>eq)"))
        self.market_label_gasPrice.setText("{}+{}*gas demand [NOK/MWh]".format(self.game_obj.gas_cost_fixed, self.game_obj.gas_cost_variable))
        self.market_label_coalPrice.setText("{}+{}*coal demand [NOK/MWh]".format(self.game_obj.coal_cost_fixed, self.game_obj.coal_cost_variable))
        self.handle_button_main()
        self.stackedWidget.setCurrentIndex(5)


    def handle_button_main(self):
        self.uncheck_buttons()
        self.button_main.setChecked(True)                                                           # Checked to indicate that this tab is the current tab
        self.clearWindow()
        self.stackedWidget_inner.setCurrentIndex(0)

    def handle_button_plants(self):
        self.uncheck_buttons()
        self.button_plants.setChecked(True)                                                         # Checked to indicate that this tab is the current tab
        if self.stackedWidget_inner.currentIndex()==1:                                              # If the current page is the same it is not refreshed in order to increase performance
            return
        self.clearWindow()
        self.stackedWidget_inner.setCurrentIndex(1)
        self.drawPlants()

    def handle_button_invest(self):
        self.uncheck_buttons()
        self.button_invest.setChecked(True)
        if self.stackedWidget_inner.currentIndex()==2:
            return
        self.clearWindow()
        self.stackedWidget_inner.setCurrentIndex(2)
        self.drawStore()

    def handle_button_market(self):
        if not self.game_obj.player.plants:
            self.market_comboBox_plants.setEnabled(False)
        self.uncheck_buttons()
        self.button_market.setChecked(True)
        self.clearWindow()
        self.drawMarket()
        # Do not allow anything
        if not self.game_obj.player.plants:
            self.market_button_sendBids.setEnabled(False)
            #self.market_button_placeBids.setEnabled(False)
        # Allow saving bids
        elif self.game_obj.phase == "Strategy phase":
            self.market_button_sendBids.setEnabled(False)
            #self.market_button_placeBids.setEnabled(True)
        # Allow everything
        else:
            self.market_button_sendBids.setEnabled(True)
            #self.market_button_placeBids.setEnabled(True)
        self.stackedWidget_inner.setCurrentIndex(3)

    def handle_button_info(self):
        """

        """
        try:
            self.uncheck_buttons()
            self.button_info.setChecked(True)
            self.clearWindow()
            # Set the currentIndex of the tabWidget and a copy of this to see if it has changed
            self.info_tabWidget_currentIndex = 0
            self.info_tabWidget_plots.setCurrentIndex(0)
            self.plot_info_graphs_handle()
            #TODO Write round result from first round if only this result exists
            if self.game_obj.player.statistics.round_results:
                self.drawRoundResults()
                self.round_results_drawn = True
            self.stackedWidget_inner.setCurrentIndex(4)
        except Exception as e:
            print("Exception in handle_button_info(): ")
            print(e)

    def main_handle_button_settings(self):
        """
        Open the dialog window the calculating the expected marginal cost of different plants.
        """
        # Initialize dialog window
        self.dialog_settings = QtWidgets.QDialog()
        # Set GUI wrapper
        self.dialog_settings.ui = Ui_dialog_settings()
        # Initialize the design onto the dialog using the wrapper
        self.dialog_settings.ui.setupUi(self.dialog_settings)
        # Set up slots for the input and combobox
        self.dialog_settings.ui.dialog_settings_button_apply.clicked.connect(
            self.dialog_settings_apply)
        self.dialog_settings.ui.dialog_settings_button_close.clicked.connect(
            self.dialog_settings_close)
        # Make it so that only the dialog window can be used when it is open
        self.dialog_settings.setModal(True)
        # Get current settings
        if globals.darkmode == True:
            self.dialog_settings.ui.dialog_settings_horizontalSlider_theme.setValue(0)
        else:
            self.dialog_settings.ui.dialog_settings_horizontalSlider_theme.setValue(1)
        if self.font_setting == "small":
            self.dialog_settings.ui.dialog_settings_horizontalSlider_text_size.setValue(0)
        elif self.font_setting == "mid":
            self.dialog_settings.ui.dialog_settings_horizontalSlider_text_size.setValue(1)
        else:
            self.dialog_settings.ui.dialog_settings_horizontalSlider_text_size.setValue(2)
        # Show the dialog window
        self.dialog_settings.show()
        self.dialog_settings.exec_()

    def dialog_settings_apply(self):
        if self.dialog_settings.ui.dialog_settings_horizontalSlider_theme.value() == 0:
            globals.darkmode = True
        else:
            globals.darkmode = False
        if self.dialog_settings.ui.dialog_settings_horizontalSlider_text_size.value() == 0:
            self.font_setting = "small"
        elif self.dialog_settings.ui.dialog_settings_horizontalSlider_text_size.value() == 1:
            self.font_setting = "mid"
        else:
            self.font_setting = "big"
        self.setUpTheme()
        self.setUpFonts()

    def dialog_settings_close(self):
        self.dialog_settings.close()

    def main_handle_button_ready(self):
        self.main_button_clicks += 1
        if self.main_button_clicks > 7:
            self.main_button_ready.setEnabled(False)
            self.warningCountdown("main button spam")
            self.game_obj.player.status = "Ready"
            pixmap = QtGui.QPixmap()
            pixmap.load("Resources/check_arrow_green.png")
            pixmap = pixmap.scaledToHeight(20)
            self.label_ready_icon.setPixmap(pixmap)
            return
        elif self.main_button_ready.isChecked():
            self.game_obj.player.status = "Ready"
            pixmap = QtGui.QPixmap()
            pixmap.load("Resources/check_arrow_green.png")
            pixmap = pixmap.scaledToHeight(20)
            self.label_ready_icon.setPixmap(pixmap)
        elif not self.main_button_ready.isChecked():
            self.game_obj.player.status = "Not ready"
            self.label_ready_icon.setPixmap(QtGui.QPixmap(""))
        data = self.createData("status")
        self.send(data)
        self.warningCountdown("status")

    def invest_handle_button_purchase(self):
        # Cannot buy plants during bidding phase (cannot bid without plant (catch 22))
        if self.game_obj.phase == "Bidding phase":
            self.warningCountdown("buyInBidPhase")
            return
        # First check if store is empty
        elif len(self.game_obj.getStorePlants()) == 0:
            self.warningCountdown("noPlantsInStore")
            return
        n = self.radiobutton_getToggled()
        if n == -1:
            self.warningCountdown("noPlantChosen")
            return
        # Try to buy the plant
        self.buyPlant(n)
        # clears the window
        self.clearWindow()
        # Rebuilds the window without the bought plant
        self.drawStore()
        # Remove the text from the name line edit
        self.invest_lineEdit_setName.clear()

    def market_handle_comboBox(self):
        """
        The handler is triggered by a change in the current index of the combo box
        """
        # Clear the contents of the table
        self.clearBidTable()
        # Find out which plant is currently active
        index = self.market_comboBox_plants.currentIndex()
        plant = self.game_obj.player.getPlant(index)
        # Set plant data to labels
        self.market_label_source.setText(plant.getSource())
        self.market_label_capacity.setText(number_to_string(plant.getCapacity(), "MW"))
        if plant.isDispatchable():
            self.market_label_actual_capacity.setText(number_to_string(plant.capacity, "MW"))
        else:
            self.market_label_actual_capacity.setText(number_to_string(plant.getActualCapacity(self.game_obj.weather_effect), "MW"))
        self.market_label_efficiency.setText(number_to_string(plant.getEfficiency(), "%"))
        self.market_label_annualCosts.setText(number_to_string(plant.getAnnualCost(), "MNOK/year"))
        self.market_label_variableCost.setText(number_to_string(plant.getVariableCost(), "NOK/MWh"))
        self.market_label_emissions.setText(number_to_string(plant.getEmissions(), "kg CO<sub>2</sub>eq/MWh"))
        self.market_label_bidsCount.setText(str(len(self.game_obj.player.getPlantBids(plant))))
        # Draw the bid table
        self.drawBidTable()

    def market_handle_button_save_bid1(self):
        try:
            row = 0
            amount = self.market_lineEdit_dispatch_bid1.text()
            price = self.market_lineEdit_price_bid1.text()
            self.market_saveBids(row, amount, price)
        except Exception as e:
            print("Exception in market_handle_button_save_bid1")
            print(e)

    def market_handle_button_save_bid2(self):
        try:
            row = 1
            amount = self.market_lineEdit_dispatch_bid2.text()
            price = self.market_lineEdit_price_bid2.text()
            self.market_saveBids(row, amount, price)
        except Exception as e:
            print("Exception in market_handle_button_save_bid2")
            print(e)

    def market_handle_button_save_bid3(self):
        try:
            row = 2
            amount = self.market_lineEdit_dispatch_bid3.text()
            price = self.market_lineEdit_price_bid3.text()
            self.market_saveBids(row, amount, price)
        except Exception as e:
            print("Exception in market_handle_button_save_bid3")
            print(e)

    def market_saveBids(self, row, amount, price):
        """
        The method is triggered by clicking the place bids button. It fetches, edits or deletes the bids in the table
        """
        try:
            n = self.market_comboBox_plants.currentIndex()
            plant = self.game_obj.player.getPlant(n)
            bids = self.game_obj.player.getBids()
            # If the bid is nonempty. Check if it's valid and save or edit bid if it is.
            if amount == "" and price == "":
                # Remove it if the bid exists in the players bid list
                self.game_obj.player.removeBid(row, plant)
            elif isNumber(amount) and isNumber(price):
                if globals.DEBUGGING:
                    print("Saving bid")
                # Create bid from data
                bid = Bid(self.game_obj.player.getNumber(), plant, float(amount), float(price))
                # Set number of bid so that it is remembered if the window is redrawn
                bid.setNumber(row)
                # place the bid (the method also handles editing of existing bids, or too high capacity)
                self.addOrEditBid(bid)
            else:
                # Invalid bid show some warning
                self.warningCountdown("invalidBid")
            self.market_label_bidsCount.setText(str(len(self.game_obj.player.getPlantBids(plant))))
            self.market_label_totalBids.setText(str(len(self.game_obj.player.bids)))
            # Clear existing plot
            self.clear_market_plot()
            # Plot bids
            self.plot_market_graph()
        except Exception as e:
            print("Exception in market_saveBids:")
            print(e)

    def market_handle_button_sendBids(self):
        data = self.createData("bids")
        self.send(data)
        self.stackedWidget.setCurrentIndex(7)

    def market_handle_button_delete_bid1(self):
        self.market_deleteBid(0)

    def market_handle_button_delete_bid2(self):
        self.market_deleteBid(1)

    def market_handle_button_delete_bid3(self):
        self.market_deleteBid(2)

    def market_deleteBid(self, row):
        n = self.market_comboBox_plants.currentIndex()
        plant = self.game_obj.player.getPlant(n)
        try:
            self.game_obj.player.removeBid(row, plant)
        except:
            self.warningCountdown("noBidToDelete")
        if row == 0:
            self.market_lineEdit_dispatch_bid1.setText("")
            self.market_lineEdit_price_bid1.setText("")
        elif row == 1:
            self.market_lineEdit_dispatch_bid2.setText("")
            self.market_lineEdit_price_bid2.setText("")
        elif row == 2:
            self.market_lineEdit_dispatch_bid3.setText("")
            self.market_lineEdit_price_bid3.setText("")
        else:
            print("Warning: row {} is not defined in market_deleteBid".format(row))
            return
        self.market_label_bidsCount.setText(str(len(self.game_obj.player.getPlantBids(plant))))
        self.market_label_totalBids.setText(str(len(self.game_obj.player.bids)))
        self.clearBidTable()
        self.drawBidTable()
        # Clear existing plot
        self.clear_market_plot()
        # Draw new plot
        self.plot_market_graph()

    def market_handle_button_calculator(self):
        """
        Open the dialog window the calculating the expected marginal cost of different plants.
        """
        # Initialize dialog window
        self.dialog_expected_marginal_cost = QtWidgets.QDialog()
        # Set GUI wrapper
        self.dialog_expected_marginal_cost.ui = Ui_dialog_expected_marginal_cost()
        # Initialize the design onto the dialog using the wrapper
        self.dialog_expected_marginal_cost.ui.setupUi(self.dialog_expected_marginal_cost)
        # Set up slots for the input and combobox
        self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_plant_comboBox.currentIndexChanged.connect(self.dialog_expected_marginal_cost_handle_comboBox)
        self.dialog_expected_marginal_cost.ui.dialog_expected_marginal_cost_button_calculate.clicked.connect(self.dialog_expected_marginal_cost_handle_button_calculate)
        self.dialog_expected_marginal_cost.ui.dialog_expected_marginal_cost_button_close.clicked.connect(self.dialog_expected_marginal_cost_handle_button_close)
        # Enable validators for input fields
        self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_own_production_lineEdit.setValidator(self.float_positive_validator)
        self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_total_production_lineEdit.setValidator(self.float_positive_validator)
        # Make it so that only the dialog window can be used when it is open
        self.dialog_expected_marginal_cost.setModal(True)
        # Add items to the combobox
        for plant in self.game_obj.player.plants:
            self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_plant_comboBox.addItem(plant.name)
        # Show the dialog window
        self.dialog_expected_marginal_cost.show()
        self.dialog_expected_marginal_cost.exec_()

    def dialog_expected_marginal_cost_handle_comboBox(self):
        """
        Method is triggere by a change in the current index of the combobox in the dialog window for calculating expected marginal cost
        """
        # Find out which plant is currently active
        index = self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_plant_comboBox.currentIndex()
        self.dialog_expected_marginal_cost.plant = self.game_obj.player.getPlant(index)
        # Set label of fuel price
        if self.dialog_expected_marginal_cost.plant.source == "Coal":
            self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_source.setText("Coal")
            self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_fuel_cost.setText("{}+{}Q".format(self.game_obj.coal_cost_fixed, self.game_obj.coal_cost_variable))
        elif self.dialog_expected_marginal_cost.plant.source == "Gas":
            self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_source.setText("Gas")
            # Set label of fuel price
            self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_fuel_cost.setText(
                "{}+{}Q".format(self.game_obj.gas_cost_fixed, self.game_obj.gas_cost_variable))
        elif self.dialog_expected_marginal_cost.plant.source == "PV":
            self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_source.setText("PV")
            # Set label of fuel price
            self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_fuel_cost.setText("0")
        else:
            print("Error source {} has not been defined in dialog_expected_marginal_cost".format(self.dialog_expected_marginal_cost.plant.source))
        # Set other plant data to labels
        self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_variable_cost.setText(number_to_string(self.dialog_expected_marginal_cost.plant.variableCost))
        if self.dialog_expected_marginal_cost.plant.isDispatchable():
            self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_capacity.setText(
                number_to_string(self.dialog_expected_marginal_cost.plant.capacity))
        else:
            self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_capacity.setText(
                number_to_string(self.dialog_expected_marginal_cost.plant.getActualCapacity(self.game_obj.weather_effect)))

    def dialog_expected_marginal_cost_handle_button_calculate(self):
        """
        Calculate the expected marginal cost and the production
        """
        hours = 8760/self.game_obj.bidRounds # hours bid on
        if self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_own_production_lineEdit.text() == "":
            own_production = 0
        else:
            own_production = float(self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_own_production_lineEdit.text()) * hours
        if self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_total_production_lineEdit.text() == "":
            total_production = own_production
        else:
            total_production = own_production + float(self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_total_production_lineEdit.text()) * hours
        # Calculate marginal cost from fuel
        if self.dialog_expected_marginal_cost.plant.source == "PV":
            fuel_cost = 0
        elif self.dialog_expected_marginal_cost.plant.source == "Coal":
            fuel_cost = self.game_obj.coal_cost_variable * total_production
        elif self.dialog_expected_marginal_cost.plant.source == "Gas":
            fuel_cost = self.game_obj.coal_cost_variable * total_production
            print(self.dialog_expected_marginal_cost.plant.variableCost)
        co2_addition = self.dialog_expected_marginal_cost.plant.emissions * self.game_obj.co2_tax
        marginal_cost = self.dialog_expected_marginal_cost.plant.variableCost + fuel_cost + co2_addition

        self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_label_production.setText(number_to_string(own_production/1000)) # to GWh
        self.dialog_expected_marginal_cost.ui.dialog_marginal_cost_label_calculated_marginal_cost.setText(number_to_string(marginal_cost))

    def dialog_expected_marginal_cost_handle_button_close(self):
        # Close window
        self.dialog_expected_marginal_cost.close()

    def info_handle_comboBox(self):
        """
        Triggered by a change in the current index of the combobox for the bid results
        Triggers:   player enters another item in the combobox
                    player enters info tab
        """
        try:
            # Clear the current round results but only if some round result has been written
            if self.round_results_drawn:
                if globals.DEBUGGING:
                    print("Results exists, so old results are cleared before drawing new results")
                self.clearRoundResults()
                if globals.DEBUGGING:
                    print("Results were cleared")
                self.round_results_drawn = False
            # Draw the round results

            self.drawRoundResults() # round_results_drawn flag set if drawing is successful
            if globals.DEBUGGING:
                print("New results were drawn")

        except Exception as e:
            print("Exception in info_handle_comboBox")
            print(e)

    def transition_handle_button_next(self):
        """
        Start the new phase.
        """
        if globals.DEBUGGING:
            print("Starting new phase")
        # Reset the countdown stop flag
        self.countdown_stop_flag = False
        if self.game_obj.phase == "End game":
            self.drawLeaderboard()
            self.stackedWidget.setCurrentIndex(8)
            return
        elif self.game_obj.phase == "Strategy phase" or self.game_obj.bidRound > 1:
            # elif True if a bid round has finished

            if self.post_results_shown:
                self.clearTransitionResults()
            # Update players money
            self.label_money.setText(number_to_string(self.game_obj.player.money, "MNOK"))
            # Reset the boolean results_shown for the transition window
            self.post_results_shown = False
            # Add new item to round results
            if len(self.game_obj.player.statistics.round_results) > 1:
                if globals.DEBUGGING:
                    print("transition_handle_button_next(): Debugging - item added to combobox")
                self.info_comboBox_results.addItem(
                    "Year {} round {}".format(self.game_obj.player.statistics.round_results[-1]["year"],
                                              self.game_obj.player.statistics.round_results[-1]["round"]))
            self.updateInfo()
        self.handle_button_main()
        # Reset ready button in main
        self.main_button_ready.setEnabled(True)
        self.main_button_ready.setChecked(False)
        self.label_ready_icon.setPixmap(QtGui.QPixmap())
        self.transition_button_next.setEnabled(False)
        self.post_round_button_next.setEnabled(False)
        self.post_round_button_show_results.setEnabled(False)
        # Reset the timer color
        if globals.darkmode:
            self.label_time.setStyleSheet("QLabel {color: " + globals.darkmode_color_white_styleSheet + "}")
        else:
            self.label_time.setStyleSheet("QLabel {color : black; }")
        self.main_button_clicks = 0
        # Reset the tab widget so that the general tab opens the next time the results are shown
        self.post_round_tabWidget.setCurrentIndex(0)
        # Start countdown
        self.startCountdown()
        self.stackedWidget.setCurrentIndex(5)
        self.post_results_shown = False

    def post_round_handle_button_show_results(self):
        self.post_results_shown = True
        self.drawTransitionResults()
        self.post_round_button_show_results.setEnabled(False)

    #### Other methods ####
    """
    These methods are methods needed to change aspects of the GUI ie. the text of labels or contents in a grid layout etc.
    """

    def startCountdown(self):
        """
        Start the countdown.
        Calculate the remaining seconds first, and initialize the triggered method once.
        :return:
        """
        self.sec_remaining = endTime_to_seconds(self.game_obj.endTime)
        self.countdown.start(500)
        self.update_countdown()

    def update_countdown(self):
        """
        Method is run everytime the timer times out ie every 100ms or so
        """
        # Calculate seconds remaining from end time of the timer
        self.sec_remaining = endTime_to_seconds(self.game_obj.endTime)
        if self.sec_remaining == 10:
            # Set red warning color of clock
            self.trigger = True
            if globals.darkmode:
                self.label_time.setStyleSheet("QLabel {color : " + globals.darkmode_color_red_styleSheet + "}")
            else:
                self.label_time.setStyleSheet("QLabel {color : red; }")
        """
        # Code for flashing red screen
        if self.game_obj.phase == "Bidding phase" and self.sec_remaining <= 10:
            self.trigger = not self.trigger
            if self.trigger:
                if globals.darkmode:
                    self.label_time.setStyleSheet("QLabel {color : " + globals.darkmode_color_red_styleSheet + "}")
                else:
                    self.label_time.setStyleSheet("QLabel {color : red; }")
            else:
                self.centralwidget.setStyleSheet("background-color: ")
        """
        timeString = time.strftime("%M:%S", time.gmtime(self.sec_remaining))
        self.label_time.setText(timeString)
        self.wait_label_countdown.setText(timeString)
        # Act from timeout or other stop triggers
        if self.sec_remaining == 0 or self.countdown_stop_flag:
            if globals.DEBUGGING:
                print("The countdown is stopped")
            self.countdown_stop_flag = False
            self.countdown.stop()
            self.centralwidget.setStyleSheet("background-color: ")
            self.label_time.setText("00:00")
            self.wait_label_countdown.setText("")
            self.label_time.setStyleSheet("QLabel {color : black; }")

    def warningCountdown(self, filter, optional_filter = None):
        """
        Defines the timer that shows a error message to the player if something illegal is done or to show some feedback. The string filter
        is used to show which error message should be shown. An optional filter is used to differentiate where a certain
        error message should be displayed.
        """
        # Stop current warning if it is already running
        try:
            self.warnTimer.stop()
        except:  # do nothing
            pass
        self.warnTimer.start(globals.warningTimer*1000)                 # input is ms so globals.warningTimer is multiplied with 1000
        # self.warning is used to notify the finish method which label is showing a warning, so that it can remove that warning message
        self.warning = None
        if filter == "invalidIP":
            self.warning = self.connect_label_warning
            self.warning.setText("Please input a valid IP-address (example 10.0.0.2)")
        elif filter == "connecting":
            self.warning = self.connect_label_warning
            self.warning.setText("Connecting to host..")
        elif filter == "connection failed":
            self.warning = self.connect_label_warning
            self.warning.setText("Connection failed. Make sure the IP-address is correct")
        elif filter == "connection refused":
            self.warning = self.connect_label_warning
            self.warning.setText("Connection was refused by the host. The server might not be running properly yet. Please retry the connection")
        elif filter == "invalidName":
            self.warning = self.create_label_warning
            self.warning.setText("Please input a valid firm name")
        elif filter == "invalidMotto":
            self.warning = self.create_label_warning
            self.warning.setText("Please input a valid firm motto")
        elif filter == "name collision":
            self.warning = self.lobby_label_warning
            self.warning.setText("Your firm name has changed because it collides with another player")
        elif filter == "lobby ready":
            self.warning = self.lobby_label_warning
            self.warning.setText("Status set to ready")
        elif filter == "lobby not ready":
            self.warning = self.lobby_label_warning
            self.warning.setText("Status set to not ready")
        elif filter == "lobby button spam":
            self.warning = self.lobby_label_warning
            self.warning.setText("Status forced to ready due to button spam")
        elif filter == "main button spam":
            self.warning = self.main_label_warning
            self.warning.setText("Ready button is disabled due to spamming")
        elif filter == "marketTab" or filter =="infoTab":
            if optional_filter == 0:
                self.warning = self.main_label_warning
            elif optional_filter == 1:
                self.warning = self.plants_label_warning
            elif optional_filter == 2:
                self.warning = self.invest_label_warning
            elif optional_filter == 3:
                self.warning = self.market_label_warning
            elif optional_filter == 4:
                self.warning = self.info_label_warning
            if filter == "marketTab":
                self.warning.setText("Cannot enter market tab without owning a plant")
            elif filter =="infoTab":
                self.warning.setText("Cannot enter info tab before a bid round has been finished")
        elif filter =="bid saved":
            self.warning = self.market_label_warning
            self.warning.setText("Bid saved")
        elif filter == "bid already exists":
            self.warning = self.market_label_warning
            self.warning.setText("Bid already exists. Appending amount to existing bid")
        elif filter == "overBid":
            self.warning = self.market_label_warning
            self.warning.setText("Cannot bid more than plant's capacity")
        elif filter == "invalidBid":
            self.warning = self.market_label_warning
            self.warning.setText("Invalid bid(s).")
        elif filter == "bid no plants owned":
            self.warning = self.market_label_warning
            self.warning.setText("You do not own any plants")
        elif filter == "noBidToDelete":
            self.warning = self.market_label_warning
            self.warning.setText("The row does not contain a saved bid")
        elif filter == "cannotAfford":
            self.warning = self.invest_label_warning
            self.warning.setText("Insufficient funds")
        elif filter == "noPlantChosen":
            self.warning = self.invest_label_warning
            self.warning.setText("No plant chosen")
        elif filter == "noPlantsInStore":
            self.warning = self.invest_label_warning
            self.warning.setText("There are no plants to buy. Try again later")
        elif filter == "freePlant":
            self.warning = self.invest_label_warning
            self.warnng.setText("You have chosen your free plant. The other choices will now get their original price")
        elif filter == "buyInBidPhase":
            self.warning = self.invest_label_warning
            self.warning.setText("You are not allowed to invest in plants during the bidding phase. Consider buying a plant next strategy phase..")
        elif filter == "status":
            self.warning = self.main_label_warning
            if self.main_button_ready.isChecked():
                self.warning.setText("You are now waiting for the other players")
            else:
                self.warning.setText("You are no longer ready")
        elif filter == "info cannot plot":
            self.warning = self.info_label_warning
            self.warning.setText("Cannot make plot. A bid round has not been finished yet. Come back later")
        else:
            pass
        #self.countdown.start(500)
        #self.update_countdown()

    def warningCountdownFinished(self):
        # Set empty text to hide the label
        self.warning.setText("")

    def automatic_lobby_refresh(self):
        """
        Lobby refreshes automatically in intervals to avoid the network thread from making changes it does not have
        permission to make. If a change in the number of players is made the window is updated
        """
        if self.num_players != len(self.game_obj.simple_players):
            self.num_players = len(self.game_obj.simple_players)
            # Redraw the lobby
            self.clearLobby()
            self.drawLobby()

    def uncheck_buttons(self):
        """
        This method simply unchecks the buttons in the menu. It only unchecks the one currently checked for performance
        """
        if self.stackedWidget_inner.currentIndex()==0:
            self.button_main.setChecked(False)
        elif self.stackedWidget_inner.currentIndex()==1:
            self.button_plants.setChecked(False)
        elif self.stackedWidget_inner.currentIndex()==2:
            self.button_invest.setChecked(False)
        elif self.stackedWidget_inner.currentIndex()==3:
            self.button_market.setChecked(False)
        elif self.stackedWidget_inner.currentIndex()==4:
            self.button_info.setChecked(False)

    def drawLobby(self):
        """
        Draw the lobby for the player.
        Note labels are already set
        """
        # Define font to be applied to new widgets
        #font = QtGui.QFont()
        #font.setPointSize(18)
        # Draw list of players gotten from host
        players = self.game_obj.simple_players
        # Go through every plant in list of plants and create a widget for every element
        elements = len(players)
        # Creating empty lists for every variable in the simple player class.
        self.players_widget_name = [None] * elements
        self.players_widget_motto = [None] * elements
        # Initialize status label
        self.player_widget_status = None
        # Looping through plants in order to draw information in window
        try:
            for row, player in enumerate(players):
                # Name
                self.players_widget_name[row] = QtWidgets.QLabel(self.page_lobby)
                self.players_widget_name[row].setFont(self.fonts["small_text"])
                self.lobby_gridLayout.addWidget(self.players_widget_name[row], row, 0, 1,
                                                1)
                if player.firm_name == self.game_obj.player.firm_name:
                    # Set name of own firm to the one stored in self to handle name collisions
                    self.players_widget_name[row].setText(self.game_obj.player.firm_name + " (you)")
                    #self.draw_lobby_player_row_number = row
                    # Also create status label for own player
                    self.player_widget_status = QtWidgets.QLabel(self.page_lobby)
                    self.player_widget_status.setFont(self.fonts["small_text"])
                    self.lobby_gridLayout.addWidget(self.player_widget_status, row, 2, 1, 1)
                    self.player_widget_status.setText(self.game_obj.player.status)
                else:
                    # For other players get firm name from simple player list
                    self.players_widget_name[row].setText(player.firm_name)
                # Motto
                self.players_widget_motto[row] = QtWidgets.QLabel(self.page_lobby)
                self.players_widget_motto[row].setFont(self.fonts["small_text"])
                self.lobby_gridLayout.addWidget(self.players_widget_motto[row], row, 1, 1, 1)
                self.players_widget_motto[row].setText(player.firm_motto)
        except Exception as e:
            print("Exception in drawLobby(): ")
            print(e)

    def drawPlants(self):
        """
        This method draws the players plants in the plants tab of the main window.
        It reads this from the plants list in the player class

        The method is not well written in terms of extensions and updates. Consider changing some things to make changes
        made to the plant class included here

        """
        # Define font to be applied to new widgets
        #font = QtGui.QFont()
        #font.setPointSize(18)
        # Get plants from player
        plants = self.game_obj.player.getPlants()
        # Go through every plant in list of plants and create a widget for every element
        elements = len(plants)
        if elements == 0:
            self.plants_empty = QtWidgets.QLabel(self.page_plants)
            self.plants_empty.setFont(self.fonts["small_text"])
            self.plants_verticalLayout_emptyList.addWidget(self.plants_empty)
            self.plants_empty.setText("You do not own any plants. Invested plants will show up here.")
            return
        # Creating empty lists for every variable in the plant class.
        self.plants_widget_name = [None] * elements
        self.plants_widget_source = [None] * elements
        self.plants_widget_capacity = [None] * elements
        self.plants_widget_investmentCost = [None] * elements
        self.plants_widget_efficiency = [None] * elements
        self.plants_widget_annualCost = [None] * elements
        self.plants_widget_variableCost= [None] * elements
        self.plants_widget_emissions = [None] * elements
        # Looping through plants in order to draw information in window
        try:
            for row, plant in enumerate(plants):
                # Name
                self.plants_widget_name[row] = QtWidgets.QLabel(self.page_plants)
                self.plants_widget_name[row].setFont(self.fonts["small_text"])
                self.plants_gridLayout.addWidget(self.plants_widget_name[row], row+1, 0, 1, 1)                               # Drawing at row+1 because information is drawn in row 0
                self.plants_widget_name[row].setText(plant.getName())
                # Source
                self.plants_widget_source[row] = QtWidgets.QLabel(self.page_plants)
                self.plants_widget_source[row].setFont(self.fonts["small_text"])
                self.plants_gridLayout.addWidget(self.plants_widget_source[row], row+1, 1, 1, 1)
                self.plants_widget_source[row].setText(plant.getSource())
                # Capacity
                self.plants_widget_capacity[row] = QtWidgets.QLabel(self.page_plants)
                self.plants_widget_capacity[row].setFont(self.fonts["small_text"])
                self.plants_gridLayout.addWidget(self.plants_widget_capacity[row], row+1, 2, 1, 1)
                self.plants_widget_capacity[row].setText(number_to_string(plant.getCapacity(), "MW"))
                # Original investment cost
                self.plants_widget_investmentCost[row] = QtWidgets.QLabel(self.page_plants)
                self.plants_widget_investmentCost[row].setFont(self.fonts["small_text"])
                self.plants_gridLayout.addWidget(self.plants_widget_investmentCost[row], row+1, 3, 1, 1)
                self.plants_widget_investmentCost[row].setText(number_to_string(plant.getInvestmentCost(), "MNOK"))
                # Efficiency
                self.plants_widget_efficiency[row] = QtWidgets.QLabel(self.page_plants)
                self.plants_widget_efficiency[row].setFont(self.fonts["small_text"])
                self.plants_gridLayout.addWidget(self.plants_widget_efficiency[row], row+1, 4, 1, 1)
                self.plants_widget_efficiency[row].setText(number_to_string(plant.getEfficiency(), "%"))
                # Annual cost
                self.plants_widget_annualCost[row] = QtWidgets.QLabel(self.page_plants)
                self.plants_widget_annualCost[row].setFont(self.fonts["small_text"])
                self.plants_gridLayout.addWidget(self.plants_widget_annualCost[row], row+1, 5, 1, 1)
                self.plants_widget_annualCost[row].setText(number_to_string(plant.getAnnualCost(), "MNOK"))
                # Variable cost
                self.plants_widget_variableCost[row] = QtWidgets.QLabel(self.page_plants)
                self.plants_widget_variableCost[row].setFont(self.fonts["small_text"])
                self.plants_gridLayout.addWidget(self.plants_widget_variableCost[row], row + 1, 6, 1, 1)
                self.plants_widget_variableCost[row].setText(number_to_string(plant.getVariableCost(), "NOK/MWh"))
                # Emissions
                self.plants_widget_emissions[row] = QtWidgets.QLabel(self.page_plants)
                self.plants_widget_emissions[row].setFont(self.fonts["small_text"])
                self.plants_gridLayout.addWidget(self.plants_widget_emissions[row], row + 1, 7, 1, 1)
                self.plants_widget_emissions[row].setText(number_to_string(plant.getEmissions(), "kg CO<sub>2</sub>eq/MWh"))
        except Exception as e:
            print("Exception in drawPlants(): ")
            print(e)

    def drawStore(self):
        """
        Set up the store (invest tab) in the correct format. ie listing most attributes like in plants but now with a
        row for price, name setting and purchase button.
        :param storePlants:
        :return:
        """
        # Define font to be applied to new widgets
        #font = QtGui.QFont()
        #font.setPointSize(18)
        # Get plants in store
        storePlants = self.game_obj.getStorePlants()
        # Go through every plant in list of plants and create a widget for every element
        elements = len(storePlants)
        if len(storePlants) == 0:
            self.invest_empty = QtWidgets.QLabel(self.page_invest)
            self.invest_empty.setFont(self.fonts["small_text"])
            self.invest_verticalLayout_emptyList.addWidget(self.invest_empty)
            self.invest_empty.setText("There are no plants available for purchase. Try again later.")
            return
        # Creating empty lists for every variable in the plant class.
        self.invest_widget_source = [None] * elements
        #self.invest_widget_class = [None] * elements
        self.invest_widget_capacity = [None] * elements
        self.invest_widget_efficiency = [None] * elements
        self.invest_widget_annualCost = [None] * elements
        self.invest_widget_variableCost = [None] * elements
        self.invest_widget_emissions = [None] * elements
        self.invest_widget_price = [None] * elements
        self.invest_widget_radiobutton = [None] * elements
        # Looping through plants in order to draw information in window
        try:
            for row, plant in enumerate(storePlants):
                # Source
                self.invest_widget_source[row] = QtWidgets.QLabel(self.page_invest)
                self.invest_widget_source[row].setFont(self.fonts["small_text"])
                self.invest_gridLayout.addWidget(self.invest_widget_source[row], row + 1, 0, 1, 1)
                self.invest_widget_source[row].setText(plant.getSource())
                # Capacity
                self.invest_widget_capacity[row] = QtWidgets.QLabel(self.page_invest)
                self.invest_widget_capacity[row].setFont(self.fonts["small_text"])
                self.invest_gridLayout.addWidget(self.invest_widget_capacity[row], row + 1, 1, 1, 1)
                self.invest_widget_capacity[row].setText(number_to_string(plant.getCapacity(), "MW"))
                # Efficiency
                self.invest_widget_efficiency[row] = QtWidgets.QLabel(self.page_invest)
                self.invest_widget_efficiency[row].setFont(self.fonts["small_text"])
                self.invest_gridLayout.addWidget(self.invest_widget_efficiency[row], row + 1, 2, 1, 1)
                self.invest_widget_efficiency[row].setText(number_to_string(plant.getEfficiency(), "%"))
                # Annual cost
                self.invest_widget_annualCost[row] = QtWidgets.QLabel(self.page_invest)
                self.invest_widget_annualCost[row].setFont(self.fonts["small_text"])
                self.invest_gridLayout.addWidget(self.invest_widget_annualCost[row], row + 1, 3, 1, 1)
                self.invest_widget_annualCost[row].setText(number_to_string(plant.getAnnualCost(), "MNOK/year"))
                # Variable cost
                self.invest_widget_variableCost[row] = QtWidgets.QLabel(self.page_invest)
                self.invest_widget_variableCost[row].setFont(self.fonts["small_text"])
                self.invest_gridLayout.addWidget(self.invest_widget_variableCost[row], row + 1, 4, 1, 1)
                self.invest_widget_variableCost[row].setText(number_to_string(plant.getVariableCost(), "NOK/MWh"))
                # Emissions
                self.invest_widget_emissions[row] = QtWidgets.QLabel(self.page_invest)
                self.invest_widget_emissions[row].setFont(self.fonts["small_text"])
                self.invest_gridLayout.addWidget(self.invest_widget_emissions[row], row + 1, 5, 1, 1)
                self.invest_widget_emissions[row].setText(number_to_string(plant.getEmissions(), "kg CO<sub>2</sub>eq/MWh"))
                # Price
                self.invest_widget_price[row] = QtWidgets.QLabel(self.page_invest)
                self.invest_widget_price[row].setFont(self.fonts["small_text"])
                self.invest_gridLayout.addWidget(self.invest_widget_price[row], row+1, 6, 1, 1)
                self.invest_widget_price[row].setText(number_to_string(plant.getInvestmentCost(), "MNOK"))
                # Radio button
                self.invest_widget_radiobutton[row] = QtWidgets.QRadioButton(self.page_invest)
                self.invest_widget_radiobutton[row].setText("")
                if globals.darkmode:
                    self.invest_widget_radiobutton[row].setStyleSheet("QRadioButton::checked {background-color: " + globals.darkmode_background_color_styleSheet + "}" +"QRadioButton::indicator { width: " + self.fonts["radiobutton_width"] + "px; height: " + self.fonts["radiobutton_height"] + "px;};") # Set size and color of radiobutton
                else:
                    self.invest_widget_radiobutton[row].setStyleSheet(
                        "QRadioButton::checked {background-color: " + globals.lightmode_color_background_styleSheet + "}" + "QRadioButton::indicator { width: " +
                        self.fonts["radiobutton_width"] + "px; height: " + self.fonts[
                            "radiobutton_height"] + "px;};")  # Set size and color of radiobutton
                self.invest_gridLayout.addWidget(self.invest_widget_radiobutton[row], row +1, 7, 1, 1)
        except Exception as e:
            print("Exception in drawStore(): ")
            print(e)

    def drawMarket(self):
        """
        This method draws the elements of the market page
        """
        try:
            if self.market_lineEdit_dispatch_bid1.isReadOnly() == False:
                # Skip the status change if it has already been done
                pass
            elif self.game_obj.player.plants:
                # Set status of buttons and lineedits of bidding table
                self.market_lineEdit_dispatch_bid1.setReadOnly(False)
                self.market_lineEdit_dispatch_bid2.setReadOnly(False)
                self.market_lineEdit_dispatch_bid3.setReadOnly(False)
                self.market_lineEdit_price_bid1.setReadOnly(False)
                self.market_lineEdit_price_bid2.setReadOnly(False)
                self.market_lineEdit_price_bid3.setReadOnly(False)
                self.market_button_accept_bid1.setEnabled(True)
                self.market_button_accept_bid2.setEnabled(True)
                self.market_button_accept_bid3.setEnabled(True)
                self.market_button_delete_bid1.setEnabled(True)
                self.market_button_delete_bid2.setEnabled(True)
                self.market_button_delete_bid3.setEnabled(True)
                if globals.darkmode:
                    self.market_button_accept_bid1.setIcon(QtGui.QIcon("Resources/check_arrow_white"))
                    self.market_button_accept_bid2.setIcon(QtGui.QIcon("Resources/check_arrow_white"))
                    self.market_button_accept_bid3.setIcon(QtGui.QIcon("Resources/check_arrow_white"))
                    self.market_button_delete_bid1.setIcon(QtGui.QIcon("Resources/cross_white"))
                    self.market_button_delete_bid2.setIcon(QtGui.QIcon("Resources/cross_white"))
                    self.market_button_delete_bid3.setIcon(QtGui.QIcon("Resources/cross_white"))

                else:
                    self.market_button_accept_bid1.setIcon(QtGui.QIcon("Resources/check_arrow_black"))
                    self.market_button_accept_bid2.setIcon(QtGui.QIcon("Resources/check_arrow_black"))
                    self.market_button_accept_bid3.setIcon(QtGui.QIcon("Resources/check_arrow_black"))
                    self.market_button_delete_bid1.setIcon(QtGui.QIcon("Resources/cross_black"))
                    self.market_button_delete_bid2.setIcon(QtGui.QIcon("Resources/cross_black"))
                    self.market_button_delete_bid3.setIcon(QtGui.QIcon("Resources/cross_black"))
            # Set labels
            self.market_label_bidRound.setText(str(self.game_obj.bidRound))
            self.market_label_expectedDemand.setText(number_to_string(self.game_obj.expected_demand_fixed) + "-" + number_to_string(self.game_obj.expected_demand_variable) + "Q [NOK/MW]")
            # Make plot
            self.plot_market_graph()
            # Add plants to combobox
            for plant in self.game_obj.player.getPlants():
                self.market_comboBox_plants.addItem(plant.name)
            # Enable calculator if the player owns at least one plant
            if self.game_obj.player.plants:
                self.market_button_dialog_expected_marginal_cost.setEnabled(True)
            # Fetch existing bids for current plant
            self.drawBidTable()
        except Exception as e:
            print("Exception in drawMarket(): ")
            print(e)

    def drawBidTable(self):
        """
        Get the index from the combobox, link that to a plant, get the bids for that plant and draw them in the table if they exist
        """
        # New version with grid layout
        try:
            n = self.market_comboBox_plants.currentIndex()
            try: # Finding plant
                plant = self.game_obj.player.getPlant(n)
            except: # plant n does not exist
                return
            bids = self.game_obj.player.getPlantBids(plant)
            # Not drawing anything if there are no bids
            if not bids:
                # No bids
                return
            # Go through all the bids and place them in the correct row
            for bid in bids:
                row = bid.getNumber()
                amount = bid.getAmount()
                price = bid.getPrice()
                if row== 0: # bid number 1
                    self.market_lineEdit_dispatch_bid1.setText(str(amount))
                    self.market_lineEdit_price_bid1.setText(str(price))
                elif row == 1: # bid number 2
                    self.market_lineEdit_dispatch_bid2.setText(str(amount))
                    self.market_lineEdit_price_bid2.setText(str(price))
                elif row == 2: # bid number 3
                    self.market_lineEdit_dispatch_bid3.setText(str(amount))
                    self.market_lineEdit_price_bid3.setText(str(price))
                else:
                    print("Warning: bid number {} cannot be formatted in bid table".format(row))
        except Exception as e:
            print("Exception in drawBidTable(): ")
            print(e)

    def updateInfo(self):
        """
        The rest of the drawing is handled by info_handle_comboBox.
        """
        try:
            if self.game_obj.player.statistics.round_results:
                self.info_comboBox_results.setEnabled(True)
            else:
                self.info_comboBox_results.setEnabled(False)
            # Set labels
            self.info_label_profit.setText(number_to_string(self.game_obj.player.statistics.profits, "MNOK"))
            self.info_label_revenue.setText(number_to_string(self.game_obj.player.statistics.revenue, "MNOK"))
            self.info_label_costs.setText(number_to_string(self.game_obj.player.statistics.cost, "MNOK"))
            self.info_label_taxes.setText(number_to_string(self.game_obj.player.statistics.taxes, "MNOK"))
            self.info_label_emissions.setText(number_to_string(self.game_obj.player.statistics.emissions, "TON CO<sub>2</sub>eq"))
            self.info_label_total_capacity.setText(number_to_string(self.game_obj.player.getTotalCapacity(), "MW"))
        except Exception as e:
            print("Exception in updateInfo(): ")
            print(e)

    def drawRoundResults(self):
        #font = QtGui.QFont()
        #font.setPointSize(12)
        try:
            n = self.info_comboBox_results.currentIndex()
            result = self.game_obj.player.statistics.round_results[n]
            # Set labels
            #    for general
            self.round_results_label_hours_bid_on.setText(number_to_string(8760/self.game_obj.bidRounds, "hours"))
            self.round_results_label_demand.setText(number_to_string(result["demand"], "MW"))
            self.round_results_label_system_price.setText(number_to_string(result["system_price"], "NOK/MW"))
            self.round_results_label_used_capacity.setText("{}/{} MW".format(result["sold_amount"], result["bid_amount"]))
            self.round_results_label_production.setText(number_to_string(result["sold_amount"]*8760/self.game_obj.bidRounds, "GWh")) # /1000 to get GWh
            self.round_results_label_profits.setText(number_to_string(result["profits"], "MNOK"))
            self.round_results_label_revenue.setText(number_to_string(result["revenue"], "MNOK"))
            self.round_results_label_costs.setText(number_to_string(result["cost"], "MNOK"))
            self.round_results_label_administrative_costs.setText(number_to_string(result["administrative_cost"], "MNOK"))
            self.round_results_label_operational_costs.setText(
                number_to_string(result["operational_cost"], "MNOK"))
            self.round_results_label_taxes.setText(number_to_string(result["taxes"], "MNOK"))
            self.round_results_label_emissions.setText(
                number_to_string(result["emissions"], "TON CO<sub>2</sub>eq"))
            self.round_results_label_gas_price.setText(number_to_string(result["gas_price"], "NOK/MWh"))
            self.round_results_label_gas_fuel.setText(number_to_string(result["gas_fuel"], "GWh"))
            self.round_results_label_gas_production.setText(number_to_string(result["player_gas_production"], "GWh"))
            self.round_results_label_coal_price.setText(number_to_string(result["coal_price"], "NOK/MWh"))
            self.round_results_label_coal_fuel.setText(
                number_to_string(result["coal_fuel"], "GWh"))
            self.round_results_label_coal_production.setText(number_to_string(result["player_coal_production"], "GWh"))
            #    labels for sources
            self.total_production = result["total_pv_production"] + result["total_gas_production"] + result[
                "total_coal_production"]
            # Calculate player market shares for sources
            if result["total_pv_production"] == 0:
                self.player_pv_market_share = 0
            else:
                self.player_pv_market_share = result["player_pv_production"] / result["total_pv_production"]
            if result["total_gas_production"] == 0:
                self.player_gas_market_share = 0
            else:
                self.player_gas_market_share = result["player_gas_production"] / result["total_gas_production"]
            if result["total_coal_production"] == 0:
                self.player_coal_market_share = 0
            else:
                self.player_coal_market_share = result["player_coal_production"] / result["total_coal_production"]
            # Calculate the source market shares
            if self.total_production == 0:
                self.pv_market_share = 0
                self.gas_market_share = 0
                self.coal_market_share = 0
            else:
                self.pv_market_share = result["total_pv_production"] / self.total_production
                self.gas_market_share = result["total_gas_production"] / self.total_production
                self.coal_market_share = result["total_coal_production"] / self.total_production
            # Set players production label
            self.info_sources_label_your_production_pv.setText(number_to_string(result["player_pv_production"], "GWh"))
            self.info_sources_label_your_production_gas.setText(
                number_to_string(result["player_gas_production"], "GWh"))
            self.info_sources_label_your_production_coal.setText(
                number_to_string(result["player_coal_production"], "GWh"))
            # Set total production label
            self.info_sources_label_total_production_pv.setText(number_to_string(result["total_pv_production"], "GWh"))
            self.info_sources_label_total_production_gas.setText(
                number_to_string(result["total_gas_production"], "GWh"))
            self.info_sources_label_total_production_coal.setText(
                number_to_string(result["total_coal_production"],"GWh"))
            # Set players market share label
            self.info_sources_label_your_market_share_pv.setText(number_to_string(self.player_pv_market_share, "%"))
            self.info_sources_label_your_market_share_gas.setText(number_to_string(self.player_gas_market_share, "%"))
            self.info_sources_label_your_market_share_coal.setText(number_to_string(self.player_coal_market_share, "%"))
            # Set source market share label (formatting to "-" if zero)
            self.info_sources_label_source_market_share_pv.setText(number_to_string(self.pv_market_share, "%"))
            self.info_sources_label_source_market_share_gas.setText(number_to_string(self.gas_market_share, "%"))
            self.info_sources_label_source_market_share_coal.setText(number_to_string(self.coal_market_share, "%"))
            # Set flag
            self.round_results_drawn = True
            # Draw the demand plot for the general tab
            bids = dict_bids_to_bids_object_list(result["own_bids"])
            bids.extend(dict_bids_to_bids_object_list(result["other_bids"]))
            real_demand = [result["demand_curve_fixed"], result["demand_curve_variable"]]
            self.plot_info_demand_graph(bids, result["system_price"], real_demand )
            # Draw the pie chart for the sources tab
            self.plot_info_round_results_sources_graphs()
            # Print all the bids
            elements = len(result["own_bids"]["plant"])
            if elements == 0:
                self.info_empty = QtWidgets.QLabel(self.page_info)
                self.info_empty.setFont(self.fonts["tiny_text"])
                self.info_verticalLayout_emptyList.addWidget(self.info_empty)
                self.info_empty.setText("You did not send any bids this round")
                return
            # Creating empty lists for every column in the bid list
            self.info_widget_name= [None] * elements
            self.info_widget_price = [None] * elements
            self.info_widget_amount= [None] * elements
            self.info_widget_producer_surplus = [None] * elements
            self.info_widget_revenues = [None] * elements
            self.info_widget_operational_costs = [None] * elements
            self.info_widget_taxes = [None] * elements
            self.info_widget_emissions = [None] * elements
            for row in range(elements):
                # Plant name
                self.info_widget_name[row] = QtWidgets.QLabel(self.page_info)
                self.info_widget_name[row].setFont(self.fonts["tiny_text"])
                self.info_gridLayout.addWidget(self.info_widget_name[row], row + 1, 0, 1, 1)
                self.info_widget_name[row].setText(self.game_obj.player.getPlantName(result["own_bids"]["plant"][row]))
                # Price
                self.info_widget_price[row] = QtWidgets.QLabel(self.page_info)
                self.info_widget_price[row].setFont(self.fonts["tiny_text"])
                self.info_gridLayout.addWidget(self.info_widget_price[row], row + 1, 1, 1, 1)
                self.info_widget_price[row].setText(number_to_string(result["own_bids"]["price"][row], "NOK/MW"))
                # Amount
                self.info_widget_amount[row] = QtWidgets.QLabel(self.page_info)
                self.info_widget_amount[row].setFont(self.fonts["tiny_text"])
                self.info_gridLayout.addWidget(self.info_widget_amount[row], row + 1, 2, 1, 1)
                self.info_widget_amount[row].setText("{}/{} MW".format(result["own_bids"]["actual_amount"][row], result["own_bids"]["amount"][row]))
                # Producer surplus
                self.info_widget_producer_surplus[row] = QtWidgets.QLabel(self.page_info)
                self.info_widget_producer_surplus[row].setFont(self.fonts["tiny_text"])
                self.info_gridLayout.addWidget(self.info_widget_producer_surplus[row], row + 1, 3, 1, 1)
                self.info_widget_producer_surplus[row].setText(number_to_string(result["own_bids"]["producer_surplus"][row], "MNOK"))
                # Revenues
                self.info_widget_revenues[row] = QtWidgets.QLabel(self.page_info)
                self.info_widget_revenues[row].setFont(self.fonts["tiny_text"])
                self.info_gridLayout.addWidget(self.info_widget_revenues[row], row + 1, 4, 1, 1)
                self.info_widget_revenues[row].setText(number_to_string(result["own_bids"]["revenues"][row], "MNOK"))
                # Operational costs
                self.info_widget_operational_costs[row] = QtWidgets.QLabel(self.page_info)
                self.info_widget_operational_costs[row].setFont(self.fonts["tiny_text"])
                self.info_gridLayout.addWidget(self.info_widget_operational_costs[row], row + 1, 5, 1, 1)
                self.info_widget_operational_costs[row].setText(number_to_string(result["own_bids"]["operational_costs"][row], "MNOK"))
                # Taxes
                self.info_widget_taxes[row] = QtWidgets.QLabel(self.page_info)
                self.info_widget_taxes[row].setFont(self.fonts["tiny_text"])
                self.info_gridLayout.addWidget(self.info_widget_taxes[row], row + 1, 6, 1, 1)
                self.info_widget_taxes[row].setText(number_to_string(result["own_bids"]["taxes"][row], "MNOK"))
                # Emissions
                self.info_widget_emissions[row] = QtWidgets.QLabel(self.page_info)
                self.info_widget_emissions[row].setFont(self.fonts["tiny_text"])
                self.info_gridLayout.addWidget(self.info_widget_emissions[row], row + 1, 7, 1, 1)
                self.info_widget_emissions[row].setText(number_to_string(result["own_bids"]["emissions"][row], "TON CO<sub>2</sub>eq"))
        except Exception as e:
            print("Exception in drawRoundResults(): ")
            print(e)


    def clearRoundResults(self):
        """
        The results are cleared when a index is changed or the window is left.
        """
        self.clear_info_round_results_demand_graph()
        # Remove the sources pie chart
        self.clear_info_round_results_sources_graph()
        try:
            # Iterating through all rows and deleting contents
            for row in range(len(self.info_widget_name)):
                # Name
                self.info_gridLayout.removeWidget(self.info_widget_name[row])
                self.info_widget_name[row].deleteLater()
                self.info_widget_name[row] = None
                # Price
                self.info_gridLayout.removeWidget(self.info_widget_price[row])
                self.info_widget_price[row].deleteLater()
                self.info_widget_price[row] = None
                # Amount
                self.info_gridLayout.removeWidget(self.info_widget_amount[row])
                self.info_widget_amount[row].deleteLater()
                self.info_widget_amount[row] = None
                # Profit
                self.info_gridLayout.removeWidget(self.info_widget_producer_surplus[row])
                self.info_widget_producer_surplus[row].deleteLater()
                self.info_widget_producer_surplus[row] = None
                # Revenue
                self.info_gridLayout.removeWidget(self.info_widget_revenues[row])
                self.info_widget_revenues[row].deleteLater()
                self.info_widget_revenues[row] = None
                # Operational costs
                self.info_gridLayout.removeWidget(self.info_widget_operational_costs[row])
                self.info_widget_operational_costs[row].deleteLater()
                self.info_widget_operational_costs[row] = None
                # Taxes
                self.info_gridLayout.removeWidget(self.info_widget_taxes[row])
                self.info_widget_taxes[row].deleteLater()
                self.info_widget_taxes[row] = None
                # Emissions
                self.info_gridLayout.removeWidget(self.info_widget_emissions[row])
                self.info_widget_emissions[row].deleteLater()
                self.info_widget_emissions[row] = None

        # If the list does not exist only the empty list label does so it should delete that instead
        except:
            self.info_verticalLayout_emptyList.removeWidget(self.info_empty)
            self.info_empty.deleteLater()
            self.info_empty = None


    def drawTransitionResults(self):
        """
        Draws the results in the post bid round transition page.
        """
        #  Get the data, it should be the last element of the list indexed -1 (last element)
        result = self.game_obj.player.statistics.round_results[-1]
        # Set labels for general tab
        self.post_results_label_hours_bid_on.setText(number_to_string(8760 / self.game_obj.bidRounds, "hours"))
        self.post_results_label_demand.setText(number_to_string(result["demand"], "MW"))
        self.post_results_label_system_price.setText(number_to_string(result["system_price"], "NOK/MW"))
        self.post_results_label_used_capacity.setText("{}/{} MW".format(result["sold_amount"], result["bid_amount"]))
        self.post_results_label_production.setText(
            number_to_string(result["sold_amount"] * 8760 / self.game_obj.bidRounds, "GWh"))  # /1000 to get GWh
        self.post_results_label_profits.setText(number_to_string(result["profits"], "MNOK"))
        self.post_results_label_revenue.setText(number_to_string(result["revenue"], "MNOK"))
        self.post_results_label_costs.setText(number_to_string(result["cost"], "MNOK"))
        self.post_results_label_administrative_costs.setText(number_to_string(result["administrative_cost"], "MNOK"))
        self.post_results_label_operational_costs.setText(number_to_string(result["operational_cost"], "MNOK"))
        self.post_results_label_taxes.setText(number_to_string(result["taxes"], "MNOK"))
        self.post_results_label_emissions.setText(
                number_to_string(result["emissions"], "TON CO<sub>2</sub>eq"))
        self.post_results_label_gas_price.setText(number_to_string(result["gas_price"], "NOK/MWh"))
        self.post_results_label_gas_fuel.setText(number_to_string(result["gas_fuel"], "GWh"))
        self.post_results_label_gas_production.setText(number_to_string(result["player_gas_production"], "GWh"))
        self.post_results_label_coal_price.setText(number_to_string(result["coal_price"], "NOK/MWh"))
        self.post_results_label_coal_fuel.setText(
            number_to_string(result["coal_fuel"], "GWh"))
        self.post_results_label_coal_production.setText(number_to_string(result["player_coal_production"], "GWh"))
        # Set labels for source tab
        self.total_production = result["total_pv_production"] + result["total_gas_production"] + result[
            "total_coal_production"]
        # Calculate player market shares for sources
        if result["total_pv_production"] == 0:
            self.player_pv_market_share = 0
        else:
            self.player_pv_market_share = result["player_pv_production"] / result["total_pv_production"]
        if result["total_gas_production"] == 0:
            self.player_gas_market_share = 0
        else:
            self.player_gas_market_share = result["player_gas_production"] / result["total_gas_production"]
        if result["total_coal_production"] == 0:
            self.player_coal_market_share = 0
        else:
            self.player_coal_market_share = result["player_coal_production"] / result["total_coal_production"]
        # Calculate the source market shares
        if self.total_production == 0:
            self.pv_market_share = 0
            self.gas_market_share = 0
            self.coal_market_share = 0
        else:
            self.pv_market_share = result["total_pv_production"] / self.total_production
            self.gas_market_share = result["total_gas_production"] / self.total_production
            self.coal_market_share = result["total_coal_production"] / self.total_production
        # Set players production label
        self.post_results_label_your_production_pv.setText(number_to_string(result["player_pv_production"], "GWh"))
        self.post_results_label_your_production_gas.setText(
            number_to_string(result["player_gas_production"], "GWh"))
        self.post_results_label_your_production_coal.setText(
            number_to_string(result["player_coal_production"], "GWh"))
        # Set total production label
        self.post_results_label_total_production_pv.setText(number_to_string(result["total_pv_production"], "GWh"))
        self.post_results_label_total_production_gas.setText(
            number_to_string(result["total_gas_production"], "GWh"))
        self.post_results_label_total_production_coal.setText(
            number_to_string(result["total_coal_production"], "GWh"))
        # Set players market share label
        self.post_results_label_your_market_share_pv.setText(number_to_string(self.player_pv_market_share, "%"))
        self.post_results_label_your_market_share_gas.setText(number_to_string(self.player_gas_market_share, "%"))
        self.post_results_label_your_market_share_coal.setText(number_to_string(self.player_coal_market_share, "%"))
        # Set source market share label (formatting to "-" if zero)
        self.post_results_label_source_market_share_pv.setText(number_to_string(self.pv_market_share, "%"))
        self.post_results_label_source_market_share_gas.setText(number_to_string(self.gas_market_share, "%"))
        self.post_results_label_source_market_share_coal.setText(number_to_string(self.coal_market_share, "%"))
        # Draw the demand plot for the general tab
        bids = dict_bids_to_bids_object_list(result["own_bids"])
        bids.extend(dict_bids_to_bids_object_list(result["other_bids"]))
        real_demand = [result["demand_curve_fixed"], result["demand_curve_variable"]]
        self.plot_post_results_demand_graph(bids, result["system_price"], real_demand)
        # Draw the pie chart for the sources tab
        self.plot_post_round_results_sources_graph()
        # Print all the bids
        elements = len(result["own_bids"]["plant"])
        #font = QtGui.QFont()
        #font.setPointSize(12)
        if elements == 0:
            self.post_results_empty = QtWidgets.QLabel(self.page_post_round)
            self.post_results_empty.setFont(self.fonts["tiny_text"])
            self.post_results_verticalLayout_emptyList.addWidget(self.post_results_empty)
            self.post_results_empty.setText("You did not send any bids this round")
            return
        # Creating empty lists for every column in the bid list
        self.post_results_widget_name = [None] * elements
        self.post_results_widget_price = [None] * elements
        self.post_results_widget_amount = [None] * elements
        self.post_results_widget_producer_surplus = [None] * elements
        self.post_results_widget_revenues = [None] * elements
        self.post_results_widget_operational_costs = [None] * elements
        self.post_results_widget_taxes = [None] * elements
        self.post_results_widget_emissions = [None] * elements
        for row in range(elements):
            # Plant name
            self.post_results_widget_name[row] = QtWidgets.QLabel(self.page_post_round)
            self.post_results_widget_name[row].setFont(self.fonts["tiny_text"])
            self.post_results_gridLayout.addWidget(self.post_results_widget_name[row], row + 1, 0, 1, 1)
            self.post_results_widget_name[row].setText(self.game_obj.player.getPlantName(result["own_bids"]["plant"][row]))
            # Price
            self.post_results_widget_price[row] = QtWidgets.QLabel(self.page_post_round)
            self.post_results_widget_price[row].setFont(self.fonts["tiny_text"])
            self.post_results_gridLayout.addWidget(self.post_results_widget_price[row], row + 1, 1, 1, 1)
            self.post_results_widget_price[row].setText(number_to_string(result["own_bids"]["price"][row], "NOK/MW"))
            # Amount
            self.post_results_widget_amount[row] = QtWidgets.QLabel(self.page_post_round)
            self.post_results_widget_amount[row].setFont(self.fonts["tiny_text"])
            self.post_results_gridLayout.addWidget(self.post_results_widget_amount[row], row + 1, 2, 1, 1)
            self.post_results_widget_amount[row].setText(
                "{}/{} MW".format(result["own_bids"]["actual_amount"][row], result["own_bids"]["amount"][row]))
            # Producer_surplus
            self.post_results_widget_producer_surplus[row] = QtWidgets.QLabel(self.page_post_round)
            self.post_results_widget_producer_surplus[row].setFont(self.fonts["tiny_text"])
            self.post_results_gridLayout.addWidget(self.post_results_widget_producer_surplus[row], row + 1, 3, 1, 1)
            self.post_results_widget_producer_surplus[row].setText(number_to_string(result["own_bids"]["producer_surplus"][row], "MNOK"))
            # Revenues
            self.post_results_widget_revenues[row] = QtWidgets.QLabel(self.page_post_round)
            self.post_results_widget_revenues[row].setFont(self.fonts["tiny_text"])
            self.post_results_gridLayout.addWidget(self.post_results_widget_revenues[row], row + 1, 4, 1, 1)
            self.post_results_widget_revenues[row].setText(number_to_string(result["own_bids"]["revenues"][row], "MNOK"))
            # Operational costs
            self.post_results_widget_operational_costs[row] = QtWidgets.QLabel(self.page_post_round)
            self.post_results_widget_operational_costs[row].setFont(self.fonts["tiny_text"])
            self.post_results_gridLayout.addWidget(self.post_results_widget_operational_costs[row], row + 1, 5, 1, 1)
            self.post_results_widget_operational_costs[row].setText(number_to_string(result["own_bids"]["operational_costs"][row], "MNOK"))
            # Taxes
            self.post_results_widget_taxes[row] = QtWidgets.QLabel(self.page_post_round)
            self.post_results_widget_taxes[row].setFont(self.fonts["tiny_text"])
            self.post_results_gridLayout.addWidget(self.post_results_widget_taxes[row], row + 1, 6, 1, 1)
            self.post_results_widget_taxes[row].setText(number_to_string(result["own_bids"]["taxes"][row], "MNOK"))
            # Emissions
            self.post_results_widget_emissions[row] = QtWidgets.QLabel(self.page_post_round)
            self.post_results_widget_emissions[row].setFont(self.fonts["tiny_text"])
            self.post_results_gridLayout.addWidget(self.post_results_widget_emissions[row], row + 1, 7, 1, 1)
            self.post_results_widget_emissions[row].setText(
                number_to_string(result["own_bids"]["emissions"][row], "TON CO<sub>2</sub>eq"))

    def drawLeaderboard(self):
        #font = QtGui.QFont()
        #font.setPointSize(24)
        elements = len(self.game_obj.player.statistics.leaderboard["players"])
        self.leaderboard_widget_placement = [None] * elements
        self.leaderboard_widget_name = [None] * elements
        self.leaderboard_widget_motto = [None] * elements
        self.leaderboard_widget_profit = [None] * elements
        try: 
            self.leaderboards_label_placement.setText("{}/{}".format(self.game_obj.player.statistics.placement, elements))
            for row in range(elements):
                # Placement
                self.leaderboard_widget_placement[row] = QtWidgets.QLabel(self.page_leaderboard)
                self.leaderboard_widget_placement[row].setFont(self.fonts["big_text"])
                self.leaderboards_gridLayout.addWidget(self.leaderboard_widget_placement[row], row + 1, 0, 1, 1)
                self.leaderboard_widget_placement[row].setText(str(row+1))
                # Name
                self.leaderboard_widget_name[row] = QtWidgets.QLabel(self.page_leaderboard)
                self.leaderboard_widget_name[row].setFont(self.fonts["big_text"])
                self.leaderboards_gridLayout.addWidget(self.leaderboard_widget_name[row], row + 1, 1, 1, 1)
                self.leaderboard_widget_name[row].setText(self.game_obj.player.statistics.leaderboard["players"][row])
                # Motto
                self.leaderboard_widget_motto[row] = QtWidgets.QLabel(self.page_leaderboard)
                self.leaderboard_widget_motto[row].setFont(self.fonts["big_text"])
                self.leaderboards_gridLayout.addWidget(self.leaderboard_widget_motto[row], row + 1, 2, 1, 1)
                self.leaderboard_widget_motto[row].setText(self.game_obj.player.statistics.leaderboard["mottos"][row])
                # Profits
                self.leaderboard_widget_profit[row] = QtWidgets.QLabel(self.page_leaderboard)
                self.leaderboard_widget_profit[row].setFont(self.fonts["big_text"])
                self.leaderboards_gridLayout.addWidget(self.leaderboard_widget_profit[row], row + 1, 3, 1, 1)
                self.leaderboard_widget_profit[row].setText(number_to_string(self.game_obj.player.statistics.leaderboard["profits"][row], "MNOK"))
        except Exception as e:
            print("Exception raised in drawLeaderboard()")
            print(e)

    def clearLobby(self):
        """
        Clear the players from the lobby.
        Method is used to clear so that the lobby can be redrawn with the new information if someone leaves or joins.
        """
        # Iterating through all rows and deleting contents
        try:
            for row in range(0, len(self.players_widget_name)):
                # Name
                self.lobby_gridLayout.removeWidget(self.players_widget_name[row])
                self.players_widget_name[row].deleteLater()
                self.players_widget_name[row] = None
                # Motto
                self.lobby_gridLayout.removeWidget(self.players_widget_motto[row])
                self.players_widget_motto[row].deleteLater()
                self.players_widget_motto[row] = None
            # Status (only for self)
            self.lobby_gridLayout.removeWidget(self.player_widget_status)
            self.player_widget_status.deleteLater()
            self.player_widget_status = None
        except: # ignore
            pass

    def clearBidTable(self):
        """
        The method clears all the items so that new data can be written.
        Be aware that the designer might not set items to the cell and if the item is empty one can not set value to it
        """
        self.market_lineEdit_dispatch_bid1.setText("")
        self.market_lineEdit_dispatch_bid2.setText("")
        self.market_lineEdit_dispatch_bid3.setText("")
        self.market_lineEdit_price_bid1.setText("")
        self.market_lineEdit_price_bid2.setText("")
        self.market_lineEdit_price_bid3.setText("")
        # Replaced
        #for row in range(0, self.market_table_bids.rowCount()):
        #    # Clearing cell
        #    self.market_table_bids.item(row, 0).setText("")                             # Empty string (should not be read)
        #    self.market_table_bids.item(row, 1).setText("")

    def clearPlants(self):
        """
        The method destructs the plant widgets to avoid memory leakage and duplicate drawing
        """
        # Checks if the list exist and if it does, goes through it
        try:
            # Iterating through all rows and deleting contents
            for row in range(0, len(self.plants_widget_name)):
                # Name
                self.plants_gridLayout.removeWidget(self.plants_widget_name[row])
                self.plants_widget_name[row].deleteLater()
                self.plants_widget_name[row] = None
                # Source
                self.plants_gridLayout.removeWidget(self.plants_widget_source[row])
                self.plants_widget_source[row].deleteLater()
                self.plants_widget_source[row] = None
                # Capacity
                self.plants_gridLayout.removeWidget(self.plants_widget_capacity[row])
                self.plants_widget_capacity[row].deleteLater()
                self.plants_widget_capacity[row] = None
                # Investment Cost
                self.plants_gridLayout.removeWidget(self.plants_widget_investmentCost[row])
                self.plants_widget_investmentCost[row].deleteLater()
                self.plants_widget_investmentCost[row] = None
                # Efficiency
                self.plants_gridLayout.removeWidget(self.plants_widget_efficiency[row])
                self.plants_widget_efficiency[row].deleteLater()
                self.plants_widget_efficiency[row] = None
                # Annual cost
                self.plants_gridLayout.removeWidget(self.plants_widget_annualCost[row])
                self.plants_widget_annualCost[row].deleteLater()
                self.plants_widget_annualCost[row] = None
                # Variable cost
                self.plants_gridLayout.removeWidget(self.plants_widget_variableCost[row])
                self.plants_widget_variableCost[row].deleteLater()
                self.plants_widget_variableCost[row] = None
                # Emissions
                self.plants_gridLayout.removeWidget(self.plants_widget_emissions[row])
                self.plants_widget_emissions[row].deleteLater()
                self.plants_widget_emissions[row] = None
        # If the list does not exist only the empty list label does so it should delete that instead
        except:
            self.plants_verticalLayout_emptyList.removeWidget(self.plants_empty)
            self.plants_empty.deleteLater()
            self.plants_empty = None

    def clearInvest(self):
        """
        This method destructs the invest tab widgets
        """
        # The methods checks the existence of the list widgets
        try:
            for row in range(0, len(self.invest_widget_source)):
                # Source
                self.invest_gridLayout.removeWidget(self.invest_widget_source[row])
                self.invest_widget_source[row].deleteLater()
                self.invest_widget_source[row] = None
                # Capacity
                self.invest_gridLayout.removeWidget(self.invest_widget_capacity[row])
                self.invest_widget_capacity[row].deleteLater()
                self.invest_widget_capacity[row] = None
                # Efficiency
                self.invest_gridLayout.removeWidget(self.invest_widget_efficiency[row])
                self.invest_widget_efficiency[row].deleteLater()
                self.invest_widget_efficiency[row] = None
                # Annual cost
                self.invest_gridLayout.removeWidget(self.invest_widget_annualCost[row])
                self.invest_widget_annualCost[row].deleteLater()
                self.invest_widget_annualCost[row] = None
                # Variable costs
                self.invest_gridLayout.removeWidget(self.invest_widget_variableCost[row])
                self.invest_widget_variableCost[row].deleteLater()
                self.invest_widget_variableCost[row] = None
                # Emissions
                self.invest_gridLayout.removeWidget(self.invest_widget_emissions[row])
                self.invest_widget_emissions[row].deleteLater()
                self.invest_widget_emissions[row] = None
                # Price
                self.invest_gridLayout.removeWidget(self.invest_widget_price[row])
                self.invest_widget_price[row].deleteLater()
                self.invest_widget_price[row] = None
                # Radiobutton
                self.invest_gridLayout.removeWidget(self.invest_widget_radiobutton[row])
                self.invest_widget_radiobutton[row].deleteLater()
                self.invest_widget_radiobutton[row] = None
        # if the list does not exist it will remove the empty list label instead
        except:
            self.invest_verticalLayout_emptyList.removeWidget(self.invest_empty)
            self.invest_empty.deleteLater()
            self.invest_empty = None

    def clearPageMarket(self):
        """
        Should anything else be cleared?
        """
        # Clearing combo box
        self.market_comboBox_plants.clear()
        """
        for item in range(len(self.game_obj.player.getPlants())):
            #Remove the first item in the combobox (note that on the next iteration a new item is the first one)
            self.market_comboBox_plants.removeItem(0)
        """
        # Clearing table
        self.clearBidTable()
        # Clear plot
        self.clear_market_plot()

    def clearInfo(self):
        """
        Clear widgets from the info tab when left
        :return:
        """
        if self.round_results_drawn:
            self.clearRoundResults()
        self.clear_info_plot()
        # Reset tab indices
        self.info_tabWidget_outer.setCurrentIndex(0)
        self.info_tabWidget_inner.setCurrentIndex(0)

    def clearTransitionResults(self):
        self.clear_post_round_results_demand_graph()
        # Remove the sources pie chart
        self.clear_post_round_results_sources_graph()
        # Clear labels
        self.post_results_label_hours_bid_on.setText("-")
        self.post_results_label_demand.setText("-")
        self.post_results_label_system_price.setText("-")
        self.post_results_label_used_capacity.setText("-")
        self.post_results_label_production.setText("-")
        self.post_results_label_profits.setText("-")
        self.post_results_label_revenue.setText("-")
        self.post_results_label_costs.setText("-")
        self.post_results_label_administrative_costs.setText("-")
        self.post_results_label_operational_costs.setText("-")
        self.post_results_label_taxes.setText("-")
        self.post_results_label_emissions.setText("-")
        self.post_results_label_gas_price.setText("-")
        self.post_results_label_gas_fuel.setText("-")
        self.post_results_label_gas_production.setText("-")
        self.post_results_label_coal_price.setText("-")
        self.post_results_label_coal_fuel.setText("-")
        self.post_results_label_coal_production.setText("-")
        try:
            # Iterating through all rows and deleting contents
            for row in range(len(self.post_results_widget_name)):
                # Name
                self.post_results_gridLayout.removeWidget(self.post_results_widget_name[row])
                self.post_results_widget_name[row].deleteLater()
                self.post_results_widget_name[row] = None
                # Price
                self.post_results_gridLayout.removeWidget(self.post_results_widget_price[row])
                self.post_results_widget_price[row].deleteLater()
                self.post_results_widget_price[row] = None
                # Amount
                self.post_results_gridLayout.removeWidget(self.post_results_widget_amount[row])
                self.post_results_widget_amount[row].deleteLater()
                self.post_results_widget_amount[row] = None
                # Producer surplus
                self.post_results_gridLayout.removeWidget(self.post_results_widget_producer_surplus[row])
                self.post_results_widget_producer_surplus[row].deleteLater()
                self.post_results_widget_producer_surplus[row] = None
                # Revenue
                self.post_results_gridLayout.removeWidget(self.post_results_widget_revenues[row])
                self.post_results_widget_revenues[row].deleteLater()
                self.post_results_widget_revenues[row] = None
                # Operational_costs
                self.post_results_gridLayout.removeWidget(self.post_results_widget_operational_costs[row])
                self.post_results_widget_operational_costs[row].deleteLater()
                self.post_results_widget_operational_costs[row] = None
                # Taxes
                self.post_results_gridLayout.removeWidget(self.post_results_widget_taxes[row])
                self.post_results_widget_taxes[row].deleteLater()
                self.post_results_widget_taxes[row] = None
                # Emissions
                self.post_results_gridLayout.removeWidget(self.post_results_widget_emissions[row])
                self.post_results_widget_emissions[row].deleteLater()
                self.post_results_widget_emissions[row] = None

        # If the list does not exist only the empty list label does so it should delete that instead
        except:
            self.post_results_verticalLayout_emptyList.removeWidget(self.post_results_empty)
            self.post_results_empty.deleteLater()
            self.post_results_empty = None

    def clearWindow(self):
        """
        The method checks which page is currently open and clears that page
        """
        try:
            if self.stackedWidget_inner.currentIndex() == 0:
                self.main_label_warning.setText("")
            elif self.stackedWidget_inner.currentIndex() == 1:
                self.clearPlants()
                self.plants_label_warning.setText("")
            elif self.stackedWidget_inner.currentIndex() == 2:
                self.clearInvest()
                self.invest_label_warning.setText("")
            elif self.stackedWidget_inner.currentIndex() == 3:
                self.clearPageMarket()
                self.market_label_warning.setText("")
            elif self.stackedWidget_inner.currentIndex() == 4:
                self.clearInfo()
                self.info_label_warning.setText("")
        except Exception as e:
            print("Exception in clearWindow(): ")
            print(e)

    def buyPlant(self, buttonNumber):
        """
        This method inputs the available purchasable plants and the number of the button clicked to get the correct plant
        It then checks if the player can afford it and if it can it adds that plant to the players portfolio and
        removes the cost from the players balance
        """
        try:
            storePlants = self.game_obj.getStorePlants()
            plant = storePlants[buttonNumber]
            if self.game_obj.player.getMoney() < plant.getInvestmentCost():
                self.warningCountdown("cannotAfford")
                return
            else:
                if self.invest_lineEdit_setName.text().strip() != "":
                    name = self.invest_lineEdit_setName.text()
                    plant.setName(name)
                self.game_obj.player.appendPlant(plant)                                                                     # Add the plant to the players plant list
                self.game_obj.player.pay(plant.getInvestmentCost())                                                         # Remove funds from balance
                self.label_money.setText(number_to_string(self.game_obj.player.getMoney(), "MNOK"))                                     # Updating window to reflect new player balance
                self.game_obj.removePlant(buttonNumber)
                if len(self.game_obj.player.getPlants()) == 1 and self.lobby_label_startPlant.text() == "Free choice":      # Value is set to 1 because the player has bought the plant already
                    self.warningCountdown("freePlant")
                    for plant in self.game_obj.storePlants:
                        plant.setInvestmentCost(globals.initialPlantPrice)
                # Update label in info
                self.info_label_total_capacity.setText(number_to_string(self.game_obj.player.getTotalCapacity(), "MW"))
                # Inform the host of the purchase
                data = self.createData("plantBought")
                self.send(data)
                # Enable market combobox
                self.market_comboBox_plants.setEnabled(True)
        except Exception as e:
            print("Exception in buyPlant: ")
            print(e)

    def radiobutton_getToggled(self):
        """
        The method goes through all the radiobuttons and finds the one checked and returns the row of this button
        If none are checked it returns -1
        """
        for row in range(0, len(self.invest_widget_radiobutton)):
            if self.invest_widget_radiobutton[row].isChecked() == True:
                break
            if row == (len(self.invest_widget_radiobutton)-1):
                row = -1
        return row

    def addOrEditBid(self, newBid):
        """
        This method inputs a bid that is edited and looks through the players bids to find that bid and change it
        to the new data
        This method is poorly written and can be optimized for speed and readability but this was not prioritized
        """
        try:
            # Get attributes of the new bid
            new_plantIdentifier = newBid.getPlantIdentifier()
            new_number = newBid.getNumber()
            # Data to edit
            new_amount = newBid.getAmount()
            new_price = newBid.getPrice()
            # Get the list of bids for the player
            playerBids = self.game_obj.player.getBids()
            row = 0
            for i, bid in enumerate(playerBids):
                # Look for that particular bid (ie. check bid number and plant identifer)
                existing_plantIdentifier = bid.getPlantIdentifier()
                existing_number = bid.getNumber()
                if existing_plantIdentifier == new_plantIdentifier and new_number == existing_number:
                    # Found the particular bid. Edit it and return
                    self.game_obj.player.editBid(i, new_amount, new_price)
                    self.warningCountdown("bid saved")
                    return
                elif existing_plantIdentifier == new_plantIdentifier and new_price == bid.price:
                    # A bid with the same price already exists so append that bid instead of creating a new one, but only if max capacity is not reached..
                    if self.game_obj.player.accumulatedPlantProduction(newBid.plant) + new_amount <= newBid.plant.getActualCapacity(self.game_obj.weather_effect):
                        if globals.DEBUGGING:
                            print("Bid should be appended")
                        self.game_obj.player.bids[i].amount = bid.amount + new_amount
                        # Set labels for the corrected bid
                        if row == 0:
                            self.market_lineEdit_dispatch_bid1.setText(str(self.game_obj.player.bids[i].amount))
                        elif row == 1:
                            self.market_lineEdit_dispatch_bid2.setText(str(self.game_obj.player.bids[i].amount))
                        elif row == 2:
                            self.market_lineEdit_dispatch_bid3.setText(str(self.game_obj.player.bids[i].amount))
                        # Set labels for the one actually saved but dismised
                        if new_number == 0:
                            self.market_lineEdit_dispatch_bid1.setText("")
                            self.market_lineEdit_price_bid1.setText("")
                        elif new_number == 1:
                            self.market_lineEdit_dispatch_bid2.setText("")
                            self.market_lineEdit_price_bid2.setText("")
                        elif new_number == 2:
                            self.market_lineEdit_dispatch_bid3.setText("")
                            self.market_lineEdit_price_bid3.setText("")
                        self.warningCountdown("bid already exists")
                    else:
                        # New bid has amount higher than the capacity when the other bid is included
                        if new_number == 0:
                            self.market_lineEdit_dispatch_bid1.setText("")
                            self.market_lineEdit_price_bid1.setText("")
                        elif new_number == 1:
                            self.market_lineEdit_dispatch_bid2.setText("")
                            self.market_lineEdit_price_bid2.setText("")
                        elif new_number == 2:
                            self.market_lineEdit_dispatch_bid3.setText("")
                            self.market_lineEdit_price_bid3.setText("")
                        self.warningCountdown("overBid")
                    return
                # The bid is not found so keep looking and increment row
                row += 1
            # Went through for loop without finding the bid
            if self.game_obj.player.accumulatedPlantProduction(newBid.plant) +new_amount <= newBid.plant.getActualCapacity(self.game_obj.weather_effect):
                self.game_obj.player.appendBid(newBid)
                self.warningCountdown("bid saved")
            else:
                # Bid amount is higher than the power plants capacity so drop it
                if row == 0:
                    self.market_lineEdit_dispatch_bid1.setText("")
                    self.market_lineEdit_price_bid1.setText("")
                elif row == 1:
                    self.market_lineEdit_dispatch_bid2.setText("")
                    self.market_lineEdit_price_bid2.setText("")
                elif row == 2:
                    self.market_lineEdit_dispatch_bid3.setText("")
                    self.market_lineEdit_price_bid3.setText("")
                self.warningCountdown("overBid")
        except Exception as e:
            print("Exception in addOrEditBid():")
            print(e)

    """
    Network methods
    """
    def createData(self, header):
        """
        Headers (string) input should be:
        info
        bids
        Returns ready to send data with header readable by reciever to find out how to treat data
        """
        data = {}  # dictionary
        if header == "info":
            data["header"] = header
            data["playerNumber"] = self.game_obj.player.getNumber()
            data["name"] = self.game_obj.player.getName()
            data["motto"] = self.game_obj.player.getMotto()
        elif header == "status":
            data["header"] = header
            data["playerNumber"] = self.game_obj.player.getNumber()
            data["status"] = self.game_obj.player.status
        elif header == "plantBought":
            data["header"] = header
            data["plantIdentifier"] = self.game_obj.player.plants[-1].identifier
        elif header == "bids":
            data["header"] = header
            bids = [] # list of bids
            data["playerNumber"] = self.game_obj.player.getNumber()
            for playerbid in self.game_obj.player.getBids():
                bid = {
                    "plantIdentifier": playerbid.getPlantIdentifier(),
                    "amount": playerbid.getAmount(),
                    "price": playerbid.getPrice()
                }
                bids.append(bid)
            data["bids"] = bids
        elif header == "end game":
            data["header"] = header
            data["profits"] = self.game_obj.player.statistics.profits
            data["plants"] = len(self.game_obj.player.plants)
        else:
            print("Error: the header type: {} is not defined..".format(header))
        return data


    def send(self, data):
        serialized_data = json.dumps(data)
        # send data
        try:
            self.game_obj.player.tcpClient.send(serialized_data.encode())
            if globals.DEBUGGING:
                print("Packet {} was sent to host".format(data["header"]))
        except Exception as e:
            print(e)
        finally: time.sleep(0.1)

    """
    Plotting
    """
    def plot_demand_inside_window(self, layout, bids=None, system_price=None, demand=None):
        """
        Creates a demand (and bids) plot for the inputted layout (Note this is a general method)
        Used in market, transitions, and info?
        """
        try:
            # Get lists of demand slope
            demand_x_list = [0, self.game_obj.expected_demand_fixed / self.game_obj.expected_demand_variable]
            demand_y_list = [self.game_obj.expected_demand_fixed, 0]
            if demand:
                real_demand_x_list = [0, demand[0] / demand[1]]
                real_demand_y_list = [demand[0], 0]
            # Create generic canvas and static ax so generalize three functions
            if layout == self.market_horizontalLayout_info_graph:
                # Ceate the canvas for the plot
                self.static_canvas_market_demand = FigureCanvas(Figure(figsize=(5, 4)))
                static_canvas = self.static_canvas_market_demand
                # Create a subplot on the canvas
                self._static_ax_market_demand = self.static_canvas_market_demand.figure.subplots()
                static_ax = self._static_ax_market_demand
            elif layout == self.info_round_results_horizontalLayout_general:
                self.static_canvas_info_round_results = FigureCanvas(Figure(figsize=(5, 4)))
                static_canvas = self.static_canvas_info_round_results
                self._static_ax_info_round_results = self.static_canvas_info_round_results.figure.subplots()
                static_ax = self._static_ax_info_round_results
            elif layout == self.post_results_horizontalLayout_general:
                self.static_canvas_post_results = FigureCanvas(Figure(figsize=(5, 4)))
                static_canvas = self.static_canvas_post_results
                self._static_ax_post_results = self.static_canvas_post_results.figure.subplots()
                static_ax = self._static_ax_post_results
            else:
                print("Warning layout is not defined")
            # Ceate the canvas for the plot
            #self.static_canvas = FigureCanvas(Figure(figsize=(5, 4)))
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            #self.static_canvas.setSizePolicy(sizePolicy)
            static_canvas.setSizePolicy(sizePolicy)
            # Adding the plot canvas to the layout
            #layout.addWidget(self.static_canvas)
            layout.addWidget(static_canvas)
            #self.addToolBar(NavigationToolbar(self.static_canvas, self))
            self.addToolBar(NavigationToolbar(static_canvas, self))
            #self._static_ax = self.static_canvas.figure.subplots()
            # Plotting
            # Demand
            legend_elements = []
            legend_labels = []
            if demand:
                static_ax.plot(real_demand_x_list, real_demand_y_list, color="tab:orange")
                static_ax.plot(demand_x_list, demand_y_list, linestyle="--", color="tab:red")
                legend_elements.append(Line2D([0], [0], color='tab:orange', lw=1)) # for real demand
                legend_elements.append(Line2D([0], [0], color='tab:red', lw=1))  # for forecasted demand
                legend_labels.append("Demand")
            else:
                static_ax.plot(demand_x_list, demand_y_list, color="tab:orange")
                legend_elements.append(Line2D([0], [0], color='tab:orange', lw=1))  # for forecasted demand
            legend_labels.append("Forecasted demand")
            if bids:
                own_amount_list, own_price_list, other_amount_list, other_price_list = create_plot_lists(bids,
                                                                                                         self.game_obj.player.playerNumber)
                # Bids belonging to other players
                for index in range(len(other_amount_list)):
                    static_ax.plot(other_amount_list[index], other_price_list[index], color="tab:blue")
                # Bids belonging to player
                for index in range(len(own_amount_list)):
                    static_ax.plot(own_amount_list[index], own_price_list[index], color="tab:green")
                if other_amount_list:
                    legend_elements.append(Line2D([0], [0], color='tab:blue', lw=1))
                    legend_labels.append("Other bids")
                if own_amount_list:
                    legend_elements.append(Line2D([0], [0], color='tab:green', lw=1))
                    legend_labels.append("Your bids")
            static_ax.legend(legend_elements, legend_labels, loc="upper right")
            # https://matplotlib.org/api/axes_api.html#appearance
            if globals.darkmode:
                static_canvas.figure.set_facecolor(globals.darkmode_light_dark_color)
                static_ax.set_xlabel("Q [MW]", color="white")
                static_ax.set_ylabel("Price [NOK/MW]", color="white")
                static_ax.set_facecolor(globals.darkmode_light_dark_color)
                static_ax.tick_params(axis='x', colors=globals.darkmode_color_white)
                static_ax.tick_params(axis='y', colors=globals.darkmode_color_white)
                static_ax.spines['bottom'].set_color(globals.darkmode_color_white)
                static_ax.spines['top'].set_color(globals.darkmode_light_dark_color)
                static_ax.spines['right'].set_color(globals.darkmode_light_dark_color)
                static_ax.spines['left'].set_color(globals.darkmode_color_white)
            else:
                static_ax.set_xlabel("Q [MW]")
                static_ax.set_ylabel("Price [NOK/MW]")
            #if system_price and demand:
            #    static_ax.axhline(y=system_price, xmin=0, xmax=demand, color="tab:red")
            #    static_ax.axvline(x=demand, ymin=0, ymax=system_price, color="tab:red")
            static_ax.set_ylim(0,3010) # 3000 is the rationing price +10 to show rationing price if applicable (todo: should be generalized perhaps to globals)
        except Exception as e:
            print("Exception in plot_demand_inside_window:")
            print(e)

    def plot_market_graph(self):
        """
        Checks if bids exists, and then uses plot_demand_inside_window to plot to the correct layout
        """
        layout = self.market_horizontalLayout_info_graph
        if self.game_obj.player.bids:
            self.plot_demand_inside_window(layout, self.game_obj.player.bids)
        else:
            self.plot_demand_inside_window(layout)

    def plot_info_demand_graph(self, bids, system_price, demand):
        layout = self.info_round_results_horizontalLayout_general
        if bids:
            self.plot_demand_inside_window(layout, bids, system_price, demand)
        else:
            self.plot_demand_inside_window(layout)

    def plot_post_results_demand_graph(self, bids, system_price, demand):
        layout = self.post_results_horizontalLayout_general
        if bids:
            self.plot_demand_inside_window(layout, bids, system_price, demand)
        else:
            self.plot_demand_inside_window(layout)

    def plot_info_graphs_handle(self):
        """
        Handler for plotting one of the graphs in the info window
        Based on what tab is open it will plot profits, revenue, costs or emissions
        It does not plot before two rounds have been played as one result does not plot well and does not give better information than the labels
        """
        try:
            if len(self.game_obj.player.statistics.round_results) < 2:
                return
            else:
                self.info_tabWidget_plots.setEnabled(True)
            # Determine size of bars
            if len(self.game_obj.player.statistics.round_results) < 5:
                bar_width = 0.4
            else:
                bar_width = 0.6
            # Check if clearing of plots are needed
            if self.info_tabWidget_currentIndex != self.info_tabWidget_plots.currentIndex():
                self.clear_info_plot()
            # Get the results
            round_results = self.game_obj.player.statistics.round_results
            rounds_list = []
            # Conditional color list based on value (positive green, negative red)
            colors_list = []
            # Store the current index
            self.info_tabWidget_currentIndex = self.info_tabWidget_plots.currentIndex()
            # Create the canvas
            self.static_canvas_info = FigureCanvas(Figure(figsize=(5, 3)))
            self.addToolBar(NavigationToolbar(self.static_canvas_info, self))
            rounds_list.append("")
            #colors_list.append("red")
            # Add to correct layout based on current index
            if self.info_tabWidget_currentIndex == 0: # profits
                profits_list = []
                profits_list.append(0)
                self.info_verticalLayout_profit_plot.addWidget(self.static_canvas_info)
                self._static_ax_info = self.static_canvas_info.figure.subplots()
                for round_result in round_results:
                    rounds_list.append("Year {} b{}".format(round_result["year"], round_result["round"]))
                    profits_list.append(round_result["profits"]/1000000)
                for profit in profits_list:
                    if profit > 0:
                        colors_list.append("green")
                    else:
                        if globals.darkmode:
                            colors_list.append(globals.darkmode_color_red)
                        else: colors_list.append("red")
                self._static_ax_info.bar(rounds_list, profits_list, width=bar_width, color=colors_list)
                self._static_ax_info.set_ylabel("Profits [MNOK]")
            elif self.info_tabWidget_currentIndex == 1: # revenue
                revenue_list = []
                revenue_list.append(0)
                self.info_verticalLayout_revenue_plot.addWidget(self.static_canvas_info)
                self._static_ax_info = self.static_canvas_info.figure.subplots()
                for round_result in round_results:
                    rounds_list.append("Year {} b{}".format(round_result["year"], round_result["round"]))
                    revenue_list.append(round_result["revenue"]/1000000)
                self._static_ax_info.bar(rounds_list, revenue_list, width=bar_width, color="green")
                self._static_ax_info.set_ylabel("Revenue [MNOK]")
            elif self.info_tabWidget_currentIndex == 2: # cost
                cost_list = []
                cost_list.append(0)
                self.info_verticalLayout_cost_plot.addWidget(self.static_canvas_info)
                self._static_ax_info = self.static_canvas_info.figure.subplots()
                for round_result in round_results:
                    rounds_list.append("Year {} b{}".format(round_result["year"], round_result["round"]))
                    cost_list.append(round_result["cost"] + round_result["taxes"]/1000000)
                self._static_ax_info.bar(rounds_list, cost_list, width=bar_width, color=globals.darkmode_color_red)
                self._static_ax_info.set_ylabel("Costs incl. taxes [MNOK]")
            elif self.info_tabWidget_currentIndex == 3: # emissions
                emissions_list = []
                emissions_list.append(0)
                self.info_verticalLayout_emissions_plot.addWidget(self.static_canvas_info)
                self._static_ax_info = self.static_canvas_info.figure.subplots()
                for round_result in round_results:
                    rounds_list.append("Year {} b{}".format(round_result["year"], round_result["round"]))
                    emissions_list.append(round_result["emissions"]/1000000)
                self._static_ax_info.bar(rounds_list, emissions_list, width=bar_width, color=globals.darkmode_color_red)
                self._static_ax_info.set_ylabel("Emissions [1000 TON CO2eq]") # proper formatting of CO2 is not possible in label
            # Set x axis at y = 0
            self._static_ax_info.spines['bottom'].set_position('zero')
            self._static_ax_info.spines['left'].set_position('zero')
            # Change color if in darkmode
            if globals.darkmode:
                self.static_canvas_info.figure.set_facecolor(globals.darkmode_light_dark_color)
                self._static_ax_info.set_facecolor(globals.darkmode_light_dark_color)
                self._static_ax_info.tick_params(axis='x', color=globals.darkmode_color_white)
                self._static_ax_info.tick_params(axis='y', color=globals.darkmode_color_white)
                self._static_ax_info.yaxis.label.set_color(color=globals.darkmode_color_white)
                self._static_ax_info.spines['bottom'].set_color(globals.darkmode_color_white)
                self._static_ax_info.spines['top'].set_color(globals.darkmode_light_dark_color)
                self._static_ax_info.spines['right'].set_color(globals.darkmode_light_dark_color)
                self._static_ax_info.spines['left'].set_color(globals.darkmode_color_white)
        except Exception as e:
            print("Exception in plot_info_graphs_handle")
            print(e)

    def plot_info_round_results_sources_graphs(self):
        """
        Plots market share pie plots in the sources tab under round results in the info page
        """
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
            self.static_canvas_sources = FigureCanvas(Figure(figsize=(5, 3)))
            self.addToolBar(NavigationToolbar(self.static_canvas_sources, self))
            # Add canvas to the layout
            self.info_round_results_horizontalLayout_sources.addWidget(self.static_canvas_sources)
            self._static_ax_sources = self.static_canvas_sources.figure.subplots()
            self._static_ax_sources.pie(market_shares, explode=explode_list, labels=source_labels,
                                            autopct="%1.1f%%", shadow=True, startangle=180)
            self._static_ax_sources.axis("equal")
            if globals.darkmode:
                self.static_canvas_sources.figure.set_facecolor(globals.darkmode_light_dark_color)
        except Exception as e:
            print("Exception in plot_info_round_results_sources_graphs:")
            print(e)

    def plot_post_round_results_sources_graph(self):
        """
        Plots market share pie plots in the sources tab under round results in the transition window for post bid rounds
        """
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
            explode_list = [0.05 for i in range(len(source_labels))] # Set explode value to 0.05 for all the labels. Line makes sure explode_list has same length as source_labels
            # Create the canvas
            self.static_canvas_post_results_sources = FigureCanvas(Figure(figsize=(5, 3)))
            self.addToolBar(NavigationToolbar(self.static_canvas_post_results_sources, self))
            # Add canvas to the layout
            self.post_results_horizontalLayout_sources.addWidget(self.static_canvas_post_results_sources)
            self._static_ax_post_results_sources = self.static_canvas_post_results_sources.figure.subplots()
            self._static_ax_post_results_sources.pie(market_shares, explode=explode_list, labels=source_labels,
                                        autopct="%1.1f%%", shadow=True, startangle=180)
            self._static_ax_post_results_sources.axis("equal")
            if globals.darkmode:
                self.static_canvas_post_results_sources.figure.set_facecolor(globals.darkmode_light_dark_color)
        except Exception as e:
            print("Exception in plot_info_round_results_sources_graphs:")
            print(e)

    def clear_market_plot(self):
        """
        Clear market plot ie. when leaving the window. if it exists
        """
        if self._static_ax_market_demand:
            self.market_horizontalLayout_info_graph.removeWidget(self.static_canvas_market_demand)
            self.static_canvas_market_demand.deleteLater()
            self.static_canvas_market_demand = None
        else:
            pass

    def clear_info_plot(self):
        if len(self.game_obj.player.statistics.round_results) <2: # Two rounds have not been played yet
            return
        elif self._static_ax_info:
            if self.info_tabWidget_currentIndex == 0:
                self.info_verticalLayout_profit_plot.removeWidget(self.static_canvas_info)
            elif self.info_tabWidget_currentIndex == 1:
                self.info_verticalLayout_revenue_plot.removeWidget(self.static_canvas_info)
            elif self.info_tabWidget_currentIndex == 2:
                self.info_verticalLayout_cost_plot.removeWidget(self.static_canvas_info)
            elif self.info_tabWidget_currentIndex == 3:
                self.info_verticalLayout_emissions_plot.removeWidget(self.static_canvas_info)
            self.static_canvas_info.deleteLater()
            self.static_canvas_info = None
        else:
            return

    def clear_info_round_results_demand_graph(self):
        if self._static_ax_info_round_results:
            self.info_round_results_horizontalLayout_general.removeWidget(self.static_canvas_info_round_results)
            self.static_canvas_info_round_results.deleteLater()
            self.static_canvas_info_round_results = None
        else:
            pass

    def clear_post_round_results_demand_graph(self):
        if self._static_ax_post_results:
            self.post_results_horizontalLayout_general.removeWidget(self.static_canvas_post_results)
            self.static_canvas_post_results.deleteLater()
            self.static_canvas_post_results= None
        else:
            pass

    def clear_info_round_results_sources_graph(self):
        if self._static_ax_sources:
            self.info_round_results_horizontalLayout_sources.removeWidget(self.static_canvas_sources)
            self.static_canvas_sources.deleteLater()
            self.static_canvas_sources = None
        else:
            pass

    def clear_post_round_results_sources_graph(self):
        if self._static_ax_post_results_sources:
            self.post_results_horizontalLayout_sources.removeWidget(self.static_canvas_post_results_sources)
            self.static_canvas_post_results_sources.deleteLater()
            self.static_canvas_post_results_sources = None
        else:
            pass