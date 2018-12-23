import unittest
from minecraft.sink.sink import *


class ChatMessageClassifier(unittest.TestCase):

    conn = None

    def setUp(self):
        self.conn = SinkFileReader()
        self.conn.read_file()

    def test_chat_cassification(self):
        sink = Chat2StdOutSink(self.conn)
        while self.conn.dispatch():
            pass
