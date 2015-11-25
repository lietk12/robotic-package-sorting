"""Script to calibrate a robot."""
import sys
import Tkinter as tk
import ttk

from components.messaging import Signal
from components.robots import VirtualRobot, Mover
from components.sensors import SimpleMonitor, FilteringMonitor
from components.world import VirtualWorld, Wall
from components.app import Simulator

class GUICalibrate(Simulator):
    """Reads out robot sensor values."""
    def __init__(self, name="Calibration GUI", update_interval=10):
        super(GUICalibrate, self).__init__(name, update_interval, 1)
        self._initialize_widgets()
        self._initialize_world(2)

    # Implementing abstract methods
    def _react(self, signal):
        pass
    def _initialize_widgets(self):
        toolbar_frame = ttk.Frame(self._root, name="toolbarFrame")
        toolbar_frame.pack(side="top", fill="x")
        app_frame = ttk.LabelFrame(toolbar_frame, name="appFrame",
                                   borderwidth=2, relief="ridge", text="App")
        app_frame.pack(side="left", fill="y")
        self._initialize_robotapp_widgets(app_frame)

        # Calibration toolbar
        self.__calibrate_frame = ttk.LabelFrame(toolbar_frame, name="calibrateFrame",
                                                borderwidth=2, relief="ridge",
                                                text="Calibrate")
        self.__calibrate_frame.pack(side="left")
        # Movement multipliers
        multipliers_frame = ttk.Frame(self.__calibrate_frame, name="multipliersFrame")
        multipliers_frame.pack(side="left", fill="y")
        self.__move_multiplier = tk.StringVar()
        self.__move_multiplier.set("0.11")
        self.__move_multiplier.trace("w", self._move_multiplier)
        move_multiplier_frame = ttk.LabelFrame(multipliers_frame, name="move",
                                               borderwidth=2, relief="ridge",
                                               text="Move Multiplier")
        move_multiplier_frame.pack(side="top", fill="x")
        ttk.Combobox(move_multiplier_frame, name="multipliers",
                     textvariable=self.__move_multiplier, state="disabled",
                     values=[str(0.005 * i) for i in range(2, 41)]).pack()
        self.__rotate_multiplier = tk.StringVar()
        self.__rotate_multiplier.set("0.056")
        self.__rotate_multiplier.trace("w", self._rotate_multiplier)
        rotate_multiplier_frame = ttk.LabelFrame(multipliers_frame, name="rotate",
                                                 borderwidth=2, relief="ridge",
                                                 text="Rotate Multiplier")
        rotate_multiplier_frame.pack(side="bottom", fill="y")
        ttk.Combobox(rotate_multiplier_frame, name="multipliers",
                     textvariable=self.__rotate_multiplier, state="disabled",
                     values=[str(0.001 * i) for i in range(40, 81)]).pack()
        # Commands
        commands_frame = ttk.LabelFrame(self.__calibrate_frame, name="commandsFrame",
                                        borderwidth=2, relief="ridge", text="Commands")
        commands_frame.pack(side="right", fill="y")
        # Stop button
        stop_frame = ttk.Frame(commands_frame, name="stopFrame")
        stop_frame.pack(side="left", fill="y")
        self.__stop_button = ttk.Button(stop_frame, name="stop", text="Stop",
                                        command=self._stop, state="disabled")
        self.__stop_button.pack(side="top", fill="x")
        # Rotate buttons
        rotate_frame = ttk.Frame(commands_frame, name="rotateFrame")
        rotate_frame.pack(side="left", fill="y")
        self.__rotateccw_button = ttk.Button(rotate_frame, name="rotateccw",
                                             text="Rotate CCW", command=self._rotateccw,
                                             state="disabled")
        self.__rotateccw_button.pack(side="top", fill="x")
        self.__rotatecw_button = ttk.Button(rotate_frame, name="rotatecw",
                                            text="Rotate CW", command=self._rotatecw,
                                            state="disabled")
        self.__rotatecw_button.pack(side="top", fill="x")
        # Move buttons
        move_frame = ttk.Frame(commands_frame, name="moveFrame")
        move_frame.pack(side="left", fill="y")
        self.__moveforwards_button = ttk.Button(move_frame, name="moveforwards",
                                                text="Advance", command=self._moveforwards,
                                                state="disabled")
        self.__moveforwards_button.pack(side="top", fill="x")
        self.__movereverse_button = ttk.Button(move_frame, name="movereverse",
                                               text="Reverse", command=self._movereverse,
                                               state="disabled")
        self.__movereverse_button.pack(side="top", fill="x")

        simulator_frame = ttk.LabelFrame(self._root, name="simulatorFrame",
                                         borderwidth=2, relief="ridge",
                                         text="Simulator")
        simulator_frame.pack(fill="both", expand="yes")
        self._initialize_simulator_widgets(simulator_frame, [-40, -40, 40, 40], 10)
    def _initialize_threads(self):
        self._add_virtual_world_threads()
        mover = Mover("Mover", self._robots[0])
        self.register("Advance", mover)
        self.register("Reverse", mover)
        self.register("Rotate Left", mover)
        self.register("Rotate Right", mover)
        self.register("Stop", mover)
        self._add_thread(mover)
    def _connect_post(self):
        self._add_robots()
        self._change_reset_button("Reset")
        movement_multipliers = self.__calibrate_frame.nametowidget("""multipliersFrame.move"""
                                                                   """.multipliers""")
        movement_multipliers.config(state="normal")
        self._move_multiplier(None, None, "w")
        rotate_multipliers = self.__calibrate_frame.nametowidget("""multipliersFrame.rotate"""
                                                                 """.multipliers""")
        rotate_multipliers.config(state="normal")
        self._rotate_multiplier(None, None, "w")
        self.__stop_button.config(state="normal")
        self.__rotateccw_button.config(state="normal")
        self.__rotatecw_button.config(state="normal")
        self.__moveforwards_button.config(state="normal")
        self.__movereverse_button.config(state="normal")
    def _generate_virtual_robots(self):
        for i in range(0, self._num_robots):
            yield VirtualRobot("Virtual {}".format(i))
    def _populate_world(self):
        self._world.add_wall(Wall(0, 0, 8))

    # Multiplier dropdown callbacks
    def _move_multiplier(self, _, dummy, operation):
        robot = self._robots[0].get_virtual()
        if operation == "w":
            robot.move_multiplier = float(self.__move_multiplier.get())
    def _rotate_multiplier(self, _, dummy, operation):
        robot = self._robots[0].get_virtual()
        if operation == "w":
            robot.rotate_multiplier = float(self.__rotate_multiplier.get())

    # Stop button callback
    def _stop(self):
        self.broadcast(Signal("Stop", self.get_name(), self._robots[0].get_name(), None))

    # Rotate button callbacks
    def _rotateccw(self):
        self.broadcast(Signal("Rotate Left", self.get_name(), self._robots[0].get_name(), 10))
    def _rotatecw(self):
        self.broadcast(Signal("Rotate Right", self.get_name(), self._robots[0].get_name(), 10))

    # Move button callbacks
    def _moveforwards(self):
        self.broadcast(Signal("Advance", self.get_name(), self._robots[0].get_name(), 10))
    def _movereverse(self):
        self.broadcast(Signal("Reverse", self.get_name(), self._robots[0].get_name(), 10))

def main():
    """Runs test."""
    gui = GUICalibrate()
    gui.start()

if __name__ == "__main__":
    sys.exit(main())
