import anki_vector
from anki_vector.util import degrees, distance_mm, speed_mmps, Pose
from anki_vector.objects import CustomObjectMarkers, CustomObjectTypes, LightCube
from OpenGL.GL import *
import time
import math

# Global variable
found_cube = False

'''
SearchNode object contains the x and y coordinates of a location in the map
'''
class SearchNode():
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y

'''
Makes the robot turn one round
'''
def scan(robot: anki_vector.robot.Robot):
    print('scanning')
    time_scan = 10.0
    robot.behavior.turn_in_place(angle=degrees(360.0), speed=degrees(360.0 / time_scan))
    
'''
Calculates and returns SearchNodes that surrounds the robot in a circle
'''
def get_surrounding_nodes(robot: anki_vector.robot.Robot):
    print('get surrounding nodes')
    search_point = 100
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
    
'''
Gets a list of SearchNode that is explorable by the robot
'''
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
            
'''
Checks if a SearchNode contains enough space to fit the robot
'''
def node_fits_robot(node: SearchNode, robot: anki_vector.robot.Robot):
    curr_map = robot.nav_map.latest_nav_map
    robot_size = 75
    
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

'''
Checks if the given SearchNode was explored by Vector before.
'''
def node_explored(node: SearchNode, explored_nodes, robot: anki_vector.robot.Robot):
    radius = 149
    curr_map = robot.nav_map.latest_nav_map
    
    for explored in explored_nodes:
        distance = math.sqrt((explored.x - node.x) ** 2 + (explored.y - node.y) ** 2)
        if distance < radius:
            if curr_map.get_content(node.x, node.y) == 1 or curr_map.get_content(node.x, node.y) == 2:
                return True
    
    return False

'''
Calculates the angle between sourch and destination
'''
def get_angle_from_to(source: SearchNode, dest: SearchNode):
    x = dest.x - source.x
    y = dest.y - source.y
    return math.atan2(y , x)

'''
Requests Vector to drive to the location of the supplied SearchNode
'''
def drive_to(dest: SearchNode, robot: anki_vector.robot.Robot):
    posi = robot.pose.position
    angle = get_angle_from_to(SearchNode(posi.x, posi.y), dest)
    
    print('driving: ', dest.x, ',', dest.y)

    pose = Pose(x=dest.x, y=dest.y, z=0, angle_z=anki_vector.util.Angle(radians=angle))
    robot.behavior.go_to_pose(pose)
    
'''
Remove explorable nodes if it has been explored before
'''
def clear_explorables(explorable, explored, robot):
    before = len(explorable)
    explorable[:] = [candidate for candidate in explorable if not node_explored(candidate, explored, robot)]
    after = len(explorable)

    print(str(before - after), 'nodes cleared.')
    
'''
Prints a list of all explorable nodes
'''
def print_exp(explorable):
    for e in explorable:
        print('(', e.x,',', e.y, ')')

'''
Listener for when an object appears
'''
def handle_object_appeared(event_type, event):
    # This will be called whenever an EvtObjectAppeared is dispatched -
    # whenever an Object comes into view.
    if(isinstance(event.obj, LightCube)):
        print('I found cube!')
        global found_cube 
        found_cube = True

'''
Explore the space!
'''
def explore(robot, explorable, explored):
    connect_cube(robot)
    scan(robot)

    posi = robot.pose.position
    explored.append(SearchNode(posi.x, posi.y))

    get_explorable_nodes(robot, explorable, explored)

    print('==============================================')
    print_exp(explorable)

'''
Connects to the cube. Cube must remain connected for the robot
to visually identify it. (Unfortunately unintuitive)
'''
def connect_cube(robot: anki_vector.robot.Robot):
    robot.world.connect_cube()
    while not robot.world.connected_light_cube:
        print('Cube not found. Retrying...')
        time.sleep(0.5)
        robot.world.connect_cube()

    

def main():
    robot = anki_vector.Robot(
                       enable_nav_map_feed=True,
                       show_3d_viewer=True)
    robot.connect()
    robot.nav_map.init_nav_map_feed(frequency=0.5)

    # initialize target
    connect_cube(robot)
    global found_cube

    # initialize cube listener
    robot.events.subscribe(handle_object_appeared, anki_vector.events.Events.object_appeared)

    # initialize stacks
    explored = []
    explorable = []

    robot.behavior.drive_off_charger()
    explore(robot, explorable, explored)

    while (explorable):
        if (found_cube):
            print('roger cube found')
            robot.anim.play_animation('anim_pounce_success_03')
            robot.anim.play_animation('anim_spinner_tap_01')
            break
        new_loc = explorable.pop()
        drive_to(new_loc, robot)
        explore(robot, explorable, explored)
    

    robot.behavior.drive_on_charger()
    robot.disconnect()
    


if __name__ == "__main__":
    main()
    