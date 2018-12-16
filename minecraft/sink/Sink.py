"""
This module is the focal point of the DC bot
"""
from typing import List, Dict, Union, Tuple

from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound
from minecraft.networking.packets.clientbound import (
    play as cplay,
    status as cstatus,
    login as clogin,
    handshake as chandshake
)
import json
from enum import Enum
import re

DC_IP = "172.106.14.42"


class Sink:
    """
    Base class for Sinks.
    """
    connection = None

    def __init__(self, connection: Connection):
        """
        Sets up a bot
        :param connection: The connection to be used
        """
        self.connection = connection

    def register(self):
        raise NotImplementedError("Must be overwritten by subclass.")

    def receive_packet(self, packet: Packet):
        raise NotImplementedError("Must be overwritten by subclass.")


class ChatSink(Sink):
    """
    Sink receiving only chat messages
    """

    def __init__(self, connection: Connection):
        super().__init__(connection)
        self.register()

    def register(self):
        self.connection.register_packet_listener(self.receive_packet, cplay.ChatMessagePacket)

    def receive_packet(self, packet: cplay.ChatMessagePacket):
        """
        Reads an incoming chat packet.
        :param packet: The chat packet to read
        """
        pos = packet.field_string('position')
        jsn = json.loads(packet.json_data)
        fmt_string, links = self._dict_to_string(jsn)
        string = re.compile(r"\033\[\d{2}?m").sub("", fmt_string)

        self.receive_chat_packet(pos, jsn, fmt_string, string, links)

    def receive_chat_packet(self, position: str, json_data: dict, formatted_string: str, plain_string: str,
                            links: List[Dict[str, str]]):
        """
        Consumes chat message. Must be overwritten
        :param position: The position of the chat message
        :param json_data: The json dict with all the raw data
        :param formatted_string: The formatted string
        :param plain_string: The unformatted string
        :param links: List of links found in the string. Dict with action and value as fields.
        """
        raise NotImplementedError("Must be overwritten by subclass.")

    def _dict_to_string(self, jsn: dict) -> Tuple[str, List[Dict[str, str]]]:
        """
        Converts a JSON object from chat messages to a string.
        :param jsn: The json data from the chat message
        """
        # print(jsn)
        string = ''
        links = []
        if 'text' in jsn:
            string = jsn['text']
        if 'extra' in jsn:
            for el in jsn['extra']:
                if type(el) is dict:
                    prefix = ''
                    suffix = ''
                    if 'italic' in el:
                        prefix += TERM_CODES.ITALIC.value
                        suffix = TERM_CODES.RESET.value
                    if 'strikethrough' in el:
                        prefix += TERM_CODES.STRIKETHROUGH.value
                        suffix = TERM_CODES.RESET.value
                    if 'clickEvent' in el:
                        # clickev = el['clickEvent']
                        # action = clickev['action']
                        # value = clickev['value']
                        # print("{}: {}".format(action, value))
                        links.append(el['clickEvent'])
                    if 'color' in el:
                        color = el['color']
                        if color in COLORSTR2TERMCODE:
                            prefix = COLORSTR2TERMCODE[color].value
                            suffix = TERM_CODES.RESET.value
                        else:
                            print("ERROR: Color {} unmatched!".format(color))
                    string += prefix + el['text'] + suffix
                elif type(el) is str:
                    string += el
                else:
                    print("ERROR: No clue what this is: {}".format(el))
                    print(jsn)
        # &00&88&77&ff&44&cc&22&aa&66&ee&11&99&55&dd&33&bb
        for old_col in OLDCOLOR2COLORSTR.keys():
            string = string.replace(old_col, COLORSTR2TERMCODE[OLDCOLOR2COLORSTR[old_col]].value)
        return string, links


