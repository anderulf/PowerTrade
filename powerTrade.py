"""

# The distribution python file
run in terminal: pyinstaller.exe --onefile --windowed --name PowerTrade play.py
"""
# Importing
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPalette, QColor
from GUI_player import startWindow_player     # The GUI window for the player
from thread import ClientNetwork
import globals


def main():
    """
    Initializing the neccessary processes
    """

    # Start splash screen (loading)
    app = QtWidgets.QApplication(sys.argv)
    globals.app = app
    globals.standard_palette = app.palette() # Store standard palette if user wants to change back to the default light palette
    app.setAttribute(QtCore.Qt.AA_DisableHighDpiScaling)
    MainWindow = QtWidgets.QMainWindow()
    ui = startWindow_player()
    ui.setupUi(MainWindow)
    ui.setUpSlots()
    ui.setUpValidators()
    ui.setUpImages()
    ui.setUpTheme()
    ui.setUpFonts()
    ui.setUpMisc()
    """
    print("************** NB DEBUGGING SETTINGS ARE SET IN play_duplicate.py ********************")
    ui.game_obj.player.setPlayerNumber(0)
    ui.game_obj.player.setMoney(10000000)
    ui.game_obj.player.setName("testing..")
    ui.game_obj.player.setMotto("testing..")
    ui.game_obj.bidRound = 0

    plant = Plant("PV", "testingplant", 500, 10000, 0.5, 1000, 20, 10, 0)
    plant2 = Plant("PV", "secondplant", 500, 10000, 0.5, 1000, 20, 10, 1)
    ui.game_obj.player.appendPlant(plant)
    ui.game_obj.player.appendPlant(plant2)
    bid = Bid(0, plant, 500, 500)
    bids = dict(plant=[0, 0, 0, 0], actual_amount=[200, 300, 0, 0], bid_amount=[500, 300, 100, 50],
                profits=[200, 300, 0, 0])
    results = dict(year=1, round=1, profits=100, revenue=200, cost=80, taxes=20, emissions=50, bids=bids)
    ui.game_obj.player.statistics.create_round_results(results)
    results2 = dict(year=1, round=2, profits=-100, revenue=0, cost=-100, taxes=0, emissions=0,
                    bids=dict(plant=[], actual_amount=[], bid_amount=[], profits=[]))
    ui.game_obj.player.statistics.create_round_results(results2)
    ui.info_comboBox_results.addItem(
        "Year {} round {}".format(ui.game_obj.player.statistics.round_results[-1]["year"],
                                  ui.game_obj.player.statistics.round_results[-1]["round"]))
    ui.info_comboBox_results.setEnabled(True)
    ui.stackedWidget.setCurrentIndex(5)
    """
    clientNetwork = ClientNetwork(ui)
    clientNetwork.start()
    # end splash screen
    MainWindow.show()
    app.exit(app.exec_())
    clientNetwork.stop()



if __name__ == "__main__":
    main()