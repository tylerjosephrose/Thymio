from typing import Callable, Awaitable, Any

from tdmclient import ClientAsync

from Thymio import logger
from Thymio.Thymio import Thymio


class Runner:
    def __init__(self, client_addr=None, client_port=None, client_password=None):
        self.client_addr = client_addr
        self.client_port = client_port
        self.client_password = client_password

    def run(self, program: Callable[[ClientAsync, Thymio], Awaitable[Any]]):
        logger.debug(f"Connecting to client {self.client_addr}:{self.client_port} with password {self.client_password}")
        with ClientAsync(tdm_addr=self.client_addr, tdm_port=self.client_port, password=self.client_password) as client:
            with Thymio(client) as th:
                async def prog():
                    await program(client, th)

                client.run_async_program(prog)