import os
import sys
import threading
import time

from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QPoint, QUrl
from PyQt6.QtGui import QIcon, QFont, QColor, QPainter, QPixmap, QPen
from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QWidget, QVBoxLayout, QFrame, \
    QTextEdit, QScrollArea, QHBoxLayout, QSizePolicy, QGridLayout, QSlider, QDialog


class ui_first_window(object):
    def __init__(self):
        self.name = ""
        self.monster = 0
        self.stay = True

    def setUpUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        icon_main_window = QIcon(os.path.join(os.getcwd(), 'skribbl_photo.jpg'))
        MainWindow.setWindowIcon(icon_main_window)
        self.centralwidget = QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Disable the close button
        MainWindow.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        # Set the initial position of the window
        window_width = 640  # Adjust the width as needed
        window_height = 480  # Adjust the height as needed
        screen_resolution = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_resolution.width()
        screen_height = screen_resolution.height()
        x_position = int((screen_width - window_width) / 2)  # Centered horizontally
        y_position = int((screen_height - window_height) / 3)  # Adjust the divisor for desired vertical position
        MainWindow.setGeometry(x_position, y_position, window_width, window_height)

        # Create a vertical layout for the central widget
        central_layout = QVBoxLayout(self.centralwidget)
        central_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.centralwidget.setLayout(central_layout)

        # Create the title label
        self.Title = QLabel(self.centralwidget)
        self.Title.setGeometry(200, 20, 400, 100)
        font = QFont()
        font.setFamily("Sitka Display")
        font.setPointSize(48)
        self.Title.setFont(font)
        self.Title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_layout.addWidget(self.Title)
        self.Title.setObjectName("Title")
        self.Title.setText(
            "<font color='red'>S</font><font color='green'>k</font><font color='blue'>r</font><font color='purple'>i</font><font color='orange'>b</font><font color='cyan'>b</font><font color='yellow'>l</font>")

        # Create the line edit for the name input
        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setPlaceholderText("Enter your name")
        central_layout.addWidget(self.lineEdit)
        self.lineEdit.setObjectName("lineEdit")

        # Create the send button with an icon
        self.SendButton = QPushButton(self.centralwidget)
        self.SendButton.setGeometry(500, 120, 40, 40)
        central_layout.addWidget(self.SendButton)
        icon_send = QIcon(os.path.join(os.getcwd(), 'send_photo.jpg'))
        self.SendButton.setIcon(icon_send)
        self.SendButton.setIconSize(icon_send.actualSize(self.SendButton.size()))
        self.SendButton.setObjectName("SendButton")
        self.SendButton.setEnabled(False)  # Initially disable the Send button

        # Connect the textChanged signal of the line edit to a slot
        self.lineEdit.textChanged.connect(self.toggle_send_button_state)

        # Create the label for character selection
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setGeometry(290, 170, 241, 41)
        central_layout.addWidget(self.label_2)
        font = QFont()
        font.setFamily("Segoe UI Symbol")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_2.setText("Select your character")

        # Create a horizontal layout for character selection buttons
        button_layout = QHBoxLayout()

        button_width = 200
        button_height = 200
        y_position = 250

        # Monster Button 1
        self.MonsterButton_1 = QPushButton(self.centralwidget)
        self.MonsterButton_1.setGeometry(250, y_position, button_width, button_height)
        button_layout.addWidget(self.MonsterButton_1)
        icon_Monster1 = QIcon(os.path.join(os.getcwd(), 'monster_1.png'))
        self.MonsterButton_1.setIcon(icon_Monster1)
        self.MonsterButton_1.setIconSize(icon_Monster1.actualSize(self.MonsterButton_1.size()))
        self.MonsterButton_1.setObjectName("MonsterButton_1")
        self.MonsterButton_1.clicked.connect(lambda: self.set_monster(1))

        # Monster Button 2
        self.MonsterButton_2 = QPushButton(self.centralwidget)
        self.MonsterButton_2.setGeometry(360, y_position, button_width, button_height)
        button_layout.addWidget(self.MonsterButton_2)
        icon_Monster2 = QIcon(os.path.join(os.getcwd(), 'monster_2.png'))
        self.MonsterButton_2.setIcon(icon_Monster2)
        self.MonsterButton_2.setIconSize(icon_Monster2.actualSize(self.MonsterButton_2.size()))
        self.MonsterButton_2.setObjectName("MonsterButton_2")
        self.MonsterButton_2.clicked.connect(lambda: self.set_monster(2))

        # Monster Button 3
        self.MonsterButton_3 = QPushButton(self.centralwidget)
        self.MonsterButton_3.setGeometry(470, y_position, button_width, button_height)
        button_layout.addWidget(self.MonsterButton_3)
        icon_Monster3 = QIcon(os.path.join(os.getcwd(), 'monster_3.png'))
        self.MonsterButton_3.setIcon(icon_Monster3)
        self.MonsterButton_3.setIconSize(icon_Monster3.actualSize(self.MonsterButton_3.size()))
        self.MonsterButton_3.setObjectName("MonsterButton_3")
        self.MonsterButton_3.clicked.connect(lambda: self.set_monster(3))

        central_layout.addLayout(button_layout)  # Add the initial monster buttons to the main layout

        # Create a new horizontal layout for the last 3 monster buttons
        button_layout2 = QHBoxLayout()

        y_position2 = 360

        # Monster Button 4
        self.MonsterButton_4 = QPushButton(self.centralwidget)
        button_layout2.addWidget(self.MonsterButton_4)
        self.MonsterButton_4.setGeometry(250, y_position2, button_width, button_height)
        icon_Monster4 = QIcon(os.path.join(os.getcwd(), 'monster_4.png'))
        self.MonsterButton_4.setIcon(icon_Monster4)
        self.MonsterButton_4.setIconSize(icon_Monster4.actualSize(self.MonsterButton_4.size()))
        self.MonsterButton_4.setObjectName("MonsterButton_4")
        self.MonsterButton_4.clicked.connect(lambda: self.set_monster(4))

        # Monster Button 5
        self.MonsterButton_5 = QPushButton(self.centralwidget)
        button_layout2.addWidget(self.MonsterButton_5)
        self.MonsterButton_5.setGeometry(360, y_position2, button_width, button_height)
        icon_Monster5 = QIcon(os.path.join(os.getcwd(), 'monster_5.png'))
        self.MonsterButton_5.setIcon(icon_Monster5)
        self.MonsterButton_5.setIconSize(icon_Monster5.actualSize(self.MonsterButton_5.size()))
        self.MonsterButton_5.setObjectName("MonsterButton_5")
        self.MonsterButton_5.clicked.connect(lambda: self.set_monster(5))

        # Monster Button 6
        self.MonsterButton_6 = QPushButton(self.centralwidget)
        button_layout2.addWidget(self.MonsterButton_6)
        self.MonsterButton_6.setGeometry(470, y_position2, button_width, button_height)
        icon_Monster6 = QIcon(os.path.join(os.getcwd(), 'monster_6.png'))
        self.MonsterButton_6.setIcon(icon_Monster6)
        self.MonsterButton_6.setIconSize(icon_Monster6.actualSize(self.MonsterButton_6.size()))
        self.MonsterButton_6.setObjectName("MonsterButton_6")
        self.MonsterButton_6.clicked.connect(lambda: self.set_monster(6))

        # Add the last 3 monster buttons to the main layout
        central_layout.addLayout(button_layout2)

        # Create the Disconnect button
        self.DisconnectButton = QPushButton(self.centralwidget)
        self.DisconnectButton.setText("Disconnect")
        central_layout.addWidget(self.DisconnectButton)

        # Set the DisconnectButton's height to match the monster buttons
        self.DisconnectButton.setFixedHeight(button_height)

        self.DisconnectButton.clicked.connect(self.disconnect)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = MainWindow.menuBar()
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = MainWindow.statusBar()
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

    def toggle_send_button_state(self):
        # Enable the Send button only if the line edit is not empty
        if self.lineEdit.text():
            self.SendButton.setEnabled(True)
        else:
            self.SendButton.setEnabled(False)

    def disconnect(self):
        self.stay = False

    def get_stay(self):
        return self.stay

    def retranslateUi(self, MainWindow):
        _translate = QApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Skribbl"))

    def set_monster(self, number):
        self.monster = number
        self.MonsterButton_1.setEnabled(False)
        self.MonsterButton_2.setEnabled(False)
        self.MonsterButton_3.setEnabled(False)
        self.MonsterButton_4.setEnabled(False)
        self.MonsterButton_5.setEnabled(False)
        self.MonsterButton_6.setEnabled(False)

    def get_monster(self):
        return self.monster


class WaitingRoomApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.message = ""
        self.setUpUi()

    def setUpUi(self):
        self.setWindowTitle("Waiting Room")
        self.setGeometry(100, 100, 800, 600)

        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        chat_frame = QFrame()
        chat_frame.setFrameShape(QFrame.Shape.Panel)
        chat_layout = QVBoxLayout(chat_frame)

        chat_title = QLabel("Chat")
        chat_layout.addWidget(chat_title)

        chat_scroll = QScrollArea()  # Create a scroll area for the chat
        chat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        chat_scroll.setWidgetResizable(True)

        self.chat_text = QTextEdit()
        self.chat_text.setReadOnly(True)
        chat_scroll.setWidget(self.chat_text)
        chat_layout.addWidget(chat_scroll)

        self.chat_input = QTextEdit()
        self.chat_input.textChanged.connect(self.toggle_send_button_state)
        self.chat_input.setPlaceholderText("Message")
        chat_layout.addWidget(self.chat_input)

        self.chat_send_button = QPushButton("Send")  # Define chat_send_button
        self.chat_send_button.setEnabled(False)  # Initially disable the Send button
        self.chat_send_button.clicked.connect(self.send_message)
        chat_layout.addWidget(self.chat_send_button)

        main_layout.addWidget(chat_frame)

        players_frame = QFrame()
        players_frame.setFrameShape(QFrame.Shape.Panel)
        players_layout = QVBoxLayout(players_frame)

        players_title = QLabel("Players")
        players_layout.addWidget(players_title)

        players_scroll = QScrollArea()  # Create a scroll area for players
        players_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        players_scroll.setWidgetResizable(True)

        self.players_names = QTextEdit()
        self.players_names.setReadOnly(True)
        players_scroll.setWidget(self.players_names)
        players_layout.addWidget(players_scroll)

        main_layout.addWidget(players_frame)

        self.disconnect_button = QPushButton("Disconnect")
        main_layout.addWidget(self.disconnect_button)

        self.show()

    def send_message(self):
        try:
            self.message = self.chat_input.toPlainText()
            self.chat_input.clear()
            # Create a QFont object with the desired font size (15px)
            font_size = "15px"
            html_content = f"<span style='font-size: {font_size}'>{'You: ' + self.message}</span><br>"
            self.chat_text.append(html_content)
        except Exception as e:
            print("Error in send_message:", str(e))

    def get_message(self):
        return self.message

    def toggle_send_button_state(self):
        # Enable the Send button only if the line edit is not empty
        if self.chat_input.toPlainText().strip():
            self.chat_send_button.setEnabled(True)
        else:
            self.chat_send_button.setEnabled(False)


