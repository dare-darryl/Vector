import anki_vector
from anki_vector.util import degrees, distance_mm, speed_mmps, Pose
from OpenGL.GL import *
import time
import math

class SearchNode():
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y

def scan(robot: anki_vector.robot.Robot):
    print('scanning')
    time_scan = 10.0
    robot.behavior.turn_in_place(angle=degrees(360.0), speed=degrees(360.0 / time_scan))
    
def get_surrounding_nodes(robot: anki_vector.robot.Robot):
    print('get surrounding nodes')
    search_point = 50
    distance = 150
    angle_incre = 6.283 / search_point
    
    pos = robot.pose.position
    ang = robot.pose.rotation.angle_z.radians
    
    surrounding = []
    
    print('current:', pos)
    for i in range(0, search_point):
        pot_x = pos.x + distance * math.sin(ang)
        pot_y = pos.y + distance * math.cos(ang)
        explore_loc = SearchNode(pot_x, pot_y)
        surrounding.append(explore_loc)
        ang += angle_incre
        
    surrounding.reverse()
        
    return surrounding # So the frontiest node gets to the top of the stack
    
def get_explorable_nodes(robot: anki_vector.robot.Robot, explorable, explored):
    candidate_nodes = get_surrounding_nodes(robot)
    robot.nav_map.init_nav_map_feed(frequency=0.5)
    curr_map = robot.nav_map.latest_nav_map
    
    # clear explored from explorables
    clear_explorables(explorable, explored, robot)
    
    for node in candidate_nodes:
        if curr_map.get_content(node.x, node.y) == 1 or curr_map.get_content(node.x, node.y) == 2:
            if node_fits_robot(node, robot) and not node_explored(node, explored, robot):
                explorable.append(node)
                
    return explorable
            

def node_fits_robot(node: SearchNode, robot: anki_vector.robot.Robot):
    curr_map = robot.nav_map.latest_nav_map
    robot_size = 60
    
    # Check the four directions of the robot
    eval_x = node.x + robot_size
    eval_y = node.y + robot_size
    if curr_map.get_content(eval_x, eval_y) != 1 and curr_map.get_content(eval_x, eval_y) != 2:
        return False
    
    eval_x = node.x - robot_size
    eval_y = node.y + robot_size
    if curr_map.get_content(eval_x, eval_y) != 1 and curr_map.get_content(eval_x, eval_y) != 2:
        return False
    
    eval_x = node.x + robot_size
    eval_y = node.y - robot_size
    if curr_map.get_content(eval_x, eval_y) != 1 and curr_map.get_content(eval_x, eval_y) != 2:
        return False
    
    eval_x = node.x - robot_size
    eval_y = node.y - robot_size
    if curr_map.get_content(eval_x, eval_y) != 1 and curr_map.get_content(eval_x, eval_y) != 2:
        return False
    
    return True

def node_explored(node: SearchNode, explored_nodes, robot: anki_vector.robot.Robot):
    radius = 149
    curr_map = robot.nav_map.latest_nav_map
    
    for explored in explored_nodes:
        distance = math.sqrt((explored.x - node.x) ** 2 + (explored.y - node.y) ** 2)
        if distance < radius:
            if curr_map.get_content(node.x, node.y) == 1 or curr_map.get_content(node.x, node.y) == 2:
                return True
    
    return False

def get_angle_from_to(source: SearchNode, dest: SearchNode):
    x = dest.x - source.x
    y = dest.y - source.y
    return math.atan2(y , x)

def drive_to(dest: SearchNode, robot: anki_vector.robot.Robot):
    posi = robot.pose.position
    angle = get_angle_from_to(SearchNode(posi.x, posi.y), dest)
    
    print('driving: ', dest.x, ',', dest.y)

    pose = Pose(x=dest.x, y=dest.y, z=0, angle_z=anki_vector.util.Angle(radians=angle))
    robot.behavior.go_to_pose(pose)
    
    
def clear_explorables(explorable, explored, robot):
    before = len(explorable)
    explorable[:] = [candidate for candidate in explorable if not node_explored(candidate, explored, robot)]
    after = len(explorable)

    print(str(before - after), 'nodes cleared.')
    

def print_exp(explorable):
    for e in explorable:
        print('(', e.x,',', e.y, ')')


def explore(robot, explorable, explored):
    scan(robot)

    posi = robot.pose.position
    explored.append(SearchNode(posi.x, posi.y))

    get_explorable_nodes(robot, explorable, explored)

    print('==============================================')
    print_exp(explorable)
    

def main():
    robot = anki_vector.Robot(
                       enable_nav_map_feed=True)
    robot.connect()
    robot.nav_map.init_nav_map_feed(frequency=0.5)
    robot.behavior.drive_off_charger()

    # initialize stacks
    explored = []
    explorable = []

    explore(robot, explorable, explored)

    while (explorable):
        new_loc = explorable.pop()
        drive_to(new_loc, robot)
        explore(robot, explorable, explored)
    

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
    