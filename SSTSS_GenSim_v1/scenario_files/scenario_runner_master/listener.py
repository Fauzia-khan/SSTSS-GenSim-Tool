#!/usr/bin/env python
import rospy
from std_msgs.msg import Float32
from rosgraph_msgs.msg import Clock
from autoware_msgs.msg import DetectedObjectArray
from autoware_msgs.msg import VehicleCmd
import atexit
import time

dictionaryOfLists = {"clock": [], "speed1": [], "accel": [], "closObjDist": [], "closObjSpeed": [],
                     "speed3": [], "targetSpeed": []}


def exit_handler():
    currenttime = time.localtime(time.time())
    for key in dictionaryOfLists:
        file = open("results/logROS_" + time.strftime("%b_%d_%Y_%H:%M:%S", currenttime) + key + "_" + '.txt', 'a')
        file.write(key + '\n')
        file.write('\n'.join(dictionaryOfLists[key]))
        file.close()


atexit.register(exit_handler)


def callback(data, args):
    if args == "clock":
        dictionaryOfLists["clock"].append(str(time.time()) + "," + str(data.clock.secs) + "." + str(data.clock.nsecs))
    else:
        pass
        dictionaryOfLists[args].append(str(time.time()) + "," + str(data.data))


def listener():
    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("/carla/ego_vehicle/speedometer", Float32, callback, ("speed1"))
    rospy.Subscriber("/dashboard/acceleration", Float32, callback, ("accel"))
    rospy.Subscriber("/dashboard/closest_object_distance", Float32, callback, ("closObjDist"))
    rospy.Subscriber("/dashboard/closest_object_speed", Float32, callback, ("closObjSpeed"))
    rospy.Subscriber("/dashboard/current_speed", Float32, callback, ("speed3"))
    rospy.Subscriber("/dashboard/target_speed", Float32, callback, ("targetSpeed"))
    rospy.Subscriber("/clock", Clock, callback, ("clock"))

    rospy.spin()


if __name__ == '__main__':
    listener()