class CountDownClock(QMainWindow):
    # Define a custom 'closed' signal
    closed = pyqtSignal()

    def __init__(self, initial_time=0):
        super().__init__()

        self.remaining_time = initial_time  # 30 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Countdown Clock")
        self.setGeometry(100, 100, 300, 200)

        # Disable the close button (x button)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        # Create a central widget and a vertical layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add label above the timer
        self.label_above = QLabel("The game will start in", self)
        font = self.label_above.font()
        font.setPointSize(30)  # Increase the font size
        self.label_above.setFont(font)
        self.label_above.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_above)

        # Add the countdown timer
        self.finish = QLabel(self)
        font = self.finish.font()
        font.setPointSize(48)  # Increase the font size
        self.finish.setFont(font)
        self.finish.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.finish)

        # Add label below the timer
        self.label_below = QLabel("seconds", self)
        font = self.label_below.font()
        font.setPointSize(30)  # Increase the font size
        self.label_below.setFont(font)
        self.label_below.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_below)

        self.update_clock()  # Initial display

    def update_clock(self):
        self.remaining_time -= 1
        if self.remaining_time >= 0:
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            self.finish.setText(f"{minutes:02d}:{seconds:02d}")
        else:
            self.timer.stop()
            self.finish.setText("Time's up!")
            self.label_above.hide()
            self.label_below.hide()
            self.close_self()

    def close_self(self):
        # Emit the 'closed' signal when the GUI is closed
        self.closed.emit()

        # Create a timer to close the window after 3 seconds
        close_timer = QTimer(self)
        close_timer.timeout.connect(self.close)
        close_timer.start(1000)  # Close the window after 2 seconds

    def custom_exec(self):
        self.show()
        self.timer.start(1000)
        app = QApplication.instance()

        # Run the application's event loop until the closed signal is emitted
        while self.isVisible():
            app.processEvents()


class DrawingLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.new_pos = None
        self.setMouseTracking(False)
        self.last_pos = None
        self.last_pos_before = None
        self.drawing = False
        self.pixels = QPixmap(self.size())
        self.pixels.fill(QColor(Qt.GlobalColor.white))
        self.pen = QPen()
        self.pen.setColor(QColor(Qt.GlobalColor.black))
        self.pen.setWidth(2)
        self.complete_painted_area = QPixmap(self.size())  # Store the complete painted area
        self.complete_painted_area.fill(QColor(Qt.GlobalColor.white))
        self.event_drawing = threading.Event()

    def create_line(self, start_point, end_point, width, color):
        painter = QPainter(self.pixels)
        pen = QPen(self.pen)  # Make a copy of the current pen
        pen.setWidth(width)  # Set the new width
        pen.setColor(QColor(color))  # Set the line color
        painter.setPen(pen)  # Use the updated pen
        painter.drawLine(start_point, end_point)

        # Update the complete painted area as well
        painter = QPainter(self.complete_painted_area)
        painter.setPen(pen)  # Use the updated pen
        painter.drawLine(start_point, end_point)

        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.pixels.size() != self.size():
            # Create a new pixmap only when the label size increases
            new_pixmap = QPixmap(self.size())
            new_pixmap.fill(QColor(Qt.GlobalColor.white))
            painter = QPainter(new_pixmap)

            # Copy the existing painted area onto the new pixmap
            painter.drawPixmap(0, 0, self.pixels)
            self.pixels = new_pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixels)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_pos = event.pos()
            self.drawing = True

    def mouseMoveEvent(self, event):
        if self.drawing:
            # Store the previous position before updating last_pos
            self.last_pos_before = self.last_pos

            # Update last_pos and new_pos
            self.last_pos = event.pos()
            self.new_pos = self.last_pos

            # Draw on the pixels canvas
            painter_pixels = QPainter(self.pixels)
            painter_pixels.setPen(self.pen)
            painter_pixels.drawLine(self.last_pos_before, self.last_pos)
            painter_pixels.end()

            # Draw on the complete painted area
            painter_complete = QPainter(self.complete_painted_area)
            painter_complete.setPen(self.pen)
            painter_complete.drawLine(self.last_pos_before, self.last_pos)
            painter_complete.end()

            # Signal the event for drawing update
            self.event_drawing.set()

            # Trigger the update to repaint the widget
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            # self.event_drawing.clear()

    def pen_color_change(self, color):
        self.pen.setColor(color)

    def get_pencil_color(self):
        return self.pen.color().name()

    def clear(self):
        self.pixels.fill(QColor(Qt.GlobalColor.white))
        self.update()

    def change_width(self, width):
        self.pen.setWidth(width)

    def get_last_pos(self):
        return self.last_pos_before

    def get_new_pos(self):
        return self.new_pos

    def get_pencil_width(self):
        return self.pen.width()

    def get_drawing(self):
        return self.drawing

    def set_complete_painted_area(self, complete_painted_area):
        self.complete_painted_area = complete_painted_area


