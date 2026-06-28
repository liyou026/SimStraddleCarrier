#!/usr/bin/python3
"""Keyboard teleoperation for the Straddle Carrier simulation.

Topics published:
  /straddle_carrier/cmd_vel  (geometry_msgs/Twist)  — operator velocity intent
  /spreader/cmd              (std_msgs/Float64)      — spreader height setpoint [0, 9] m
"""

import os
import sys

# Re-exec with system Python 3.12 if invoked via conda/wrong interpreter.
# rclpy is built against /usr/bin/python3 (3.12); conda's python3 (3.13) lacks
# the compiled _rclpy_pybind11 extension.
_ROS_PYTHON = "/usr/bin/python3"
if sys.executable != _ROS_PYTHON and os.path.isfile(_ROS_PYTHON):
    os.execv(_ROS_PYTHON, [_ROS_PYTHON] + sys.argv)

import termios
import tty

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

HELP = """
Straddle Carrier Teleop
-----------------------
  W / S  : forward / backward  (+/- 0.5 m/s, clamp ±8.0 m/s)
  A / D  : turn left / right   (+/- 0.1 rad/s, clamp ±0.5 rad/s)
  Q / E  : spreader up / down  (+/- 0.5 m, clamp 0–9 m)
  Space  : stop (linear + angular; spreader unchanged)
  Ctrl-C : quit
"""

MAX_LINEAR   = 8.0   # m/s
MAX_ANGULAR  = 0.5   # rad/s
MAX_SPREADER = 9.0   # m
MIN_SPREADER = 0.0   # m

LINEAR_STEP   = 0.5  # m/s per keypress
ANGULAR_STEP  = 0.1  # rad/s per keypress
SPREADER_STEP = 0.5  # m per keypress


def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


class TeleopNode(Node):
    def __init__(self):
        super().__init__("teleop_node")
        self.cmd_pub      = self.create_publisher(Twist,   "/straddle_carrier/cmd_vel", 10)
        self.spreader_pub = self.create_publisher(Float64, "/spreader/cmd",             10)
        self.linear   = 0.0   # m/s
        self.angular  = 0.0   # rad/s
        self.spreader = 0.0   # m

    def publish(self):
        twist = Twist()
        twist.linear.x  = self.linear
        twist.angular.z = self.angular
        self.cmd_pub.publish(twist)

        spreader_msg = Float64()
        spreader_msg.data = self.spreader
        self.spreader_pub.publish(spreader_msg)

        print(
            f"\rSpeed: {self.linear:+.2f} m/s  "
            f"Angular: {self.angular:+.3f} rad/s  "
            f"Spreader: {self.spreader:.2f} m    ",
            end="",
            flush=True,
        )


def main():
    rclpy.init()
    node = TeleopNode()
    settings = termios.tcgetattr(sys.stdin)
    print(HELP)
    try:
        while rclpy.ok():
            key = get_key(settings)
            if key == "\x03":   # Ctrl-C
                break
            elif key == " ":
                node.linear  = 0.0
                node.angular = 0.0
            elif key in ("w", "W"):
                node.linear = max(-MAX_LINEAR,  min(MAX_LINEAR,  node.linear  + LINEAR_STEP))
            elif key in ("s", "S"):
                node.linear = max(-MAX_LINEAR,  min(MAX_LINEAR,  node.linear  - LINEAR_STEP))
            elif key in ("a", "A"):
                node.angular = max(-MAX_ANGULAR, min(MAX_ANGULAR, node.angular + ANGULAR_STEP))
            elif key in ("d", "D"):
                node.angular = max(-MAX_ANGULAR, min(MAX_ANGULAR, node.angular - ANGULAR_STEP))
            elif key in ("q", "Q"):
                node.spreader = min(node.spreader + SPREADER_STEP, MAX_SPREADER)
            elif key in ("e", "E"):
                node.spreader = max(node.spreader - SPREADER_STEP, MIN_SPREADER)
            node.publish()
    finally:
        print()  # newline after the status line
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
