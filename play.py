"""

This is the main file for running the game as a player. For running the game as a host see host.py.
This file will import the game components: graphics, mechanics, network
and mend these together


"""
# Importing
from sys import argv
from sys import exit as sys_exit
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication
from GUI_player import startWindow_player     # The GUI window for the player
from thread import ClientNetwork
import globals


def main():
    """
    Initializing the neccessary processes
    """
    if globals.DEBUGGING:
        print("DEBUGGING MODE")
    # Start splash screen (loading)
    app = QApplication(argv)
    globals.app = app
    globals.standard_palette = app.palette() # Store standard palette if user wants to change back to the default light palette
    app.setAttribute(Qt.AA_DisableHighDpiScaling)
    MainWindow = QMainWindow()
    ui = startWindow_player()
    ui.setupUi(MainWindow)
    ui.setUpSlots()
    ui.setUpValidators()
    ui.setUpImages()
    ui.setUpTheme()
    ui.setUpFonts()
    ui.setUpMisc()
    clientNetwork = ClientNetwork(ui)
    clientNetwork.start()
    # end splash screen
    MainWindow.show()
    app.exit(app.exec_())
    clientNetwork.stop()
    #sys_exit()


if __name__ == "__main__":
    main()