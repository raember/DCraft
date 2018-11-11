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

DC_IP = "172.106.14.42"

class Bot(object):
    """
    Base class for Bots. Prints ever text message, when forwarded.
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

        print("{}: {}".format(pos[1], self._to_string(jsn)))

    def _to_string(self, jsn):
        """
        Converts a JSON object from chat messages to a string.
        :param jsn: The json data from the chat message
        :type jsn: dict
        :return: The converted string
        :rtype: str
        """
        print(jsn)
        string = ''
        if 'text' in jsn:
            string = jsn['text']
        if 'extra' in jsn:
            for el in jsn['extra']:
                if el is dict:
                    if 'color' in el:
                        string += self._to_color(el)
                    else:
                        print("Unexpectedly not colored text: {}".format(el))
                elif el is str:
                    string += el
                else:
                    print("No clue what this is: {}".format(el))
        return string

    def _to_color(self, jsn):
        """
        Converts a colored text json object into a string.
        :param jsn: The colored text
        :type jsn: dict
        :return: The string
        :rtype: str
        """
        color = jsn['color']
        color2escape = {
            'black': '\033[30m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'purple': '\033[35m',
            'aqua': '\033[36m',
            'gray': '\033[37m',
            'dark_gray': '\033[90m',
            'dark_red': '\033[91m',
            'dark_green': '\033[92m',
            'gold': '\033[93m',
            'dark_blue': '\033[94m',
            'light_purple': '\033[95m',
            'dark_aqua': '\033[96m',
            'white': '\033[97m'
        }
        if color not in color2escape:
            print("ERROR: Color {} unmatched!".format(color))
            return jsn['text']
        string = color2escape[color]
        # if 'strikethrough' in jsn:
        #     string = "\033[{}"
        return "{}{}\033[m".format(string, jsn['text'])
