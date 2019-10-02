#!/usr/bin/env python

import sys
import rospy
from art_utils import ArtApiHelper
from art_msgs.msg import CollisionPrimitive
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import PoseStamped, PolygonStamped, Point32
import os
from art_msgs.msg import Program, ProgramBlock, ProgramItem
from art_utils.art_msgs_functions import obj_type

setup = None


def main(args):

    global setup

    rospy.init_node('setup_init_script', anonymous=True)

    try:
        setup = os.environ["ARTABLE_SETUP"]
    except KeyError:
        rospy.logerr("ARTABLE_SETUP has to be set!")
        return

    api = ArtApiHelper()
    api.wait_for_db_api()

    rospy.loginfo("Refreshing collision environment...")
    api.clear_collision_primitives(setup)

    api.store_object_type(obj_type("desticka", 0.08, 0.08, 0.0125))
    api.store_object_type(obj_type("Modry_kontejner", 0.11, 0.165, 0.075, container=True))

    # delete all created programs
    ph = api.get_program_headers()
    if ph:
        for h in ph:
            api.program_clear_ro(h.id)
            api.delete_program(h.id)

    # TODO add parameters
    prog = Program()
    prog.header.id = 1
    prog.header.name = "MSV DEMO"

    pb = ProgramBlock()
    pb.id = 1
    pb.name = "Pick and place"
    pb.on_success = 1
    pb.on_failure = 0
    prog.blocks.append(pb)

    pi = ProgramItem()
    pi.id = 1
    pi.on_success = 2
    pi.on_failure = 0
    pi.type = "PickFromPolygon"
    pi.object.append("")
    pi.polygon.append(PolygonStamped())
    pb.items.append(pi)

    pi = ProgramItem()
    pi.id = 2
    pi.on_success = 1
    pi.on_failure = 0
    pi.type = "PlaceToContainer"
    pi.object.append("")
    pi.polygon.append(PolygonStamped())
    pi.ref_id.append(1)
    pb.items.append(pi)

    api.store_program(prog)

    rospy.loginfo("Done!")


if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("Shutting down")