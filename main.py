import subprocess
from datetime import datetime
import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QProgressBar, QLabel, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt


class PingThread(QThread):
    ping_finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.servers = ["upload.superintendent.me", "www.facebook.com", "www.amazon.com"]
        self.lowest_ping_time = None
        self.fastest_server = None

    def run(self):
        with open(f"pingtimes/ping_times_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt", "w") as file:
            for server in self.servers:
                try:
                    ping_output = subprocess.run(['ping', '-n', '3', server], capture_output=True, text=True, timeout=5)
                    print(f"Ping output for {server}:")
                    print(ping_output.stdout)

                    # Extract the ping time from the ping output
                    ping_time_str = ping_output.stdout.split('time=')[1].split(' ')[0]
                    ping_time = float(ping_time_str.replace('ms', ''))
                    print(f"{ping_time}")

                    file.write(f"Ping time for {server}: {ping_time} ms\n")

                    if self.lowest_ping_time is None or ping_time < self.lowest_ping_time:
                        self.lowest_ping_time = ping_time
                        self.fastest_server = server
                except subprocess.TimeoutExpired:
                    print(f"Timeout expired while pinging {server}")
                except Exception as e:
                    print(f"Error while pinging {server}: {str(e)}")

            if self.fastest_server is not None:
                print(f"We found a Server With the lowest ping of {self.lowest_ping_time} ms")
                file.write(f"The fastest server is {self.fastest_server} with a ping time of {self.lowest_ping_time} ms\n")
                self.ping_finished.emit(f"The fastest server is {self.fastest_server} with a ping time of {self.lowest_ping_time} ms")

            else:
                print("No servers responded to ping")


class PingChecker(QWidget):
    def __init__(self):
        super().__init__()

        self.ping_thread = PingThread()
        self.ping_thread.ping_finished.connect(self.ping_finished)

        font = QFont("Arial", 14)

        self.label = QLabel("Updating DNS, please wait...")
        self.label.setFont(font)


        self.progress_bar = QProgressBar()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def start_ping_test(self):
        self.ping_thread.start()

    def ping_finished(self, result):
        self.label.setText(result)
        self.progress_bar.setValue(100)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ping_checker = PingChecker()
    ping_checker.setGeometry(100, 100, 400, 200)  # set the geometry of the widget
    ping_checker.show()

    ping_checker.start_ping_test()

    QTimer.singleShot(60000, app.quit)

    sys.exit(app.exec_())