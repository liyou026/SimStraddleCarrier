#pragma once

#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <std_msgs/msg/float64.hpp>

namespace sim_straddle_carrier
{

class ControlNode : public rclcpp::Node
{
public:
  explicit ControlNode(const rclcpp::NodeOptions & options = rclcpp::NodeOptions{});

private:
  void onCmdVel(const geometry_msgs::msg::Twist::SharedPtr msg);
  void onOdom(const nav_msgs::msg::Odometry::SharedPtr msg);

  // Publishes velocity command forwarded to Gazebo diff-drive plugin
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_pub_;
  // Publishes hoist height setpoint
  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr hoist_pub_;

  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_sub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr   odom_sub_;

  double max_linear_vel_;   // m/s
  double max_angular_vel_;  // rad/s
};

}  // namespace sim_straddle_carrier
