import anki_vector
from anki_vector.events import Events
import time

def find_cube(name,data):
    print(data)
    print("Cube found")
    
with anki_vector.Robot() as robot:
    robot.world.disconnect_cube()
    robot.events.subscribe(find_cube,Events.object_observed)
    if robot.world.connected_light_cube:
        cube = robot.world.connected_light_cube
        robot.conn.run_coroutine(robot.events.dispatch_event(cube.is_visible,Events.object_observed))
    robot.conn.run_coroutine(robot.events.dispatch_event(False,Events.object_observed))

    for obj in robot.world.all_objects:
        print(obj)
    connect_cube = robot.world.connect_cube()

    if robot.world.connected_light_cube:
            cube = robot.world.connected_light_cube
            cube.VISIBILITY_TIMEOUT = 100.0

    for _ in range(100):
        print('Running')

        #for obj in robot.world.all_objects:
            #print(obj)
        
            #print(f"{cube.is_connected}")
            #print(cube.is_visible)
            #print(cube)
        #for obj in robot.world.all_objects:
            #print(obj)

        time.sleep(1.0)
        

    

