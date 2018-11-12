"""
This module is the focal point of the DC bot
"""

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

class Bot(object):
    """
    Base class for Bots. Prints every text message, when forwarded.
    """
    conn = None

    def __init__(self, connection):
        """
        Sets up a bot
        :param connection: The connection to be used
        :type connection: Connection
        """
        self.conn = connection
        self.conn.register_packet_listener(self._read_chat, cplay.ChatMessagePacket)

    def _read_chat(self, packet):
        """
        Reads an incoming chat packet and prints it
        :param packet: The packet to read
        :type packet: cplay.ChatMessagePacket
        """
        pos = packet.field_string('position')
        jsn = json.loads(packet.json_data)
        fmt_string, links = self._to_string(jsn)
        string = re.compile(r"\033\[\d{2}m").sub("", fmt_string)

        self._chat_sink(pos, jsn, fmt_string, string, links)

    def _chat_sink(self, position, json_data, formatted_string, plain_string, links):
        """
        Consumes chat message. Must be overwritten
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
        raise NotImplementedError("Must be overwritten by subclass.")

    def _to_string(self, jsn):
        """
        Converts a JSON object from chat messages to a string.
        :param jsn: The json data from the chat message
        :type jsn: dict
        :return: The converted string
        :rtype: str, list
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

class DCBot(Bot):
    def __init__(self, connection):
        super().__init__(connection)

    def _chat_sink(self, position, json_data, formatted_string, plain_string, links):
        """
        Consumes chat message. Must be overwritten
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
        print("{}: {}".format(position[0], formatted_string))
        for link in links:
            print("Link: {}: {}".format(link['action'], link['value']))