class GameUi(QMainWindow):
    window_closed_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.message = ""
        self.timer_value = 60
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)  # Make the window unresizable
        self.setWindowFlag(Qt.WindowType.CustomizeWindowHint)  # Allow customization of the window frame
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)  # Disable the close button (x button)
        self.setWindowSizeToScreen()
        self.initUI()

    def setWindowSizeToScreen(self):
        desktop = QApplication.primaryScreen().geometry()  # Get the screen's geometry
        self.setFixedSize(desktop.width(), desktop.height())  # Set the window size to match the screen size

    def initUI(self):
        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a main layout for the central widget
        main_layout = QHBoxLayout(central_widget)

        # Create the left frame with 8 buttons and a big label
        left_frame = QFrame()
        left_layout = QGridLayout(left_frame)

        self.dict_colors = {
            "Crimson": QColor(220, 20, 60),
            "Gold": QColor(255, 215, 0),
            "Lime": QColor(50, 205, 50),
            "Turquoise": QColor(64, 224, 208),
            "Indigo": QColor(75, 0, 130),
            "Magenta": QColor(255, 0, 255),
            "Teal": QColor(0, 128, 128),
            "Salmon": QColor(250, 128, 114),
            "Olive": QColor(128, 128, 0),
            "SlateBlue": QColor(106, 90, 205),
            "Tomato": QColor(255, 99, 71),
            "DarkOrange": QColor(255, 140, 0),
            "SteelBlue": QColor(70, 130, 180),
            "MediumPurple": QColor(147, 112, 219),
            "LawnGreen": QColor(124, 252, 0),
            "SkyBlue": QColor(135, 206, 235),
            "DimGray": QColor(105, 105, 105),
            "Black": QColor(Qt.GlobalColor.black)
        }

        keys = [key for key in self.dict_colors]
        self.buttons_colors = []
        for i in range(9):
            self.button = QPushButton()
            self.button.setStyleSheet(f'background-color: {keys[i]};')
            self.button.clicked.connect(lambda checked, color=self.dict_colors[keys[i]]: self.change_color(color))
            self.buttons_colors.append(self.button)
            left_layout.addWidget(self.button, 1, i)
        for i in range(9):
            self.button = QPushButton()
            self.button.setStyleSheet(f'background-color: {keys[i + 9]};')
            self.button.clicked.connect(lambda checked, color=self.dict_colors[keys[i + 9]]: self.change_color(color))
            self.buttons_colors.append(self.button)
            left_layout.addWidget(self.button, 2, i)

        self.eraser_button = QPushButton()
        eraser_icon = QIcon(os.path.join(os.getcwd(), 'eraser.png'))
        self.eraser_button.setIcon(eraser_icon)
        self.eraser_button.setIconSize(QSize(30, 20))
        self.eraser_button.clicked.connect(lambda: self.change_color(QColor(Qt.GlobalColor.white)))
        left_layout.addWidget(self.eraser_button, 1, 9)

        self.trash_button = QPushButton()
        trash_icon = QIcon(os.path.join(os.getcwd(), 'trash.jpg'))
        self.trash_button.setIcon(trash_icon)
        self.trash_button.setIconSize(QSize(30, 20))
        self.trash_button.clicked.connect(self.clear_label)
        left_layout.addWidget(self.trash_button, 2, 9)

        self.pencil_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.pencil_width_slider.setRange(0, 100)
        self.pencil_width_slider.setValue(2)
        self.pencil_width_slider.setTickInterval(10)
        self.pencil_width_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.pencil_width_slider.valueChanged.connect(self.change_width)
        left_layout.addWidget(self.pencil_width_slider, 3, 0, 1, 10)

        self.big_label = DrawingLabel()
        self.big_label.setStyleSheet('background-color: white;')

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.big_label)
        scroll_area.setWidgetResizable(True)

        left_layout.addWidget(scroll_area, 4, 0, 1, 10)

        # Add the disconnect button
        self.disconnect_button = QPushButton('Disconnect')
        left_layout.addWidget(self.disconnect_button, 5, 0, 1, 10)

        # Initialize a QTimer for the countdown
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # Add a QLabel to display the countdown timer
        self.timer_label = QLabel(self)
        font = self.timer_label.font()
        font.setPointSize(20)
        self.timer_label.setFont(font)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setText(f"Time left: {self.timer_value} seconds")
        # Insert the timer label into the layout
        left_layout.addWidget(self.timer_label, 0, 0, 1, 10)

        # Create the right frame with a label, QTextEdits, and a button
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)

        answer_label = QLabel('Chat answers', alignment=Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setFamily("Segoe UI Symbol")
        font.setPointSize(20)

        self.chat_text = QTextEdit()
        answer_label.setFont(font)
        self.chat_text.setReadOnly(True)
        self.chat_input = QTextEdit()
        self.chat_input.textChanged.connect(self.toggle_send_button_state)
        self.chat_send_button = QPushButton('Send')
        self.chat_send_button.setEnabled(False)
        self.chat_send_button.clicked.connect(self.send_message)

        self.chat_text.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        answer_label.setFixedSize(255, 75)
        self.chat_input.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.chat_input.setFixedSize(255, 30)

        right_layout.addWidget(answer_label)
        right_layout.addWidget(self.chat_text)
        right_layout.addWidget(self.chat_input)
        right_layout.addWidget(self.chat_send_button)

        left_frame.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        left_layout.setSizeConstraint(QGridLayout.SizeConstraint.SetDefaultConstraint)
        left_layout.setVerticalSpacing(0)

        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)

        self.showMaximized()  # Set the window to full-screen mode
        self.setWindowTitle('Flexible PyQt Application')

    def resizeEvent(self, event):
        # Get the current size of the window
        new_size = event.size()

        # Get the size of the painted area (pixmap in DrawingLabel)
        painted_size = self.big_label.complete_painted_area.size()

        # If the window size is smaller than the painted area, set it to the painted area size
        if new_size.width() < painted_size.width() or new_size.height() < painted_size.height():
            new_size.setWidth(max(new_size.width(), painted_size.width()))
            new_size.setHeight(max(new_size.height(), painted_size.height()))
            self.resize(new_size)

        super().resizeEvent(event)

    def change_color(self, color):
        self.big_label.pen_color_change(color)

    def clear_label(self):
        try:
            self.big_label.clear()
        except Exception as e:
            print(e)

    def change_width(self, width):
        self.big_label.change_width(width)

    def toggle_send_button_state(self):
        # Enable the Send button only if the line edit is not empty
        if self.chat_input.toPlainText().strip():
            self.chat_send_button.setEnabled(True)
        else:
            self.chat_send_button.setEnabled(False)

    def send_message(self):
        try:
            self.message = self.chat_input.toPlainText()
            self.chat_input.clear()
            # Create a QFont object with the desired font size (15px)
            font_size = "15px"
            html_content = f"<span style='font-size: {font_size}'>{'You: ' + self.message}</span><br>"
            self.chat_text.append(html_content)
        except Exception as e:
            print("Error in send_message:", str(e))

    def get_message(self):
        return self.message

    def update_timer(self):
        # Update the timer value and display it
        self.timer_value -= 1
        self.timer_label.setText(f"Time left: {self.timer_value} seconds")

        # Check if the timer has reached 0
        if self.timer_value <= 0:
            self.timer.stop()  # Stop the timer
            self.timer_label.setText("Time's up!")
            self.window_closed_signal.emit()
            self.close()  # Close the window when the timer reaches 0

    def start_timer(self):
        # Start the timer with a 1000ms (1 second) interval
        self.timer.start(1000)

    def closeEvent(self, event):
        self.timer.stop()
        self.timer.timeout.disconnect(self.update_timer)
        super().closeEvent(event)


