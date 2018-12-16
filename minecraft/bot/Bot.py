import json
import re
from enum import Enum
from typing import List, Dict, Tuple

from minecraft.networking.packets import Packet
from minecraft.networking.packets.clientbound import play as cplay
from minecraft.networking.packets.serverbound import play as splay
from minecraft.networking.connection import Connection
from minecraft.sink.Sink import Sink, ChatSink

from minecraft.networking.types import (
    Integer, FixedPointInteger, UnsignedByte, Byte, Boolean, UUID, Short,
    VarInt, Double, Float, String, Enum,
)

class Bot():
    def __init__(self, connection: Connection):
        self.connection = connection
        self.connection.register_packet_listener(self._receive_chat_message, cplay.ChatMessagePacket)
        self.connection.register_packet_listener(self._receive_join_game, cplay.JoinGamePacket)
        self.connection.register_packet_listener(self._receive_player_list_item, cplay.PlayerListItemPacket)
        self.connection.register_packet_listener(self._receive_disconnect, cplay.DisconnectPacket)

    def read_input(self) -> bool:
        try:
            return self.process_input(input('>'))
        except KeyboardInterrupt:
            print("Bye!")
            return False

    def process_input(self, string: str) -> bool:
        if string == '/respawn':
            print("respawning...")
            packet = splay.ClientStatusPacket()
            packet.action_id = splay.ClientStatusPacket.RESPAWN
            self.connection.write_packet(packet)
        else:
            packet = splay.ChatPacket()
            packet.message = string
            self.connection.write_packet(packet)
        return True

    def _receive_chat_message(self, packet: cplay.ChatMessagePacket):
        """
        Reads an incoming chat packet.
        :param packet: The chat packet to read
        """
        pos = packet.field_string('position')
        jsn = json.loads(packet.json_data)
        fmt_string, links = self._dict_to_string(jsn)
        string = re.compile(r"\033\[\d{2}?m").sub("", fmt_string)
        self.receive_chat_message(pos, jsn, fmt_string, string, links)

    def receive_chat_message(self, position: str, json_data: dict, formatted_string: str, plain_string: str,
                             links: List[Dict[str, str]]):
        """
        Consumes chat message. Must be overwritten
        :param position: The position of the chat message
        :param json_data: The json dict with all the raw data
        :param formatted_string: The formatted string
        :param plain_string: The unformatted string
        :param links: List of links found in the string. Dict with action and value as fields.
        """
        print("{}: {}".format(position, formatted_string))
        for link in links:
            print("Link: {}: {}".format(link['action'], link['value']))

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
                        prefix += TerminalCodes.ITALIC
                        suffix = TerminalCodes.RESET
                    if 'strikethrough' in el:
                        prefix += TerminalCodes.STRIKETHROUGH
                        suffix = TerminalCodes.RESET
                    if 'clickEvent' in el:
                        # clickev = el['clickEvent']
                        # action = clickev['action']
                        # value = clickev['value']
                        # print("{}: {}".format(action, value))
                        links.append(el['clickEvent'])
                    if 'color' in el:
                        color = el['color']
                        if color in COLORSTR2TERMCODE:
                            prefix = COLORSTR2TERMCODE[color]
                            suffix = TerminalCodes.RESET
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
            string = string.replace(old_col, COLORSTR2TERMCODE[OLDCOLOR2COLORSTR[old_col]])
        return string, links

    def _receive_join_game(self, packet: cplay.JoinGamePacket):
        entity_id: Integer = packet.entity_id
        game_mode: UnsignedByte = packet.game_mode
        dimension: Integer = packet.dimension
        difficulty: UnsignedByte = packet.difficulty
        max_players: UnsignedByte = packet.max_players
        level_type: String = packet.field_string('level_type')
        reduced_debug_info: Boolean = packet.reduced_debug_info
        self.receive_join_game(entity_id, game_mode, dimension, difficulty, max_players, level_type, reduced_debug_info)

    def receive_join_game(self, entity_id: int, game_mode: int, dimension: int, difficulty: int, max_players: int, level_type: str, reduced_debug_info: bool):
        print('Joined game')

    def _receive_player_list_item(self, packet: cplay.PlayerListItemPacket):
        # print("PlayerListItem({}): {}".format(packet.action_type, packet.actions))
        if packet.action_type == cplay.PlayerListItemPacket.AddPlayerAction:
            packet: cplay.PlayerListItemPacket.AddPlayerAction = packet.actions[0]
            # print(packet.__dict__)
            props = {}
            for prop in packet.properties:
                props[prop.name] = prop.value
            print("Added player: {} ({}) GM{}".format(packet.display_name, props, packet.gamemode))
        elif packet.action_type == 1:
            packet: cplay.PlayerListItemPacket.UpdateGameModeAction = packet.actions[0]
            print("Updated game mode: {} for {}".format(packet.gamemode, packet.uuid))
        elif packet.action_type == 2:
            packet: cplay.PlayerListItemPacket.UpdateLatencyAction = packet.actions[0]
            print("Updated latency: {} for {}".format(packet.ping, packet.uuid))
        elif packet.action_type == 3:
            packet: cplay.PlayerListItemPacket.UpdateDisplayNameAction = packet.actions[0]
            print("Updated display name: {} for {}".format(packet.display_name, packet.uuid))
        elif packet.action_type == 4:
            packet: cplay.PlayerListItemPacket.RemovePlayerAction = packet.actions[0]
            print("Removed player: {}".format(packet.uuid))

    def _receive_disconnect(self, packet: cplay.DisconnectPacket):
        jsn = json.loads(packet.json_data)
        string = self._dict_to_string(jsn)
        raise Exception("Disconnected: {}".format(string))


class TerminalCodes(Enum):
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
    'black': TerminalCodes.BLACK,
    'red': TerminalCodes.LIGHT_RED,
    'green': TerminalCodes.LIGHT_GREEN,
    'yellow': TerminalCodes.LIGHT_YELLOW,
    'blue': TerminalCodes.LIGHT_BLUE,
    'light_purple': TerminalCodes.LIGHT_MAGENTA,
    'aqua': TerminalCodes.LIGHT_CYAN,
    'gray': TerminalCodes.LIGHT_GRAY,
    'dark_gray': TerminalCodes.DARK_GRAY,
    'dark_red': TerminalCodes.RED,
    'dark_green': TerminalCodes.GREEN,
    'gold': TerminalCodes.YELLOW,
    'dark_blue': TerminalCodes.BLUE,
    'dark_purple': TerminalCodes.MAGENTA,
    'dark_aqua': TerminalCodes.CYAN,
    'white': TerminalCodes.WHITE,
    'reset': TerminalCodes.RESET
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


class DcBot(Bot):

    def receive_chat_message(self, position: str, json_data: dict, formatted_string: str, plain_string: str,
                             links: List[Dict[str, str]]):
        """
        Consumes chat message. Must be overwritten
        :param position: The position of the chat message
        :param json_data: The json dict with all the raw data
        :param formatted_string: The formatted string
        :param plain_string: The unformatted string
        :param links: List of links found in the string. Dict with action and value as fields.
        """
        print("{}: {}".format(position, formatted_string))
        for link in links:
            print("Link: {}: {}".format(link['action'], link['value']))
