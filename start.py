#!/usr/bin/env python

from __future__ import print_function

import getpass
import sys
import re
from optparse import OptionParser

from Configuration import Configuration
from minecraft import authentication
from minecraft.bot.bot import Bot
from minecraft.config import AppConfig, PlayerConfig
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound
from minecraft.compat import input
from minecraft.player import McLeaksPlayer, Player
from minecraft.sink.sink import DC_IP


def main():
    config = AppConfig()
    config.load()
    server = config[AppConfig.Keys.SERVER][AppConfig.Keys.SERVER_ADDRESS]
    server_port = config[AppConfig.Keys.SERVER][AppConfig.Keys.SERVER_PORT]
    players = []
    for player_dict in config[AppConfig.Keys.PLAYERS]:
        if PlayerConfig.Keys.ALTTOKEN in player_dict and len(player_dict[PlayerConfig.Keys.ALTTOKEN]) > 0:
            saved_player = McLeaksPlayer.deserialize(player_dict)
            saved_player.set_server(server)
        else:
            saved_player = Player.deserialize(player_dict)
        players.append(saved_player)
    if len(players) > 1:
        print("Please choose one of the following users:")
        index = 0
        for saved_player in players:
            print("{}: {} ({})".format(index, saved_player.profile['name'], saved_player.username))
            index += 1
        index = int(input("> "))
        player = players[index]
    else:
        player = players[0]
    auth_token = player.login('obVO6vo6v56iv8oh9o78i6kbKjtvJ878')
    if not auth_token:
        print("Couldn't login")
        exit(1)
    print("Logged in as %s..." % auth_token.username)
    print(auth_token.profile.to_dict())
    print(auth_token.client_token)
    print(auth_token.access_token)
    if type(auth_token) == authentication.MCLeaksAuthenticationToken:
        print(auth_token.session)
    config[AppConfig.Keys.PLAYERS] = []
    for saved_player in players:
        config[AppConfig.Keys.PLAYERS].append(saved_player.serialize())
    config.save()
    print("Saved player data.")
    connection = Connection(server, server_port, auth_token=auth_token)
    bot = Bot(connection)
    connection.connect()
    while bot.read_input():
        pass

    # if options.dump_packets:
    #     def print_incoming(packet):
    #         if type(packet) is Packet:
    #             # This is a direct instance of the base Packet type, meaning
    #             # that it is a packet of unknown type, so we do not print it.
    #             return
    #         print('--> %s' % packet, file=sys.stderr)
    #
    #     def print_outgoing(packet):
    #         print('<-- %s' % packet, file=sys.stderr)
    #
    #     connection.register_packet_listener(
    #         print_incoming, Packet, early=True)
    #     connection.register_packet_listener(
    #         print_outgoing, Packet, outgoing=True)
    #
    # def handle_join_game(join_game_packet):
    #     print('Connected.')
    #
    # connection.register_packet_listener(
    #     handle_join_game, clientbound.play.JoinGamePacket)
    #
    # def print_chat(chat_packet):
    #     print("Message (%s): %s" % (
    #         chat_packet.field_string('position'), chat_packet.json_data))
    #
    # connection.register_packet_listener(
    #     print_chat, clientbound.play.ChatMessagePacket)
    # printingSink = NormalSink(connection)
    # toFileSink = ToFileSink(connection)


if __name__ == "__main__":
    main()
