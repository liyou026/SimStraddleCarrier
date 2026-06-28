#include "sim_straddle_carrier/control_node.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>

namespace sim_straddle_carrier
{

ControlNode::ControlNode(const rclcpp::NodeOptions & options)
: Node("control_node", options),
  spreader_height_(0.0),
  spreader_target_(-1.0)   // sentinel: no setpoint forwarded yet
{
  max_linear_vel_  = declare_parameter("max_linear_vel",  8.0);
  max_angular_vel_ = declare_parameter("max_angular_vel", 0.5);

  // ── Publishers ────────────────────────────────────────────────────────────
  cmd_pub_           = create_publisher<geometry_msgs::msg::Twist>("/cmd_vel",        10);
  spreader_cmd_pub_  = create_publisher<std_msgs::msg::Float64>("/spreader/cmd",      10);
  spreader_state_pub_ = create_publisher<std_msgs::msg::Float64>("/spreader/state",   10);

  // ── Subscriptions ─────────────────────────────────────────────────────────
  cmd_sub_ = create_subscription<geometry_msgs::msg::Twist>(
    "/straddle_carrier/cmd_vel", 10,
    [this](geometry_msgs::msg::Twist::SharedPtr msg) { onCmdVel(msg); });

  spreader_cmd_sub_ = create_subscription<std_msgs::msg::Float64>(
    "/spreader/cmd", 10,
    [this](std_msgs::msg::Float64::SharedPtr msg) { onSpreaderCmd(msg); });

  joint_states_sub_ = create_subscription<sensor_msgs::msg::JointState>(
    "/joint_states", 10,
    [this](sensor_msgs::msg::JointState::SharedPtr msg) { onJointStates(msg); });

  // ── 20 Hz spreader state timer ────────────────────────────────────────────
  spreader_state_timer_ = create_wall_timer(
    std::chrono::milliseconds(50),
    [this]() { publishSpreaderState(); });

  RCLCPP_INFO(get_logger(),
    "ControlNode started (max_v=%.1f m/s, max_w=%.2f rad/s)",
    max_linear_vel_, max_angular_vel_);
}

void ControlNode::onCmdVel(const geometry_msgs::msg::Twist::SharedPtr msg)
{
  // Clamp to vehicle limits; zero all fields except linear.x and angular.z
  geometry_msgs::msg::Twist out;
  out.linear.x  = std::clamp(msg->linear.x,  -max_linear_vel_,  max_linear_vel_);
  out.linear.y  = 0.0;
  out.linear.z  = 0.0;
  out.angular.x = 0.0;
  out.angular.y = 0.0;
  out.angular.z = std::clamp(msg->angular.z, -max_angular_vel_, max_angular_vel_);
  cmd_pub_->publish(out);
}

void ControlNode::onSpreaderCmd(const std_msgs::msg::Float64::SharedPtr msg)
{
  double clamped = std::clamp(msg->data, 0.0, 9.0);

  // Only forward a new setpoint to Gazebo when the clamped value actually
  // differs from the last one we sent.  This prevents a publish→receive→
  // publish feedback loop since this node subscribes to the same topic it
  // publishes on (/spreader/cmd is also consumed directly by the Gazebo
  // JointPositionController).
  if (std::abs(clamped - spreader_target_) > 1e-9) {
    spreader_target_ = clamped;
    std_msgs::msg::Float64 out;
    out.data = spreader_target_;
    spreader_cmd_pub_->publish(out);
  }
}

void ControlNode::onJointStates(const sensor_msgs::msg::JointState::SharedPtr msg)
{
  for (std::size_t i = 0; i < msg->name.size(); ++i) {
    if (msg->name[i] == "spreader_joint" && i < msg->position.size()) {
      spreader_height_ = msg->position[i];
      break;
    }
  }
}

void ControlNode::publishSpreaderState()
{
  std_msgs::msg::Float64 state;
  state.data = spreader_height_;
  spreader_state_pub_->publish(state);
}

}  // namespace sim_straddle_carrier

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<sim_straddle_carrier::ControlNode>());
  rclcpp::shutdown();
  return 0;
}
