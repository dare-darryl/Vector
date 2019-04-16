import anki_vector
from anki_vector.util import degrees, distance_mm, speed_mmps, Pose
from OpenGL.GL import *
import time


def main():
    robot = anki_vector.Robot(
                       enable_nav_map_feed=True)

    robot.connect()
    robot.behavior.drive_off_charger()
    print(robot.pose.position)
    print(Content.NO_CLIFF)
    robot.behavior.drive_on_charger()
    
    robot.disconnect()
    


class Content:
    NO_CLIFF = 2
    NO_OBSTABLE = 1
    CLIFF = 7
    INTERESTING_EDGE = 8
    OBSTACLE_CUBE = 3
    OBSTACLE_PROXIMITY = 4
    OBSTACLE_PROXIMITY_EXPLORED = 5
    OBSTACLE_UNRECOGNIZED = 6
    UNKNOWN = 0


if __name__ == "__main__":
    main()
    