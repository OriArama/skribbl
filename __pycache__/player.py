import socket
import os
import time
from first_window import *
import threading
from PyQt6 import QtWidgets, QtCore
import sys

app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()


class player(QtCore.QObject):
    quit_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.listening = True
        # Start a separate thread to listen for messages from the server
        message_listener = threading.Thread(target=self.listen_for_server_messages)
        message_listener.daemon = True
        message_listener.start()
        self.gui = Ui_MainWindow()
        self.handle_gui()

    def handle_gui(self):
        global MainWindow
        self.gui.setupUi(MainWindow)
        self.gui.retranslateUi(MainWindow)
        self.gui.MonsterButton_1.clicked.connect(self.send_monster)
        self.gui.MonsterButton_2.clicked.connect(self.send_monster)
        self.gui.MonsterButton_3.clicked.connect(self.send_monster)
        self.gui.MonsterButton_4.clicked.connect(self.send_monster)
        self.gui.MonsterButton_5.clicked.connect(self.send_monster)
        self.gui.MonsterButton_6.clicked.connect(self.send_monster)
        self.gui.SendButton.clicked.connect(self.send_name)
        self.gui.DisconnectButton.clicked.connect(self.disconnect)
        MainWindow.show()

    def listen_for_server_messages(self):
        while self.listening:
            try:
                data = client_socket.recv(1024).decode("utf-8")
                if data == "You can now close the app":
                    self.quit_signal.emit()
                    break  # Exit the thread when quitting the app
            except Exception as e:
                pass  # Handle exceptions, e.g., if the connection is closed

    def disconnect(self):
        self.listening = False  # Stop listening for messages
        stay = self.gui.get_stay()
        if not stay:
            client_socket.send(b'quit')
            client_socket.close()
            self.quit_signal.emit()

    def send_name(self):
        name = self.gui.get_name()
        if name:
            try:
                client_socket.send(("name: " + name).encode())
                print(f"Sent name to server: {name}")
            except Exception as e:
                print(f"Error sending name: {e}")

    def send_monster(self):
        monster = self.gui.get_monster()
        if monster:
            try:
                client_socket.send(("monster: " + str(monster)).encode())
                print(f"Sent monster to server: {str(monster)}")
            except Exception as e:
                print(f"Error sending monster: {e}")


if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 12345)
    while True:
        try:
            client_socket.connect(server_address)
            break
        except socket.error as e:
            if isinstance(e, ConnectionRefusedError):
                print("The server is not working right now")
            else:
                print("An error occurred:", e)
            time.sleep(5)
    new_player = player()

    # Connect the quit signal to the application's quit method
    new_player.quit_signal.connect(app.quit)

    sys.exit(app.exec())
