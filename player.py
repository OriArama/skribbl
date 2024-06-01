import subprocess
import warnings
import socket
import os
import time
import threading
from functools import partial
import PyQt6
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QPainter, QPen
import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QMessageBox
import gui as g

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
client_socket_lock = threading.Lock()
buffer_size = 1464  # 1024 bytes + 440 bytes of the cipher key


def encrypt(data):
    """Encrypt data using Fernet cipher suite."""
    encrypted_data = cipher_suite.encrypt(data.encode('utf-8'))
    return encrypted_data


def decrypt(encrypted_data):
    """Decrypt encrypted data using Fernet cipher suite."""
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode('utf-8')
    return decrypted_data


class player(QtCore.QObject):
    close_first_window_signal = QtCore.pyqtSignal()  # Signal to close the main window.
    open_waiting_room_signal = QtCore.pyqtSignal()  # Signal to open the waiting room window.
    update_gui_players_names_signal = QtCore.pyqtSignal(str, object)  # Signal to update GUI with players' names.
    update_gui_chat_text_signal = QtCore.pyqtSignal(str, object, str)  # Signal to update GUI with chat messages.
    remove_player_signal = QtCore.pyqtSignal(str, object)  # Signal to remove a player from the GUI. 
    turn_on_timer_signal = QtCore.pyqtSignal()  # Signal to turn on the timer.
    close_timer_signal = QtCore.pyqtSignal()  # Signal to close the timer.
    open_game_signal = QtCore.pyqtSignal()  # Signal to open the game window.
    update_drawing_signal = QtCore.pyqtSignal(float, float, float, float, int,
                                              str)  # Signal to update drawing on the GUI.
    clear_painting_signal = QtCore.pyqtSignal()  # Signal to clear the drawing on the GUI.
    start_game_timer_signal = QtCore.pyqtSignal()  # Signal to start the game timer.
    close_game_signal = QtCore.pyqtSignal(object)  # Signal to close the game.
    open_not_available_window_signal = QtCore.pyqtSignal()
    number_of_players = 0
    game_word = ""
    players_order = []
    number_of_player_limits_to_start_the_game = 3
    already_close_game = False
    word_button_clicked = False

    def __init__(self):
        super().__init__()
        self.is_thread_running = None
        self.gui_current_results = None
        self.name = ""
        self.monster = ""
        self.initial_time = 0
        self.gui_waiting_room = None
        self.gui_game = None
        self.clock = None
        self.gui_server_shut_down = None
        self.timer = QTimer()  # Create a QTimer to periodically check button states
        self.timer.timeout.connect(self.check_button_states)
        self.timer.start(1000)  # Adjust the timer interval as needed
        self.event_listen_for_server_messages = threading.Event()
        self.event_number_players = threading.Event()
        thread1 = threading.Thread(target=self.listen_for_server_messages, daemon=True)
        thread1.daemon = True
        thread1.start()
        self.gui_first_window = g.ui_first_window()
        self.handle_gui_first_window()

    def handle_gui_first_window(self):
        """
        Handle the initial GUI window.

        Sets up the main window, connects UI elements to functions, and displays the window.
        """
        global MainWindow
        self.gui_first_window.setUpUi(MainWindow)
        self.gui_first_window.retranslateUi(MainWindow)
        self.gui_first_window.MonsterButton_1.clicked.connect(self.send_monster)
        self.gui_first_window.MonsterButton_2.clicked.connect(self.send_monster)
        self.gui_first_window.MonsterButton_3.clicked.connect(self.send_monster)
        self.gui_first_window.MonsterButton_4.clicked.connect(self.send_monster)
        self.gui_first_window.MonsterButton_5.clicked.connect(self.send_monster)
        self.gui_first_window.MonsterButton_6.clicked.connect(self.send_monster)
        self.gui_first_window.SendButton.clicked.connect(self.send_name)
        self.gui_first_window.DisconnectButton.clicked.connect(self.disconnect_first_window)
        MainWindow.show()


    def check_button_states(self):
        """
        Check button states periodically.

        Checks if the monster selection buttons and name input field are enabled.
        If they are disabled, sets the event to notify that the main window is ready to be closed.
        """
        if not self.gui_first_window.MonsterButton_1.isEnabled() and not self.gui_first_window.lineEdit.isEnabled():
            self.event_listen_for_server_messages.set()

    def handle_waiting_room_window(self):
        """
        Handle the waiting room GUI window.

        Sets up the waiting room window, connects UI elements to functions,
        starts a thread to handle incoming messages, and displays the window.
        """
        try:
            self.gui_waiting_room = g.WaitingRoomApp()
            self.gui_waiting_room.setUpUi()
            self.gui_waiting_room.chat_send_button.clicked.connect(lambda: self.send_messages(self.gui_waiting_room))
            self.gui_waiting_room.disconnect_button.clicked.connect(self.disconnect_from_server)
            self.is_thread_running = True  # Flag to control the thread
            tread1 = threading.Thread(target=self.handle_messages, args=(self.gui_waiting_room,), daemon=True)
            tread1.daemon = True
            tread1.start()
            self.gui_waiting_room.show()
        except Exception as e:
            print(f"Error: {e}")

    def handle_game_window(self):
        """
        Handle the game GUI window.

        Sets up the game window, determines the role of the player (drawer or guesser),
        and connects UI elements to functions accordingly.
        """
        drawer = ""
        try:
            message = decrypt(client_socket.recv(buffer_size))
            client_socket.send(encrypt("thanks"))
        except ConnectionResetError as cre:
            self.gui_server_shut_down = g.ServerShutDown()
            self.gui_server_shut_down.show()
            self.gui_server_shut_down.windowClosed.connect(quit)
        if message == "You are the drawer":
            try:
                words_message = decrypt(client_socket.recv(buffer_size))
                client_socket.send(encrypt("thanks"))
            except ConnectionResetError as cre:
                self.gui_server_shut_down = g.ServerShutDown()
                self.gui_server_shut_down.show()
                self.gui_server_shut_down.windowClosed.connect(quit)
            list_words = words_message.split(',')
            list_words = list_words[1:]
            self.gui_words = g.WordsUi()
            for i in range(3):
                self.gui_words.buttons[i].setText(list_words[i])
                self.gui_words.buttons[i].clicked.connect(partial(self.send_word, self.gui_words.buttons[i].text()))
            self.gui_words.custom_exec()
            self.gui_game = g.GameUi()
            self.gui_game.timer_value = 60
            self.thread3 = threading.Thread(target=self.handle_messages, args=(self.gui_game,), daemon=True)
            self.thread3.start()
            self.gui_game.timer_label.hide()
            self.gui_game.chat_input.hide()
            self.gui_game.chat_send_button.hide()
            self.gui_game.trash_button.clicked.connect(self.clear_painting_message)
            self.gui_game.disconnect_button.clicked.connect(self.drawer_disconnected)
            if not self.word_button_clicked:
                client_socket.send(encrypt(' '))
                self.drawer_disconnected()
            else:
                self.word_button_clicked = False
            thread4 = threading.Thread(target=self.drawing_change, daemon=True)
            thread4.start()
            self.gui_game.window_closed_signal.connect(lambda: self.close_game(self.gui_game))
        elif message == "You are a guesser":
            try:
                drawer = decrypt(client_socket.recv(buffer_size))
                client_socket.send(encrypt("thanks"))
            except ConnectionResetError as cre:
                self.gui_server_shut_down = g.ServerShutDown()
                self.gui_server_shut_down.show()
                self.gui_server_shut_down.windowClosed.connect(quit)
            self.gui_game = g.GameUi()
            self.gui_game.timer_value = 60
            self.thread3 = threading.Thread(target=self.handle_messages, args=(self.gui_game,), daemon=True)
            self.thread3.start()
            self.gui_game.big_label.setEnabled(False)
            for button_color in self.gui_game.buttons_colors:
                button_color.hide()
            self.gui_game.timer_label.hide()
            self.gui_game.eraser_button.hide()
            self.gui_game.trash_button.hide()
            self.gui_game.pencil_width_slider.hide()
            self.gui_game.disconnect_button.hide()
            self.gui_game.chat_text.append(f'<span style="font-size: 15px; color: blue;">{drawer}</span><br>')
            self.gui_game.chat_send_button.clicked.connect(lambda: self.send_messages(self.gui_game))
            self.gui_game.disconnect_button.clicked.connect(self.guesser_disconnected)
            self.gui_game.window_closed_signal.connect(lambda: self.close_game(self.gui_game))


    def handle_winner_window(self):
        """
        Handle the winner window.

        Displays the winner of the game in a separate window.
        """
        winner = decrypt(client_socket.recv(buffer_size))
        client_socket.send(encrypt("thanks".ljust(1024)))
        self.gui_winner = g.WinnerWindow(winner)
        self.gui_winner.show()

    def drawer_disconnected(self):
        """
        Handle the case when the drawer disconnects.

        Closes the game window, notifies the server, and terminates the client.
        """
        self.gui_game.close()
        try:
            client_socket.send(encrypt("Drawer_disconnected"))
        except ConnectionResetError as cre:
            quit()
        client_socket.close()
        quit()

    def guesser_disconnected(self):
        """
        Handle the case when the guesser disconnects.

        Closes the game window, notifies the server, and terminates the client.
        """
        self.gui_game.close()
        try:
            client_socket.send(encrypt("Guesser_disconnected"))
        except ConnectionResetError as cre:
            quit()
        client_socket.close()
        quit()

    def no_more_players(self):
        """
        Handle the case when there are no more players in the game except for one.

        Displays a message indicating that the game is over.
        """
        self.gui_game_over = g.GameOverWindow()
        self.gui_game_over.show()

    def start_game_timer(self):
        """
        Start the game timer.

        Displays the timer in the game window and enables the disconnect button.
        """
        self.gui_game.disconnect_button.show()
        self.gui_game.timer_label.show()
        self.gui_game.start_timer()

    def send_word(self, word):
        """
        Send the chosen word to the server.

        Args:
            word (str): The word chosen by the player.

        Sends the chosen word to the server for the drawing round.
        """
        try:
            self.word_button_clicked = True
            client_socket.send(encrypt(("Word," + word)))
        except ConnectionResetError as cre:
            self.gui_words.close()
            self.gui_server_shut_down = g.ServerShutDown()
            self.gui_server_shut_down.show()
            self.gui_server_shut_down.windowClosed.connect(quit)
        self.gui_words.close()

    def clear_painting_message(self):
        """
        Send a message to clear the drawing on the canvas.

        Sends a message to the server to clear the drawing canvas.
        """
        try:
            client_socket.send(encrypt("Clear painting"))
        except ConnectionResetError as cre:
            self.gui_game.close()
            self.gui_server_shut_down = g.ServerShutDown()
            self.gui_server_shut_down.show()
            self.gui_server_shut_down.windowClosed.connect(quit)

    def send_finish(self):
        """
        Send a message to indicate the end of the game round.

        Sends a message to the server to indicate that the game round has finished.
        """
        self.is_thread_running = False
        client_socket.send(encrypt("Game round finish"))

    def current_results(self):
        """
        Display the current game results.

        Displays the current game results including player scores in a separate window.
        """
        self.gui_current_results = g.CurrentResults(self.game_word, self.number_of_players)
        for i in range(self.number_of_players):
            row = self.players_order[i].split(",")
            html_content = f"<img src='file://{os.path.join(os.getcwd(), 'images', 'monster_' + row[0] + '.png')}' height='30' width='30'>"
            text_content = f"{self.gui_current_results.row_label[i].text()} {html_content} {row[1]} {row[2]} points"

            # Set text format to RichText and set HTML content
            self.gui_current_results.row_label[i].setTextFormat(Qt.TextFormat.RichText)
            self.gui_current_results.row_label[i].setText(text_content)
        self.gui_current_results.show()
        self.gui_current_results.window_closed_signal.connect(self.starting_another_round)

    def starting_another_round(self):
        """
        Prepare for starting another round of the game.

        Sends a message to the server to start another round of the game.
        """
        try:
            client_socket.send(encrypt("Finish current results"))
            self.game_word = ""
            self.players_order = []
            self.is_thread_running = True
            self.already_close_game = False
            is_last_round = decrypt(client_socket.recv(buffer_size))
            client_socket.send(encrypt("thanks"))
            if is_last_round == "The last player":
                self.no_more_players()
            elif is_last_round == "show the winner":
                self.handle_winner_window()
            else:
                self.handle_game_window()
        except ConnectionResetError as cre:
            self.gui_server_shut_down = g.ServerShutDown()
            self.gui_server_shut_down.show()
            self.gui_server_shut_down.windowClosed.connect(quit)

    def drawing_change(self):
        """
        Continuously monitor and send drawing updates.

        Monitors for changes in the drawing canvas and sends updates to the server.
        """
        last_pos1 = None
        new_pos1 = None

        while self.is_thread_running:
            # Wait for the event with a timeout
            self.gui_game.big_label.event_drawing.wait(timeout=0.1)

            if not self.is_thread_running:
                break  # Exit the loop if the thread is no longer running

            if self.gui_game.big_label.event_drawing.is_set():
                # The event is set, perform your drawing update
                current_last_pos = self.gui_game.big_label.get_last_pos()
                current_new_pos = self.gui_game.big_label.get_new_pos()

                if current_last_pos is not None and current_new_pos is not None:
                    if current_last_pos != last_pos1 or current_new_pos != new_pos1:
                        self.send_drawing_update(current_last_pos,
                                                 current_new_pos,
                                                 self.gui_game.big_label.get_pencil_width(),
                                                 self.gui_game.big_label.get_pencil_color())
                last_pos1 = current_last_pos
                new_pos1 = current_new_pos
                self.gui_game.big_label.event_drawing.clear()
            else:
                pass

    def normalize_coordinates(self, sender_size, start_pos, end_pos):
        """
        Normalize coordinates relative to the sender's size.

        Args:
            sender_size (QSize): Size of the sender widget.
            start_pos (QPoint): Starting position of the drawing.
            end_pos (QPoint): Ending position of the drawing.

        Returns:
            Tuple[float, float, float, float]: Normalized coordinates (start_x, start_y, end_x, end_y).
        """
        sender_width, sender_height = sender_size.width(), sender_size.height()

        # Ensure the coordinates are integers
        start_x = start_pos.x() / sender_width
        start_y = start_pos.y() / sender_height
        end_x = end_pos.x() / sender_width
        end_y = end_pos.y() / sender_height

        return start_x, start_y, end_x, end_y

    def send_drawing_update(self, start_pos, end_pos, width, color):
        """
        Send drawing updates to the server.

        Args:
            start_pos (QPoint): Starting position of the drawing.
            end_pos (QPoint): Ending position of the drawing.
            width (int): Width of the drawing.
            color (str): Color of the drawing.

        Sends drawing updates to the server for synchronization.
        """
        # Create a message containing drawing updates (start_pos, end_pos, width)
        start_x, start_y, end_x, end_y = self.normalize_coordinates(self.gui_game.big_label.size(), start_pos, end_pos)
        message = f"DRAWING|{start_x},{start_y}|{end_x},{end_y}|{width}|{color}|"
        message = message.ljust(1024)
        # Send the message to the server using your client_socket
        try:
            client_socket.send(encrypt(message))
        except ConnectionResetError as e:
            pass

    def handle_messages(self, window):
        """
        Continuously handle incoming messages from the server.

        Args:
            window (QObject): The window instance to handle messages for.

        Monitors for incoming messages from the server and handles them accordingly.
        """
        while True:
            try:
                data = decrypt(client_socket.recv(buffer_size))
            except:
                break
            client_socket.send(encrypt("thanks".ljust(1024)))
            if data.startswith("Player joins"):
                self.number_of_players = self.number_of_players + 1
                parts = data.split(',')
                name = parts[1]
                monster = parts[2]
                # Set the desired font size (change 16 to your preferred size)
                font_size = "30px"
                # Create HTML content for displaying the monster image and player's name
                html_content = f"<img src='file://{os.path.join(os.getcwd(), 'images', 'monster_' + monster + '.png')}' height='30' width='30'>"
                html_content += f"<span style='font-size: {font_size}'>{name}</span><br>"
                # Append the HTML content to the players_names QTextEdit
                self.update_gui_players_names_signal.emit(html_content, window)
            elif data.startswith("message: "):
                parts = data.split(" ")
                for i in range(2):
                    parts.pop(0)
                name = ""
                i = 0
                for part in parts:
                    if part == "monster:":
                        monster = parts[i + 1]
                        break
                    name += part + " "
                    i = i + 1
                name = name + ": "
                text = ""
                i = i + 3
                for part in parts[i:]:
                    text = text + part + " "
                font_size = "15px"
                html_content = f"<img src='file://{os.path.join(os.getcwd(), 'images', 'monster_' + monster + '.png')}' height='15' width='15'>"
                html_content += f"<span style='font-size: {font_size}'>{name + text}</span><br>"
                self.update_gui_chat_text_signal.emit(html_content, window, None)
            elif data.startswith("remove "):
                self.number_of_players = self.number_of_players - 1
                parts = data.split(",")
                name = parts[1]
                monster = parts[2]
                self.remove_player_signal.emit(name, window)
            elif data.startswith("Timer"):
                self.initial_time = int(data.split(',')[1])
                self.turn_on_timer_signal.emit()
            elif data.startswith("Close app"):
                self.open_game_signal.emit()
                break
            elif data.startswith("DRAWING"):
                parts = data.split("|")
                last_pos_x = float(parts[1].split(',')[0])
                last_pos_y = float(parts[1].split(',')[1])
                new_pos_x = float(parts[2].split(',')[0])
                new_pos_y = float(parts[2].split(',')[1])
                pencil_width = int(parts[3])
                pencil_color = parts[4]
                self.update_drawing_signal.emit(last_pos_x, last_pos_y, new_pos_x, new_pos_y, pencil_width,
                                                pencil_color)
            elif data.startswith("Clear painting"):
                self.clear_painting_signal.emit()
            elif data.startswith("Solve"):
                parts = data.split(',')
                name = parts[1]
                state = None
                if name == self.name:
                    name = "You "
                    font_size = "15px"
                    text = parts[3]
                    html_content = f"<span style='font-size: {font_size}; color: green;'>{name + text}</span><br>"
                    state = "disable"
                else:
                    name = parts[1] + ": "
                    monster = parts[2]
                    text = parts[3]
                    font_size = "15px"
                    html_content = f"<img src='file://{os.path.join(os.getcwd(), 'images', 'monster_' + monster + '.png')}' height='15' width='15'>"
                    html_content += f"<span style='font-size: {font_size}; color: green;'>{name + text}</span><br>"
                    state = "enable"
                self.update_gui_chat_text_signal.emit(html_content, window, state)
            elif data == "Start Timer game":
                self.start_game_timer_signal.emit()
            elif data.startswith("Game word: "):
                self.game_word = data[11:]
                message = decrypt(client_socket.recv(buffer_size))
                self.number_of_players = 0
                while message != "stop":
                    self.players_order.append(message)
                    self.number_of_players = self.number_of_players + 1
                    client_socket.send(encrypt("thanks"))
                    message = decrypt(client_socket.recv(buffer_size))
                client_socket.send(encrypt("thanks"))
                break
            elif data == "Finish game round":
                self.close_game_signal.emit(window)

            elif data.startswith("Left"):
                text = data.split(",")[1]
                font_size = "15px"
                html_content = f"<span style='font-size: {font_size}; color: red;'>{text}</span><br>"
                state = "enable"
                self.update_gui_chat_text_signal.emit(html_content, window, state)

    def close_game(self, window):
        """
        Close game window GUI.
        """
        if not self.already_close_game:
            self.already_close_game = True
            if window.isVisible():
                window.close()
            self.send_finish()
            self.thread3.join()
            self.current_results()

    def clear_painting(self):
        """
        Clear the board
        """
        self.gui_game.big_label.clear()

    # Example of denormalizing coordinates on the receiver side
    def denormalize_coordinates(self, receiver_size, normalized_start_pos_x, normalized_start_pos_y,
                                normalized_end_pos_x,
                                normalized_end_pos_y):
        """
        Denormalize coordinates relative to the receiver's size.

        Args:
            receiver_size (QSize): Size of the receiver widget.
            denormalized_start_pos (QPoint): Starting position of the drawing.
            denormalized_end_pos (QPoint): Ending position of the drawing.

        Returns:
            Denormalized coordinates
        """
        receiver_width, receiver_height = receiver_size.width(), receiver_size.height()
        denormalized_start_pos = PyQt6.QtCore.QPoint(int(normalized_start_pos_x * receiver_width),
                                                     int(normalized_start_pos_y * receiver_height))
        denormalized_end_pos = PyQt6.QtCore.QPoint(int(normalized_end_pos_x * receiver_width),
                                                   int(normalized_end_pos_y * receiver_height))
        return denormalized_start_pos, denormalized_end_pos

    # Example of updating drawing with denormalized coordinates
    def update_drawing(self, normalized_start_pos_x, normalized_start_pos_y, normalized_end_pos_x, normalized_end_pos_y,
                       width, color):
        """
        Update changes in the drawing
        """
        receiver_size = self.gui_game.big_label.size()  # Get the size of the receiver's screen
        denormalized_start_pos, denormalized_end_pos = self.denormalize_coordinates(receiver_size,
                                                                                    normalized_start_pos_x,
                                                                                    normalized_start_pos_y,
                                                                                    normalized_end_pos_x,
                                                                                    normalized_end_pos_y)
        self.gui_game.big_label.create_line(denormalized_start_pos, denormalized_end_pos, width, color)

    def update_players(self, html_content, window):
        """
        Update new player
        """
        # Update the GUI element (e.g., players_names QTextEdit) with the provided HTML content
        window.players_names.append(html_content)
        window.players_names.update()

    def update_chat_text(self, html_content, window, state):
        """
        Update new chat text to the window.
        """
        window.chat_text.append(html_content)
        if state == "disable":
            window.chat_input.setEnabled(False)

    def remove_player(self, name, window):
        """
        Remove player from the waiting room window.
        """
        # Iterate through the lines in self.players_names and remove the matching line
        cursor = self.gui_waiting_room.players_names.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.Start)
        while cursor.atEnd() is False:
            cursor.select(QtGui.QTextCursor.SelectionType.LineUnderCursor)
            line = cursor.selectedText()
            if line == "￼" + name:
                cursor.select(QtGui.QTextCursor.SelectionType.BlockUnderCursor)
                cursor.removeSelectedText()
                break
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.NextBlock)

        # Move the cursor to the end of the document
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)

        # Ensure the QTextEdit is updated
        self.gui_waiting_room.players_names.setTextCursor(cursor)

    def open_timer_gui(self):
        """
        Open the CountDownClock window GUI 
        """
        self.timer_thread = threading.Thread(target=self.check_number_of_players, daemon=True)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        self.clock = g.CountDownClock(initial_time=self.initial_time)
        # Connect the CountDownClock's close event to terminate the
        self.clock.closed.connect(self.terminate_timer_thread)
        self.clock.custom_exec()

    def terminate_timer_thread(self):
        """
        When the CountDownClock ends it closes the check_number_of_players function and close the waiting room window
        """
        self.event_number_players.set()  # Set the event to terminate the thread
        if self.number_of_players >= self.number_of_player_limits_to_start_the_game:
            try:
                client_socket.send(encrypt("Timer finished"))
            except ConnectionResetError as cre:
                self.gui_waiting_room.close()
                self.gui_server_shut_down = g.ServerShutDown()
                self.gui_server_shut_down.show()
            self.gui_waiting_room.close()

    def check_number_of_players(self):
        """
        If the number of player is less than the limits when the timer is working it emits a signal to close the timer
        """
        while not self.event_number_players.is_set():
            if self.number_of_players < self.number_of_player_limits_to_start_the_game:
                self.event_number_players.set()
                self.close_timer_signal.emit()
            time.sleep(1)  # Adjust the sleep duration as needed

    def close_timer(self):
        """
        Explain that someone left and there are less player than the minimum to start a game. Then, close the CountDownClock window.
        """
        self.clock.label_below.hide()
        self.clock.finish.hide()
        self.clock.label_above.setText(
            f"Someone left , there are less than {self.number_of_player_limits_to_start_the_game} players")
        close_timer = QTimer(self)
        close_timer.timeout.connect(self.clock.close)
        close_timer.start(2000)  # Close the window after 2 seconds

    def disconnect_from_server(self):
        """
        Send a message to the server that the client wants to quit while he is in the waiting room and disconnect.
        """
        try:
            client_socket.send(encrypt("quit"))
        except ConnectionResetError as cre:
            quit()
        # client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        # cl_socket.close()
        self.gui_waiting_room.close()
        try:
            if self.clock.isVisible():
                self.clock.close()
        except:
            pass
        quit()

    def send_messages(self, window):
        """
        Send messages to chat
        """
        try:
            client_socket.send(encrypt("message_chat: " + window.get_message()))
            if window == self.gui_game:
                if self.gui_game.timer_label.isVisible():
                    client_socket.send(encrypt((str(self.gui_game.timer_value))))
        except ConnectionResetError as cre:
            # Handle the exception gracefully, inform the user, reconnect, or perform other actions as needed
            window.close()
            self.gui_server_shut_down = g.ServerShutDown()
            self.gui_server_shut_down.show()

    def listen_for_server_messages(self):
        """
        Wait for the server to allow the client to close the first window and open the waiting room window
        """
        self.event_listen_for_server_messages.wait()
        while True:
            try:
                data = None
                with client_socket_lock:
                    data = decrypt(client_socket.recv(buffer_size))
                    client_socket.send(encrypt("2 thanks"))
                if data == "You can now close the app":
                    self.close_first_window_signal.emit()  # Emit signal to close the app
                    self.open_waiting_room_signal.emit()  # Emit signal to open the waiting room window
                    break
                elif data == "not available":
                    client_socket.close()
                    self.close_first_window_signal.emit()  # Emit signal to close the app
                    self.open_not_available_window_signal.emit()
                    break
            except Exception as e:
                print(f"Error in listen_for_server_messages: {e}")

    def not_available_window(self):
        self.not_available_window_gui = g.NotAvailable()
        self.not_available_window_gui.show()

    def disconnect_first_window(self):
        """
        Send a message to the server that the client wants to quit while he is in the first window and disconnect.
        """
        self.listening = False
        stay = self.gui_first_window.get_stay()
        if not stay:
            try:
                client_socket.send(encrypt("quit"))
                # client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
                # cl_socket.close()
                self.close_first_window_signal.emit()
                quit()
            except ConnectionResetError as cre:
                quit()

    def send_name(self):
        """
        Send the name to the server
        """
        self.name = self.gui_first_window.lineEdit.text()
        if self.name:
            try:
                client_socket.send(encrypt(("name: " + self.name)))
                message = decrypt(client_socket.recv(buffer_size))
                client_socket.send(encrypt("1 thanks"))
                if message == "already used":
                    self.gui_first_window.lineEdit.clear()
                    self.gui_first_window.lineEdit.setPlaceholderText("Someone else is using this name")
                elif message == "invalid name":
                    self.gui_first_window.lineEdit.clear()
                    self.gui_first_window.lineEdit.setPlaceholderText("Invalid name")
                else:
                    self.gui_first_window.lineEdit.setEnabled(False)
                    self.gui_first_window.SendButton.setEnabled(False)
            except ConnectionResetError as cre:
                # Handle the exception gracefully, inform the user, reconnect, or perform other actions as needed
                MainWindow.close()
                self.gui_server_shut_down = g.ServerShutDown()
                self.gui_server_shut_down.show()

    def send_monster(self):
        """
        Send the chosen monster to the server
        """
        self.monster = self.gui_first_window.get_monster()
        if self.monster:
            try:
                client_socket.send(encrypt(("monster: " + str(self.monster))))
            except ConnectionResetError as cre:
                # Handle the exception gracefully, inform the user, reconnect, or perform other actions as needed
                MainWindow.close()
                self.gui_server_shut_down = g.ServerShutDown()
                self.gui_server_shut_down.show()


