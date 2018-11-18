#!/usr/bin/env python

from __future__ import print_function

import getpass
import sys
import re
import argparse
import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-4s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
from minecraft import authentication
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound
from minecraft.compat import input
from minecraft.sink.Sink import DC_IP, NormalSink, ToFileSink


class Main:
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        parser = argparse.ArgumentParser()
        parser.add_argument('p', 'profile', action='store',
                            help='Loads profile from specific config file.')
        parser.add_argument('c', 'config', action='store_true',
                            help='Loads configuration from the config file.')
        self.args = parser.parse_args()

    def main(self):
        options = self.args

        if options.offline:
            print("Connecting in offline mode...")
            connection = Connection(
                options.address, options.port, username=options.username)
        else:
            # auth_token = authentication.AuthenticationToken()
            auth_token = authentication.MCLeaksAuthenticationToken(server=options.address)
            # auth_token.server = options.address
            try:
                auth_token.authenticate(options.username, options.password)
            except YggdrasilError as e:
                print(e)
                sys.exit()
            print("Logged in as %s..." % auth_token.username)
            connection = Connection(
                options.address, options.port, auth_token=auth_token)

        if options.dump_packets:
            def print_incoming(packet):
                if type(packet) is Packet:
                    # This is a direct instance of the base Packet type, meaning
                    # that it is a packet of unknown type, so we do not print it.
                    return
                print('--> %s' % packet, file=sys.stderr)

            def print_outgoing(packet):
                print('<-- %s' % packet, file=sys.stderr)

            connection.register_packet_listener(
                print_incoming, Packet, early=True)
            connection.register_packet_listener(
                print_outgoing, Packet, outgoing=True)

        def handle_join_game(join_game_packet):
            print('Connected.')

        connection.register_packet_listener(
            handle_join_game, clientbound.play.JoinGamePacket)

        # def print_chat(chat_packet):
        #     print("Message (%s): %s" % (
        #         chat_packet.field_string('position'), chat_packet.json_data))
        #
        # connection.register_packet_listener(
        #     print_chat, clientbound.play.ChatMessagePacket)
        printingSink = NormalSink(connection)
        # toFileSink = ToFileSink(connection)
        connection.connect()

        while True:
            try:
                text = input('>')
                if text == "/respawn":
                    print("respawning...")
                    packet = serverbound.play.ClientStatusPacket()
                    packet.action_id = serverbound.play.ClientStatusPacket.RESPAWN
                    connection.write_packet(packet)
                else:
                    packet = serverbound.play.ChatPacket()
                    packet.message = text
                    connection.write_packet(packet)
            except KeyboardInterrupt:
                print("Bye!")
                sys.exit()


if __name__ == "__main__":
    Main().main()
