import anki_vector
import time


def main():
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(enable_nav_map_feed=True) as robot:
        print("Look for Nav_Map")
        # robot.init_nav_map_feed(frequency=0.5)
        robot.nav_map.init_nav_map_feed(frequency=0.5)
        robot.behavior.drive_off_charger()

        time.sleep(3)
        robot.behavior.drive_on_charger()
        latest_nav_map = robot.nav_map.latest_nav_map

        print(latest_nav_map.center.x_y_z)

        robot.nav_map.close_nav_map_feed()
        # print(latest_nav_map.center.size())


if __name__ == "__main__":
    main()
