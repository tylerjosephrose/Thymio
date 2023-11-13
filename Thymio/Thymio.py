import re

import PySimpleGUI as sg
from tdmclient import ClientAsync, aw, ClientAsyncCacheNode

from Thymio import logger
from Thymio.Enums import Color, Sound
from Thymio.Exceptions import ThymioException, NoNodesException

"""
Resources:
https://wiki.thymio.org/en:thymioapi
https://www.thymio.org/products/programming-with-thymio-suite/programming-with-python/
https://pypi.org/project/tdmclient/
"""


class Thymio:
    """
    Class to control a Thymio robot.
    """
    node: ClientAsyncCacheNode = None
    __callbacks__ = []

    # Connection Methods
    def __init__(self, client: ClientAsync, delay_for_nodes: float = 0.5, node_name: str = None,
                 prompt_node: bool = False, temp_in_fahrenheit: bool = True):
        """
        Create a Thymio object which will connect to the first node it finds, search for a specific node name, or
        display a prompt to allow the user to choose which node to connect to.
        :param client: ClientAsync object to connect to the node with
        :param delay_for_nodes: delay in seconds to wait for nodes to be found
        :param node_name: string of the specific node name of the node to connect to
        :param prompt_node: boolean of whether to always prompt for a node name regardless of if only a single node was
        found
        :param temp_in_fahrenheit: boolean of whether to display the temperature in Fahrenheit or Celsius
        """
        self.client = client
        self.temp_in_fahrenheit = temp_in_fahrenheit
        aw(self.client.sleep(delay_for_nodes))

        if prompt_node:
            logger.debug("Prompting for node")
            self.node = self.__select_node__()
        elif len(self.client.nodes) == 0:
            raise NoNodesException()
        elif node_name is not None:
            for node in self.client.nodes:
                if node.props["name"] == node_name:
                    logger.info(f"Connecting to node '{node_name}'")
                    self.node = node
                    break
            else:
                raise NoNodesException(node_name=node_name)
        elif len(self.client.nodes) == 1 and not prompt_node:
            logger.info(f"Connecting to node '{self.client.nodes[0].props['name']}'")
            self.node = self.client.nodes[0]
        else:
            self.node = self.__select_node__()

        if self.node is None:
            raise NoNodesException(msg="No Node Selected")
        aw(self.node.lock())

    def __select_node__(self):
        """
        Display a prompt to allow the user to choose which node to connect to.
        :return: ClientAsyncCacheNode object of the node to connect to
        """
        def get_nodes():
            """
            Get a dictionary of the nodes with the node name as the key and the node object as the value.
            :return:
            """
            nodes = {}
            for node in self.client.nodes:
                nodes[node.props["name"]] = node
            return nodes

        nodes = get_nodes()

        layout = [
            [
                sg.Text('Available Nodes:'),
                sg.Listbox(list(nodes.keys()),
                           size=(50, min(len(nodes), 8)),
                           key='Node')
            ],
            [sg.Button('Ok'), sg.Button('Refresh'), sg.Button('Cancel')]
        ]

        window = sg.Window('Choose a Thymio Robot', layout)

        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event == 'Ok':
                window.close()
                if len(values["Node"]) == 0:
                    logger.debug("No node selected")
                    return None

                logger.info(f"Connecting to node '{values['Node'][0]}'")
                return nodes[values["Node"][0]]
            elif event == 'Refresh':
                logger.debug("Refreshing nodes")
                aw(self.client.wait_for_node())
                nodes = get_nodes()
                window['Node'].update(values=list(nodes.keys()))
                window['Node'].Widget.configure(width=50, height=min(len(nodes), 8))
            else:
                window.close()
                sg.popup_auto_close('No Node Selected. Exiting.')
                logger.debug("No node selected")
                return None
        window.close()

    def disconnect(self):
        """
        Unlock the node.
        """
        if self.node:
            logger.info(f"Disconnecting from node '{self.node.props['name']}'")
            aw(self.node.unlock())

    def __enter__(self):
        """
        Enter the Thymio object. Used for with statements.
        :return: Thymio object
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the Thymio object. Used for with statements.
        """
        self.disconnect()

    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        """
        Convert a temperature in Celsius to Fahrenheit.
        :param celsius: float of the temperature in Celsius
        :return: float of the temperature in Fahrenheit
        """
        return celsius * 9 / 5 + 32

    # Action Functions
    async def motors(self, left: int, right: int):
        """
        Set the motor speeds. Range of -500 to 500.
        :param left: Integer of left wheel target speed.
        :param right: Integer of right wheel target speed.
        """
        v = {
            "motor.left.target": [min(500, max(-500, left))],
            "motor.right.target": [min(500, max(-500, right))]
        }
        logger.debug(f"Setting motors to {v}")
        await self.node.set_variables(v)

    async def circle_leds(self, front: int = 0, front_right: int = 0, right: int = 0, back_right: int = 0,
                          back: int = 0, back_left: int = 0, left: int = 0, front_left: int = 0):
        """
        Set the circle LEDs. Range of 0 to 32. Note that these leds by default will display how level the robot is.
        :param front: Integer of the front LED.
        :param front_right: Integer of the front right LED.
        :param right: Integer of the right LED.
        :param back_right: Integer of the back right LED.
        :param back: Integer of the back LED.
        :param back_left: Integer of the back left LED.
        :param left: Integer of the left LED.
        :param front_left: Integer of the front left LED.
        """
        program = f"call leds.circle({front}, {front_right}, {right}, {back_right}, {back}, {back_left}, {left}, {front_left})"
        await self.node.compile(program)
        logger.debug(f"Setting circle LEDs to {program}")
        await self.node.run()

    async def __set_led_color__(self, led: str, hex_code: str = None, color: Color = None, rgb: tuple[int, int, int] = [0, 0, 0]):
        """
        Set the specified LED. Either specify a color, hex_code, or an RGB value.
        """
        if hex_code:
            if re.match(r'^#?[0-9A-Fa-f]{6}$', color):
                rgb = self.hex_to_rgb(color)
            else:
                raise ThymioException(f"Invalid hex code: {hex_code}")
        elif color:
            rgb = self.hex_to_rgb(color.value)
        red = rgb[0]
        green = rgb[1]
        blue = rgb[2]
        program = f"call leds.{led}({red}, {green}, {blue})"
        await self.node.compile(program)
        logger.debug(f"Setting {led} LED to {program}")
        await self.node.run()

    async def top_leds(self, hex_code: str = None, color: Color = None, rgb: tuple[int, int, int] = [0, 0, 0]):
        """
        Set the top LEDs.
        """
        await self.__set_led_color__("top", hex_code, color, rgb)

    async def bottom_left_led(self, hex_code: str = None, color: Color = None, rgb: tuple[int, int, int] = [0, 0, 0]):
        """
        Set the bottom left LED.
        """
        await self.__set_led_color__("bottom.left", hex_code, color, rgb)

    async def bottom_right_led(self, hex_code: str = None, color: Color = None, rgb: tuple[int, int, int] = [0, 0, 0]):
        """
        Set the bottom right LED.
        """
        await self.__set_led_color__("bottom.right", hex_code, color, rgb)

    async def button_leds(self, front: int = 0, right: int = 0, back: int = 0, left: int = 0):
        """
        Set the button LEDs. Range of 0 to 32. Note that these leds by default will display when buttons are pressed.
        :param front: Integer of the front LED.
        :param right: Integer of the right LED.
        :param back: Integer of the back LED.
        :param left: Integer of the left LED.
        """
        program = f"call leds.buttons({front}, {right}, {back}, {left})"
        await self.node.compile(program)
        logger.debug(f"Setting button LEDs to {program}")
        await self.node.run()

    async def receiver_leds(self, power: int = 0):
        """
        Set the receiver LED. Range of 0 to 32. Note that these leds by default will display when the robot recieves an rc code.
        :param power: Integer of the power set the LED to
        """
        program = f"call leds.rc({power})"
        await self.node.compile(program)
        logger.debug(f"Setting rc LED to {program}")
        await self.node.run()

    async def temperature_leds(self, red_power: int = 0, blue_power: int = 0):
        """
        Set the temperature LED. Range of 0 to 32. Note that these leds by default will display based on the temperature
        Red if the temperature is > 28C, Blue if the temperature is < 15C, and both otherwise.
        :param red_power: Integer of the power set the red LED to
        :param blue_power: Integer of the power set the blue LED to
        """
        program = f"call leds.temperature({red_power}, {blue_power})"
        await self.node.compile(program)
        logger.debug(f"Setting temperature LEDs to {program}")
        await self.node.run()

    async def microphone_leds(self, power: int = 0):
        """
        Set the temperature LED. Range of 0 to 32. Note that these leds by default will display based on the temperature
        Red if the temperature is > 28C, Blue if the temperature is < 15C, and both otherwise.
        :param power: Integer of the power set the LED to
        """
        program = f"call leds.microphone({power})"
        await self.node.compile(program)
        logger.debug(f"Setting temperature LEDs to {program}")
        await self.node.run()

    async def play_system_sound(self, sound: Sound):
        """
        Play a system sound.
        :param sound: Sound enum of the sound to play
        """
        program = f"call sound.system({sound})"
        await self.node.compile(program)
        logger.debug(f"Playing sound {sound}")
        await self.node.run()

    async def play_sound_file(self, sound: str):
        """
        Play a sound wav file found on the sd card of the Thymio
        :param sound: string of the sound file to play
        """
        program = f"call sound.play({sound})"
        await self.node.compile(program)
        logger.debug(f"Playing sound {sound}")
        await self.node.run()

    async def start_sound_recording(self, id: int = 0):
        """
        Start recording a sound to the sd card of the Thymio
        :param id: integer of the id to save the sound as (0 - 32767)
        """
        id = min(32767, max(0, id))
        program = f"call sound.record({id})"
        await self.node.compile(program)
        logger.debug(f"Recording sound {id}")
        await self.node.run()

    async def stop_sound_recording(self):
        """
        Stop recording a sound to the sd card of the Thymio
        """
        program = f"call sound.record(-1)"
        await self.node.compile(program)
        logger.debug(f"Stopping recording sound")
        await self.node.run()

    async def replay_recorded_sound(self, id: int = 0):
        """
        Replay a recorded sound from the sd card of the Thymio
        :param id: integer of the id of the sound to replay (0 - 32767)
        """
        id = min(32767, max(0, id))
        program = f"call sound.replay({id})"
        await self.node.compile(program)
        logger.debug(f"Replaying sound {id}")
        await self.node.run()
