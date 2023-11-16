from Thymio.Logger import logger
from Thymio.Exceptions import ThymioException
from XboxController import XboxController
import time
from tdmclient import aw


async def manual_control(client, th):
    controller = XboxController()
    trip_distance = 3000
    max_distance = 4000
    await th.node.wait_for_variables({"prox.horizontal"})
    while True:
        lx, lt, rt, start = controller.read()
        if start:
            await th.motors(0, 0)
            break

        if -0.1 <= lx <= 0.1:
            lx = 0

        # Rumble by front proximity sensors if over trip_distance
        # TODO: This math is off, but I'm too tired to figure it out right now
        prox_front_left = min(max(0, th.node.v.prox.horizontal[0]-trip_distance), max_distance-trip_distance)
        prox_front_middle_left = min(max(0, th.node.v.prox.horizontal[1]-trip_distance), max_distance-trip_distance)
        prox_front = min(max(0, th.node.v.prox.horizontal[2]-trip_distance), max_distance-trip_distance)
        prox_front_middle_right = min(max(0, th.node.v.prox.horizontal[3]-trip_distance), max_distance-trip_distance)
        prox_front_right = min(max(0, th.node.v.prox.horizontal[4]-trip_distance), max_distance-trip_distance)

        left_rumble = max(prox_front_left, prox_front_middle_left, prox_front)/(max_distance - trip_distance)
        right_rumble = max(prox_front, prox_front_middle_right, prox_front_right)/(max_distance - trip_distance)
        logger.info(f"prox_front_left: {prox_front_left}, prox_front_middle_left: {prox_front_middle_left}, prox_front: {prox_front}, prox_front_middle_right: {prox_front_middle_right}, prox_front_right: {prox_front_right}\n\tleft_rumble: {left_rumble}, right_rumble: {right_rumble}")
        controller.set_vibration(left_rumble, right_rumble)

        # GamePad Controls
        speed = int((rt - lt)*500)
        if speed > 0:  # forward
            if lx > 0:  # turn right
                left_speed = speed
                right_speed = speed - int(lx * 500)
            elif lx < 0:  # turn left
                left_speed = speed - int(abs(lx) * 500)
                right_speed = speed
            else:  # straight
                left_speed = speed
                right_speed = speed
        elif speed == 0:  # Neutral
            mod_speed = int(abs(lx) * 500)
            if lx > 0:  # turn right
                left_speed = mod_speed
                right_speed = mod_speed*-1
            elif lx < 0:  # turn left
                left_speed = mod_speed*-1
                right_speed = mod_speed
            else:  # idle
                left_speed = 0
                right_speed = 0
        else:  # reverse
            if lx > 0:  # turn right
                left_speed = speed
                right_speed = speed + int(lx * 500)
            elif lx < 0:  # turn left
                left_speed = speed + int(abs(lx) * 500)
                right_speed = speed
            else:  # straight
                left_speed = speed
                right_speed = speed

        logger.debug(f"lx: {lx}, lt: {lt}, rt: {rt}, start: {start}\n\tleft_speed: {left_speed}, right_speed: {right_speed}")

        await th.motors(left_speed, right_speed)
