import sys
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget


class CountdownClock(QMainWindow):
    def __init__(self):
        super().__init__()

        self.remaining_time = 30  # 30 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Countdown Clock")
        self.setGeometry(100, 100, 300, 200)

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
        # Create a timer to close the window after 3 seconds
        close_timer = QTimer(self)
        close_timer.timeout.connect(self.close)
        close_timer.start(2000)  # Close the window after 2 seconds


def main():
    app = QApplication(sys.argv)
    clock = CountdownClock()
    clock.show()
    clock.timer.start(1000)  # Start the timer with a 1-second interval
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
