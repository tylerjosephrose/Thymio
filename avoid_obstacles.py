from Thymio.Logger import logger
from Thymio.Exceptions import ThymioException


async def avoid_obstacles(client, th):
    await th.node.wait_for_variables({"prox.horizontal"})
    while True:
        close_limit = 4000
        prox_front_left = th.node.v.prox.horizontal[0]
        prox_front_middle_left = th.node.v.prox.horizontal[1]
        prox_front = th.node.v.prox.horizontal[2]
        prox_front_middle_right = th.node.v.prox.horizontal[3]
        prox_front_right = th.node.v.prox.horizontal[4]
        prox_back_left = th.node.v.prox.horizontal[5]
        prox_back_right = th.node.v.prox.horizontal[6]

        logger.debug(f"prox_front_left: {prox_front_left}")
        logger.debug(f"prox_front_middle_left: {prox_front_middle_left}")
        logger.debug(f"prox_front: {prox_front}")
        logger.debug(f"prox_front_middle_right: {prox_front_middle_right}")
        logger.debug(f"prox_front_right: {prox_front_right}")
        logger.debug(f"prox_back_left: {prox_back_left}")
        logger.debug(f"prox_back_right: {prox_back_right}")

        if prox_front_middle_left > close_limit or prox_front > close_limit or prox_front_middle_right > close_limit:
            await th.motors(0, 0)
            raise ThymioException("Too close to an obstacle: FAIL!")

        # TODO: if we get too close, slow down the other wheel as well

        left_speed, right_speed = 250, 250
        if prox_front_middle_left > close_limit - 500:
            left_speed = 0
        elif prox_front_left > 0:
            left_speed = 500

        if prox_front_middle_right > close_limit - 500:
            right_speed = 0
        if prox_front_right > 0:
            right_speed = 500

        await th.motors(left_speed, right_speed)
        await client.sleep(0.1)
