#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped

def publish_goal():
    rospy.init_node('auto_goal_setter', anonymous=True)
    goal_pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=1)
    rospy.sleep(2)  # Wait for RViz/subscribers to connect

    goal = PoseStamped()
    goal.header.frame_id = "map"
    goal.header.stamp = rospy.Time.now()

    # Set your desired destination coordinates here
    goal.pose.position.x = 397   #120.0
    goal.pose.position.y = 316 #35.0
    goal.pose.position.z = 0.0
    goal.pose.orientation.w = 1.0  # Facing forward

    rospy.loginfo("Publishing goal to /move_base_simple/goal")
    goal_pub.publish(goal)

if __name__ == '__main__':
    try:
        publish_goal()
    except rospy.ROSInterruptException:
        pass
