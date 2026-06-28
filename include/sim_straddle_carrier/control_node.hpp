#pragma once

#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <std_msgs/msg/float64.hpp>

namespace sim_straddle_carrier
{

class ControlNode : public rclcpp::Node
{
public:
  explicit ControlNode(const rclcpp::NodeOptions & options = rclcpp::NodeOptions{});

private:
  // Callbacks
  void onCmdVel(const geometry_msgs::msg::Twist::SharedPtr msg);
  void onSpreaderCmd(const std_msgs::msg::Float64::SharedPtr msg);
  void onJointStates(const sensor_msgs::msg::JointState::SharedPtr msg);
  void publishSpreaderState();

  // Publishers
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_pub_;           // /cmd_vel → Gazebo diff-drive
  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr    spreader_cmd_pub_;  // /spreader/cmd → Gazebo JPC
  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr    spreader_state_pub_; // /spreader/state → external

  // Subscriptions
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr    cmd_sub_;           // /straddle_carrier/cmd_vel
  rclcpp::Subscription<std_msgs::msg::Float64>::SharedPtr       spreader_cmd_sub_;  // /spreader/cmd
  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_states_sub_;  // /joint_states

  // 20 Hz timer for spreader state publication
  rclcpp::TimerBase::SharedPtr spreader_state_timer_;

  double max_linear_vel_;   // m/s   — from parameter
  double max_angular_vel_;  // rad/s — from parameter
  double spreader_height_;  // m     — current position read from /joint_states
  double spreader_target_;  // m     — last clamped setpoint forwarded to Gazebo
};

}  // namespace sim_straddle_carrier
