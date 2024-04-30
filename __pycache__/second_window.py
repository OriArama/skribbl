import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame, QLabel, QTextEdit, QPushButton, QScrollBar

class WaitingRoomApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Waiting Room")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        chat_frame = QFrame()
        chat_frame.setFrameShape(QFrame.Shape.Panel)
        chat_layout = QVBoxLayout(chat_frame)

        chat_title = QLabel("Chat")
        chat_layout.addWidget(chat_title)

        chat_label = QTextEdit()
        chat_label.setReadOnly(True)
        chat_layout.addWidget(chat_label)

        chat_input = QTextEdit()
        chat_layout.addWidget(chat_input)

        chat_send_button = QPushButton("Send")
        chat_layout.addWidget(chat_send_button)

        chat_scroll = QScrollBar()
        chat_layout.addWidget(chat_scroll)

        main_layout.addWidget(chat_frame)

        players_frame = QFrame()
        players_frame.setFrameShape(QFrame.Shape.Panel)
        players_layout = QVBoxLayout(players_frame)

        players_title = QLabel("Players")
        players_layout.addWidget(players_title)

        players_label = QLabel()
        players_label.setWordWrap(True)
        players_layout.addWidget(players_label)

        players_scroll = QScrollBar()
        players_layout.addWidget(players_scroll)

        main_layout.addWidget(players_frame)

        self.show()

def main():
    app = QApplication(sys.argv)
    ex = WaitingRoomApp()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
