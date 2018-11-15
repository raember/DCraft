import unittest
from minecraft.sink.Sink import *


class ChatMessageClassifier(unittest.TestCase):

    conn = None

    def setUp(self):
        self.conn = SinkFileReader()
        self.conn.read_file()

    def test_chat_cassification(self):
        sink = NormalSink(self.conn)
        while self.conn.dispatch():
            pass