class WordsUi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Words to Draw')
        self.setGeometry(100, 100, 400, 200)

        # Disable the close button
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()

        self.title = QLabel('Choose word to draw', alignment=Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setFamily("Segoe UI Symbol")
        font.setPointSize(20)
        self.title.setFont(font)

        self.buttons = (QPushButton(), QPushButton(), QPushButton())

        # Set the vertical size policy to Expanding for the buttons
        self.buttons[0].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.buttons[1].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.buttons[2].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        v_layout.addWidget(self.title)
        v_layout.addLayout(h_layout)  # Add the horizontal layout to the vertical layout

        # Adjust the stretch factor for the title to make it take less space
        v_layout.setStretchFactor(self.title, 1)
        v_layout.setStretchFactor(h_layout, 7)

        h_layout.addWidget(self.buttons[0])
        h_layout.addWidget(self.buttons[1])
        h_layout.addWidget(self.buttons[2])

        central_widget.setLayout(v_layout)

    def custom_exec(self):
        self.show()
        app = QApplication.instance()
        while self.isVisible():
            app.processEvents()


class CurrentResults(QMainWindow):
    window_closed_signal = QtCore.pyqtSignal()

    def __init__(self, word, num_rows):
        super().__init__()

        self.row_label = []
        self.word = word
        self.num_rows = num_rows

        self.init_ui()
        self.init_timer()

    def init_ui(self):
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)  # Disable the close button (x button)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        title_label = QLabel(f"The word was: {self.word}")
        title_label.setFont(QFont("Arial", 30))
        layout.addWidget(title_label)

        for i in range(self.num_rows):
            self.row_label.append(QLabel(f"{i + 1}"))
            self.row_label[i].setFont(QFont("Arial", 20))
            layout.addWidget(self.row_label[i])

        self.setWindowTitle("Word Display App")
        self.setGeometry(100, 100, 400, 300)

    def init_timer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.close_window)
        timer.start(5000)  # 5000 milliseconds = 5 seconds

    def close_window(self):
        self.close()

    def closeEvent(self, event):
        self.window_closed_signal.emit()
        super().closeEvent(event)


class GameOverWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Over")
        self.setGeometry(600, 350, 800, 400)

        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)  # Disable the close button (x button)

        # Set window size policy to fixed
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # Disable resizing
        self.setFixedSize(self.size())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        label = QLabel("Game over\nYou are the last survivor", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = label.font()
        font.setPointSize(50)  # Adjust the font size as desired
        label.setFont(font)
        layout.addWidget(label)
        self.game_over_sound()

    def game_over_sound(self):
        filename = "game_over.wav"
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile(filename))
        self.audio_output.setVolume(50)
        # Connect the finished signal of QMediaPlayer to close_window method
        self.player.mediaStatusChanged.connect(self.close_window)
        # Play the audio
        self.player.play()

    def close_window(self, status):
        # Close the window one second after the sound ends
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            QTimer.singleShot(2000, self.close)


class WinnerWindow(QWidget):
    def __init__(self, winner):
        super().__init__()
        self.setWindowTitle("Winner Window")

        # Load the image
        pixmap = QPixmap("winner.jpg")
        if pixmap.isNull():
            print("Error loading image!")
            sys.exit(1)

        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)  # Disable the close button (x button)

        # Set the window size to match the image
        self.setFixedSize(pixmap.size())

        # Create a label to display the image
        self.image_label = QLabel(self)
        self.image_label.setPixmap(pixmap)

        # Display the winner text
        self.winner_label = QLabel(self)
        self.winner_label.setText(f"{winner}!")
        self.winner_label.setFont(QFont("Ink Free", 80))  # Adjust font size here
        self.winner_label.setStyleSheet("color: rgb(82, 107, 127)")
        self.winner_label.adjustSize()

        # Calculate the position of the winner label centered on the image
        winner_label_x = (self.width() - self.winner_label.width()) // 2 + 10
        winner_label_y = (self.height() - self.winner_label.height()) // 2 + 30

        # Set the position of the winner label
        self.winner_label.move(winner_label_x, winner_label_y)

        # Center the window on the screen
        self.center_on_screen()
        self.win_sound()

    def center_on_screen(self):
        # Get the primary screen's geometry
        screen_geometry = QApplication.primaryScreen().geometry()

        # Calculate the center point of the screen
        center_point = screen_geometry.center()

        # Move the window to the center of the screen
        self.move(center_point - self.rect().center())

    def win_sound(self):
        filename = "win_sound.wav"
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile(filename))
        self.audio_output.setVolume(50)
        # Connect the finished signal of QMediaPlayer to close_window method
        self.player.mediaStatusChanged.connect(self.close_window)
        # Play the audio
        self.player.play()

    def close_window(self, status):
        # Close the window one second after the sound ends
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            QTimer.singleShot(2000, self.close)


