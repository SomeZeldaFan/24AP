import sys
import json
import asyncio
import websockets
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QVBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, Signal, QThread, Slot

from PySide6.QtGui import QFont

# bg worker thread
class Worker(QThread):
    """
    Runs the websocket connection in the background to prevent the UI from freezing.
    Communicates with the main UI thread via signals.
    """
    # defining signals
    callsign_found = Signal()
    callsign_not_found = Signal(str) 
    heading_updated = Signal(int)

    def __init__(self, callsign):
        super().__init__()
        self.callsign = callsign
        self._is_running = True

    async def listen_for_data(self):
        """The main async function to connect and process data."""
        uri = "wss://24data.ptfs.app/wss"
        try:
            async with websockets.connect(uri) as websocket:
                print(f"Successfully connected to WebSocket. Searching for {self.callsign}...")
                
                # timeout logic
                timeout_counter = 0
                found = False

                while self._is_running:
                    message_json = await websocket.recv()
                    data = json.loads(message_json)

                    if data.get("t") == "ACFT_DATA":
                        aircraft_data = data.get("d", {})
                        
                        # check callsign
                        if self.callsign in aircraft_data:
                            # emit signal
                            if not found:
                                print(f"Callsign {self.callsign} found!")
                                self.callsign_found.emit()
                                found = True
                            
                            # get heading data
                            heading = aircraft_data[self.callsign].get("heading")
                            if heading is not None:
                                self.heading_updated.emit(heading)
                        
                        elif not found:
                            timeout_counter += 1
                            if timeout_counter > 20: 
                                self.callsign_not_found.emit(f"Callsign '{self.callsign}' not found. Check spelling or if spawned.")
                                self.stop()


        except Exception as e:
            print(f"An error occurred: {e}")
            self.callsign_not_found.emit(f"Error: {e}")

    def run(self):
        """This method is executed when the thread starts."""
        try:
            asyncio.run(self.listen_for_data())
        except Exception as e:
            print(f"Error starting thread's event loop: {e}")


    def stop(self):
        """Stops the listening loop."""
        print("Stopping worker thread...")
        self._is_running = False


# app ui
class HeadingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("True Heading Indicator - ATC24")
        self.setFixedSize(500, 250)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.callsign = ""
        self.worker = None # To hold a reference to the worker thread

        self.main_widget = self.create_main_widget()
        self.heading_widget = self.create_heading_widget()
        self.error_label = QLabel("") # For showing errors
        self.error_label.setStyleSheet("color: red; font-size: 10pt;")
        self.error_label.hide()

        self.main_layout.addWidget(self.main_widget)
        self.main_layout.addWidget(self.heading_widget)
        self.main_layout.addWidget(self.error_label)
        self.heading_widget.hide()

    def create_main_widget(self):
        container_widget = QWidget()
        layout = QVBoxLayout(container_widget)
        layout.setSpacing(15)

        label = QLabel("Enter your Callsign:")
        label.setFont(QFont("Arial", 12))
        label.setAlignment(Qt.AlignCenter)

        self.callsign_input = QLineEdit()
        # fix: changed placeholder
        self.callsign_input.setPlaceholderText("CALLSIGNNNNNNNNNNNNNNNNNNNNNN")
        self.callsign_input.setFont(QFont("Arial", 11))
        self.callsign_input.setMinimumHeight(35)

        self.submit_button = QPushButton("Find Callsign")
        self.submit_button.setFont(QFont("Arial", 11, QFont.Bold))
        self.submit_button.setMinimumHeight(40)
        self.submit_button.clicked.connect(self.handle_submission)

        self.stay_on_top_checkbox = QCheckBox("Stay on Top")
        self.stay_on_top_checkbox.setFont(QFont("Arial", 10))
        self.stay_on_top_checkbox.stateChanged.connect(self.toggle_stay_on_top)

        layout.addWidget(label)
        layout.addWidget(self.callsign_input)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.stay_on_top_checkbox)
        layout.addStretch()

        return container_widget
    
    def create_heading_widget(self):
        container_widget = QWidget()
        layout = QVBoxLayout(container_widget)
        layout.setSpacing(10)

        self.heading_label = QLabel("CALLSIGN - HEADING:")
        self.heading_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.heading_label.setAlignment(Qt.AlignCenter)

        self.heading_value = QLabel("---°")
        font = QFont("Courier New", 48, QFont.Bold)
        self.heading_value.setFont(font)
        self.heading_value.setAlignment(Qt.AlignCenter)
        self.heading_value.setStyleSheet("color: #007bff;")

        self.reset_button = QPushButton("Reset")
        self.reset_button.setFont(QFont("Arial", 10))
        self.reset_button.setMinimumHeight(35)
        self.reset_button.clicked.connect(self.reset)

        layout.addStretch()
        layout.addWidget(self.heading_label)
        layout.addWidget(self.heading_value)
        layout.addStretch()
        layout.addWidget(self.reset_button)

        return container_widget

    def handle_submission(self):
        # fix: remove upper()
        self.callsign = self.callsign_input.text().strip()
        if not self.callsign:
            self.show_error("Callsign cannot be empty.")
            return
        
        self.error_label.hide()
        self.submit_button.setText("Searching...")
        self.submit_button.setEnabled(False)

        # worker thread
        self.worker = Worker(callsign=self.callsign)
        self.worker.callsign_found.connect(self.on_callsign_found)
        self.worker.callsign_not_found.connect(self.on_callsign_not_found)
        self.worker.heading_updated.connect(self.on_heading_updated)
        self.worker.start()

    @Slot()
    def on_callsign_found(self):
        """This is executed when the worker emits the 'callsign_found' signal."""
        self.heading_label.setText(f"{self.callsign} - HEADING:")
        self.main_widget.hide()
        self.heading_widget.show()

    @Slot(str)
    def on_callsign_not_found(self, message):
        """Executed when the worker emits 'callsign_not_found'."""
        self.show_error(message)
        self.reset_submit_button()

    @Slot(int)
    def on_heading_updated(self, heading):
        """Executed when the worker emits 'heading_updated'."""
        self.heading_value.setText(f"{heading}°")

    def reset(self):
        if self.worker:
            self.worker.stop()
        self.heading_widget.hide()
        self.main_widget.show()
        self.callsign_input.clear()
        self.reset_submit_button()
        self.error_label.hide()

    def reset_submit_button(self):
        self.submit_button.setText("Find Callsign")
        self.submit_button.setEnabled(True)

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

    def toggle_stay_on_top(self, state):
        if state == Qt.Checked.value:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.show()

    def closeEvent(self, event):
        """Ensures the worker thread is stopped when the window is closed."""
        if self.worker:
            self.worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeadingApp()
    window.show()
    sys.exit(app.exec())
