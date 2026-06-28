#include "sim_straddle_carrier/control_node.hpp"

#include <algorithm>

namespace sim_straddle_carrier
{

ControlNode::ControlNode(const rclcpp::NodeOptions & options)
: Node("control_node", options)
{
  max_linear_vel_  = declare_parameter("max_linear_vel",  3.0);
  max_angular_vel_ = declare_parameter("max_angular_vel", 0.5);

  cmd_pub_  = create_publisher<geometry_msgs::msg::Twist>("/cmd_vel",      10);
  hoist_pub_ = create_publisher<std_msgs::msg::Float64>("/hoist/setpoint", 10);

  cmd_sub_ = create_subscription<geometry_msgs::msg::Twist>(
    "/straddle_carrier/cmd_vel", 10,
    [this](geometry_msgs::msg::Twist::SharedPtr msg) { onCmdVel(msg); });

  odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
    "/odom", 10,
    [this](nav_msgs::msg::Odometry::SharedPtr msg) { onOdom(msg); });

  RCLCPP_INFO(get_logger(), "ControlNode started (max_v=%.1f m/s, max_w=%.2f rad/s)",
    max_linear_vel_, max_angular_vel_);
}

void ControlNode::onCmdVel(const geometry_msgs::msg::Twist::SharedPtr msg)
{
  // Clamp to vehicle limits before forwarding to the Gazebo diff-drive plugin
  auto out = *msg;
  out.linear.x  = std::clamp(msg->linear.x,  -max_linear_vel_,  max_linear_vel_);
  out.angular.z = std::clamp(msg->angular.z, -max_angular_vel_, max_angular_vel_);
  cmd_pub_->publish(out);
}

void ControlNode::onOdom(const nav_msgs::msg::Odometry::SharedPtr /*msg*/)
{
  // Placeholder: odometry feedback for future autonomy stack integration
}

}  // namespace sim_straddle_carrier

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<sim_straddle_carrier::ControlNode>());
  rclcpp::shutdown();
  return 0;
}
