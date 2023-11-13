import argparse

from Thymio import logger
from Thymio.Runner import Runner
from avoid_obstacles import avoid_obstacles


async def actual_prog(client, th):
    await th.node.wait_for_variables({"prox.horizontal"})
    while True:
        prox_front = th.node.v.prox.horizontal[2]
        speed = -prox_front // 10
        await th.motors(speed, speed)
        await client.sleep(0.1)


PROGRAMS = {
    "test": actual_prog,
    "avoid_obstacles": avoid_obstacles
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Thymio Controller")
    parser.add_argument("--loglevel", default='info', help="The log level to use for the run",
                        choices=["critical", "error", "warn", "info", "debug"])
    parser.add_argument("--client_addr", default=None,
                        help="The address of the client to connect to. Defaults to the local device.")
    parser.add_argument("--client_port", default=None, type=int, help="The port of the client to connect to.")
    parser.add_argument("--client_password", default=None, help="The password of the client to connect to.")
    parser.add_argument("--list-programs", action="store_true", help="List the available programs")
    parser.add_argument("--program", default="test", help="The program to run", choices=PROGRAMS.keys())
    args = parser.parse_args()
    logger.setLevel(args.loglevel.upper())
    if args.list_programs:
        print("Available programs:")
        for program in PROGRAMS.keys():
            print(f"  {program}")
        exit(0)

    logger.info("Starting program")
    runner = Runner(args.client_addr, args.client_port, args.client_password)
    runner.run(PROGRAMS[args.program])
    logger.info("End of program")
