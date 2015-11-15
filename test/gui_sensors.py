"""Script to test basic message-passing with GUIReactor.
Continuously reads out sensor values monitored by Monitor."""
import sys
import Tkinter as tk

from components.messaging import Signal
from components.robots import RobotApp
from components.sensors import Monitor
from components.actions import Beeper

class GUISensors(RobotApp):
    """Reads out robot sensor values."""
    def __init__(self):
        super(GUISensors, self).__init__()
        self.__sensors_frame = None
        self.__effectors_frame = None
        self._initialize_widgets()

    # Implementing abstract methods
    def _react(self, signal):
        if signal.Name == "Floor":
            self.__sensors_frame.nametowidget("floor").config(text="Floor: ({}, {})"
                                                              .format(*signal.Data))
        elif signal.Name == "Proximity":
            self.__sensors_frame.nametowidget("proximity").config(text="Prox: ({}, {})"
                                                                  .format(*signal.Data))
        elif signal.Name == "PSD":
            self.__sensors_frame.nametowidget("psd").config(text="PSD: {}"
                                                            .format(signal.Data))
    def _initialize_widgets(self):
        app_frame = tk.LabelFrame(self._root, name="appFrame",
                                  borderwidth=2, relief=tk.RIDGE,
                                  text="App")
        app_frame.pack(fill=tk.X)
        self._initialize_robotapp_widgets(app_frame)

        self.__sensors_frame = tk.LabelFrame(self._root, name="sensorsFrame",
                                             borderwidth=2, relief=tk.RIDGE,
                                             text="Sensors")
        self.__sensors_frame.pack(fill=tk.X)
        tk.Label(self.__sensors_frame, name="floor",
                 text="Floor: (?, ?)").pack(fill=tk.X)
        tk.Label(self.__sensors_frame, name="proximity",
                 text="Prox: (?, ?)").pack(fill=tk.X)
        tk.Label(self.__sensors_frame, name="psd",
                 text="PSD: ?").pack(fill=tk.X)
        tk.Button(self.__sensors_frame, name="monitor", text="Monitor",
                  command=self._toggle_monitor, state=tk.DISABLED).pack(fill=tk.X)

        self.__effectors_frame = tk.LabelFrame(self._root, name="effectorsFrame",
                                               borderwidth=2, relief=tk.RIDGE,
                                               text="Effectors")
        self.__effectors_frame.pack(fill=tk.X)
        tk.Button(self.__effectors_frame, name="beep", text="Beep",
                  command=self._beep, state=tk.DISABLED).pack(fill=tk.X)
        self.__servo_angle = tk.IntVar()
        self.__servo_angle.set(90)
        self.__servo_angle.trace("w", self._servo)
        tk.OptionMenu(self.__effectors_frame, self.__servo_angle,
                      *range(6, 181, 6)).pack(fill=tk.X)
    def _initialize_threads(self):
        sensor_monitor = Monitor("Sensors Monitor", self._robots[0])
        self.register("Servo", sensor_monitor)
        self._threads["Sensors Monitor"] = sensor_monitor

        beeper = Beeper("Beeper", self._robots[0])
        self.register("Beep", beeper)
        self._threads["Beeper"] = beeper
    def _connect_post(self):
        self.__sensors_frame.nametowidget("monitor").config(state=tk.NORMAL)
        self.__effectors_frame.nametowidget("beep").config(state=tk.NORMAL)

    # Monitor button callback
    def _toggle_monitor(self):
        sensor_monitor = self._threads["Sensors Monitor"]
        sensor_monitor.toggle_registered("Floor", self)
        sensor_monitor.toggle_registered("Proximity", self)
        sensor_monitor.toggle_registered("PSD", self)
        monitor_button = self.__sensors_frame.nametowidget("monitor")
        if sensor_monitor.is_registered("Floor", self):
            monitor_button.config(text="Stop Monitoring")
        else:
            monitor_button.config(text="Monitor")

    # Beep button callback
    def _beep(self):
        self.broadcast(Signal("Beep", (40, 0.2)))
        self.broadcast(Signal("Beep", (0, 0.1)))

    # Servo scale callback
    def _servo(self, _, dummy, operation):
        if operation == "w":
            self.broadcast(Signal("Servo", self.__servo_angle.get()))

def main():
    """Runs test."""
    gui = GUISensors()
    gui.start()

if __name__ == "__main__":
    sys.exit(main())
