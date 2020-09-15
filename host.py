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