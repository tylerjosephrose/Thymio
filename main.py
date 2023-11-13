from Thymio import Thymio, Color
from tdmclient import ClientAsync
from Thymio.logger import logger, setup_logger
import asyncio


async def main():
    with ClientAsync() as client:
        with Thymio(client) as th:
            await th.top_leds(color=Color.OFF)
            await th.motors(0, 0)


if __name__ == '__main__':
    setup_logger()
    asyncio.run(main())
    logger.info("End of program")
