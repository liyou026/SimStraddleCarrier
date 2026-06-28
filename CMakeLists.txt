cmake_minimum_required(VERSION 3.8)
project(sim_straddle_carrier)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)

# ── C++ control node ──────────────────────────────────────────────────────────
add_executable(control_node src/control_node.cpp)
target_include_directories(control_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
target_compile_features(control_node PUBLIC cxx_std_17)
ament_target_dependencies(control_node
  rclcpp geometry_msgs nav_msgs sensor_msgs std_msgs tf2 tf2_ros)

install(TARGETS control_node DESTINATION lib/${PROJECT_NAME})

# ── Python scripts ────────────────────────────────────────────────────────────
install(PROGRAMS
  scripts/teleop.py
  DESTINATION lib/${PROJECT_NAME})

# ── Install shared assets ─────────────────────────────────────────────────────
install(DIRECTORY
  description
  worlds
  launch
  config
  DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
