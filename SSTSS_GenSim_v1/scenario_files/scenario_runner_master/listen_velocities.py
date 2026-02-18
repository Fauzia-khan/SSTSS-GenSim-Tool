#!/usr/bin/env python
import rospy
from std_msgs.msg import Float32
from geometry_msgs.msg import TwistStamped
import csv
import time

# Storage lists
all_linear_x = []
all_linear_y = []
all_carla_speed = []
all_dashboard_speed =[]
all_closest_object_distance = []
all_closest_object_speed = []
all_timestamps = []


# Target number of messages before saving and exiting
DATA_LIMIT = 1000

def callback_localisation(msg):

    all_linear_x.append(msg.twist.linear.x)
    all_linear_y.append(msg.twist.linear.y)
    all_timestamps.append(msg.header.stamp.to_sec())  # Convert to float seconds

    check_and_exit()

def callback_carla(msg):
    all_carla_speed.append(msg.data)
    check_and_exit()

def callback_closest_object_distance(msg):
    all_closest_object_distance.append(msg.data)
    check_and_exit()

def callback_closest_object_speed(msg):
    all_closest_object_speed.append(msg.data)
    check_and_exit()


def callback_dashboard(msg):

    all_dashboard_speed.append(msg.data)
    check_and_exit()


def check_and_exit():
    if len(all_linear_x) >= DATA_LIMIT and len(all_carla_speed) >= DATA_LIMIT:
        write_data()
        print("Data written. Exiting.")
        rospy.signal_shutdown("Data collection complete.")


def write_data():

    rows = zip(all_timestamps, all_linear_x, all_linear_y, all_carla_speed, all_dashboard_speed, all_closest_object_distance, all_closest_object_speed)

    with open('full_speed_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['time', 'linear_x', 'linear_y', 'carla_speed', 'dashboard', 'closest_object_distance', 'closest_object_speed'])
        writer.writerows(rows)

    print('data written')


def listener():
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("/localization/current_velocity", TwistStamped, callback_localisation)
    rospy.Subscriber("/carla/ego_vehicle/speedometer", Float32, callback_carla)
    rospy.Subscriber("/dashboard/current_speed", Float32, callback_dashboard)
    rospy.Subscriber("/dashboard/closest_object_speed", Float32, callback_closest_object_speed)
    rospy.Subscriber("/dashboard/closest_object_distance", Float32, callback_closest_object_distance)
    
    rospy.spin()

if __name__ == '__main__':
    listener()
