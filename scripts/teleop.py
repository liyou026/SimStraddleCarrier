#!/usr/bin/env python3
"""Keyboard teleoperation for the Straddle Carrier simulation."""

import sys
import termios
import tty

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

HELP = """
Straddle Carrier Teleop
-----------------------
  W / S  : forward / backward
  A / D  : turn left / right
  Q / E  : hoist up / down
  Space  : stop
  Ctrl-C : quit
"""

KEY_BINDINGS = {
    "w": (1, 0),
    "s": (-1, 0),
    "a": (0, 1),
    "d": (0, -1),
}

LINEAR_STEP  = 0.5   # m/s per keypress
ANGULAR_STEP = 0.1   # rad/s per keypress
HOIST_STEP   = 0.1   # m per keypress


def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


class TeleopNode(Node):
    def __init__(self):
        super().__init__("teleop_node")
        self.cmd_pub   = self.create_publisher(Twist,    "/straddle_carrier/cmd_vel", 10)
        self.hoist_pub = self.create_publisher(Float64,  "/hoist/setpoint",          10)
        self.linear    = 0.0
        self.angular   = 0.0
        self.hoist     = 0.0

    def publish(self):
        twist = Twist()
        twist.linear.x  = self.linear
        twist.angular.z = self.angular
        self.cmd_pub.publish(twist)

        hoist_msg = Float64()
        hoist_msg.data = self.hoist
        self.hoist_pub.publish(hoist_msg)


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
                node.linear = 0.0
                node.angular = 0.0
            elif key in KEY_BINDINGS:
                lx, az = KEY_BINDINGS[key]
                node.linear  = max(-3.0, min(3.0,  node.linear  + lx * LINEAR_STEP))
                node.angular = max(-0.5, min(0.5, node.angular + az * ANGULAR_STEP))
            elif key == "q":
                node.hoist = min(node.hoist + HOIST_STEP, 4.9)
            elif key == "e":
                node.hoist = max(node.hoist - HOIST_STEP, 0.0)
            node.publish()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
