import argparse
import asyncio

from tdmclient import ClientAsync

from Thymio import logger
from Thymio.Thymio import Thymio, Color


async def main(client_addr=None, client_port=None, client_password=None):
    logger.debug(f"Connecting to client {client_addr}:{client_port} with password {client_password}")
    with ClientAsync(tdm_addr=client_addr, tdm_port=client_port, password=client_password) as client:
        with Thymio(client) as th:
            await th.top_leds(color=Color.OFF)
            await th.motors(0, 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Thymio Controller")
    parser.add_argument("--loglevel", default='info', help="The log level to use for the run",
                        choices=["critical", "error", "warn", "info", "debug"])
    parser.add_argument("--client_addr", default=None,
                        help="The address of the client to connect to. Defaults to the local device.")
    parser.add_argument("--client_port", default=None, type=int, help="The port of the client to connect to.")
    parser.add_argument("--client_password", default=None, help="The password of the client to connect to.")
    args = parser.parse_args()
    logger.setLevel(args.loglevel.upper())
    asyncio.run(main(client_addr=args.client_addr, client_port=args.client_port, client_password=args.client_password))
    logger.info("End of program")
