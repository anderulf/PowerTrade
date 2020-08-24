import sys,time
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QScrollBar,QSplitter,QTableWidgetItem,QTableWidget,QComboBox,QVBoxLayout,QGridLayout,QDialog,QWidget, QPushButton, QApplication, QMainWindow,QAction,QMessageBox,QLabel,QTextEdit,QProgressBar,QLineEdit
from PyQt5.QtCore import QCoreApplication
import socket
from threading import Thread
from socketserver import ThreadingMixIn
from game_client import Game_client

tcpClientA=None

class Window(QDialog):
    def __init__(self):
        super().__init__()
        self.flag=0
        self.chatTextField=QLineEdit(self)
        self.chatTextField.resize(480,100)
        self.chatTextField.move(10,350)
        self.btnSend=QPushButton("Send",self)
        self.btnSend.resize(480,30)
        self.btnSendFont=self.btnSend.font()
        self.btnSendFont.setPointSize(15)
        self.btnSend.setFont(self.btnSendFont)
        self.btnSend.move(10,460)
        #self.btnSend.setStyleSheet("background-color: #F7CE16")
        self.btnSend.clicked.connect(self.send)

        self.chatBody=QVBoxLayout(self)
        splitter=QSplitter(QtCore.Qt.Vertical)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)

        splitter.addWidget(self.chat)
        splitter.addWidget(self.chatTextField)
        splitter.setSizes([400,100])

        splitter2=QSplitter(QtCore.Qt.Vertical)
        splitter2.addWidget(splitter)
        splitter2.addWidget(self.btnSend)
        splitter2.setSizes([200,10])

        self.chatBody.addWidget(splitter2)


        self.setWindowTitle("Chat Application: client")
        self.resize(500, 500)

        # test
        self.game_obj = Game_client("server")
        self.game_obj.setYear(3)
        print(self.game_obj.getYear())
    def send(self):
        print("Sending message to destination.. ")
        text=self.chatTextField.text()
        if text == "secretword":
            print(self.game_obj.getYear())
        font=self.chat.font()
        font.setPointSize(13)
        self.chat.setFont(font)
        textFormatted='{:>80}'.format(text)
        self.chat.append(textFormatted)
        tcpClientA.send(text.encode())
        self.chatTextField.setText("")

class ClientThread(Thread):
    def __init__(self,window):
        Thread.__init__(self)
        self.window=window

    def run(self):
        self.host = socket.gethostname()
        self.port = 5555
        self.BUFFER_SIZE = 2000
        global tcpClientA
        tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpClientA.connect((self.host, self.port))
        self.connect()
    def connect(self):
        while True:                                                             # Infinite loop waiting for packets from server
            data = tcpClientA.recv(self.BUFFER_SIZE)
            print("Message recieved.. drawing in window")
            if data.decode("utf-8") == "test":
                window.btnSend.setText("WOrked")
                window.game_obj.setYear(10)
            window.chat.append(data.decode("utf-8"))
        tcpClientA.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    clientThread=ClientThread(window)
    clientThread.start()
    window.exec()
    sys.exit(app.exec_())