def open_port():
    """
    Find the first free port and return it
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def Info():
    """
    Get server ip and port
    """
    my_data = subprocess.check_output('ipconfig').decode('iso-8859-1')
    my_ip = [line for line in my_data.split('\n') if line.find('IPv4 Address') >= 0][0][39:].replace('\r',
                                                                                                     '')  # machine IP
    port = open_port()
    data = "Client\n" + my_ip + "\n" + str(port)
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(data.encode('utf-8'), ('255.255.255.255', port))
    sock.close()
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", port))
    while True:
        data = sock.recv(1024).decode('utf-8')
        if "Server Hello" in data:
            sock.close()
            break
        else:
            pass

    data = data.split('\n')
    s_ip = data[1].replace('\r', '')
    s_port = data[2]
    return s_ip, int(s_port)


if __name__ == "__main__":
    server_ip, server_port = Info()
    # Create a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    server_address = (server_ip, server_port)
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
    # Generate RSA key pair for client
    client_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    client_public_key = client_private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    # Send client's public key to the server
    client_socket.sendall(client_public_key)
    # Receive encrypted shared symmetric key from server
    encrypted_key = client_socket.recv(4096)
    # Decrypt the shared symmetric key using client's private key
    shared_key = client_private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # Create cipher suite with the received symmetric key
    cipher_suite = Fernet(shared_key)

    is_available = decrypt(client_socket.recv(buffer_size))
    if is_available == "Not available":
        client_socket.send(encrypt("thanks"))
        client_socket.close()
        not_available_window = g.NotAvailable()
        not_available_window.show()
    else:
        client_socket.send(encrypt("thanks"))

        new_player = player()
        new_player.close_first_window_signal.connect(MainWindow.close)  # Connect signal to close the app
        new_player.open_waiting_room_signal.connect(
            new_player.handle_waiting_room_window)  # Connect signal to open the waiting room window
        new_player.update_gui_players_names_signal.connect(new_player.update_players)
        new_player.update_gui_chat_text_signal.connect(new_player.update_chat_text)
        new_player.remove_player_signal.connect(new_player.remove_player)
        new_player.turn_on_timer_signal.connect(new_player.open_timer_gui)
        new_player.close_timer_signal.connect(new_player.close_timer)
        new_player.open_game_signal.connect(new_player.handle_game_window)
        new_player.update_drawing_signal.connect(new_player.update_drawing)
        new_player.clear_painting_signal.connect(new_player.clear_painting)
        new_player.start_game_timer_signal.connect(new_player.start_game_timer)
        new_player.close_game_signal.connect(new_player.close_game)
        new_player.open_not_available_window_signal.connect(new_player.not_available_window)
    sys.exit(app.exec())
