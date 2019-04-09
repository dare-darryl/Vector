import anki_vector
import time


def main():
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(enable_nav_map_feed=True) as robot:
        robot.behavior.drive_off_charger()
        
        print("Looking for proximity")
        time.sleep(3)
        proximity_data = robot.proximity.last_sensor_reading
        if proximity_data is not None:
            print('Proximity distance: {0}, engine considers useful: {1}'.format(proximity_data.distance, proximity_data.is_valid))


if __name__ == "__main__":
    main()