class NotAvailable(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)  # Disable the close button (x button)
        # Create a label with the message
        self.message_label = QLabel("The server is busy\ncome back later", self)

        # Create a QFont object with the desired font size
        font = QFont()
        font.setPointSize(50)  # Set the font size to 14 points
        font.setBold(True)  # Optionally, set the font to bold

        # Apply the custom font to the label
        self.message_label.setFont(font)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.message_label)
        self.setLayout(layout)

        # Adjust the window size to fit the label's preferred size
        self.adjustSize()

        # Create a timer to close the window after 10 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)  # Connect timer timeout signal to close method
        self.timer.start(5000)


class ServerShutDown(QDialog):
    # Define a custom signal
    windowClosed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)  # Disable the close button (x button)
        # Create a label with the message
        self.message_label = QLabel("The server experienced an unplanned shutdown", self)

        # Create a QFont object with the desired font size
        font = QFont()
        font.setPointSize(50)  # Set the font size to 14 points
        font.setBold(True)  # Optionally, set the font to bold

        # Apply the custom font to the label
        self.message_label.setFont(font)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.message_label)
        self.setLayout(layout)

        # Adjust the window size to fit the label's preferred size
        self.adjustSize()

        # Create a timer to close the window after 10 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)  # Connect timer timeout signal to close method
        self.timer.start(5000)

    # Override closeEvent to emit the custom signal
    def closeEvent(self, event):
        self.windowClosed.emit()
        super().closeEvent(event)


def main_words():
    app = QApplication([])
    window = WordsUi()
    window.show()
    app.exec()


def main_game():
    app = QApplication(sys.argv)
    window = GameUi()
    sys.exit(app.exec())


def main_timer():
    app = QApplication(sys.argv)
    clock = CountDownClock()
    clock.show()
    clock.timer.start(1000)  # Start the timer with a 1-second interval
    sys.exit(app.exec())


def main_first_window():
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = ui_first_window()
    ui.setUpUi(MainWindow)

    screen = QApplication.primaryScreen()
    screen_size = screen.size()
    MainWindow.resize(screen_size)
    MainWindow.show()
    sys.exit(app.exec())


def main_second_window():
    app = QApplication(sys.argv)
    waiting_room_app = WaitingRoomApp()  # Create an instance of the WaitingRoomApp
    waiting_room_app.show()
    sys.exit(app.exec())


def main_current_results():
    app = QApplication(sys.argv)
    word_display_app = CurrentResults("ExampleWord", 9)
    word_display_app.show()
    sys.exit(app.exec())


def main_game_over():
    app = QApplication(sys.argv)
    window = GameOverWindow()
    window.show()
    sys.exit(app.exec())


def main_winner():
    app = QApplication(sys.argv)
    winner = "John"  # You can replace this with the actual winner name
    window = WinnerWindow(winner)
    window.show()
    sys.exit(app.exec())


def main_not_available_window():
    app = QApplication(sys.argv)
    busy_window = NotAvailable()
    busy_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main_not_available_window()