class TERM_CODES(Enum):
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    LIGHT_GRAY = '\033[37m'
    DARK_GRAY = '\033[90m'
    LIGHT_RED = '\033[91m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_YELLOW = '\033[93m'
    LIGHT_BLUE = '\033[94m'
    LIGHT_MAGENTA = '\033[95m'
    LIGHT_CYAN = '\033[96m'
    WHITE = '\033[97m'

    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    OVERLINE = '\033[6m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'

    RESET = '\033[m'


COLORSTR2TERMCODE = {
    'black': TERM_CODES.BLACK,
    'red': TERM_CODES.LIGHT_RED,
    'green': TERM_CODES.LIGHT_GREEN,
    'yellow': TERM_CODES.LIGHT_YELLOW,
    'blue': TERM_CODES.LIGHT_BLUE,
    'light_purple': TERM_CODES.LIGHT_MAGENTA,
    'aqua': TERM_CODES.LIGHT_CYAN,
    'gray': TERM_CODES.LIGHT_GRAY,
    'dark_gray': TERM_CODES.DARK_GRAY,
    'dark_red': TERM_CODES.RED,
    'dark_green': TERM_CODES.GREEN,
    'gold': TERM_CODES.YELLOW,
    'dark_blue': TERM_CODES.BLUE,
    'dark_purple': TERM_CODES.MAGENTA,
    'dark_aqua': TERM_CODES.CYAN,
    'white': TERM_CODES.WHITE,
    'reset': TERM_CODES.RESET
    # 'black': TERM_CODES.BLACK,
    # 'red': TERM_CODES.RED,
    # 'green': TERM_CODES.GREEN,
    # 'yellow': TERM_CODES.YELLOW,
    # 'blue': TERM_CODES.BLUE,
    # 'light_purple': TERM_CODES.MAGENTA,
    # 'aqua': TERM_CODES.CYAN,
    # 'gray': TERM_CODES.LIGHT_GRAY,
    # 'dark_gray': TERM_CODES.DARK_GRAY,
    # 'dark_red': TERM_CODES.LIGHT_RED,
    # 'dark_green': TERM_CODES.LIGHT_GREEN,
    # 'gold': TERM_CODES.LIGHT_YELLOW,
    # 'dark_blue': TERM_CODES.LIGHT_BLUE,
    # 'dark_purple': TERM_CODES.LIGHT_MAGENTA,
    # 'dark_aqua': TERM_CODES.LIGHT_CYAN,
    # 'white': TERM_CODES.WHITE
}

OLDCOLOR2COLORSTR = {
    '§0': 'black',
    '§8': 'dark_gray',
    '§7': 'gray',
    '§f': 'white',
    '§4': 'dark_red',
    '§c': 'red',
    '§2': 'dark_green',
    '§a': 'green',
    '§6': 'gold',
    '§e': 'yellow',
    '§1': 'dark_blue',
    '§9': 'blue',
    '§5': 'dark_purple',
    '§d': 'light_purple',
    '§3': 'dark_aqua',
    '§b': 'aqua',
    '§n': 'reset'
}


class Chat2StdOutSink(ChatSink):
    """
    Prints every text message when forwarded.
    """
    def __init__(self, connection: Connection):
        super().__init__(connection)

    def receive_chat_packet(self, position: str, json_data: dict, formatted_string: str, plain_string: str, links: List[Dict[str, str]]):
        """
        Consumes chat message and prints it.
        :param position: The position of the chat message
        :param json_data: The json dict with all the raw data
        :param formatted_string: The formatted string
        :param plain_string: The unformatted string
        :param links: List of links found in the string. Dict with action and value as fields.
        """
        print("{}: {}".format(position, formatted_string))
        for link in links:
            print("Link: {}: {}".format(link['action'], link['value']))


class ToFileSink(ChatSink):
    def __init__(self, connection: Connection, sinkfilename="sinkedChat.txt"):
        super().__init__(connection)
        self.sinkfilename = sinkfilename

    def receive_chat_packet(self, position, json_data, formatted_string, plain_string, links):
        """
        Consumes chat message and saves it to a file.
        :param position: The position of the chat message
        :type position: str
        :param json_data: The json dict with all the raw data
        :type json_data: dict
        :param formatted_string: The formatted string
        :type formatted_string: str
        :param plain_string: The unformatted string
        :type plain_string: str
        :param links: List of links found in the string. Dict with action and value as fields.
        :type links: list
        """
        packetmock = {
            "json_data": json_data,
            "position": position
        }
        with open(self.sinkfilename, 'a') as sinkfile:
            sinkfile.write(json.dumps(packetmock) + '\n')


class SinkFileReader():
    def __init__(self, sinkfilename="sinkedChat.txt"):
        self.sinkfilename = sinkfilename
        self.chatpackets = []
        self.callback = None

    def read_file(self):
        """
        Reads the sink file and loads the chat messages.
        """
        with open(self.sinkfilename, 'r') as sinkfile:
            lines = sinkfile.readlines()
        lines.reverse()
        for line in lines:
            jsn = json.loads(line)
            chatpacket = cplay.ChatMessagePacket()
            chatpacket.set_values(
                json_data=json.dumps(jsn['json_data']),
                position=jsn['position']
            )
            self.chatpackets.append(chatpacket)

    def register_packet_listener(self, callback, packet, **kwargs):
        """
        Mocks connection.
        :param callback: The callback function for the packet
        :param packet: The packet to filter for
        :param kwargs: others
        """
        self.callback = callback

    def dispatch(self):
        """
        Dispatches a chat message to the listener.
        :return: Whether there are still messages to dispatch.
        :rtype: bool
        """
        self.callback(self.chatpackets.pop())
        return len(self.chatpackets) != 0
