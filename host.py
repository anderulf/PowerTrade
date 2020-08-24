"""

This is the main file for running the game as a host. For running the game as a player see play.py.
This file will import the game components: graphics, mechanics, network
and mend these together

The host A game can be hosted and played on the same computer.

"""
# Importing
from sys import argv
from sys import exit as sys_exit
from PyQt5.QtWidgets import QApplication, QMainWindow
from GUI_host import startWindow_host  # The GUI window for the host
import globals

def main():
    """
    Initializing the neccessary processes
    """
    if globals.DEBUGGING:
        print("DEBUGGING MODE")
    app = QApplication(argv)
    MainWindow = QMainWindow()
    ui = startWindow_host()
    ui.setupUi(MainWindow)
    # Set ut the connections
    ui.setUpSlots()
    # Set up validators
    ui.setUpValidators()
    ui.setUpMisc()
    """
    print("************** NB DEBUGGING SETTINGS ARE SET IN host.py ********************")
    ui.game_obj.host.addPlayer(0)
    ui.game_obj.host.players[0].firm_name = "testing"
    ui.game_obj.host.players[0].firm_motto= "testing"
    ui.game_obj.host.players[0].statistics.placement = 1
    ui.game_obj.host.players[0].statistics.profits = 100000
    ui.game_obj.host.players[0].statistics.emissions = 1000000
    ui.game_obj.host.addPlayer(1)
    ui.game_obj.host.players[1].firm_name = "Statkraft"
    ui.game_obj.host.players[1].firm_motto = "Grønn som faen"
    ui.game_obj.host.players[1].statistics.placement = 2
    ui.game_obj.host.players[1].statistics.profits = 90000
    ui.game_obj.host.players[1].statistics.emissions = 140000
    
    plant = Plant("PV", "testingplant", 500, 10000, 0.5, 1000, 20, 10, 0)
    plant2 = Plant("PV", "secondplant", 500, 10000, 0.5, 1000, 20, 10, 1)
    bid = Bid(0, plant, 500, 500)
    ui.game_obj.host.players[0].appendPlant(plant)
    bids = dict(plant=[0, 0, 0, 0], actual_amount=[200, 300, 0, 0], bid_amount=[500, 300, 100, 50],
                profits=[200, 300, 0, 0])
    results = dict(year=1, round=1, profits=100, revenue=200, cost=80, taxes=20, emissions=50, bids=bids)
    ui.game_obj.host.getPlayer(0).statistics.create_round_results(results)
    results2 = dict(year=1, round=2, profits=-100, revenue=0, cost=-100, taxes=0, emissions=0,
                    bids=dict(plant=[], actual_amount=[], bid_amount=[], profits=[]))
    ui.game_obj.host.getPlayer(0).statistics.create_round_results(results2)
    """

    #ui.setUpImages()
    # MainWindow.setWindowState(QtCore.Qt.WindowFullScreen)
    MainWindow.show()
    app.exit(app.exec_())
    # Closing down
    try:
        ui.serverThread.stop()
        print("Server shut down")
    except: pass # The server thread has not been started yet (most likely due to termination before creating server)
    raise SystemExit
    # sys_exit() # Might be solution to properly terminating on exit

if __name__ == "__main__":
    """
    Infinite loop
    """
    main()